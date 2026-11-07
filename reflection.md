# Reflection

In this assignment, I developed a Knowledge Graph using information extracted from five Wikipedia articles and one private document. The main purpose was to identify relationships between people and other entities using five predicates: bornIn, educatedAt, receivedAward, worksAt, and doctoralAdvisor.

I used Python and spaCy for information extraction, RDFLib to build the Knowledge Graph, and SHACL to validate the graph. I also used Apache Jena Fuseki to upload the graph and execute SPARQL queries.

During development, I faced several challenges. Some extraction rules selected incorrect information, while other rules missed relevant relationships. I improved the extraction process by refining the award extraction rules, correcting birthplace extraction and normalization, and adding conditions to avoid incorrect university matches.

The evaluation results showed improvement in several areas. For example, receivedAward true positives increased from 5 to 16, and its precision improved from 0.278 to 0.889. For bornIn, true positives increased from 3 to 5, and precision remained 1.000. The final Knowledge Graph contained 91 RDF triples, and SHACL validation confirmed that the graph conforms to the defined shapes.

The SPARQL queries helped me explore the graph, count relationships, find people without education records, identify common birthplaces, and retrieve doctoral advisor relationships.

However, some limitations remained. The worksAt predicate had no true positives, and the recall for educatedAt and receivedAward remained low. Some facts available in Wikidata were not found in the selected documents. This shows that rule-based information extraction cannot identify every relationship correctly.

Overall, this assignment helped me understand knowledge representation, ontology design, information extraction, RDF, SHACL validation, and SPARQL querying. I also learned that improving extraction rules can increase the accuracy of a Knowledge Graph.