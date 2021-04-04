# -*- coding: utf-8 -*-
"""
Different evaluation metrics comparing to corpus instances
- Metric (superclass)
- ExactMatchAccuracy
- OrderInvariantExactMatchAccuracy
- WellFormednessPercentage
- TokenLevelEditDistance

author: weissenh ( piaw@coli.uni-saarland.de )
test environment: Ubuntu 20.04, Python 3.7
date: April 2021
"""


from overrides import overrides
from nltk.metrics import edit_distance  # for toke-level edit distance

from corpus_instance import CorpusInstance

# todo add main() method with small demo
# todo better support for macro/micro-level evaluation??
# todo more metrics: #conj, #iotas, edit dist?, #wellformed, commonpref?
# todo: needs more testing: order-invariant ema and edit distance


# todo refine metric superclass as more metrics are implemented
# todo should I assert here that sentences match ..., gold form well-formed...
class Metric:
    """Superclass for metrics"""

    def __init__(self):
        self.total = 0
        self.good = 0

    def get_name(self) -> str:
        raise NotImplementedError()

    def update(self, gold: CorpusInstance, system: CorpusInstance):
        raise NotImplementedError()

    def get_score(self):
        # as [0, 1], multiply by 100 to get percentage
        if self.total == 0:
            return 0.0
        return self.good / self.total


class ExactMatchAccuracy(Metric):
    """Exact match accuracy: prediction must exactly match gold logical form"""

    def __init__(self):
        super(ExactMatchAccuracy, self).__init__()

    @overrides
    def get_name(self) -> str:
        return "Exact match accuracy"

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance):
        self.total += 1
        self.good += int(gold.logical_form_str == system.logical_form_str)
        return


class OrderInvariantExactMatchAccuracy(Metric):
    """
    Order-invariant exact match accuracy

    Logical form considered correct even if order of conjuncts /iotas doesn't
    match the order in the gold standard form.
    However, iotas still have to precede the conjunction.
    """

    def __init__(self):
        super(OrderInvariantExactMatchAccuracy, self).__init__()

    @overrides
    def get_name(self) -> str:
        return "Order-invariant Exact match accuracy"

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance):
        self.total += 1
        # todo revise this ugly code
        assert(gold.has_wellformed_lf())
        if not system.has_wellformed_lf():
            return  # can't equal gold LF anyway if it's not wellformed
        goldlf = gold.logical_form_parsed  # datattype: COGSLogicalForm
        systemlf = system.logical_form_parsed  # datatype: COGSLogicalForm
        goldtype = goldlf.type_of_formula()
        if goldtype != systemlf.type_of_formula():
            return  # can't equal gold LF anyway if not same type of forumla
        # 'iotas', 'lambdas', 'name'
        if goldtype == "name":
            return int(goldlf.get_name() == systemlf.get_name())
        # g_prefix, s_prefix = set(), set()
        if goldtype == 'iotas':
            g_prefix = set(goldlf.get_iotas())
            s_prefix = set(systemlf.get_iotas())
        elif goldtype == 'lambdas':
            g_prefix = set(goldlf.get_lambdas())
            s_prefix = set(systemlf.get_lambdas())
        else:
            assert False  # this shouldn't happen (there are only 3 types)
        g_conj = set(goldlf.get_conjuncts())
        s_conj = set(systemlf.get_conjuncts())
        prefix_same = g_prefix == s_prefix
        conjuncts_same = g_conj == s_conj
        self.good += int(prefix_same and conjuncts_same)
        return


class WellFormednessPercentage(Metric):
    """
    Percentage of system predictions that are well-formed

    Actually that's independent of the gold standard form,
    but could check that gold-standard is well-formed too (as a sanity check)
    """

    def __init__(self):
        super(WellFormednessPercentage, self).__init__()

    @overrides
    def get_name(self) -> str:
        return "Well-formedness percentage"

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance):
        self.total += 1
        assert(gold.has_wellformed_lf())
        # if not system.has_wellformed_lf():
        #    print("Not wellformed: ", system)
        # self.good += int(system.has_wellformed_lf())  # short version
        self.good += 1 if system.has_wellformed_lf() else 0
        return


# maybe use nltk:
# https://www.nltk.org/api/nltk.metrics.html#nltk.metrics.distance.edit_distance
# todo how to get reliable tokens ? (whitespace split???)
# todo macro- or micro-avergae somehow?
# todo check this implementation
class TokenLevelEditDistance(Metric):
    """
    Average Token-Level Edit distance (Levenshtein)

    Given the tokens
    """
    def __init__(self):
        super(TokenLevelEditDistance, self).__init__()

    @overrides
    def get_name(self) -> str:
        return "Avg. token-level edit distance"

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance):
        self.total += 1
        # self.good += int(gold.logical_form_str == system.logical_form_str)
        distance = edit_distance(s1=gold.logical_form_parsed.tokens,
                                 s2=system.logical_form_parsed.tokens,
                                 substitution_cost=1, transpositions=False)
        self.good += distance
        # raise NotImplementedError("Not yet implemented")
        return
