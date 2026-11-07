# SHACL Validation and OWL Reasoner

During SHACL validation, two types of problems were initially found in the extracted data. First, some incorrect subjects were extracted from Wikipedia page headings and formatting, such as the symbol "=". Second, Murray Gell-Mann was assigned two birthplaces because the extraction program incorrectly treated his parents' place of origin as his own birthplace.

These problems were corrected by improving the extraction rules. The incorrect subjects and birthplace were removed. After running the validation program again, the result was **Conforms: True**. This shows that the data satisfies the defined SHACL constraints.

An OWL reasoner and SHACL have different purposes. An OWL reasoner uses ontology rules to infer new knowledge and identify logical relationships. It follows the Open World Assumption, meaning missing information is not automatically considered an error. SHACL checks data against specific conditions, such as requiring a person to have no more than one birthplace. It reports constraint violations when the data does not follow these conditions.

Therefore, OWL is mainly used for reasoning and knowledge inference, while SHACL is used for data validation and quality checking.