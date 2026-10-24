from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .cleaning import clean_table
from .issues import IssueLog
from .rules import load_rules
from .sqlchecks import run_sql_checks
from .validate import (
    check_computed_totals,
    check_duplicate_keys,
    check_fields,
    check_foreign_keys,
)


@dataclass
class PipelineResult:
    issues: pd.DataFrame
    cleaned: dict
    raw_counts: dict
    rules: dict


def read_table(data_dir, spec):
    path = Path(data_dir) / spec["file"]
    if not path.exists():
        raise FileNotFoundError(f"Expected data file not found: {path}")
    return pd.read_csv(path, dtype="string", keep_default_na=False)


def run_checks(data_dir, rules_path, sql_path):
    """Clean every table, run every rule, then run the cross-table SQL checks."""
    rules = load_rules(rules_path)
    log = IssueLog(rules["categories"])
    cleaned = {}
    raw_counts = {}
    for table, spec in rules["tables"].items():
        raw = read_table(data_dir, spec)
        raw_counts[table] = len(raw)
        cleaned[table] = clean_table(raw, table, spec, rules, log)
    for table, spec in rules["tables"].items():
        check_fields(cleaned[table], table, spec, log)
        check_duplicate_keys(cleaned[table], table, spec, log)
    check_computed_totals(cleaned, rules, log)
    check_foreign_keys(cleaned, rules, log)
    run_sql_checks(cleaned, sql_path, log)
    return PipelineResult(issues=log.frame(), cleaned=cleaned, raw_counts=raw_counts, rules=rules)
