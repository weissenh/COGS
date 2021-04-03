#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
(Main function used for testing/showing small demo)

author: weissenh ( piaw@coli.uni-saarland.de )
test environment: Ubuntu 20.04, Python 3.7
date: April 2020
"""

# todo: implement, including parsing logical form
from cogs_logical_form import COGSLogicalForm


class CorpusInstance:
    """
    A sample consisting of the sentence, the logical form and gen-type-info

    This class basically represents one row/line in the COGS data files.
    Sentences are tokenized and logical forms are parsed
    """

    def __init__(self, sentence: str, logical_form: str,
                 gen_type_required: str, line_num=None):
        self.sent_str = sentence
        self.logical_form_str = logical_form
        self.gen_type_required = gen_type_required
        self.line_number = line_num
        self.logical_form_parsed = COGSLogicalForm(self.logical_form_str)
        self.sent_tokens = self.sent_str.split()
        self.sent_length = len(self.sent_tokens)
        return

    def is_same_sentence(self, other_instance) -> bool:
        # todo check other_instance has correct type?
        if self.sent_length != other_instance.sent_length:
            return False  # easy check first (int cmp faster than str compare)
        return self.sent_str == other_instance.sent_str

    def has_wellformed_lf(self) -> bool:
        return self.logical_form_parsed.is_wellformed()

    def __str__(self):
        return "\t".join([self.sent_str,
                          self.logical_form_str,
                          self.gen_type_required])


def main():
    """
    this should be a small demo of the CorpusInstance class

    python3 corpus_instance.py
    """
    corpus = [
        (
            "The boy wanted to go .",
            "* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 )"
            " AND want . xcomp ( x _ 2 , x _ 4 )"
            " AND go . agent ( x _ 4 , x _ 1 )",
            "in_distribution"
        ),
        (
            "The cat ran .",
            "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )",
            "in_distribution"
        )
    ]
    instances = list()
    for i, (sent, repres, gentype) in enumerate(corpus):
        ins = CorpusInstance(sentence=sent, logical_form=repres,
                             gen_type_required=gentype, line_num=i)
        instances.append(ins)
    for instance in instances:
        print(f"\nLine no: {instance.line_number}")
        print(f"Generalization type required: {instance.gen_type_required}")
        print(f"Sentence length: {instance.sent_length}")
        print("Tokens: ", instance.sent_tokens)
        print("to do: parsed logical form")
    print("Done!")
    return


if __name__ == "__main__":
    main()
