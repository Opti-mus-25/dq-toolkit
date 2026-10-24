# SOP: Data Quality Review of Incoming Research Data

Scope: weekly review of exported research tables before they are used for analysis.
All data in this repository is synthetic. This SOP shows the process, it is not an official procedure of any organization.

## 1. Purpose

Find errors in incoming data, fix the ones that are safe to fix automatically, and send everything else to the person who can resolve it, with a record of what happened.

## 2. Inputs

| File | Contents |
| --- | --- |
| participants.csv | One row per enrolled participant |
| visits.csv | One row per study visit |
| cognitive_scores.csv | One row per visit with a cognitive screen |
| clinical_participants.csv | Demographics from the separate clinical database |

The rules for every field live in `rules/rules.yaml`. Cross-table checks live in `sql/cross_checks.sql`.

## 3. Steps

1. Place the new exports in `data/raw/`. Never edit the raw files by hand. They stay as received.
2. Run `python -m dqkit check`.
3. Open `output/discrepancy_report.xlsx`. Start on the Summary sheet, then work through Needs Review.
4. For each issue in Needs Review, send it to the team in the `route_to` column (see section 5).
5. Review the Auto-fixes sheet. Spot check at least 10 rows to confirm the fixes were correct.
6. When the owners reply with corrected values, the correction is made in the source system, a new export is placed in `data/raw/`, and the check is run again.
7. The review is finished when Needs Review is empty or every remaining item has a documented reason.
8. Keep `issues_log.csv` with the export it belongs to.

## 4. What is fixed automatically and what is not

Fixed automatically and logged row by row (low risk, the intended value is not in doubt):

- Label variants standardized, such as `female` or `f` to `F`.
- Dates written as MM/DD/YYYY converted to YYYY-MM-DD.
- Exact duplicate rows removed.

Never fixed automatically (a person must decide what the true value is):

- Missing required values, wrong types, values out of range, invalid categories, bad ID formats.
- Duplicate keys with different values.
- Total scores that do not match their item scores.
- Records that refer to an ID that does not exist.
- Visit dates before enrollment.
- Any difference between the research and clinical databases.

The checker reports these and leaves the value untouched.

## 5. Routing

| Category | Severity | Send to |
| --- | --- | --- |
| missing_required, invalid_type, out_of_range, invalid_category | high / medium | Clinical Core study coordinator |
| total_score_mismatch, visit_before_enrollment | high | Clinical Core study coordinator |
| duplicate_conflict, orphan_record, invalid_format, missing_column | high / medium | Data Services |
| cross_db_* (any difference between the two databases) | high / medium | Data Services (cross-database) |

Severity guide: high means the data cannot be trusted for analysis until resolved. Medium means it should be fixed but does not block other work. Low is informational (all automatic fixes).

## 6. Writing up an issue

Each issue sent to an owner includes: issue ID, table, record key, field, the value found, and the message from the report. Do not include more participant information than needed to find the record.

## 7. Changing the rules

Rules are changed only by editing `rules/rules.yaml` and re-running the tests (`python -m pytest`). Record the reason for the change in the commit message. A rule change is never made to hide an error.

## 8. Privacy

Real participant data must never be committed to this repository or pasted into a report that is shared outside the approved team. The synthetic data here contains no real people.
