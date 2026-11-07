
import csv
import re
from pathlib import Path

from rdflib import Graph, Namespace, RDF

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_FILE = BASE_DIR / "out" / "triples.csv"
ONTOLOGY_FILE = BASE_DIR / "ontology" / "ontology.ttl"
OUTPUT_FILE = BASE_DIR / "out" / "kg.ttl"

EX = Namespace("http://example.org/kg/24p-0009/")

MAIN_PEOPLE = {
    "Charles H. Townes",
    "Erwin Schrödinger",
    "Eugene Wigner",
    "Murray Gell-Mann",
    "Richard Feynman",
}

ALIASES = {
    "Townes": "Charles H. Townes",
    "Wigner": "Eugene Wigner",
    "Feynman": "Richard Feynman",
}

def normalize_name(name):
    name = name.strip()
    return ALIASES.get(name, name)

def make_uri(name):
    name = normalize_name(name)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-zA-Z0-9_-]", "", name)
    return EX[name]

graph = Graph()
graph.bind("ex", EX)

# Load ontology
graph.parse(ONTOLOGY_FILE, format="turtle")

# Read extracted triples
with open(CSV_FILE, encoding="utf-8") as file:
    reader = csv.DictReader(file)

    for row in reader:
        subject_name = normalize_name(row["subject"])
        object_name = row["object"].strip()
        predicate_name = row["predicate"].strip()

        subject = make_uri(subject_name)
        predicate = EX[predicate_name]
        obj = make_uri(object_name)

        graph.add((subject, predicate, obj))

        if subject_name in MAIN_PEOPLE:
            graph.add((subject, RDF.type, EX.Person))

        if predicate_name == "bornIn":
            graph.add((obj, RDF.type, EX.Place))

        elif predicate_name in {"educatedAt", "worksAt"}:
            graph.add((obj, RDF.type, EX.Organization))

        elif predicate_name == "receivedAward":
            graph.add((obj, RDF.type, EX.Award))

        elif predicate_name == "doctoralAdvisor":
            if object_name not in MAIN_PEOPLE:
                graph.add((obj, RDF.type, EX.Person))

# Save Knowledge Graph
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
graph.serialize(destination=str(OUTPUT_FILE), format="turtle")

print("Knowledge Graph created successfully!")
print("Total RDF triples:", len(graph))
print("Saved at:", OUTPUT_FILE)
