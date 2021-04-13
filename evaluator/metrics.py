# -*- coding: utf-8 -*-
"""
Different evaluation metrics comparing two corpus instances
- Metric (superclass)
- ExactMatchAccuracy
- OrderInvariantExactMatchAccuracy
- WellFormednessPercentage
- TokenLevelEditDistance

author: weissenh
test environment: Ubuntu 20.04, Python 3.7
date: April 2021
"""


from overrides import overrides
from nltk.metrics import edit_distance  # for toke-level edit distance

from corpus_instance import CorpusInstance
from cogs_logical_form import COGSLogicalForm

# todo add main() method with small demo
# todo better support for macro/micro-level evaluation??
# todo more metrics: #conj, #iotas, commonpref?
# todo: needs more testing: additional metrics


def safe_div(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def f1score(precision: float, recall: float) -> float:
    return safe_div(numerator=2*precision*recall, denominator=precision+recall)


# todo refine metric superclass as more metrics are implemented
# todo should I assert here that sentences match ..., gold form well-formed...
class Metric:
    """Superclass for metrics"""

    def __init__(self, name: str, abbreviation: str):
        self.total = 0
        self.good = 0
        self.name = name
        self.abbreviation = abbreviation

    def get_name(self) -> str:
        """Get full name for metric"""
        return self.name

    def get_abbreviation(self) -> str:
        """Get abbreviated name for metric (should be ideally <=6 chars long)"""
        return self.abbreviation

    def update(self, gold: CorpusInstance, system: CorpusInstance) -> float:
        """Updates internal counts, returns sentence score"""
        raise NotImplementedError()

    def get_score(self) -> float:
        """:returns overall metric score"""
        # as [0, 1], multiply by 100 to get percentage
        return safe_div(self.good, self.total)


# Precision, Recall, F1 superclass
# todo set for removing duplicates or rather use counter?
class PRF1Metric(Metric):
    """
    Superclass for precision/recall/F1 metrics

    supports micro and macro average
    (micro: first sum counts, compute global precision, recall
    vs macro: compute individual precison, recall and sum the up)
    """
    ALLOWED_OPTIONS = {"f1", "prec", "rec"}

    def __init__(self, name: str, abbreviation: str, micro=True, main="f1"):
        super().__init__(name, abbreviation)
        self.total = 0
        self.good = 0
        self.precision, self.recall, self.f1 = 0, 0, 0
        self.tp, self.sysp, self.goldp = 0, 0, 0
        self.is_micro_averaged = micro
        if main not in PRF1Metric.ALLOWED_OPTIONS:
            raise ValueError(f"Invalid main metric, allowed options: "
                             f"{PRF1Metric.ALLOWED_OPTIONS}")
        self.mainmetric = main
        self.name = name
        self.abbreviation = abbreviation

    @overrides
    def get_name(self) -> str:
        """Get full name for metric"""
        return f"{self.name} {self.mainmetric.upper()}" \
               f"{'(micro)' if self.is_micro_averaged else '(macro)'}"

    @overrides
    def get_abbreviation(self) -> str:
        """Get abbreviated name for metric (should be ideally <=6 chars long)"""
        return f"{self.abbreviation}{self.mainmetric.upper()}" \
               f"{'(i)' if self.is_micro_averaged else '(a)'}"

    def _update_attrs(self, tp, sysp, goldp) -> tuple:
        self.total += 1
        self.tp += tp
        self.sysp += sysp
        self.goldp += goldp
        prec = safe_div(tp, sysp)
        rec = safe_div(tp, goldp)
        f1 = f1score(precision=prec, recall=rec)
        self.precision += prec
        self.recall += rec
        self.f1 += f1
        self.good += f1  # useless inherited attribute
        return prec, rec, f1

    def _pick_main_score(self, p, r, f1) -> float:
        scores = {"f1": f1, "prec": p, "rec": r}  # keys match allowed options
        return scores[self.mainmetric]

    def _extract_items(self, lf: COGSLogicalForm):
        # what do we want to extract and measure?
        raise NotImplementedError()

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance) -> float:
        # todo revise this ugly code
        assert (gold.has_wellformed_lf())
        if not system.has_wellformed_lf():
            # todo early exit creates inequality here cuz not added in attribute
            self.total += 1
            return 0.0  # can't equal gold LF anyway if it's not well-formed
        goldlf = gold.logical_form_parsed  # datattype: COGSLogicalForm
        systemlf = system.logical_form_parsed  # datatype: COGSLogicalForm
        golditems = set(self._extract_items(lf=goldlf))
        systemitems = set(self._extract_items(lf=systemlf))
        # NOTE: duplicates in the system prediction are ignored (cuz of set)!!!
        correct = golditems.intersection(systemitems)
        good, sysp, goldp = len(correct), len(systemitems), len(golditems)
        prec, rec, f1 = self._update_attrs(tp=good, sysp=sysp, goldp=goldp)
        sent_score = self._pick_main_score(p=prec, r=rec, f1=f1)
        return sent_score

    @overrides
    def get_score(self) -> float:
        """:returns overall metric score"""
        # as [0, 1], multiply by 100 to get percentage
        if self.is_micro_averaged:
            p = safe_div(self.tp, self.sysp)
            r = safe_div(self.tp, self.goldp)
            # f1 = f1score(precision=p, recall=r)
        else:
            p = safe_div(self.precision, self.total)
            r = safe_div(self.recall, self.total)
        f1 = f1score(precision=p, recall=r)
        return self._pick_main_score(p=p, r=r, f1=f1)


# todo based on the plain string of the logical form (problems with whitespace?)
class ExactMatchAccuracy(Metric):
    """Exact match accuracy: prediction must exactly match gold logical form"""

    def __init__(self):
        super(ExactMatchAccuracy, self).__init__(
            name="Exact match accuracy",
            abbreviation="EMAcc")

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance) -> float:
        self.total += 1
        sentence_score = int(gold.logical_form_str == system.logical_form_str)
        self.good += sentence_score
        return sentence_score


class OrderInvariantExactMatchAccuracy(Metric):
    """
    Order-invariant exact match accuracy

    Logical form considered correct even if order of conjuncts/iotas/lambdas
    doesn't match the order in the gold standard form.
    However, iotas/lambdas still have to precede the conjunction.
    """

    def __init__(self):
        super(OrderInvariantExactMatchAccuracy, self).__init__(
            name="Order-invariant Exact match accuracy",
            abbreviation="OiEMAcc")

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance) -> float:
        self.total += 1
        # todo revise this ugly code
        assert(gold.has_wellformed_lf())
        if not system.has_wellformed_lf():
            return 0.0  # can't equal gold LF anyway if it's not well-formed
        goldlf = gold.logical_form_parsed  # datattype: COGSLogicalForm
        systemlf = system.logical_form_parsed  # datatype: COGSLogicalForm
        goldtype = goldlf.type_of_formula()
        if goldtype != systemlf.type_of_formula():
            return 0.0  # can't equal gold LF anyway if not same type of formula
        # 'iotas', 'lambdas', 'name'
        if goldtype == "name":
            sent_score = int(goldlf.get_name() == systemlf.get_name())
            self.good += sent_score
            return sent_score
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
        sent_score = int(prefix_same and conjuncts_same)
        self.good += sent_score
        return sent_score


class WellFormednessPercentage(Metric):
    """
    Percentage of system predictions that are well-formed

    Actually that's independent of the gold standard form,
    but could check that gold-standard is well-formed too (as a sanity check)
    """

    def __init__(self):
        super(WellFormednessPercentage, self).__init__(
            name="Well-formedness percentage",
            abbreviation="Wellfm"
        )

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance) -> float:
        self.total += 1
        assert(gold.has_wellformed_lf())
        # if not system.has_wellformed_lf():
        #    print("Not wellformed: ", system)
        # self.good += int(system.has_wellformed_lf())  # short version
        sent_score = 1 if system.has_wellformed_lf() else 0
        self.good += sent_score
        return sent_score


# using nltk:
# https://www.nltk.org/api/nltk.metrics.html#nltk.metrics.distance.edit_distance
# todo how to get reliable tokens ? (whitespace split???)
# todo macro- or micro-average somehow?
# todo check this implementation
class TokenLevelEditDistance(Metric):
    """
    Average Token-Level Edit distance (Levenshtein)

    How many tokens (not characters!) have to be inserted/deleted/substituted to
    arrive at the gold standard form, given the system prediction?
    """
    def __init__(self):
        super(TokenLevelEditDistance, self).__init__(
            name="Avg. token-level edit distance",
            abbreviation="TEditD"
        )

    @overrides
    def update(self, gold: CorpusInstance, system: CorpusInstance) -> float:
        self.total += 1
        distance = edit_distance(s1=gold.logical_form_parsed.tokens,
                                 s2=system.logical_form_parsed.tokens,
                                 substitution_cost=1, transpositions=False)
        self.good += distance
        return distance


# todo: measuring duplicates?
class TermCorrectness(PRF1Metric):
    """
    Term correctness score (set based! duplicates removed!)

    Vaguely`term := predicatename ( arguments )` (how many lambda x were
    predicted doesn't count here, but if model predicts `*cat(x_1)`, then
    `cat(x_1)` contributes (we don't distinguish terms in prefix from the ones
    in the conjunction)
    This is obviously 0 if the predicted logical form is not well-formed.
    if forms have different types (iota vs lambda) will still allow evaluation.
    """

    def __init__(self, micro=True, main="f1"):
        super(TermCorrectness, self).__init__(
            name="Term correctness", abbreviation="Term",
            micro=micro, main=main)

    @overrides
    def _extract_items(self, lf: COGSLogicalForm):
        return lf.get_terms()


# todo: measuring duplicates?
class PredicateNameCorrectness(PRF1Metric):
    """
    Predicate name correctness score (set based! duplicates removed!)

    Predicate name consists of one, two or three parts, e.g.
    `cat`, `eat, theme` or ookie, nmod, beside`
    Joining predicates appearing in iota prefix and conjunction.
    This is obviously 0 if the predicted logical form is not well-formed.
    if forms have different types (iota vs lambda) will still allow evaluation.
    """

    def __init__(self, micro=True, main="f1"):
        super(PredicateNameCorrectness, self).__init__(
            name="Predicate name correctness", abbreviation="Pred",
            micro=micro, main=main)

    @overrides
    def _extract_items(self, lf: COGSLogicalForm):
        return lf.get_predicate_names()


# todo measuring duplicates?
# todo arguments also in lambda? is name lambda?
class ArgumentsCorrectness(PRF1Metric):
    """
    Arguments correctness score (set based! duplicates removed!)

    Arguments can be variables (indices or lambda) and proper names (e.g. Ava)
    Joining apperance in iota prefix and conjunction.
    This is obviously 0 if the predicted logical form is not well-formed.
    if forms have different types (iota vs lambda) will still allow evaluation.
    """

    def __init__(self, micro=True, main="f1"):
        super(ArgumentsCorrectness, self).__init__(
            name="Arguments correctness", abbreviation="Pred",
            micro=micro, main=main)

    @overrides
    def _extract_items(self, lf: COGSLogicalForm):
        return lf.get_arguments()
