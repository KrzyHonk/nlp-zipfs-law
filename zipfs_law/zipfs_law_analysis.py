import html
import re
from typing import List

import matplotlib.pyplot as plt
import numpy
import scipy.stats as stats
import spacy
from ebooklib import epub
from spacy.tokens.doc import Doc
import json
import datetime
import os
import errno


def zipfs_law_analysis(epub_title: str):
    words_count, pairs_count, triplets_count = __get_word_pair_triple_count(epub_title)

    words_ranked_data = __get_words_count_rank(words_count)
    pairs_ranked_data = __get_pairs_count_rank(pairs_count)
    triplets_ranked_data = __get_triplets_count_rank(triplets_count)

    words_data = zip(words_count, words_ranked_data)
    words_most_common = __get_top_range(words_data)

    pairs_data = zip(pairs_count, pairs_ranked_data)
    pairs_most_common = __get_top_range(pairs_data)

    triplets_data = zip(triplets_count, triplets_ranked_data)
    triplets_most_common = __get_top_range(triplets_data)

    # TODO Ranked data is not serializable to JSON. Find some solution
    json_output = {
        'name': epub_title,
        'words_count': words_count,
        'words_most_common': words_most_common,
        'words_most_common_number': 50,
        'pairs_count': pairs_count,
        'pairs_most_common': pairs_most_common,
        'pairs_most_common_number': 50,
        'triplets_count': triplets_count,
        'triplets_most_common': triplets_most_common,
        'triplets_most_common_number': 50,
    }
    output_directory = "./output/" + epub_title + "/"
    delta = datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)
    timestamp = int(delta.total_seconds() * 1000)
    output_filename = epub_title + str(timestamp)

    try:
        os.makedirs(output_directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    with open(output_directory + output_filename, 'w') as file:
        json.dump(json_output, file)

    __generate_plots(words_count, words_ranked_data, 1, title="Words frequency", xlabel="log(rank)", ylabel="log(count)")
    __generate_plots(pairs_count, pairs_ranked_data, 2, title="Pairs frequency", xlabel="log(rank)", ylabel="log(count)")
    __generate_plots(triplets_count, triplets_ranked_data, 3, title="Triplets frequency", xlabel="log(rank)", ylabel="log(count)")
    plt.show()


def __get_word_pair_triple_count(epub_title: str):
    book = epub.read_epub(epub_title + ".epub")
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
        # split = re.compile('^[a-zA-Z0-9\']+$').findall(preprocessed_content)
        if preprocessed_content:
            # print("CONTENT: ", preprocessed_content)
            nlp = spacy.load('en')
            doc = nlp(preprocessed_content)
            # [utils.to_nltk_tree(sentence.root).pretty_print() for sentence in doc.sents]
            for word in doc:
                if word.pos_ in ["ADJ", "VERB", "CONJ", "DET", "NUM", "ADV", "ADP", "NOUN", "PROPN", "PRON"]:
                    words_list.append(word.text.lower())
            pairs_list = pairs_list + __extract_word_pairs(doc)
            triplets_list = triplets_list + __extract_word_triplets(doc)

    words_set = set(words_list)
    words_count = [(w, words_list.count(w)) for w in words_set]

    pairs_set = set(pairs_list)
    pairs_count = [(p, pairs_list.count(p)) for p in pairs_set]

    triplets_set = set(triplets_list)
    triplets_count = [(t, triplets_list.count(t)) for t in triplets_set]

    return words_count, pairs_count, triplets_count


def __extract_word_pairs(doc: Doc) -> List:
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


def __extract_word_triplets(doc: Doc) -> List:
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


def __get_words_count_rank(words_count):
    words_count_rank = stats.rankdata([count for (word, count) in words_count])
    return words_count_rank


def __get_pairs_count_rank(pairs_count):
    pair_count_rank = stats.rankdata([count for (pair, count) in pairs_count])
    return pair_count_rank


def __get_triplets_count_rank(triplets_count):
    triplets_count_rank = stats.rankdata([count for (triple, count) in triplets_count])
    return triplets_count_rank


def __generate_plots(counts_data, ranks_data, number=1, title="", xlabel="", ylabel="", plot_type ='ro'):
    numpy.corrcoef(ranks_data, [numpy.math.log(count) for (word, count) in counts_data])
    ranks_range = [len(ranks_data) - rank + 1 for rank in ranks_data]

    plt.figure(number)
    plt.plot([numpy.math.log(rank) for rank in ranks_range], [numpy.math.log(count) for (word, count) in counts_data], plot_type)
    plt.draw()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)


def __get_top_range(ranked_data, limit=50):
    sorted_data = sorted(ranked_data, reverse=True, key=lambda count: count[0][1])
    return sorted_data[0:limit]
