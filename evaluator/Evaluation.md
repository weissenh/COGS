author: [weissenh](https://github.com/weissenh) (Disclaimer: I'm **not** one of the authors of the COGS paper!)

**this is work in progress**

This should be a documentation of my efforts to evaluate models predictions on 
COGS (independent of OpenNMT) along with some proposed additional evaluation metrics.

Dependencies:
- [LARK parser](https://github.com/lark-parser/lark)  
  for parsing the logical forms. Parsing is needed to evaluate metrics like 
  well-formedness and order-invariant exact match accuracy.  
  You can install it with pip: `pip install lark-parser`  
  (Tested with version 0.11.2: `pip install lark-parser==0.11.2`)
- [tqdm](https://tqdm.github.io/)  
  for the progress bar when calling `evaluator.py`.  
  You can install it with pip: `pip install tqdm`  
  (Tested with version 4.36.1)
- [nltk](https://www.nltk.org/)  
  for the Levenshtein distance (average token-level edit distance metric)  
  You can install it with pip: `pip install nltk`  
  (Tested with version 3.4.5)


**TO DO**:
- [ ] faster parsing (currently needs nearly 30secs for dev set, also: code smell)
- [ ] stricter grammar? (see also `tests_lfgrammar`)
- [ ] check and test new metrics (order-invariant ema, edit distance, ...)
- [ ] more metrics
- [ ] document usage
- [ ] (enhancement) better/more readers
- [ ] (enhancement) micro/macro level evaluation
- [ ] add option to specify output file for evaluation results (instead of stdout)
- [x] print sentence-wise results (actually use verbosity parameter!)
- [ ] summarize evaluation for each 3rd row type (`ìn_distribution`, `prim_to_obj_proper`, ...)


Table of contents:
1. What is reported in the COGS paper
2. Extending evaluation beyond exact match accuracy
3. OpenNMT-independent evaluation
4. References


## 1. What is reported in the COGS paper

The COGS paper (Kim & Linzen [2020](https://www.aclweb.org/anthology/2020.emnlp-main.731)):

> An output sequence is considered correct only if it exactly matches the gold sequence. 
> (p. 9092, caption of Figure 2(a))

Additionally, in 
[appendix G.2, p. 9102](https://www.aclweb.org/anthology/2020.emnlp-main.731.pdf#page=16), 
they comment on average token-level edit distance and ill-formedness.

**So main evaluation metric is exact match accuracy.**

According to p.c. they obtained the numbers as part of the OpenNMT commands run.

See also the main `README.md` on how to reproduce their results.


## 2. Extending evaluation beyond exact match accuracy

### Motivating example
Note that exact match accuracy wouldn't tell us how 'close' 
the model's incorrect prediction are to the gold standard output.

E.g. for the sentence *The boy wants to go* (made up example), 
the correct logical form would be
```
* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 ) AND want . xcomp ( x _ 2 , x _ 4 ) AND go . agent ( x _ 4 , x _ 1 )
```
The following forms are all considered equally 'bad' by the exact match accuracy,
ranging from just conjuncts permuted, over only one token wrong, a conjunct missing, to completely off.
```
* boy ( x _ 1 ) ; go . agent ( x _ 4 , x _ 1 ) AND want . xcomp ( x _ 2 , x _ 4 ) AND want . agent ( x _ 2 , x _ 1 )
* boy ( x _ 0 ) ; want . agent ( x _ 2 , x _ 1 ) AND want . xcomp ( x _ 2 , x _ 4 ) AND go . agent ( x _ 4 , x _ 1 )
* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 ) AND go . agent ( x _ 4 , x _ 1 )
girl ( x _ 1 ) AND go . agent ( x _ 2 , x _ 7 )
```
In the above examples token-edit distance can help for some examples,
but especially for the first (conjuncts permuted) this might overestimate the errors made,
especially if we assume that the order of the conjuncts shouldn't affect the 'meaning' of the sentence.

### Proposed additions

For the implementations of the metrics see `evaluator/metrics.py`  
**to do**: additions
- [x] token-level edit distance (**todo** since it is reported in the paper, code from the authors?) (**todo: testing needed**)
- [x] well-formedness 
- [x] order-invariant exact match accuracy (**todo: testing needed**)
- [ ] partial success? (predicate names, variables, ...)

**Well-formedness.** For each sentence the logical form is either well-formed or not.
Therefore, we can count the samples for which the predicted logical form is well-formed.
Well-formedness is determined by our parser which might not be optimal 
(**todo improve parser**, see `cogs_logical_form.py`).
Similar to exact match accuracy, we can compute and report the percentage of 
samples/predictions that are considered 'correct' under this metric.  
A prediction that is well-formed can still be incorrect, but  all gold standard 
forms should be well-formed: a success in exact match implies well-formedness.  
Note: in [appendix G.2 of the COGS paper, p. 9102](https://www.aclweb.org/anthology/2020.emnlp-main.731.pdf#page=16)
the authors do mention ill-formedness with the example of missing a final 
closing parenthesis in the Transformer output. However, according to p.c. with 
the authors, they only evaluated well-formedness partially and didn't have an 
overall metric for it.  

**Order invariant exact match accuracy.** (OiEMAcc) 
*Background* The COGS logical form consists of a possibly empty list of prefix 
terms (iotas or lambdas) and a conjunction with 1 or more conjuncts 
(except for named entities as primitive).
To have a deterministic order of conjuncts, the authors of COGS decided to order 
them by subscript of the Skolem constants (see 
[page 9099, appendix C](https://www.aclweb.org/anthology/2020.emnlp-main.731.pdf#page=13)).
The order of the prefix terms **---to do---** order of prefix terms and scope.  
As logical conjunction is commutative, the denotation should be invariant to the
order of the conjuncts. Furthermore we believe that obtaining the correct order 
of conjuncts and prefix terms can easily be delegated to a post-processing step.  
We consider predicted logical forms to be correct under this metric if the 
predicted conjuncts and prefix terms can be reordered such that we would have a 
strict exact match with the gold standard logical form. However, we require that
the iotas and lambdas in the original output precede the conjunction.
For a named entity primitive, this metric trivially equals strict exact match.  
A model can obtain a perfect score here without having to learn the correct 
ordering of the conjuncts and prefix terms.
Note that this metric, 
just like well-formedness but unlike the (strict) exact match accuracy, 
depends on the grammar used. Further note that if the prediction is not 
well-formed we consider the OiEMAcc to be 0.

**Average token-level edit distance.**
Uses [Levenshtein Distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
to measure average token-level edit distance between gold and system logical form.
We use NLTK to calculate it and use the standard version where substitution cost 
is 1 and transposition is  not among the atomic operations.  
Distances are non-negative, and lower distances are considered better: 
a distance of 0 is equivalent to a (strict) exact match, i.e. the prediction is 
equal to the gold standard form.


More to come...

*Possible future extensions*:  
- precision/recall/F1 for skolem constants like `x_1` (and maybe proper names, lambda vars too?) (prefix and conjunction seprate or overall?)
- precision/recall/F1 for predicate names like `eat.agent` and `cat` (prefix and conjunction seprate or overall?)
- precision/recall/F1 for correct terms like `cat(x_1)` or `eat.agent(x_2,x_1)` (prefix and conjunction seprate or overall?)


## 3. OpenNMT-independent evaluation

I propose to separate the framework used for building models (e.g. OpenNMT)
from the evaluation code, such that one can evaluate their models' predictions 
without using OpenNMT. Furthermore, this allows us to add more evaluation metrics as needed.

**to do** implement this
- `evaluator.py` contains Evaluator class and main function?
- `metrics.py`  contains different metrics (e.g. ExactMatchAccuracy )
- `readers.py` contains different readers (taking a file and returning a generator of CorpusInstance s)
- `corpus_instance.py` class for one sample from the corpus (sentence, logical form, required generalization type)
- `cogs_logical_form.py` class for the logical form, including parsing into it **to do** improve parser

**to do** how to call evaluator and get results (Python 3.7)
```bash
python3 evaluator.py --gold ../data/dev.tsv --system ../data/dev.tsv  # should give perfect results
python3 evaluator.py --gold ./sampledata/gold1.tsv --system ./sampledata/system1.tsv
```

```
python3 evaluator.py --gold ./sampledata/gold3.tsv --system ./sampledata/system3.tsv
Iterating over samples : 10it [00:00, 147.70it/s]
Full corpus evaluation:
Gold file:   ./sampledata/gold3.tsv
System file: ./sampledata/system3.tsv
Seen instances: 10
Exact match accuracy                     :  10.00 %
Well-formedness percentage               :  90.00 %
Order-invariant Exact match accuracy     :  20.00 %
Avg. token-level edit distance           :   9.30
```


## 4. References

- Kim, Najoung and Tal Linzen (2020).   
  *COGS: A Compositional Generalization Challenge Based on Semantic Interpretation*.  
  In Proceedings of the 2020 EMNLP (Online, Nov. 16–20, 2020).  
  Association for Computational Linguistics, pp. 9087–9105.
  doi: [10.18653/v1/2020.emnlp-main.731](https://www.aclweb.org/anthology/2020.emnlp-main.731).  
  Dataset and code on GitHub: https://github.com/najoungkim/COGS


-----------------------
#### Background: evaluation for other meaning representations

(These are some notes regarding how evaluation work for other meaning representations.
I hope this will function as an inspiration while developing the evaluation script.)

In grounded/executable semantic parsing, one can use execution match accuracy 
additionally to exact match accuracy. However, COGS is not grounded in a knowledge/data base.

Regarding graph-based meaning representations:
- AMR uses [Smatch](https://github.com/snowblink14/smatch) 
  (Cai & Knight [2013](https://www.aclweb.org/anthology/P13-2131/)), 
  see also the [AMR website](https://amr.isi.edu/evaluation.html)
- EDS uses EDM (Dridan & Open [2011](https://www.aclweb.org/anthology/W11-2927/))
- SDP([2014](https://alt.qcri.org/semeval2014/task8/)) uses U/L dependency F1 
  (see [paragraph](https://www.aclweb.org/anthology/S14-2008.pdf#page=7) in paper, 
  [website](https://alt.qcri.org/semeval2014/task8/index.php?id=evaluation), 
  [code](https://github.com/semantic-dependency-parsing/toolkit) on github)
- [MRP](http://mrp.nlpl.eu/2020/index.php) uses [mtool](https://github.com/cfmrp/mtool) (**todo cite?**): MRP score

Out of curiosity: because we treat semantic parsing as a seq2seq task here,
just like MT, what would traditional MT evaluation metrics,
e.g. [BLEU](https://en.wikipedia.org/wiki/BLEU) 
([Papineni et al. 2002](https://www.aclweb.org/anthology/P02-1040/)) and its
proposed successors/alternations,
tell us?
