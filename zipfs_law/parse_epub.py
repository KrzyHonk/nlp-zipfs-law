import html
import re
from typing import List

import matplotlib.pyplot as plt
import numpy
import scipy.stats as stats
import spacy
from ebooklib import epub
from spacy.tokens.doc import Doc


def get_word_pair_triple_count(epub_title: str):
    book = epub.read_epub(epub_title)
    words_list = []
    pairs_list = []
    triplets_list = []
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
            pairs_list = pairs_list + extract_word_pairs(doc)
            triplets_list = triplets_list + extract_word_triplets(doc)

    words_set = set(words_list)
    words_count = [(w, words_list.count(w)) for w in words_set]

    pairs_set = set(pairs_list)
    pairs_count = [(p, pairs_list.count(p)) for p in pairs_set]

    triplets_set = set(triplets_list)
    triplets_count = [(t, triplets_list.count(t)) for t in triplets_set]

    return words_count, pairs_count, triplets_count


def extract_word_pairs(doc: Doc) -> List:
    first = None
    second = None
    output = []
    for index, word in enumerate(doc):
        if index == 0:
            second = word.text
        else:
            first = second
            second = word.text
            output.append((first, second))
    return output


def extract_word_triplets(doc: Doc) -> List:
    first = None
    second = None
    third = None
    output = []
    for index, word in enumerate(doc):
        if index == 0:
            third = word.text
        elif index == 1:
            second = third
            third = word.text
        else:
            first = second
            second = third
            third = word.text
            output.append((first, second, third))
    return output


def get_words_count_rank(words_count):
    words_count_rank = stats.rankdata([c for (w, c) in words_count])
    return words_count_rank


def get_pairs_count_rank(words_count):
    words_count_rank = stats.rankdata([c for (w, c) in words_count])
    return words_count_rank


def get_triplets_count_rank(words_count):
    words_count_rank = stats.rankdata([c for (w, c) in words_count])
    return words_count_rank

def generate_plots(amb, amb_c_rank):
    numpy.corrcoef(amb_c_rank, [numpy.math.log(c) for (w, c) in amb])
    rev = [len(amb_c_rank) - r + 1 for r in amb_c_rank]

    plt.plot([numpy.math.log(c) for c in rev], [numpy.math.log(c) for (w, c) in amb], 'ro')
    plt.show()


def print_most_fifty(words_count):
    for (w, c) in words_count:
        print((w, c))


def zipfs_law_analysis(epub_title: str):
    words_count, pairs_count, triplets_count = get_word_pair_triple_count(epub_title)
    amb_c_rank = get_words_count_rank(words_count)
    generate_plots(words_count, amb_c_rank)
    # print_most_fifty(word_count)
