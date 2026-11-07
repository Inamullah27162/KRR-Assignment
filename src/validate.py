
import csv
from pathlib import Path

from rdflib import Graph, Namespace, URIRef, RDF
from pyshacl import validate


BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "out" / "triples.csv"
ONTOLOGY_FILE = BASE_DIR / "ontology" / "ontology.ttl"
SHAPES_FILE = BASE_DIR / "ontology" / "shapes.ttl"
REPORT_FILE = BASE_DIR / "out" / "shacl_report.txt"

EX = Namespace("http://example.org/kg/24p-0009/")


# Create RDF graph
data_graph = Graph()
data_graph.bind("ex", EX)

# Load extracted triples
with open(CSV_FILE, encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        subject = EX[row["subject"].replace(" ", "_")]
        obj = EX[row["object"].replace(" ", "_")]

        predicate = EX[row["predicate"]]

        data_graph.add((subject, predicate, obj))

        # Assign subject class
        data_graph.add((subject, RDF.type, EX.Person))

        # Assign object class according to predicate
        if row["predicate"] == "bornIn":
            data_graph.add((obj, RDF.type, EX.Place))

        elif row["predicate"] in {
            "educatedAt",
            "worksAt"
        }:
            data_graph.add((obj, RDF.type, EX.Organization))

        elif row["predicate"] == "receivedAward":
            data_graph.add((obj, RDF.type, EX.Award))

        elif row["predicate"] == "doctoralAdvisor":
            data_graph.add((obj, RDF.type, EX.Person))


# Load ontology and SHACL shapes
ontology_graph = Graph()
ontology_graph.parse(ONTOLOGY_FILE, format="turtle")

shapes_graph = Graph()
shapes_graph.parse(SHAPES_FILE, format="turtle")


# Run SHACL validation
conforms, results_graph, results_text = validate(
    data_graph,
    shacl_graph=shapes_graph,
    ont_graph=ontology_graph,
    inference="none",
    abort_on_first=False,
    allow_infos=False,
    allow_warnings=False
)


# Save validation report
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

with open(REPORT_FILE, "w", encoding="utf-8") as file:

    file.write("SHACL VALIDATION REPORT\n")
    file.write("=======================\n\n")

    file.write(f"Total RDF triples: {len(data_graph)}\n")
    file.write(f"Conforms: {conforms}\n\n")

    file.write(str(results_text))


print("SHACL validation completed!")
print("Total RDF triples:", len(data_graph))
print("Conforms:", conforms)
print("Report saved at:", REPORT_FILE)
