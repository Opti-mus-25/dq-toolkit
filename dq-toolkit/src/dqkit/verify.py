from collections import Counter

import pandas as pd

KEYS = ["category", "table", "record_key", "field"]


def _tuples(frame):
    return Counter(tuple(str(value) for value in row) for row in frame[KEYS].itertuples(index=False, name=None))


def compare(issues, manifest):
    """Compare detected issues with the planted answer key."""
    found = _tuples(issues)
    planted = _tuples(manifest)
    missed = sorted((planted - found).elements())
    unexpected = sorted((found - planted).elements())
    return {
        "planted": sum(planted.values()),
        "found": sum(found.values()),
        "missed": missed,
        "unexpected": unexpected,
        "exact_match": not missed and not unexpected,
    }


def load_manifest(path):
    return pd.read_csv(path, dtype="string", keep_default_na=False)
