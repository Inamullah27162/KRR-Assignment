
# Extraction Predictions

## Expected Triple Counts

| Predicate | Expected Triples |
|---|---:|
| bornIn | 6 |
| educatedAt | 18 |
| receivedAward | 16 |
| worksAt | 15 |
| doctoralAdvisor | 5 |

These are estimated counts before running the extraction program.

## Expected Lowest Precision

I expect worksAt to have the lowest precision because a person may have multiple historical affiliations, and the program may incorrectly identify an organization as a workplace.

## Expected Challenge in Private Document

The private document may create challenges in pronoun resolution, negation handling, and alias merging.

For example, "Dr. Bhatti" and "Rukhsana Bhatti" refer to the same person. The pronoun "He" refers to Osman Gilani. The statement that she never studied at Westmere University must not produce an educatedAt triple.
