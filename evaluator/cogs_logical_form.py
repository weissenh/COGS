#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parsing the logical form used in the COGS dataset

Main function used for testing/showing small demo.

Needs [LARK parser](https://github.com/lark-parser/lark) for parsing the
logical form. You can use pip to install it:
    pip install lark-parser
Tested with lark-parser-0.11.2  (`pip install lark-parser==0.11.2`)

author: weissenh ( piaw@coli.uni-saarland.de )
test environment: Ubuntu 20.04, Python 3.7
date: April 2020
"""


# todo: implement this

from lark import Lark, Token   # remember: pip install lark-parser
from lark.exceptions import *

# todo: how to detect whether lambda or iota if not present?
# todo: not checking whether x_i used in lambda term or
#  whether lambda-variable used in iota-formula
# todo: this grammar overgenerates (
# todo would really like to narrow down lambda formulas....(and not mix up x_i and aeb
# for grammar writing see
# https://lark-parser.readthedocs.io/en/latest/grammar.html
# https://github.com/lark-parser/lark/blob/master/docs/_static/lark_cheatsheet.pdf
# https://github.com/lark-parser/lark/blob/master/docs/json_tutorial.md
grammar = """
start : (iotas | lambdas) conjuncts | NAME 
iotas : iota*
iota : "*" predicatenoun "(" variable ")" ";"
lambdas : lambdaterm~1..3
lambdaterm : "LAMBDA" LAMBDAVAR "."
conjuncts : conjunct ["AND" conjunct]*
conjunct : predicatename "(" arguments ")"
predicatenoun : ALPHALOW
predicatename : predicatenoun ("." predicatenoun)~0..2
arguments: argument ("," argument)?
argument : NAME | variable
variable : indexvar | LAMBDAVAR
indexvar : "x" "_" NUMBER
ALPHALOW : LCASE_LETTER LCASE_LETTER+  // >=2 chars, all lower
NAME : UCASE_LETTER LCASE_LETTER+  // >=2 chars, first upper, then lower
LAMBDAVAR : "a" | "b" | "e"

%import common.WS
%import common.LCASE_LETTER
%import common.UCASE_LETTER
%import common.INT -> NUMBER  // call INT now NUMBER
%ignore WS //ignores whitespace
"""
LFPARSER = Lark(grammar=grammar, start='start')


# todo: not only read but also build logical forms on the go?
class COGSLogicalForm:
    """
    Parsed logical form of COGS (note: system predictions can be illformed!)

    Parsed logical form according to some (maybe suboptimal) grammar for the
    logical forms used in COGS
    """

    def __init__(self, lf_as_string: str):
        self.original_str = lf_as_string
        self.parse_result, self.parsed = self.__parse_logical_form()
        return

    def __str__(self):
        return self.original_str

    def __parse_logical_form(self):
        # returns IsWellFormed, ParseTree/Exception
        try:
            tree = LFPARSER.parse(self.original_str)
            # todo walk the tree and store important parts
        except UnexpectedInput as e:
            return False, e  #
        return True, tree

    def is_wellformed(self) -> bool:
        return self.parse_result

    def get_conjuncts(self) -> set:
        # todo check if well-formed
        # todo implement
        return set()

    def get_iotas(self) -> set:
        # todo check if well-formed
        # todo implement
        return set()


def debugging_main():
    #example = "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )"
    example = "run . agent ( x _ 2 , x _ 1 ) AND cat ( x _ 1 )"
    try:
        tree = LFPARSER.parse(example)
        for node in tree.iter_subtrees_topdown():
            print("Data: ", node.data)
            if len(node.children)==1 and isinstance(node.children[0],Token):
                tok = node.children[0]
                print("Found token: ", repr(tok))
                print("Its preterminal: ", tok.type)
                print("Its value: ", tok.value)
                print("type of the token value", type(tok.value))
                # https://lark-parser.readthedocs.io/en/latest/classes.html#lark.Token
            #print("Children: ", node.children)
            #print(node)
    except UnexpectedInput as e:
        print("--Unexpected Input: not well-formed? won't proceed")
        return
    print(tree.pretty())
    return


# todo refactor this and make real test functions out of it (and keep a really small demo)
def main():
    """
    this should be a small demo of the COGS logical form parsing

    python3 cogs_logical_form.py
    """
    examples = [
        "want . agent ( x _ 1 , Liam ) AND want . xcomp ( x _ 1 , x _ 3 ) AND go . agent ( x _ 3 , Liam )", # Liam wanted to go
        "* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 ) AND want . xcomp ( x _ 2 , x _ 4 ) AND go . agent ( x _ 4 , x _ 1 )", # the boy wanted to go
        "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )", # [single conjunct] the cat ran
        "* woman ( x _ 1 ) ; * man ( x _ 4 ) ; love . agent ( x _ 2 , x _ 1 ) AND love . theme ( x _ 2 , x _ 4 )", # [2 iotas] The woman loved the man
        "* man ( x _ 4 ) ; woman ( x _ 1 ) AND love . agent ( x _ 2 , x _ 1 ) AND love . theme ( x _ 2 , x _ 4 )", # [noun in conjunct] A woman loved the man
        "* woman ( x _ 1 ) ; love . agent ( x _ 2 , x _ 1 ) AND love . theme ( x _ 2 , x _ 4 ) AND man ( x _ 4 )", # The woman loved a man
        "woman ( x _ 1 ) AND love . agent ( x _ 2 , x _ 1 ) AND love . theme ( x _ 2 , x _ 4 ) AND man ( x _ 4 )", # [no iota] A woman loved a man
        "* girl ( x _ 1 ) ; buy . agent ( x _ 2 , x _ 1 ) AND buy . theme ( x _ 2 , x _ 4 ) AND genie ( x _ 4 ) AND genie . nmod . in ( x _ 4 , x _ 7 ) AND bottle ( x _ 7 )", # [preposition] The girl bought a genie in a bottle
    ]
    for i, example in enumerate(examples):
        print(f"--Example: {example}")
        lform = COGSLogicalForm(lf_as_string=example)
        assert(lform.is_wellformed())
        print(f"Logical form: Conjuncts: {lform.get_conjuncts()}")
        print(f"Logical form: Iotas: {lform.get_iotas()}")
    print("\n----Now testing ill-formedness-----\n")

    illformed = [
        "",  # UnexpectedEOF
        "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 ", # missing ) at end
        "* cat ( x _ 1 ; run . agent ( x _ 2 , x _ 1 )", # missing ) in middle
        "* cat x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )", # missing ( in middle
        "* cat ( x _ 1 ) ; run . agent x _ 2 , x _ 1 )", # missing ( at end
        "* cat ( x _ 1 ) ; run . agent ( x _ 2 x _ 1 )", # missing comma
        "* cat ( x _ 1 ) ; run agent ( x _ 2 , x _ 1 )", # missing punct
        "cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )", # missing *
        "* cat ( x _ 1 ) run . agent ( x _ 2 , x _ 1 )", # missing ;
        "* cat ( x _ 1 ) AND run . agent ( x _ 2 , x _ 1 )", # missing ; plus AND inserted
        "* cat ( x _ 1 ) ; agent ( x _ 2 , x _ 1 )", # single pred with two args
        "* cat ( x _ 1 ) ; cat . nmod . in ( x _ 2 )", # three pred with one arg
        "* cat ( x _ 1 ) ;", # ok: empty conjunct ?
        "run . agent ( x _ 1 , Emma , x _ 2)",
        "* cat ( x _ 1) ; Emma"
    ]
    # todo (currently allowed) include lambda var with iota...and lambda with xi...
    # todo more than two arguments? exclude this?
    for i, example in enumerate(illformed):
        print(f"--Example: '{example}'")
        lform = COGSLogicalForm(lf_as_string=example)  # todo expect parser error?
        print(f"{'VALID' if lform.is_wellformed() else 'ILLFORMED'}")

    print("\n----Now with lambda:---")
    # todo more additional test needed:
    #  - ill-formed
    #  - more constrained: Name shouldn't be allowed as argument (currently allowed)
    examples = [
        "LAMBDA a . ball ( a )",
        "LAMBDA a . LAMBDA b . LAMBDA e . touch . agent ( e , b ) AND touch . theme ( e , a )",
        "LAMBDA a . LAMBDA e . giggle . agent ( e , a )",
        "Layla"
    ]
    for i, example in enumerate(examples):
        print(f"--Example: {example}")
        lform = COGSLogicalForm(lf_as_string=example)
        # todo print something to test
        # print(lform)
    print("Done!")
    return


if __name__ == "__main__":
    #main()
    debugging_main()
