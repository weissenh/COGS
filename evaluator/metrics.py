# -*- coding: utf-8 -*-
"""
Different evaluation metrics comparing to corpus instances
- Metric (superclass)
- ExactMatchAccuracy
- OrderInvariantExactMatchAccuracy
- WellFormednessPercentage

author: weissenh ( piaw@coli.uni-saarland.de )
test environment: Ubuntu 20.04, Python 3.7
date: April 2020
"""


from overrides import overrides
from corpus_instance import CorpusInstance

# todo add main() method with small demo
# todo better support for macro/micro-level evaluation??
# todo more metrics: #conj, #iotas, edit dist?, #wellformed, commonpref?


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


# todo implement this
class OrderInvariantExactMatchAccuracy(Metric):
    """
    Order-invariant exact match accuracy

    Logical form considered correct even if order of conjuncts /iotas doesn't
    match the order in the gold standard form.
    However, iotas still have to preceed the conjunction.
    """

    def __init__(self):
        super(OrderInvariantExactMatchAccuracy, self).__init__()

    @overrides
    def get_name(self) -> str:
        return "Order-invariant Exact match accuracy"

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance):
        self.total += 1
        # todo obtain gold standard parse (assert wellf-formed)
        # todo obtian system parse
        # todo compare both
        # self.good += int(gold.logical_form_str == system.logical_form_str)
        raise NotImplementedError("Not implemented so far")


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
