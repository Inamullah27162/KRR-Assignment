# Error Analysis

## 1. Overview

The knowledge graph extraction system was evaluated against Wikidata records for five scientists using five predicates: bornIn, educatedAt, receivedAward, worksAt, and doctoralAdvisor.

The evaluation produced 28 true positives (TP), 2 false positives (FP), and 117 false negatives (FN). The results show that the system extracts some facts correctly but misses many facts available in Wikidata.

## 2. False Positives (FP)

Two false positives were found, both under the receivedAward predicate:

- Eugene Wigner — Golden Plate Award
- Eugene Wigner — Herzl Prize

These facts were extracted by the system but were not matched with the corresponding Wikidata reference records. Possible reasons include differences in award naming, entity matching, or incorrect extraction.

## 3. False Negatives (FN)

The system missed 117 facts in total.

Examples include:

- Richard Feynman — bornIn — Far Rockaway
- Charles H. Townes — educatedAt — Duke University
- Erwin Schrödinger — educatedAt — University of Oxford
- Eugene Wigner — educatedAt — Fasori Gimnazium
- Richard Feynman — educatedAt — Princeton University
- Charles H. Townes — receivedAward — Comstock Prize in Physics

The largest number of false negatives occurred in receivedAward (75), followed by worksAt (25), educatedAt (12), doctoralAdvisor (4), and bornIn (1).

Possible reasons include incomplete extraction rules, complex sentence structures, missing aliases, and differences between the source text and Wikidata records.

## 4. Predicate-wise Evaluation

| Predicate | TP | FP | FN |
|---|---:|---:|---:|
| bornIn | 5 | 0 | 1 |
| educatedAt | 4 | 0 | 12 |
| receivedAward | 16 | 2 | 75 |
| worksAt | 1 | 0 | 25 |
| doctoralAdvisor | 2 | 0 | 4 |

## 5. Conclusion and Improvements

The system achieved high precision for most predicates, but recall was low, especially for receivedAward and worksAt. This means that extracted facts were mostly correct, but many expected facts were missed.

Future improvements should include better sentence and dependency parsing, more complete relationship patterns, improved entity normalization, and better handling of aliases and complex sentence structures. Evaluation results should also be checked against the source documents to distinguish extraction errors from differences in Wikidata coverage.