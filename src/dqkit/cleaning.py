from datetime import datetime

import pandas as pd


def _record_key(df, idx, spec):
    return df.at[idx, spec["key"]]


def standardize_labels(df, table, spec, log):
    """Map label variants such as 'female' or 'f' to the approved value."""
    for field, field_spec in spec["fields"].items():
        label_map = field_spec.get("label_map")
        if not label_map or field not in df.columns:
            continue
        for idx, raw in df[field].items():
            if pd.isna(raw) or str(raw) == "":
                continue
            canonical = label_map.get(str(raw).strip().lower())
            if canonical is not None and canonical != raw:
                log.add(
                    "label_standardized",
                    table,
                    _record_key(df, idx, spec),
                    field,
                    raw,
                    f"Standardized '{raw}' to '{canonical}'",
                    action="auto_fixed",
                )
                df.at[idx, field] = canonical
    return df


def strip_and_blank(df):
    """Trim whitespace and treat empty strings as missing values."""
    for column in df.columns:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].mask(df[column] == "", pd.NA)
    return df


def parse_date(text, formats):
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def standardize_dates(df, table, spec, formats, log):
    """Convert every recognised date format to YYYY-MM-DD."""
    for field, field_spec in spec["fields"].items():
        if field_spec.get("type") != "date" or field not in df.columns:
            continue
        for idx, raw in df[field].items():
            if pd.isna(raw):
                continue
            parsed = parse_date(raw, formats)
            if parsed is None:
                continue
            iso = parsed.strftime("%Y-%m-%d")
            if iso != raw:
                log.add(
                    "date_format_standardized",
                    table,
                    _record_key(df, idx, spec),
                    field,
                    raw,
                    f"Converted date '{raw}' to '{iso}'",
                    action="auto_fixed",
                )
                df.at[idx, field] = iso
    return df


def remove_exact_duplicates(df, table, spec, log):
    """Drop rows that are identical to an earlier row and log each one."""
    duplicate_mask = df.duplicated(keep="first")
    for idx in df.index[duplicate_mask]:
        log.add(
            "duplicate_removed",
            table,
            _record_key(df, idx, spec),
            spec["key"],
            _record_key(df, idx, spec),
            "Removed an exact duplicate of an earlier row",
            action="auto_fixed",
        )
    return df.loc[~duplicate_mask].reset_index(drop=True)


def clean_table(raw, table, spec, rules, log):
    df = raw.copy()
    df = standardize_labels(df, table, spec, log)
    df = strip_and_blank(df)
    df = standardize_dates(df, table, spec, rules["date_formats"], log)
    df = remove_exact_duplicates(df, table, spec, log)
    return df
