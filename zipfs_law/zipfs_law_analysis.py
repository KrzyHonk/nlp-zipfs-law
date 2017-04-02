import errno
import json
import multiprocessing as mp
import os
import queue
import re
import threading
from typing import List

import matplotlib.pyplot as plt
import numpy
import scipy.stats as stats


def zipfs_law_analysis(book_title: str, author: str = "", series=""):
    words_count, pairs_count, triplets_count = __get_word_pair_triple_count(book_title, author, series)

    json_output = {
        'title': book_title,
        'author': author,
        'series': series,
        'words_count': words_count,
        'pairs_count': pairs_count,
        'triplets_count': triplets_count,
    }

    output_directory = "./output/" + book_title + "/"
    output_filename = book_title + ".json"

    try:
        os.makedirs(output_directory)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    with open(output_directory + output_filename, 'w') as file:
        json.dump(json_output, file)
    print("Analysis of " + book_title + " finished")


def __get_word_pair_triple_count(epub_title: str, author: str = "", series: str = ""):
    regex = re.compile('[a-zA-z0-9\-\'`]+')
    content = None
    with open(author + "/" + series + "/" + epub_title + ".txt", 'r') as file:
        content = file.read()
    words_list = []
    pairs_list = []
    triplets_list = []
    if content:
        tmp_word_list = regex.findall(content.lower())
        words_list.extend(tmp_word_list)

        cores = mp.cpu_count()
        words_number = len(tmp_word_list)
        split_point = (int)(words_number / cores)

        index = 0
        split = split_point
        threads = []
        work_queue = queue.Queue()
        for proc in range(1, cores + 1):
            if proc == cores:
                split = words_number
                arg = tmp_word_list[index:split]
                thread = PairsThread(arg, work_queue)
                thread.start()
                threads.append(thread)
            else:
                arg = tmp_word_list[index:(split + 1)]
                thread = PairsThread(arg, work_queue)
                thread.start()
                threads.append(thread)
                index = split
                split += split_point

        for t in threads:
            t.join()
        pairs_list.extend(work_queue.get())

        index = 0
        split = split_point
        threads = []
        work_queue = queue.Queue()
        for proc in range(1, cores + 1):
            if proc == cores:
                split = words_number
                arg = tmp_word_list[index:split]
                thread = TripletsThread(arg, work_queue)
                thread.start()
                threads.append(thread)
            else:
                arg = tmp_word_list[index:(split + 2)]
                thread = TripletsThread(arg, work_queue)
                thread.start()
                threads.append(thread)
                index = split
                split += split_point

            for t in threads:
                t.join()
            triplets_list.extend(work_queue.get())

    words_set = set(words_list)
    words_count = [{"w": w, "c": words_list.count(w)} for w in words_set]

    pairs_set = set(pairs_list)
    pairs_count = [{"w": p, "c": pairs_list.count(p)} for p in pairs_set]

    triplets_set = set(triplets_list)
    triplets_count = [{"w": t, "c": triplets_list.count(t)} for t in triplets_set]

    return words_count, pairs_count, triplets_count


def __get_words_count_rank(words_count):
    words_count_rank = stats.rankdata([count for (word, count) in words_count])
    return words_count_rank


def __get_pairs_count_rank(pairs_count):
    pair_count_rank = stats.rankdata([count for (pair, count) in pairs_count])
    return pair_count_rank


def __get_triplets_count_rank(triplets_count):
    triplets_count_rank = stats.rankdata([count for (triple, count) in triplets_count])
    return triplets_count_rank


def __generate_plots(counts_data, ranks_data, number=1, title="", xlabel="", ylabel="", plot_type='ro'):
    numpy.corrcoef(ranks_data, [numpy.math.log(count) for (word, count) in counts_data])
    ranks_range = [len(ranks_data) - rank + 1 for rank in ranks_data]

    plt.figure(number)
    plt.plot([numpy.math.log(rank) for rank in ranks_range], [numpy.math.log(count) for (word, count) in counts_data],
             plot_type)
    plt.draw()
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)


def __get_top_range(ranked_data, limit=50):
    sorted_data = sorted(ranked_data, reverse=True, key=lambda count: count[0][1])
    return sorted_data[0:limit]


class PairsThread(threading.Thread):
    def __init__(self, words_list: List, result: queue.Queue):
        threading.Thread.__init__(self)
        self.words_list = words_list
        self.result = result

    def run(self):
        second = None
        output = []
        for index, word in enumerate(self.words_list):
            if index == 0:
                second = word
            else:
                first = second
                second = word
                output.append((first, second))
        self.result.put(output)


class TripletsThread(threading.Thread):
    def __init__(self, words_list: List, result: queue.Queue):
        threading.Thread.__init__(self)
        self.words_list = words_list
        self.result = result

    def run(self):
        second = None
        third = None
        output = []
        for index, word in enumerate(self.words_list):
            if index == 0:
                third = word
            elif index == 1:
                second = third
                third = word
            else:
                first = second
                second = third
                third = word
                output.append((first, second, third))
        self.result.put(output)
