#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parsing the logical form used in the COGS dataset

Main function used for testing/showing small demo.

Needs [LARK parser](https://github.com/lark-parser/lark) for parsing the
logical form. You can use pip to install it:
    pip install lark-parser
Tested with lark-parser-0.11.2  (`pip install lark-parser==0.11.2`)

author: weissenh
test environment: Ubuntu 20.04, Python 3.7
date: April 2021
"""


# todo: can I speed up the parser?
# todo: code smell: LFParser and LFTransformer:
#  can this be a singleton? static class? I only need ONE transformer and parser
#  also: a lot of magic strings, rather use namedTuples?

from lark import Lark, Transformer   # remember: pip install lark-parser
from lark.exceptions import UnexpectedInput
from collections import namedtuple  # for Term(predicate=.., argument=...)

# IMPORTANT: whenever the grammar is changed, also change the LFTransformer
# below needs to be adapted
# todo: make grammar more strict, currently overgenerating? e.g.
# - x _ i should not be allowed in Lambda term
# - variables a,e,b should ONLY be used in the presence of LAMBDAs
# - see also test in the tests_lfgrammar.py file
# for grammar writing see
# https://lark-parser.readthedocs.io/en/latest/grammar.html
# https://github.com/lark-parser/lark/blob/master/docs/_static/lark_cheatsheet.pdf
# https://github.com/lark-parser/lark/blob/master/docs/json_tutorial.md
grammar = """
start : (iotas | lambdas) conjuncts | name 
iotas : iota*
iota : "*" predicatenoun "(" variable ")" ";"
lambdas : lambdaterm~1..3
lambdaterm : "LAMBDA" LAMBDAVAR "."
conjuncts : conjunct ["AND" conjunct]*
conjunct : predicatename "(" arguments ")"
predicatenoun : ALPHALOW
predicatename : predicatenoun ("." predicatenoun)~0..2
arguments: argument ("," argument)?
argument : name | variable
variable : ("x" "_" NUMBER) | LAMBDAVAR
ALPHALOW : LCASE_LETTER LCASE_LETTER+  // >=2 chars, all lower
name: NAME
NAME : UCASE_LETTER LCASE_LETTER+  // >=2 chars, first upper, then lower
LAMBDAVAR : "a" | "b" | "e"

%import common.WS
%import common.LCASE_LETTER
%import common.UCASE_LETTER
%import common.INT -> NUMBER  // call INT now NUMBER
%ignore WS //ignores whitespace
"""
LFPARSER = Lark(grammar=grammar, start='start')

Term = namedtuple("Term", field_names=["pred", "args"])


# todo transformer or visitor?
# https://lark-parser.readthedocs.io/en/latest/visitors.html#transformer
class LFTransformer(Transformer):
    """
    Transforms parse tree to python object

    Method names are names of the left hand side nonterminals of the grammar
    If you call its method `transform` on a lark.Tree it transforms it bottom up
    : So subtrees are already transformed when the method for the larger
    constituent tree is transformed.
    """
    def _get_value_of_preterminal(self, ps) -> str:
        assert(len(ps) == 1)
        return ps[0].value

    def start(self, args):
        # start : (iotas | lambdas) conjuncts | name
        if len(args) == 1:
            # assert(args is name)
            return {"name": args[0]}
        elif len(args) == 2:
            prefixvalue, prefixtype = args[0]
            return {prefixtype: prefixvalue, "conjunction": args[1]}
        else:
            raise ValueError("More arguments than expected!")

    # prefix (lambda, iota)
    def lambdas(self, items) -> tuple:
        return list(items), "lambdas"

    def lambdaterm(self, preterminals) -> str:
        # lambdaterm : "LAMBDA" LAMBDAVAR "."
        return self._get_value_of_preterminal(ps=preterminals)

    def iotas(self, items) -> tuple:
        return items, "iotas"

    def iota(self, args) -> namedtuple:
        # iota : "*" predicatenoun "(" variable ")" ";"
        assert(len(args) == 2)
        # keep datastructure parallel to conjuncts:
        return Term(pred=(args[0],), args=(args[1],))

    # conjunction
    def conjuncts(self, conjs) -> list:
        return list(conjs)

    def conjunct(self, args) -> namedtuple:
        # return tuple(args)
        assert(len(args) == 2)
        return Term(pred=args[0], args=args[1])

    # terms
    def predicatename(self, parts) -> tuple:
        return tuple(parts)

    def predicatenoun(self, preterminals) -> str:
        return self._get_value_of_preterminal(ps=preterminals)

    def arguments(self, args) -> tuple:
        return tuple(args)

    def argument(self, args):  # str, or int
        assert(len(args) == 1)  # name or variable
        return args[0]

    def variable(self, preterminals):  # str or int
        # assert preterminals[0].data NUMBER or LAMBDAVAR
        val = self._get_value_of_preterminal(ps=preterminals)
        try:
            val = int(val)  # doesn't work for lambda vars
        except ValueError:
            pass
        return val

    def name(self, preterminals):
        # assert preterminals[0].data NAME
        return self._get_value_of_preterminal(ps=preterminals)


LFTRANSFORMER = LFTransformer()


class IllFormedLogicalForm(ValueError):
    """
    Ill-formed logical form

    can't use functionality that assumes well-formedness
    """
    pass


# todo: not only read but also build logical forms on the go?
class COGSLogicalForm:
    """
    Parsed logical form of COGS (note: system predictions can be illformed!)

    Parsed logical form according to some (maybe suboptimal) grammar for the
    logical forms used in COGS
    """

    def __init__(self, lf_as_string: str):
        self.original_str = lf_as_string
        self.tokens = lf_as_string.split()  # assumes whitespace!!!!
        self.parse_result, self.parsed = self.__parse_logical_form()
        return

    def __str__(self):
        return self.original_str

    def __parse_logical_form(self):  # Tuple[bool, OneOf[Exception, Dict]
        # returns IsWellFormed, ParseTree/Exception
        try:
            tree = LFPARSER.parse(self.original_str)
            result = LFTRANSFORMER.transform(tree)
        except UnexpectedInput as e:
            return False, e  # is ill formed, Exception
        return True, result  # is well formed, Dict

    def is_wellformed(self) -> bool:
        return self.parse_result

    def type_of_formula(self) -> str:
        if not self.is_wellformed():
            raise IllFormedLogicalForm()
        # all three are mutually exclusive
        types = {'iotas', 'lambdas', 'name'}
        found = list(self.parsed.keys() & types)  # intersection
        assert(len(found) == 1)
        return found[0]

    def get_conjuncts(self) -> set:
        if not self.is_wellformed():
            raise IllFormedLogicalForm()
        return self.parsed.get("conjunction", [])

    def get_iotas(self) -> set:
        if not self.is_wellformed():
            raise IllFormedLogicalForm()
        return self.parsed.get("iotas", [])

    def get_lambdas(self) -> set:
        if not self.is_wellformed():
            raise IllFormedLogicalForm()
        return self.parsed.get("lambdas", [])

    def get_name(self) -> str:
        if not self.is_wellformed():
            raise IllFormedLogicalForm()
        return self.parsed.get("name", [])


def debugging_main():
    example = "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )"
    # example = "run . agent ( x _ 2 , Emma ) AND cat ( x _ 1 )"
    # example = "LAMBDA a . LAMBDA e . giggle . agent ( e , a )"
    # example = "Layla"
    try:
        tree = LFPARSER.parse(example)
    except UnexpectedInput:
        print("--Unexpected Input: not well-formed? won't proceed")
        return
    # print(tree.pretty())
    mytrans = LFTransformer()
    result = mytrans.transform(tree)
    print("Result of transformation:\n", result)
    return


def main():
    """
    this should be a small demo of the COGS logical form parsing

    python3 cogs_logical_form.py
    """
    examples = [
        # the boy wanted to go
        "* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 ) AND "
        + "want . xcomp ( x _ 2 , x _ 4 ) AND go . agent ( x _ 4 , x _ 1 )",
        # [preposition] The girl bought a genie in a bottle
        "* girl ( x _ 1 ) ; buy . agent ( x _ 2 , x _ 1 ) AND "
        + "buy . theme ( x _ 2 , x _ 4 ) AND genie ( x _ 4 ) AND "
        + "genie . nmod . in ( x _ 4 , x _ 7 ) AND bottle ( x _ 7 )",
        # ill-formed
        "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 ",  # missing ) at end
        # # "* cat ( x _ 1 ) ;",  # empty conjunction
        # primitives
        "LAMBDA a . ball ( a )",
        "LAMBDA a . LAMBDA b . LAMBDA e . touch . agent ( e , b ) "
        + "AND touch . theme ( e , a )",
        "Layla"
    ]
    for i, example in enumerate(examples):
        print(f"--Example: {example}")
        lform = COGSLogicalForm(lf_as_string=example)
        print(f"Is well-formed? {'YES' if lform.is_wellformed() else 'NO'}")
        try:
            print(f"Logical form: Type: {lform.type_of_formula()}")
            print(f"Logical form: Iotas: {lform.get_iotas()}")
            print(f"Logical form: Lambdas: {lform.get_lambdas()}")
            print(f"Logical form: Conjuncts: {lform.get_conjuncts()}")
            print(f"#tokens: {len(lform.tokens)}")
        except IllFormedLogicalForm:
            print("(ill-formed, therefore can't print more details)")
            pass
    print("Done!")
    return


if __name__ == "__main__":
    main()
    # debugging_main()
