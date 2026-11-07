
import csv
import re
import time
from pathlib import Path

import requests

BASE_DIR = Path(__file__).resolve().parent.parent
TRIPLES_FILE = BASE_DIR / "out" / "triples.csv"
RESULTS_DIR = BASE_DIR / "results"

API_URL = "https://www.wikidata.org/w/api.php"

PEOPLE = {
    "Eugene Wigner": "Eugene Wigner",
    "Charles H. Townes": "Charles H. Townes",
    "Richard Feynman": "Richard Feynman",
    "Erwin Schrödinger": "Erwin Schrödinger",
    "Murray Gell-Mann": "Murray Gell-Mann"
}

PROPERTIES = {
    "bornIn": "P19",
    "educatedAt": "P69",
    "receivedAward": "P166",
    "worksAt": "P108",
    "doctoralAdvisor": "P184"
}

ALIASES = {
    "wigner": "Eugene Wigner",
    "feynman": "Richard Feynman",
    "schrödinger": "Erwin Schrödinger",
    "schrodinger": "Erwin Schrödinger"
}

session = requests.Session()

session.headers.update({
    "User-Agent": "KRR-Assignment/1.0 (student knowledge graph evaluation)"
})


def normalize(value):
    value = value.lower().strip()

    value = value.replace("ö", "o")
    value = value.replace("é", "e")
    value = value.replace("á", "a")
    value = value.replace("ü", "u")
    value = value.replace("ä", "a")

    value = re.sub(r"[^a-z0-9]+", " ", value)

    return " ".join(value.split())


def normalize_value(value):

    normalized = normalize(value)

    # Remove year prefixes from award names.
    normalized = re.sub(
        r"^\d{4}\s+",
        "",
        normalized
    )

    # Standardize common institution and award names.
    aliases = {
        "fasori evangelikus gimnazium": "fasori gimnazium",
        "fasori gimnazium": "fasori gimnazium",

        "yale university": "yale",
        "yale college": "yale",

        "nobel prize in physics": "nobel prize",
        "nobel prize": "nobel prize",

        "enrico fermi award": "enrico fermi award",
        "atoms for peace award": "atoms for peace award",
        "national medal of science": "national medal of science"
    }

    return aliases.get(normalized, normalized)

def safe_get(params):

    for attempt in range(6):

        response = session.get(
            API_URL,
            params=params,
            timeout=30
        )

        if response.status_code == 429:

            retry_after = response.headers.get("Retry-After")

            if retry_after and retry_after.isdigit():
                wait_time = int(retry_after)
            else:
                wait_time = 10 * (attempt + 1)

            print(
                f"Rate limit reached. Waiting {wait_time} seconds..."
            )

            time.sleep(wait_time)
            continue

        response.raise_for_status()

        time.sleep(3)

        return response

    raise Exception(
        "Wikidata rate limit exceeded. Please try again later."
    )


def search_person(person):

    if person == "Eugene Wigner":
        return "Q155790"

    params = {
        "action": "wbsearchentities",
        "search": person,
        "language": "en",
        "format": "json",
        "limit": 10
    }

    response = safe_get(params)

    results = response.json().get("search", [])

    if not results:
        raise ValueError(
            f"No Wikidata result found for {person}"
        )

    for result in results:

        label = result.get("label", "").strip().lower()

        aliases = [
            alias.lower()
            for alias in result.get("aliases", [])
        ]

        if person.lower() == label or person.lower() in aliases:
            return result["id"]

    print(f"\nPossible Wikidata matches for {person}:")

    for result in results[:5]:

        print(
            result.get("id"),
            "-",
            result.get("label"),
            "-",
            result.get("description", "")
        )

    return results[0]["id"]


def get_entity_values(qid, property_id):

    response = safe_get({
        "action": "wbgetentities",
        "ids": qid,
        "props": "claims",
        "format": "json"
    })

    entity = response.json()["entities"][qid]

    claims = entity.get("claims", {}).get(property_id, [])

    entity_ids = []

    for claim in claims:

        value = claim.get("mainsnak", {}).get("datavalue")

        if value and value["type"] == "wikibase-entityid":

            entity_ids.append(
                value["value"]["id"]
            )

    entity_ids = list(dict.fromkeys(entity_ids))

    if not entity_ids:
        return set()

    labels = set()

    for start in range(0, len(entity_ids), 50):

        batch = entity_ids[start:start + 50]

        label_response = safe_get({
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "labels",
            "languages": "en",
            "format": "json"
        })

        entities = label_response.json()["entities"]

        for item in entities.values():

            label = (
                item.get("labels", {})
                .get("en", {})
                .get("value")
            )

            if label:
                labels.add(label)

    return labels


def load_extracted_triples():

    extracted = []

    with open(TRIPLES_FILE, encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:

            # Do not evaluate private document facts.
            if row["source_doc"] == "private_document.txt":
                continue

            subject = row["subject"].strip()

            subject = ALIASES.get(
                subject.lower(),
                subject
            )

            if subject in PEOPLE:

                extracted.append({
                    "subject": subject,
                    "predicate": row["predicate"],
                    "object": row["object"].strip()
                })

    return extracted


def main():

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    extracted = load_extracted_triples()

    wikidata_data = {}
    qids = {}

    print("Retrieving Wikidata records...")

    for person in PEOPLE:

        qid = search_person(person)

        qids[person] = qid

        print(f"{person}: {qid}")

        for predicate, property_id in PROPERTIES.items():

            values = get_entity_values(
                qid,
                property_id
            )

            wikidata_data[(person, predicate)] = values

    # Save Wikidata values.

    with open(
        RESULTS_DIR / "wikidata_values.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "person",
            "qid",
            "predicate",
            "wikidata_property",
            "value"
        ])

        for person in PEOPLE:

            for predicate, property_id in PROPERTIES.items():

                for value in sorted(
                    wikidata_data[(person, predicate)]
                ):

                    writer.writerow([
                        person,
                        qids[person],
                        predicate,
                        property_id,
                        value
                    ])

    details = []
    summary = []

    # Compare extracted values with Wikidata values.

    for predicate in PROPERTIES:

        extracted_set = set()
        wikidata_set = set()

        for row in extracted:

            if row["predicate"] == predicate:

                extracted_set.add((
                    row["subject"],
                    normalize_value(row["object"])
                ))

        for person in PEOPLE:

            for value in wikidata_data[(person, predicate)]:

                wikidata_set.add((
                    person,
                    normalize_value(value)
                ))

        true_positives = extracted_set & wikidata_set

        false_positives = extracted_set - wikidata_set

        false_negatives = wikidata_set - extracted_set

        for person, value in sorted(true_positives):

            details.append([
                person,
                predicate,
                value,
                "TP"
            ])

        for person, value in sorted(false_positives):

            details.append([
                person,
                predicate,
                value,
                "FP"
            ])

        for person, value in sorted(false_negatives):

            details.append([
                person,
                predicate,
                value,
                "FN"
            ])

        tp = len(true_positives)
        fp = len(false_positives)
        fn = len(false_negatives)

        precision = (
            tp / (tp + fp)
            if tp + fp else 0
        )

        recall = (
            tp / (tp + fn)
            if tp + fn else 0
        )

        summary.append([
            predicate,
            tp,
            fp,
            fn,
            round(precision, 3),
            round(recall, 3)
        ])

    # Save detailed evaluation.

    with open(
        RESULTS_DIR / "evaluation_details.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "person",
            "predicate",
            "value",
            "result"
        ])

        writer.writerows(details)

    # Save evaluation summary.

    with open(
        RESULTS_DIR / "evaluation_summary.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(file)

        writer.writerow([
            "predicate",
            "TP",
            "FP",
            "FN",
            "precision",
            "recall"
        ])

        writer.writerows(summary)

    print("\nEvaluation completed!")

    print(
        "\nPredicate      TP   FP   FN   Precision   Recall"
    )

    for row in summary:

        print(
            f"{row[0]:15} {row[1]:3}  {row[2]:3}  {row[3]:3}"
            f"    {row[4]:.3f}       {row[5]:.3f}"
        )

    print("\nFiles saved in:", RESULTS_DIR)


if __name__ == "__main__":
    main()
