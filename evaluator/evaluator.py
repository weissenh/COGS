#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unofficial evaluation script for model predictions on COGS

usage: python3 evaluator.py path/to/goldfile path/to/modelfile

call `python3 evaluator.py --help` for more detailed usage info

Assumed input format:
- TSV files (see the `data` directory for examples) with 3 columns: each line
  consists of a natural language sentence, its logical form and some comment
- Logical forms are assumed to follow the syntax used in COGS
- Gold and system files are assumed to have the same ordering of samples,
  i.e. the input sentences (first column) need to match, otherwise that line is
  ignored.

author: weissenh
test environment: Ubuntu 20.04, Python 3.7
date: April 2021
"""

# todo: add option to specify output file
# todo: summarize evaluation results for each 3rd row type (in_distrib, ...)
# todo: (maybe) let evaluator get list of metrics at initialization?

import sys  # for argc,argv and exit
import os
import argparse
from tqdm import tqdm

from readers import CorpusInstance, get_samples_from_two_files
from metrics import ExactMatchAccuracy, WellFormednessPercentage, \
    OrderInvariantExactMatchAccuracy, TokenLevelEditDistance


class Evaluator:
    """
    Evaluator is responsible for updating metrics and printing final results

    The evaluator updates metrics while it sees more samples, and ultimately
    can print evaluation metric results on the full dataset.
    """

    def __init__(self, gold_file: str, system_file: str, verbose=False):
        self.gold_file = gold_file
        self.system_file = system_file
        self.verbose = verbose
        self.num_seen_samples = 0
        self.metrics = [
            ExactMatchAccuracy(),
            WellFormednessPercentage(),
            OrderInvariantExactMatchAccuracy(),
            TokenLevelEditDistance()
        ]
        if self.verbose:
            print("Sentence wise evaluation results")
            self.print_sentence_evaluation_header()
        # todo implement: read here or make it external?

    def update_counts(self, gold: CorpusInstance, system: CorpusInstance):
        # if sentence don't match, meaningless comparison:
        assert(gold.is_same_sentence(system))
        self.num_seen_samples += 1  # todo what if duplicate?
        sent_scores = list()
        for metric in self.metrics:
            sent_score = metric.update(gold=gold, system=system)
            if self.verbose:
                sent_scores.append(sent_score)
        if self.verbose:
            self.print_sentence_evaluation(sent_scores, gold.logical_form_str,
                                           system.logical_form_str)
        return

    def print_sentence_evaluation_header(self) -> None:
        print("\t".join([f"{m.get_abbreviation():<6}" for m in self.metrics] +
                        ["System logical form", "Gold logical form"]))

    def print_sentence_evaluation(self, sent_scores: list,
                                  goldlf: str, syslf: str) -> None:
        # keep this parallel to header printed (see method above)
        # watch out: system LF printed before gold
        print("\t".join([f"{s:>6.2f}" for s in sent_scores]+[syslf, goldlf]))

    def print_overall_results(self) -> None:
        """Print evaluation results based on the whole corpus seen so far"""
        print(f"Gold file:   {self.gold_file}")
        print(f"System file: {self.system_file}")
        print(f"Seen instances: {self.num_seen_samples}")
        for metric in self.metrics:
            if metric.get_name() == "Avg. token-level edit distance":
                print(f"{metric.get_name():<40} : {metric.get_score():>6.2f}")
                continue
            print(f"{metric.get_name():<40} : {metric.get_score()*100:>6.2f} %")
        return


def main(argv):
    """call `python3 evaluator.py --help` for usage info"""
    # todo maybe add output file/stream optional for where to print output to?
    argparser = argparse.ArgumentParser(add_help=True,
        description="evaluate model predictions against gold logical forms")
    argparser.add_argument("--gold", default=None, type=str, required=True,
        help="Path to TSV file with gold standard logical forms")
    argparser.add_argument("--system", default=None, type=str, required=True,
        help="Path to TSV file with system's predictions")
    argparser.add_argument("-v", "--verbose", action="store_true",
                           help="more verbose output", required=False)
    args = argparser.parse_args(argv)

    if args.verbose:
        print("Verbosity turned on")

    goldfile, systemfile = args.gold, args.system
    if args.verbose:
        print("Gold   file: ", goldfile)
        print("System file: ", systemfile)
    for inputfile in [goldfile, systemfile]:
        # print("Input file: ", inputfile)
        if not os.path.isfile(inputfile):
            raise FileNotFoundError(f"Input file {inputfile} doesn't exist!")

    # todo what if files unequal length
    evaltr = Evaluator(gold_file=goldfile, system_file=systemfile, verbose=args.verbose)
    for goldinst, systeminst in tqdm(get_samples_from_two_files(
            goldfile=goldfile, systemfile=systemfile),
            desc="Iterating over samples "):  # , file=sys.__stdout__
        evaltr.update_counts(gold=goldinst, system=systeminst)

    print("Full corpus evaluation:")
    evaltr.print_overall_results()
    return


if __name__ == "__main__":
    main(sys.argv[1:])  # exclude programme name
