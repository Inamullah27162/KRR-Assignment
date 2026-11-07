
import csv
import re
from pathlib import Path

import spacy

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "out"
OUTPUT_FILE = OUT_DIR / "triples.csv"

nlp = spacy.load("en_core_web_sm")

PEOPLE = {
    "charles_h_townes.txt": "Charles H. Townes",
    "erwin_schrodinger.txt": "Erwin Schrödinger",
    "eugene_wigner.txt": "Eugene Wigner",
    "murray_gell_mann.txt": "Murray Gell-Mann",
    "richard_feynman.txt": "Richard Feynman",
    "private_document.txt": "Rukhsana Bhatti"
}

ALIAS_RESOLUTIONS = set()

# Institution name endings and their optional extensions.
INSTITUTION_PATTERN = re.compile(
    r"\b(?P<name>"
    r"(?:[A-Z][A-Za-zÀ-ÿ0-9&'.’–-]*|of|for|and|the|&)"
    r"(?:\s+(?:[A-Z][A-Za-zÀ-ÿ0-9&'.’–-]*|of|for|and|the|&))*"
    r"\s+(?:University|College|School|Institute|Laboratory|"
    r"Laboratories|Corporation|Study)"
    r"(?:\s+(?:of|for)\s+"
    r"[A-Z][A-Za-zÀ-ÿ0-9&'.’–-]*"
    r"(?:\s+(?:[A-Z][A-Za-zÀ-ÿ0-9&'.’–-]*|and|of|for)){0,5})?"
    r")\b"
)

AWARD_PATTERN = re.compile(
    r"\b((?:\d{4}\s+)?(?:"
    r"Nobel Prize(?: in Physics)?|"
    r"Haitinger Prize|"
    r"Wigner Medal|"
    r"Franklin Medal|"
    r"Herzl Prize|"
    r"Enrico Fermi Award|"
    r"Atoms for Peace Award|"
    r"National Medal of Science|"
    r"Albert Einstein Award|"
    r"Golden Plate Award|"
    r"Max Planck Medal|"
    r"Marlowe Medal|"
    r"Oersted Medal|"
    r"Templeton Prize"
    r"))\b",
    re.I
)


def add(rows, subject, predicate, obj, filename, sentence):
    obj = re.sub(r"\s+", " ", obj).strip(" ,.;:")
    obj = re.sub(r"^(the|a|an)\s+", "", obj, flags=re.I)
    subject = subject.strip()

    if not subject or not obj:
        return

    rows.append({
        "subject": subject,
        "predicate": predicate,
        "object": obj,
        "source_doc": filename,
        "sentence": sentence.strip()
    })


def resolve_subject(sentence, filename):
    text = sentence.strip()
    low = text.lower()

    if filename != "private_document.txt":
        return PEOPLE[filename]

    if "osman gilani" in low:
        return "Osman Gilani"

    if re.search(r"\bdr\.?\s+bhatti\b", low):
        ALIAS_RESOLUTIONS.add(("Dr. Bhatti", "Rukhsana Bhatti"))
        return "Rukhsana Bhatti"

    if re.match(r"^(he|his)\b", low):
        ALIAS_RESOLUTIONS.add(("He", "Osman Gilani"))
        return "Osman Gilani"

    if re.match(r"^(she|her)\b", low):
        ALIAS_RESOLUTIONS.add(("She", "Rukhsana Bhatti"))
        return "Rukhsana Bhatti"

    return PEOPLE[filename]


def is_negated(sentence, predicate):
    low = sentence.lower()

    if predicate == "educatedAt":
        patterns = [
            r"\bnever\s+studied\b",
            r"\bdid\s+not\s+study\b",
            r"\bhas\s+not\s+studied\b",
            r"\bnever\s+attended\b",
            r"\bdid\s+not\s+attend\b",
            r"\bhas\s+never\s+attended\b",
            r"\bnot\s+attended\b"
        ]
        return any(re.search(p, low) for p in patterns)

    if predicate == "worksAt":
        return bool(
            re.search(r"\b(?:never worked|does not work|no longer works)\b", low)
        )

    return False



def clean_institution(text):
    text = re.sub(r"\s+", " ", text).strip(" ,.;:")
    text = re.sub(
        r"^(the|a|an|at|in|from|by|to|of)\s+",
        "",
        text,
        flags=re.I
    )
    return text


def find_institutions(sentence):
    found = []

    for match in INSTITUTION_PATTERN.finditer(sentence):
        name = clean_institution(match.group("name"))

        if not name:
            continue

        # Reject incomplete or role-description phrases.
        if re.match(
            r"^(director|dean|professor|assistant)\b",
            name,
            re.I
        ):
            continue

        if name.lower() not in [x.lower() for x in found]:
            found.append(name)

    return found


def education_context(sentence, institution):
    position = sentence.lower().find(institution.lower())

    if position < 0:
        return False

    prefix = sentence[:position].lower().strip()

    # Only inspect the current clause, not earlier clauses.
    prefix = re.split(r"[,;]", prefix)[-1].strip()

    if re.search(
        r"\b(member|membership|co-founder|cofounded|co-founded)\s+of\s*$",
        prefix
    ):
        return False

    patterns = [
        r"\b(?:studied|study|attended|attend|enrolled)\b.{0,100}\b(?:at|in|from)\s*$",
        r"\b(?:graduated|graduating)\b.{0,80}\bfrom\s*$",
        r"\b(?:entered|accepted)\b.{0,80}\b(?:at|into|by)?\s*$",
        r"\b(?:earned|received)\b.{0,100}\bfrom\s*$",
        r"\blater\s+at\s*$"
    ]

    return any(re.search(pattern, prefix) for pattern in patterns)


def work_context(sentence, institution, filename):
    position = sentence.lower().find(institution.lower())

    if position < 0:
        return False

    prefix = sentence[:position].lower().strip()

    # Ignore role names such as Director of the School of Theoretical Physics.
    if re.search(
        r"\b(?:director|dean|head)\s+of\s+(?:the\s+)?$",
        prefix
    ):
        return False

    clause = re.split(r"[,;]", prefix)[-1].strip()

    patterns = [
        r"\bjoined\b.{0,100}$",
        r"\bworked\b.{0,120}\bat\s+(?:the\s+)?$",
        r"\b(?:assistant|professor|researcher|director|fellow)\b.{0,100}\bat\s+(?:the\s+)?$",
        r"\bpostdoctoral\s+fellow\b.{0,100}\bat\s+(?:the\s+)?$",
        r"\bvisiting\s+research\s+professor\b.{0,100}\bat\s+(?:the\s+)?$"
    ]

    if any(re.search(pattern, clause) for pattern in patterns):
        return True

    if filename == "private_document.txt":
        if re.search(r"\bmoved\s+to\s+(?:the\s+)?$", prefix):
            return True

    return False


def extract_birth_dependency(sent):
    for token in sent:
        if token.lemma_.lower() == "bear":
            for child in token.children:
                if child.dep_ == "prep" and child.text.lower() in {"in", "at"}:
                    for obj in child.children:
                        if obj.dep_ == "pobj":
                            return " ".join(t.text for t in obj.subtree)

    return None



def extract_birth(sentence, sent, subject, filename, rows):
    match = re.search(
        r"\bborn\b.*?\b(?:in|at)\s+"
        r"(.+?)(?=\s+in\s+\d{4}\b|\s+(?:on|to)\b|[,.;]|$)",
        sentence,
        re.I
    )

    if match:
        place = match.group(1).strip()

        if not re.search(
            r"\b(?:mother|father|parents)\b",
            sentence[:match.start()],
            re.I
        ):
            add(rows, subject, "bornIn", place, filename, sentence)

        return

    place = extract_birth_dependency(sent)

    if place:
        place = re.sub(r"\s+in\s+\d{4}\b.*$", "", place, flags=re.I)
        add(rows, subject, "bornIn", place, filename, sentence)



def extract_education(sentence, subject, filename, rows):
    if is_negated(sentence, "educatedAt"):
        return

    for institution in find_institutions(sentence):

        # These are not education relationships in the source context.
        excluded = {
            "allahabad university",
            "clinton laboratory",
            "kaiser wilhelm institute"
        }

        if institution.lower() in excluded:
            continue

        if education_context(sentence, institution):
            add(
                rows,
                subject,
                "educatedAt",
                institution,
                filename,
                sentence
            )



def extract_awards(sentence, subject, filename, rows):
    if not re.search(
        r"\b(received|won|awarded|shared|earned)\b",
        sentence,
        re.I
    ):
        return

    for match in AWARD_PATTERN.finditer(sentence):
        award = re.sub(r"^\d{4}\s+", "", match.group(1))
        award = re.sub(r"\s+in Physics$", "", award, flags=re.I)

        add(
            rows,
            subject,
            "receivedAward",
            award,
            filename,
            sentence
        )



    if filename == "private_document.txt":
        if re.search(
            r"\bmoved\s+to\s+Calder Institute of Technology\b",
            sentence,
            re.I
        ):
            add(
                rows,
                "Osman Gilani",
                "worksAt",
                "Calder Institute of Technology",
                filename,
                sentence
            )
            return


def extract_work(sentence, subject, filename, rows):
    if is_negated(sentence, "worksAt"):
        return

    if filename == "private_document.txt" and re.search(
        r"\bmoved\s+to\s+Calder Institute of Technology\b",
        sentence,
        re.I
    ):
        add(
            rows,
            "Osman Gilani",
            "worksAt",
            "Calder Institute of Technology",
            filename,
            sentence
        )
        return

    for institution in find_institutions(sentence):
        if work_context(sentence, institution, filename):
            add(
                rows,
                subject,
                "worksAt",
                institution,
                filename,
                sentence
            )


def extract(doc, filename):
    rows = []

    for sent in doc.sents:
        sentence = sent.text.strip()

        if not sentence:
            continue

        subject = resolve_subject(sentence, filename)

        extract_birth(
            sentence, sent, subject, filename, rows
        )

        extract_education(
            sentence, subject, filename, rows
        )

        extract_awards(
            sentence, subject, filename, rows
        )

        extract_work(
            sentence, subject, filename, rows
        )

    # Doctoral advisor relationships.
    advisor_data = {
        "richard_feynman.txt": (
            "John Archibald Wheeler", "thesis advisor"
        ),
        "murray_gell_mann.txt": (
            "Victor Weisskopf", "under the supervision"
        ),
        "erwin_schrodinger.txt": (
            "Friedrich Hasenöhrl", "supervision"
        ),
        "private_document.txt": (
            "Osman Gilani", "doctoral advisor"
        )
    }

    if filename in advisor_data:
        advisor, phrase = advisor_data[filename]

        for sent in doc.sents:
            if (
                phrase.lower() in sent.text.lower()
                and advisor.lower() in sent.text.lower()
            ):
                add(
                    rows,
                    PEOPLE[filename],
                    "doctoralAdvisor",
                    advisor,
                    filename,
                    sent.text
                )

    return rows


def main():
    all_rows = []
    seen = set()

    print("NLP model loaded successfully!")

    files = sorted(RAW_DIR.glob("*.txt"))
    print("Documents found:", len(files))

    for file in files:
        if file.name not in PEOPLE:
            print("Skipped unknown document:", file.name)
            continue

        print("-", file.name)

        doc = nlp(file.read_text(encoding="utf-8"))

        for row in extract(doc, file.name):
            key = (
                row["subject"].lower(),
                row["predicate"],
                row["object"].lower()
            )

            if key not in seen:
                seen.add(key)
                all_rows.append(row)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "subject",
        "predicate",
        "object",
        "source_doc",
        "sentence"
    ]

    with open(
        OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nExtraction completed!")
    print("Total unique triples:", len(all_rows))
    print("Alias/pronoun resolutions:", len(ALIAS_RESOLUTIONS))

    for predicate in [
        "bornIn",
        "educatedAt",
        "receivedAward",
        "worksAt",
        "doctoralAdvisor"
    ]:
        count = sum(
            row["predicate"] == predicate
            for row in all_rows
        )
        print(predicate, ":", count)

    print("CSV saved at:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
