#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unofficial evaluation script for model predictions on COGS

usage: python3 score.py path/to/goldfile path/to/modelfile

call `python3 score.py --help` for more detailed usage info

Assumed input format:
- TSV files (see the `data` directory for examples) with 3 columns: each line
  consists of a natural language sentence, its logical form and some comment
- Logical forms are assumed to follow the syntax used in COGS
- Gold and system files are assumed to have the same ordering of samples,
  i.e. the input sentences (first column) need to match, otherwise that line is
  ignored.

author: weissenh ( piaw@coli.uni-saarland.de )
test environment: Ubuntu 20.04, Python 3.7
date: April 2020
"""

# todo: implement evaluation script

import sys  # for argc,argv and exit
import os
import csv  # for reading TSV files
import argparse


def read_cogs_tsv_file(file_path: str):
    # todo implement
    # todo maybe move to some other file (for reading files)
    assert(os.path.isfile(file_path))
    with open(file_path, encoding='utf-8', mode='r') as infile:
        for line_num, row in enumerate(csv.reader(infile, delimiter="\t")):
            sentence, representation, gen_type_required = row
            # todo or directly iterate over both files?
            # todo need Evaluator and SampleInstance classes?
    raise NotImplementedError


def main(argv):
    """call `python3 score.py --help` for usage info"""
    # todo maybe add output file/stream optional for where to print output to?
    argparser = argparse.ArgumentParser(add_help=True,
        description="evaluate model predictions against gold logical forms")
    argparser.add_argument("--gold", default=None, type=str, required=True,
        help="Path to TSV file with gold standard logical forms")
    argparser.add_argument("--system", default=None, type=str, required=True,
        help="Path to TSV file with system's predictions")
    argparser.add_argument("-v", "--verbose", action="store_true",
                           help="more verbose output")
    args = argparser.parse_args(argv)

    if args.verbose:
        print("Verbosity turned on")

    goldfile, systemfile = args.goldfile, args.systemfile
    if args.verbose:
        print("Gold   file: ", goldfile)
        print("System file: ", systemfile)
    for inputfile in [goldfile, systemfile]:
        # print("Input file: ", inputfile)
        if not os.path.isfile(inputfile):
            raise FileNotFoundError(f"Input file {inputfile} doesn't exist!")

    print("Start evaluating...")
    # todo implement here
    return


if __name__ == "__main__":
    main(sys.argv[1:])  # exclude programme name
