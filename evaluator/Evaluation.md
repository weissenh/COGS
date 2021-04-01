author: [weissenh](https://github.com/weissenh) (Disclaimer: I'm not one of the authors of the COGS paper!)

**this is work in progress**

This should be a documentation of my efforts to evaluate models predictions on 
COGS (independent of OpenNMT) along with some proposed additional evaluation metrics.

Table of contents:
1. What is reported in the COGS paper
2. Extending evaluation beyond exact match accuracy
3. OpenNMT-independent evaluation
4. References


## 1. What is reported in the COGS paper

The COGS paper (Kim & Linzen [2020](https://www.aclweb.org/anthology/2020.emnlp-main.731)):

> An output sequence is considered correct only if it exactly matches the gold sequence. 
> (p. 9092, caption of Figure 2(a))

Additionally in appendix G2, p. 9102, they comment on 
average token-level edit distance and ill-formedness.

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
* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 ) AND want . xcomp( x _ 2 , x _ 4 ) AND go . agent ( x _ 4 , x _ 1 )
```
The following forms are all considered equally 'bad' by the exact match accuracy,
ranging from just conjuncts permuted, over only one token wrong, a conjunct missing, to completely off.
```
* boy ( x _ 1 ) ; go . agent ( x _ 4 , x _ 1 ) AND want . xcomp( x _ 2 , x _ 4 ) AND want . agent ( x _ 2 , x _ 1 )
* boy ( x _ 0 ) ; want . agent ( x _ 2 , x _ 1 ) AND want . xcomp( x _ 2 , x _ 4 ) AND go . agent ( x _ 4 , x _ 1 )
* boy ( x _ 1 ) ; want . agent ( x _ 2 , x _ 1 ) AND go . agent ( x _ 4 , x _ 1 )
girl ( x _ 1 ) AND go . agent ( x _ 2 , x _ 7 )
```
In the above examples token-edit distance can help for some of the examples,
but especially for the first (conjuncts permuted) this might overestimate the errors made,
especially if we assume that the order of the conjuncts shouldn't affect the 'meaning' of the sentence.

### Proposed additions

**to do**: additions
- [ ] token-level edit distance (since it is reported in the paper, code from the authors?)
- [ ] well-formedness
- [ ] partial success?


## 3. OpenNMT-independent evaluation

I propose to separate the framework used for building models (e.g. OpenNMT)
from the evaluation code, such that one can evaluate their models prediction 
without using OpenNMT. Furthermore, this allows us add more evaluation metrics as needed.

**to do** implement this
- `evaluator.py` contains Evaluator class and main function?
- `metrics.py`  contains different metrics (e.g. ExactMatchAccuracy )
- `readers.py` contains different readers (taking a file and returning a generator of CorpusInstance s)
- `corpus_instance.py` class for one sample from the corpus, includes parsing the logical form

**to do** how to call evaluator and get results (Python 3.7)
```bash
python3 evaluator.py --gold ../data/dev.tsv --system ../data/dev.tsv  # should give perfect results
python3 evaluator.py --gold ./sampledata/gold1.tsv --system ./sampledata/system1.tsv
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

