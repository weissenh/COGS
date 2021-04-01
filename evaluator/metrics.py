# -*- coding: utf-8 -*-
"""
Different evaluation metrics comparing to corpus instances
- Metric (superclass)
- ExactMatchAccuracy

author: weissenh ( piaw@coli.uni-saarland.de )
test environment: Ubuntu 20.04, Python 3.7
date: April 2020
"""


from overrides import overrides
from corpus_instance import CorpusInstance

# todo add main() method with small demo
# todo more metrics: #conj, #iotas, edit dist?, #wellformed, commonpref?


# todo refine metric superclass as more metrics are implemented
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
