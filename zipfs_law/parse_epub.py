import html
import re

import matplotlib.pyplot as plt
import numpy
import scipy.stats as stats
import spacy
from ebooklib import epub


def get_word_count(epub_title: str):
    book = epub.read_epub(epub_title)
    words_list = []
    for document in book.get_items_of_type(9):
        content = document.get_content().decode("utf-8")
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')

        # Remove HTML tgs
        # Remove well-formed tags, fixing mistakes by legitimate users
        no_tags = tag_re.sub(' ', content)
        # Clean up anything else by escaping
        preprocessed_content = html.escape(no_tags).replace("\n", " ").strip()
        preprocessed_content = re.sub("\s\s+", " ", preprocessed_content)

        if preprocessed_content:
            # print("CONTENT: ", preprocessed_content)
            nlp = spacy.load('en')
            doc = nlp(preprocessed_content)
            # [utils.to_nltk_tree(sentence.root).pretty_print() for sentence in doc.sents]
            for word in doc:
                if word.pos_ not in ["PUNCT", "SYM", "X", "DET", "PART", "SPACE", "INTJ"]:
                    words_list.append(word.text.lower())
    words_set = set(words_list)
    words_count = [(w, words_list.count(w)) for w in words_set]
    return words_count


def wordnet_stats(words_count):
    amb_c_rank = stats.rankdata([c for (w, c) in words_count])
    return amb_c_rank


def generate_plots(amb, amb_c_rank):
    numpy.corrcoef(amb_c_rank, [numpy.math.log(c) for (w, c) in amb])
    rev = [len(amb_c_rank) - r + 1 for r in amb_c_rank]

    plt.plot([numpy.math.log(c) for c in rev], [numpy.math.log(c) for (w, c) in amb], 'ro')
    plt.show()


def zipfs_law_analysis(epub_title: str):
    word_count = get_word_count(epub_title)
    amb_c_rank = wordnet_stats(word_count)
    generate_plots(word_count, amb_c_rank)
