# Knowledge Representation and Reasoning Assignment

**Roll Number:** 24P-0009

## Project Overview
This project extracts information from five Wikipedia text documents and one private document to create a Knowledge Graph. The extracted information is stored as RDF triples, validated using SHACL, and evaluated against Wikidata records.

## Project Structure

- `data/raw/` — Five Wikipedia text files and private document.
- `src/` — Python scripts for extraction, graph construction, validation, and evaluation.
- `out/` — Extracted triples, RDF knowledge graph, and SHACL validation report.
- `ontology/` — Ontology, SHACL shapes, and SHACL notes.
- `queries/` — Six SPARQL queries.
- `results/` — Results of the six SPARQL queries and evaluation files.
- `eval/` — Evaluation metrics, Wikidata values, evaluation details, and error analysis.
- `screenshots/` — Screenshots of query results, graph count, evaluation, and validation.
- `predictions.md` — Predictions made for the assignment.
- `reflection.md` — Project reflection.

## Requirements
- Python 3
- Required Python libraries used by the project
- spaCy English language model (`en_core_web_sm`)

## How to Run

Run these commands from the project directory:

```bash
python src/extract.py
python src/build_graph.py
python src/validate.py
python src/evaluate.py
```

The scripts generate the extracted triples, knowledge graph, SHACL validation report, and evaluation results.

## Extraction Rules

The system extracts the following relationships:

1. **bornIn** — Identifies a person's place of birth.
2. **educatedAt** — Identifies educational institutions attended by a person.
3. **receivedAward** — Identifies awards received by a person.
4. **worksAt** — Identifies an organization where a person works.
5. **doctoralAdvisor** — Identifies a person's doctoral advisor.

The extraction process also handles selected aliases and pronouns to connect references to the correct person.

## Knowledge Graph and Validation

The extracted triples are converted into RDF data and stored in `out/kg.ttl`.

The ontology defines the knowledge graph classes and properties. SHACL shapes are used to validate the graph. The validation report is saved in `out/shacl_report.txt`.

## SPARQL Queries

Six SPARQL queries are available in the `queries/` directory. Their output files are stored in the `results/` directory.

## Evaluation

The extracted information is evaluated against Wikidata values. Evaluation metrics include:

- True Positives (TP)
- False Positives (FP)
- False Negatives (FN)
- Precision
- Recall

Detailed metrics and error analysis are available in the `eval/` directory.

## Fuseki Dataset

The knowledge graph can be loaded into Apache Jena Fuseki using the dataset:

`kg-24p-0009`

The named graph is:

`http://example.org/kg/24p-0009/graph`

## Conclusion

This project demonstrates information extraction, ontology development, RDF knowledge graph construction, SHACL validation, SPARQL querying, and evaluation against Wikidata.