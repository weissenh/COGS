#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testing the grammar for the logical forms (testing acceptance, not parses)

author: weissenh
date: April 2021
"""

# todo: some of the tests still fail
# todo: what should be ungrammatical and what is just ok, but semantically odd?
# todo: write more tests

# target = __import__("..cogs_logical_form.py")
# LFPARSER = target.LFPARSER

from ..cogs_logical_form import LFPARSER
import unittest
from lark.exceptions import UnexpectedInput


class TestGrammar(unittest.TestCase):
    """
    Testing the grammar of the logical forms (overgenerating?)

    `cogs_logical_form.grammar`
    """

    def parser_wrapper_bool(self, examplestr) -> bool:
        try:
            tree = LFPARSER.parse(examplestr)
            return True
        except UnexpectedInput as e:
            return False

    def test_whitespace_in_formulas(self):
        # normal
        s = "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )"
        self.assertTrue(self.parser_wrapper_bool(examplestr=s))
        # more whitespace
        s = "*  cat   ( x _ 1 ) ;  run .  agent ( x _ 2 ,  x _ 1 )  "
        self.assertTrue(self.parser_wrapper_bool(examplestr=s))
        # no whitespace
        s = "*cat(x_1);run.agent(x_2,x_1)"
        self.assertTrue(self.parser_wrapper_bool(examplestr=s))
        # with self.assertRaises(UnexpectedInput):
        #   somefunc

    def test_messed_up_parenthesis(self):
        examples = [
            "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 ",  # no ) at end
            "* cat ( x _ 1 ; run . agent ( x _ 2 , x _ 1 )",  # no ) in middle
            "* cat x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )",  # no ( in middle
            "* cat ( x _ 1 ) ; run . agent x _ 2 , x _ 1 )",  # no ( at end
            "* cat ( x _ 1 ) ) ; run . agent ( x _ 2 , x _ 1 )",  # too many )
            "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 ) )",  # too many )
            "* cat ( ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )",  # too many (
            "* cat ( x _ 1 ) ; run . agent ( ( x _ 2 , x _ 1 )",  # too many (
            "* cat ( x _ 1 ) ; run . agent ) x _ 2 , x _ 1 )",  # ) instead of (
            "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 ) ( )",  # ( )
        ]
        for example in examples:
            self.assertFalse(self.parser_wrapper_bool(examplestr=example))

    def test_unexpected_tokens(self):
        examples = [
            "* cat ( x _ 1 ) ; run . agent ( x _ 2 x _ 1 )",  # missing comma
            "* cat ( x _ 1 ) ; run agent ( x _ 2 , x _ 1 )",  # missing punct
            "cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )",  # missing *
            "* cat ( x _ 1 ) run . agent ( x _ 2 , x _ 1 )",  # missing ;
            "* cat ( x _ 1 ) AND run . agent ( x _ 2 , x _ 1 )",
            # missing ; plus AND inserted (or * too much)
            "* cat ( x _ 1 ) ;",  # ok: empty conjunction ?
            "run . agent ( x _ 1 , Emma , x _ 2)",  # three arguments
            "* cat ( x _ 1 ) ; Emma",
            "" # empty string
        ]
        for example in examples:
            self.assertFalse(self.parser_wrapper_bool(examplestr=example))

    # todo: change this test
    def test_odd_arg_number(self):
        # todo should this be false (ungrammatical) instead of True?
        # should we rule out cases like that by the grammar?
        examples = [
            "* cat ( x _ 1 ) ; dog ( x _ 2 , x _ 1 )",
            # 1-part predicate with even 2 arguments
            "* cat ( x _ 1 ) ; cat . nmod . in ( x _ 2 )",
            # 3-part predicate name with only 1 argument
            "* cat ( x _ 1 ) ; run . agent ( x _ 2 )",
            # 2-part predicate name with only 1 argument
            "run . agent ( x _ 1 , Emma , x _ 2)",  # three arguments
            "cat . nmod . in ( x _ 1 , x _ 0 , x _ 2)",  # three arguments
        ]
        for example in examples:
            self.assertTrue(self.parser_wrapper_bool(examplestr=example))

    # todo: change this test
    def test_varnames_lambda_iota(self):
        # todo more tests
        examples = [
            # lambda var names with no lambda
            "cat ( a ) AND run . agent ( e , a )",
            "* cat ( a ) ; run . agent ( e , a )",
            # indexed var names with lambda
            "LAMBDA a . ball ( x _ 0 )",
            "LAMBDA x _ 0 . ball ( x _ 0 )",
            "LAMBDA a . LAMBDA e . giggle . agent ( x _ 0 , a )",
            "LAMBDA a . LAMBDA x _ 0 . giggle . agent ( x _ 0 , a )",
        ]
        for example in examples:
            self.assertFalse(self.parser_wrapper_bool(examplestr=example))

    def test_good_lambda_forms(self):
        examples = [
            # 'fake' lambda: primitives
            "Layla",
            "Emma",
            # real lambda
            "LAMBDA a . ball ( a )",
            "LAMBDA a . LAMBDA b . LAMBDA e . touch . agent ( e , b ) "
            + "AND touch . theme ( e , a )",
            "LAMBDA a . LAMBDA e . giggle . agent ( e , a )",
        ]
        for example in examples:
            self.assertTrue(self.parser_wrapper_bool(examplestr=example))

    def test_odd_lambda_forms(self):
        # todo should odd forms be unacceptable?
        # these are maybe not ungrammatical examples, but they are at least not
        # desired in the COGS corpus and/or semantically odd
        examples = [
            "LAMBDA a . ball ( b )",  # b variable free
            # "LAMBDA a . LAMBDA b . ball ( a )",  # useless b variable
            "LAMBDA a . LAMBDA b . LAMBDA e . touch . agent ( e , x _ 0 ) "
            + "AND touch . theme ( e , a )",  # x_1 not allowed
            "LAMBDA a . LAMBDA b . LAMBDA e . touch . agent ( e , Layla ) "
            + "AND touch . theme ( e , a )",  # Names not allowed
        ]
        for example in examples:
            self.assertTrue(self.parser_wrapper_bool(examplestr=example))

    # todo change this test
    def test_bad_primitives(self):
        examples = [
            "LAMBDA a . LAMBDA e . Layla",
            "layla", "emma",
            "cat", "cat ( a )",
            # todo: "cat ( x _ 0 )" ?
        ]
        for example in examples:
            self.assertFalse(self.parser_wrapper_bool(examplestr=example))

    def test_good_example_forms(self):
        examples = [
            "want . agent ( x _ 1 , Liam ) AND want . xcomp ( x _ 1 , x _ 3 ) "
            + "AND go . agent ( x _ 3 , Liam )",
            # Liam wanted to go
            "* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 ) AND want . xcomp "
            + "( x _ 2 , x _ 4 ) AND go . agent ( x _ 4 , x _ 1 )",
            # the boy wanted to go
            "* cat ( x _ 1 ) ; run . agent ( x _ 2 , x _ 1 )",
            # the cat ran
            "* woman ( x _ 1 ) ; * man ( x _ 4 ) ; love . agent ( x _ 2 , x _ 1"
            + " ) AND love . theme ( x _ 2 , x _ 4 )",
            # The woman loved the man
            "* man ( x _ 4 ) ; woman ( x _ 1 ) AND love . agent ( x _ 2 , x _ 1"
            + " ) AND love . theme ( x _ 2 , x _ 4 )",
            # A woman loved the man
            "* woman ( x _ 1 ) ; love . agent ( x _ 2 , x _ 1 ) AND love . "
            + "theme ( x _ 2 , x _ 4 ) AND man ( x _ 4 )",
            # The woman loved a man
            "woman ( x _ 1 ) AND love . agent ( x _ 2 , x _ 1 ) AND love . "
            + "theme ( x _ 2 , x _ 4 ) AND man ( x _ 4 )",
            # A woman loved a man
            "* girl ( x _ 1 ) ; buy . agent ( x _ 2 , x _ 1 ) AND buy . theme ("
            + " x _ 2 , x _ 4 ) AND genie ( x _ 4 ) AND genie . nmod . in ( x _"
            + " 4 , x _ 7 ) AND bottle ( x _ 7 )",
            # The girl bought a genie in a bottle
        ]
        for example in examples:
            self.assertTrue(self.parser_wrapper_bool(example))


if __name__ == "__main__":
    unittest.main()
