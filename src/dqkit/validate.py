import re
from datetime import datetime

import pandas as pd

INT_PATTERN = re.compile(r"^-?\d+$")


def is_iso_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _range_issue(value, field_spec):
    """Return a message when value falls outside min/max, otherwise None."""
    low = field_spec.get("min")
    high = field_spec.get("max")
    if low is not None and value < low:
        return f"Value {value} is below the minimum of {low}"
    if high is not None and value > high:
        return f"Value {value} is above the maximum of {high}"
    return None


def check_fields(df, table, spec, log):
    """Apply the type, required, pattern, allowed-list, and range rules to every field."""
    key = spec["key"]
    for field, field_spec in spec["fields"].items():
        if field not in df.columns:
            log.add("missing_column", table, None, field, None, f"Column '{field}' is not in {spec['file']}")
            continue
        kind = field_spec.get("type", "string")
        for idx, value in df[field].items():
            record_key = df.at[idx, key] if key in df.columns else None
            if pd.isna(value):
                if field_spec.get("required"):
                    log.add("missing_required", table, record_key, field, None, f"{field_spec['label']} is required but empty")
                continue
            if kind == "int":
                if not INT_PATTERN.match(value):
                    log.add("invalid_type", table, record_key, field, value, f"'{value}' is not a whole number")
                    continue
                message = _range_issue(int(value), field_spec)
                if message:
                    log.add("out_of_range", table, record_key, field, value, message)
            elif kind == "date":
                if not is_iso_date(value):
                    log.add("invalid_type", table, record_key, field, value, f"'{value}' is not a valid date")
                    continue
                message = _range_issue(value, field_spec)
                if message:
                    log.add("out_of_range", table, record_key, field, value, message)
            elif kind == "category":
                if value not in field_spec["allowed"]:
                    allowed = ", ".join(field_spec["allowed"])
                    log.add("invalid_category", table, record_key, field, value, f"'{value}' is not one of: {allowed}")
            else:
                pattern = field_spec.get("pattern")
                if pattern and not re.match(pattern, value):
                    log.add("invalid_format", table, record_key, field, value, f"'{value}' does not match the pattern {pattern}")


def check_duplicate_keys(df, table, spec, log):
    """Report keys that appear more than once with different values."""
    key = spec["key"]
    if key not in df.columns:
        return
    counts = df[key].dropna().value_counts().sort_index()
    for value, count in counts[counts > 1].items():
        log.add("duplicate_conflict", table, value, key, value, f"Key {value} appears {count} times with different values")


def check_computed_totals(tables, rules, log):
    """Compare each reported total with the sum of its item scores."""
    for config in rules.get("computed_totals", []):
        table = config["table"]
        df = tables[table]
        key = rules["tables"][table]["key"]
        fields = list(config["item_fields"]) + [config["total_field"]]
        if any(field not in df.columns for field in fields):
            continue
        for idx in df.index:
            values = [df.at[idx, field] for field in fields]
            if any(pd.isna(value) or not INT_PATTERN.match(value) for value in values):
                continue
            item_sum = sum(int(value) for value in values[:-1])
            reported = int(values[-1])
            if item_sum != reported:
                log.add(
                    "total_score_mismatch",
                    table,
                    df.at[idx, key],
                    config["total_field"],
                    reported,
                    f"Reported total {reported} but item scores add up to {item_sum}",
                )


def check_foreign_keys(tables, rules, log):
    """Find child records whose ID does not exist in the parent table."""
    for fk in rules.get("foreign_keys", []):
        child = tables[fk["table"]]
        parent = tables[fk["ref_table"]]
        if fk["field"] not in child.columns or fk["ref_field"] not in parent.columns:
            continue
        valid = set(parent[fk["ref_field"]].dropna())
        key = rules["tables"][fk["table"]]["key"]
        for idx, value in child[fk["field"]].items():
            if pd.isna(value) or value in valid:
                continue
            log.add(
                "orphan_record",
                fk["table"],
                child.at[idx, key],
                fk["field"],
                value,
                f"{value} does not exist in {fk['ref_table']}.{fk['ref_field']}",
            )
