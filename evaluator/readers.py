#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Different readers for different file formats, readers output CorpusInstance s

author: weissenh
test environment: Ubuntu 20.04, Python 3.7
date: April 2020
"""

# todo: more readers (also for opennmt file format?), maybe turn into classes?
# todo: test/implement opennmt reader
# todo: demo should test more readers
# todo: documentation missing

import csv  # reading TSV files
import sys
import os
from corpus_instance import CorpusInstance


def check_input_files_existance(input_files: list) -> None:
    # raises Error if one of the files is not found (input_files: List[str] )
    for file_path in input_files:
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
    return


def get_samples(file_path: str):  # -> Iterator
    """
    For each line yield a CorpusInstance

    :param file_path: Path to TSV file as input
    :return: Iterator of CorpusInstance
    """
    # todo should we have the line number here or not?
    check_input_files_existance([file_path])
    with open(file_path, encoding='utf-8', mode='r') as infile:
        for line_num, row in enumerate(csv.reader(infile, delimiter="\t")):
            sentence, representation, gen_type_required = row
            yield CorpusInstance(sentence=sentence,
                                 logical_form=representation,
                                 gen_type_required=gen_type_required,
                                 line_num=line_num)


def get_samples_from_two_files(goldfile: str, systemfile):  # -> Iterator
    # todo should we raise runtime error if files of unequal length???
    # currently just silent
    # todo should we have the line number here or not?
    check_input_files_existance([goldfile, systemfile])
    with open(goldfile, encoding='utf-8', mode='r') as goldf, \
            open(systemfile, encoding='utf-8', mode='r') as systemf:
        goldreader = csv.reader(goldf, delimiter="\t")
        systemreader = csv.reader(systemf, delimiter="\t")
        # for line_num, goldrows, systemrows in enumerate(
        #         zip_longest(goldreader, systemreader, fillvalue=None)):
        #     if goldrows is None or systemrows is None:
        #         raise RuntimeError("Files have unequal number of lines")
        line_num = 0
        # for ln, goldrows, sysrows in enumerate(zip(goldreader, systemreader)):
        for goldrows, sysrows in zip(goldreader, systemreader):
            line_num += 1
            # sentence, representation, gen_type_required = row
            goldsample = CorpusInstance(sentence=goldrows[0],
                                        logical_form=goldrows[1],
                                        gen_type_required=goldrows[2],
                                        line_num=line_num)
            systemsample = CorpusInstance(sentence=sysrows[0],
                                          logical_form=sysrows[1],
                                          gen_type_required=sysrows[2],
                                          line_num=line_num)
            # todo should I test here for equality of first row?
            yield goldsample, systemsample


# todo: test this function (opennmtl files)
def get_samples_from_opennmt_file(opennmtfile: str):
    # assumes: source target model-prediction   tab separated
    # yields goldsample, systemsample pair
    # note: gen_type_required info not available!
    check_input_files_existance([opennmtfile])
    with open(opennmtfile, encoding='utf-8', mode='r') as infile:
        for line_num, row in enumerate(csv.reader(infile, delimiter="\t")):
            source, target, model_pred = row
            yield CorpusInstance(sentence=source,
                                 logical_form=target,
                                 gen_type_required="",
                                 line_num=line_num), \
                  CorpusInstance(sentence=source,
                                 logical_form=model_pred,
                                 gen_type_required="",
                                 line_num=line_num)


def main(argv):
    """
    this should be a small demo for one of the readers

    e.g.
    python3 readers.py ../data/dev.tsv
    """
    if len(argv) != 2:
        print("usage: readers.py TSVFILE")
        return

    file_path = argv[1]
    for lineno, sample in enumerate(get_samples(file_path=file_path)):
        if lineno > 3:  # just a small demo, stop somewhere
            break
        print(f"\nLine no: {sample.line_number}")
        print(f"Generalization type required: {sample.gen_type_required}")
        print(f"Sentence length: {sample.sent_length}")
        # print("Tokens: ", sample.sent_tokens)
    print("Done!")
    return


if __name__ == "__main__":
    main(sys.argv)
