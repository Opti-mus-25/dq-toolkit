import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 20261023
N_PARTICIPANTS = 200
AS_OF = date(2026, 10, 1)

ITEMS = ["orientation", "registration", "attention", "recall", "language"]
PARTICIPANT_COLUMNS = ["participant_id", "birth_date", "sex", "education_years", "enrollment_date"]
VISIT_COLUMNS = ["visit_id", "participant_id", "visit_date", "visit_number"]
COGNITIVE_COLUMNS = ["visit_id", "participant_id"] + ITEMS + ["total_reported"]
CLINICAL_COLUMNS = ["participant_id", "birth_date", "sex"]
MANIFEST_COLUMNS = ["category", "table", "record_key", "field"]


def iso(value):
    return value.strftime("%Y-%m-%d")


def us(value):
    return value.strftime("%m/%d/%Y")


def retotal(row):
    row["total_reported"] = str(sum(int(row[item]) for item in ITEMS))


def score_row(rng, visit_id, participant_id):
    row = {
        "visit_id": visit_id,
        "participant_id": participant_id,
        "orientation": str(rng.randint(7, 10)),
        "registration": "3",
        "attention": str(rng.randint(3, 5)),
        "recall": str(rng.randint(0, 3)),
        "language": str(rng.randint(6, 9)),
    }
    retotal(row)
    return row


def set_scores(row, **items):
    for name, value in items.items():
        row[name] = str(value)
    retotal(row)


def build_clean(rng):
    """Create a fully consistent synthetic dataset with no errors."""
    participants, visits, cognitive, clinical = [], [], [], []
    visit_counter = 0
    for number in range(1, N_PARTICIPANTS + 1):
        participant_id = f"P{number:04d}"
        birth = date(1930, 1, 1) + timedelta(days=rng.randint(0, 28 * 365))
        sex = rng.choice(["F", "M"])
        education = rng.randint(8, 20)
        enrollment = date(2015, 1, 1) + timedelta(days=rng.randint(0, 3649))
        participants.append(
            {
                "participant_id": participant_id,
                "birth_date": iso(birth),
                "sex": sex,
                "education_years": str(education),
                "enrollment_date": iso(enrollment),
            }
        )
        clinical.append({"participant_id": participant_id, "birth_date": iso(birth), "sex": sex})
        visit_date = enrollment
        for visit_number in range(1, 5):
            if visit_date > AS_OF:
                break
            visit_counter += 1
            visit_id = f"V{visit_counter:05d}"
            visits.append(
                {
                    "visit_id": visit_id,
                    "participant_id": participant_id,
                    "visit_date": iso(visit_date),
                    "visit_number": str(visit_number),
                }
            )
            if rng.random() < 0.75:
                cognitive.append(score_row(rng, visit_id, participant_id))
            visit_date += timedelta(days=rng.randint(300, 420))
    return participants, visits, cognitive, clinical


class Pool:
    """Hands out each record at most once so planted errors never overlap."""

    def __init__(self, rng, rows):
        self.rng = rng
        self.rows = list(rows)
        self.used = set()

    def take(self, count, where=None):
        candidates = [row for row in self.rows if id(row) not in self.used and (where is None or where(row))]
        chosen = self.rng.sample(candidates, count)
        for row in chosen:
            self.used.add(id(row))
        return chosen

    def claim(self, row):
        self.used.add(id(row))


def plant(rng, participants, visits, cognitive, clinical):
    """Inject a known set of errors and return the answer key."""
    manifest = []

    def log(table, record_key, field, category):
        manifest.append({"category": category, "table": table, "record_key": record_key, "field": field})

    people = Pool(rng, participants)
    visit_pool = Pool(rng, visits)
    score_pool = Pool(rng, cognitive)
    clinical_by_id = {row["participant_id"]: row for row in clinical}
    cognitive_visit_ids = {row["visit_id"] for row in cognitive}
    first_visit = {row["participant_id"]: row for row in visits if row["visit_number"] == "1"}

    def has_scores(row):
        return row["visit_id"] in cognitive_visit_ids

    def lacks_scores(row):
        return row["visit_id"] not in cognitive_visit_ids

    for person in people.take(4, lambda row: row["enrollment_date"] >= "2016-01-01"):
        visit = first_visit[person["participant_id"]]
        visit_pool.claim(visit)
        enrollment = date.fromisoformat(person["enrollment_date"])
        visit["visit_date"] = iso(enrollment - timedelta(days=rng.randint(20, 200)))
        log("visits", visit["visit_id"], "visit_date", "visit_before_enrollment")

    variants = {"F": ["female", "Female", "f", "F "], "M": ["Male", "male", "m", "M "]}
    for row in people.take(7):
        row["sex"] = rng.choice(variants[row["sex"]])
        log("participants", row["participant_id"], "sex", "label_standardized")

    for row in people.take(2):
        row["birth_date"] = us(date.fromisoformat(row["birth_date"]))
        log("participants", row["participant_id"], "birth_date", "date_format_standardized")
    row = people.take(1)[0]
    row["enrollment_date"] = us(date.fromisoformat(row["enrollment_date"]))
    log("participants", row["participant_id"], "enrollment_date", "date_format_standardized")
    for row in visit_pool.take(3):
        row["visit_date"] = us(date.fromisoformat(row["visit_date"]))
        log("visits", row["visit_id"], "visit_date", "date_format_standardized")

    row = people.take(1)[0]
    participants.append(dict(row))
    log("participants", row["participant_id"], "participant_id", "duplicate_removed")
    for row in visit_pool.take(2):
        visits.append(dict(row))
        log("visits", row["visit_id"], "visit_id", "duplicate_removed")

    for row in people.take(2):
        row["education_years"] = ""
        log("participants", row["participant_id"], "education_years", "missing_required")
    row = people.take(1)[0]
    row["sex"] = ""
    log("participants", row["participant_id"], "sex", "missing_required")
    row = people.take(1)[0]
    row["birth_date"] = ""
    log("participants", row["participant_id"], "birth_date", "missing_required")
    row = score_pool.take(1)[0]
    row["recall"] = ""
    log("cognitive_scores", row["visit_id"], "recall", "missing_required")
    row = visit_pool.take(1)[0]
    row["visit_date"] = ""
    log("visits", row["visit_id"], "visit_date", "missing_required")

    for row, bad in zip(people.take(2), ["twelve", "12.5"]):
        row["education_years"] = bad
        log("participants", row["participant_id"], "education_years", "invalid_type")
    row = score_pool.take(1)[0]
    row["attention"] = "N/A"
    log("cognitive_scores", row["visit_id"], "attention", "invalid_type")
    row = visit_pool.take(1)[0]
    row["visit_number"] = "two"
    log("visits", row["visit_id"], "visit_number", "invalid_type")

    for row, bad in zip(visit_pool.take(3, lacks_scores), ["V123", "V-0777", "VV0789"]):
        row["visit_id"] = bad
        log("visits", bad, "visit_id", "invalid_format")

    for row, bad in zip(people.take(3), ["X", "U", "Unknown"]):
        row["sex"] = bad
        log("participants", row["participant_id"], "sex", "invalid_category")

    for row, bad in zip(people.take(2), ["40", "-2"]):
        row["education_years"] = bad
        log("participants", row["participant_id"], "education_years", "out_of_range")
    row = people.take(1)[0]
    row["enrollment_date"] = "2010-06-01"
    log("participants", row["participant_id"], "enrollment_date", "out_of_range")
    row = visit_pool.take(1)[0]
    row["visit_date"] = "2031-05-14"
    log("visits", row["visit_id"], "visit_date", "out_of_range")
    row = visit_pool.take(1)[0]
    row["visit_number"] = "9"
    log("visits", row["visit_id"], "visit_number", "out_of_range")
    row = score_pool.take(1)[0]
    set_scores(row, orientation=14, registration=1, attention=1, recall=0, language=4)
    log("cognitive_scores", row["visit_id"], "orientation", "out_of_range")
    row = score_pool.take(1)[0]
    set_scores(row, orientation=6, registration=5, attention=1, recall=0, language=4)
    log("cognitive_scores", row["visit_id"], "registration", "out_of_range")
    row = score_pool.take(1)[0]
    set_scores(row, orientation=5, registration=1, attention=8, recall=0, language=4)
    log("cognitive_scores", row["visit_id"], "attention", "out_of_range")

    row = people.take(1)[0]
    copy = dict(row)
    education = int(row["education_years"])
    copy["education_years"] = str(education + 1 if education < 20 else education - 1)
    participants.append(copy)
    log("participants", row["participant_id"], "participant_id", "duplicate_conflict")
    row = visit_pool.take(1)[0]
    copy = dict(row)
    copy["visit_date"] = iso(date.fromisoformat(row["visit_date"]) + timedelta(days=7))
    visits.append(copy)
    log("visits", row["visit_id"], "visit_id", "duplicate_conflict")
    row = score_pool.take(1)[0]
    copy = dict(row)
    copy["recall"] = str((int(row["recall"]) + 1) % 4)
    retotal(copy)
    cognitive.append(copy)
    log("cognitive_scores", row["visit_id"], "visit_id", "duplicate_conflict")

    for row in score_pool.take(6):
        total = int(row["total_reported"])
        delta = rng.choice([1, 2, 3])
        row["total_reported"] = str(total + delta if total + delta <= 30 else total - delta)
        log("cognitive_scores", row["visit_id"], "total_reported", "total_score_mismatch")

    for row, bad in zip(visit_pool.take(2), ["P9001", "P9002"]):
        row["participant_id"] = bad
        log("visits", row["visit_id"], "participant_id", "orphan_record")
    for orphan_visit in ["V90001", "V90002"]:
        owner = rng.choice(participants[:N_PARTICIPANTS])["participant_id"]
        cognitive.append(score_row(rng, orphan_visit, owner))
        log("cognitive_scores", orphan_visit, "visit_id", "orphan_record")
    row = visit_pool.take(1, lacks_scores)[0]
    cognitive.append(score_row(rng, row["visit_id"], "P9003"))
    log("cognitive_scores", row["visit_id"], "participant_id", "orphan_record")

    for row in people.take(4):
        record = clinical_by_id[row["participant_id"]]
        shift = timedelta(days=rng.choice([-370, 370]))
        record["birth_date"] = iso(date.fromisoformat(record["birth_date"]) + shift)
        log("participants", row["participant_id"], "birth_date", "cross_db_birth_date_mismatch")
    for row in people.take(3):
        record = clinical_by_id[row["participant_id"]]
        record["sex"] = "M" if record["sex"] == "F" else "F"
        log("participants", row["participant_id"], "sex", "cross_db_sex_mismatch")
    for row in people.take(2):
        clinical.remove(clinical_by_id[row["participant_id"]])
        log("participants", row["participant_id"], "participant_id", "cross_db_missing_participant")
    for extra_id in ["P0901", "P0902"]:
        clinical.append(
            {
                "participant_id": extra_id,
                "birth_date": iso(date(1930, 1, 1) + timedelta(days=rng.randint(0, 28 * 365))),
                "sex": rng.choice(["F", "M"]),
            }
        )
        log("clinical_participants", extra_id, "participant_id", "cross_db_extra_participant")

    return manifest


def write_csv(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def generate(out_dir, manifest_path=None, clean=False, seed=SEED):
    """Write the four synthetic CSV files, and the answer key when errors are planted."""
    rng = random.Random(seed)
    participants, visits, cognitive, clinical = build_clean(rng)
    manifest = [] if clean else plant(rng, participants, visits, cognitive, clinical)
    out_dir = Path(out_dir)
    write_csv(out_dir / "participants.csv", PARTICIPANT_COLUMNS, participants)
    write_csv(out_dir / "visits.csv", VISIT_COLUMNS, visits)
    write_csv(out_dir / "cognitive_scores.csv", COGNITIVE_COLUMNS, cognitive)
    write_csv(out_dir / "clinical_participants.csv", CLINICAL_COLUMNS, clinical)
    if manifest_path is not None:
        write_csv(Path(manifest_path), MANIFEST_COLUMNS, manifest)
    return manifest
