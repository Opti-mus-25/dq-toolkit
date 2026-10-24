# Data Quality Discrepancy Report

Synthetic practice data. No real participants.

## Run summary

| table | rows_read | rows_after_cleaning |
| --- | --- | --- |
| participants | 202 | 201 |
| visits | 782 | 780 |
| cognitive_scores | 577 | 577 |
| clinical_participants | 200 | 200 |

- Issues needing review: **53**
- Fixes applied automatically and logged: **16**

## Counts by category

| action | severity | category | route_to | count |
| --- | --- | --- | --- | --- |
| needs_review | high | cross_db_birth_date_mismatch | Data Services (cross-database) | 4 |
| needs_review | high | cross_db_missing_participant | Data Services (cross-database) | 2 |
| needs_review | high | cross_db_sex_mismatch | Data Services (cross-database) | 3 |
| needs_review | high | duplicate_conflict | Data Services | 3 |
| needs_review | high | invalid_type | Clinical Core study coordinator | 4 |
| needs_review | high | missing_required | Clinical Core study coordinator | 6 |
| needs_review | high | orphan_record | Data Services | 5 |
| needs_review | high | out_of_range | Clinical Core study coordinator | 8 |
| needs_review | high | total_score_mismatch | Clinical Core study coordinator | 6 |
| needs_review | high | visit_before_enrollment | Clinical Core study coordinator | 4 |
| needs_review | medium | cross_db_extra_participant | Data Services (cross-database) | 2 |
| needs_review | medium | invalid_category | Clinical Core study coordinator | 3 |
| needs_review | medium | invalid_format | Data Services | 3 |
| auto_fixed | low | date_format_standardized | None (auto-fixed and logged) | 6 |
| auto_fixed | low | duplicate_removed | None (auto-fixed and logged) | 3 |
| auto_fixed | low | label_standardized | None (auto-fixed and logged) | 7 |

## Issues needing review, grouped by who resolves them

### Clinical Core study coordinator (31)

| issue_id | severity | category | table | record_key | field | value | message |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DQ-0040 | high | invalid_type | cognitive_scores | V00473 | attention | N/A | 'N/A' is not a whole number |
| DQ-0023 | high | invalid_type | participants | P0061 | education_years | twelve | 'twelve' is not a whole number |
| DQ-0024 | high | invalid_type | participants | P0110 | education_years | 12.5 | '12.5' is not a whole number |
| DQ-0035 | high | invalid_type | visits | V00332 | visit_number | two | 'two' is not a whole number |
| DQ-0042 | high | missing_required | cognitive_scores | V00497 | recall |  | Recall (0-3) is required but empty |
| DQ-0017 | high | missing_required | participants | P0043 | birth_date |  | Date of birth is required but empty |
| DQ-0018 | high | missing_required | participants | P0071 | sex |  | Sex is required but empty |
| DQ-0026 | high | missing_required | participants | P0197 | education_years |  | Years of education is required but empty |
| DQ-0027 | high | missing_required | participants | P0198 | education_years |  | Years of education is required but empty |
| DQ-0033 | high | missing_required | visits | V00145 | visit_date |  | Visit date is required but empty |
| DQ-0038 | high | out_of_range | cognitive_scores | V00047 | orientation | 14 | Value 14 is above the maximum of 10 |
| DQ-0039 | high | out_of_range | cognitive_scores | V00136 | registration | 5 | Value 5 is above the maximum of 3 |
| DQ-0041 | high | out_of_range | cognitive_scores | V00532 | attention | 8 | Value 8 is above the maximum of 5 |
| DQ-0022 | high | out_of_range | participants | P0050 | education_years | -2 | Value -2 is below the minimum of 0 |
| DQ-0028 | high | out_of_range | participants | P0076 | enrollment_date | 2010-06-01 | Value 2010-06-01 is below the minimum of 2015-01-01 |
| DQ-0025 | high | out_of_range | participants | P0113 | education_years | 40 | Value 40 is above the maximum of 25 |
| DQ-0034 | high | out_of_range | visits | V00188 | visit_date | 2031-05-14 | Value 2031-05-14 is above the maximum of 2026-12-31 |
| DQ-0036 | high | out_of_range | visits | V00717 | visit_number | 9 | Value 9 is above the maximum of 6 |
| DQ-0044 | high | total_score_mismatch | cognitive_scores | V00005 | total_reported | 25 | Reported total 25 but item scores add up to 24 |
| DQ-0045 | high | total_score_mismatch | cognitive_scores | V00065 | total_reported | 29 | Reported total 29 but item scores add up to 26 |
| DQ-0046 | high | total_score_mismatch | cognitive_scores | V00511 | total_reported | 24 | Reported total 24 but item scores add up to 22 |
| DQ-0047 | high | total_score_mismatch | cognitive_scores | V00517 | total_reported | 28 | Reported total 28 but item scores add up to 27 |
| DQ-0048 | high | total_score_mismatch | cognitive_scores | V00580 | total_reported | 27 | Reported total 27 but item scores add up to 25 |
| DQ-0049 | high | total_score_mismatch | cognitive_scores | V00774 | total_reported | 25 | Reported total 25 but item scores add up to 24 |
| DQ-0055 | high | visit_before_enrollment | visits | V00037 | visit_date | 2018-01-25 | Visit date 2018-01-25 is before enrollment date 2018-06-01 |
| DQ-0056 | high | visit_before_enrollment | visits | V00158 | visit_date | 2016-08-25 | Visit date 2016-08-25 is before enrollment date 2016-10-26 |
| DQ-0057 | high | visit_before_enrollment | visits | V00399 | visit_date | 2022-06-23 | Visit date 2022-06-23 is before enrollment date 2022-12-10 |
| DQ-0058 | high | visit_before_enrollment | visits | V00598 | visit_date | 2017-03-26 | Visit date 2017-03-26 is before enrollment date 2017-05-27 |
| DQ-0019 | medium | invalid_category | participants | P0089 | sex | X | 'X' is not one of: F, M |
| DQ-0020 | medium | invalid_category | participants | P0132 | sex | Unknown | 'Unknown' is not one of: F, M |
| DQ-0021 | medium | invalid_category | participants | P0173 | sex | U | 'U' is not one of: F, M |

### Data Services (11)

| issue_id | severity | category | table | record_key | field | value | message |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DQ-0043 | high | duplicate_conflict | cognitive_scores | V00050 | visit_id | V00050 | Key V00050 appears 2 times with different values |
| DQ-0029 | high | duplicate_conflict | participants | P0077 | participant_id | P0077 | Key P0077 appears 2 times with different values |
| DQ-0037 | high | duplicate_conflict | visits | V00530 | visit_id | V00530 | Key V00530 appears 2 times with different values |
| DQ-0054 | high | orphan_record | cognitive_scores | V00024 | participant_id | P9003 | P9003 does not exist in participants.participant_id |
| DQ-0052 | high | orphan_record | cognitive_scores | V90001 | visit_id | V90001 | V90001 does not exist in visits.visit_id |
| DQ-0053 | high | orphan_record | cognitive_scores | V90002 | visit_id | V90002 | V90002 does not exist in visits.visit_id |
| DQ-0050 | high | orphan_record | visits | V00341 | participant_id | P9002 | P9002 does not exist in participants.participant_id |
| DQ-0051 | high | orphan_record | visits | V00420 | participant_id | P9001 | P9001 does not exist in participants.participant_id |
| DQ-0030 | medium | invalid_format | visits | V-0777 | visit_id | V-0777 | 'V-0777' does not match the pattern ^V\d{5}$ |
| DQ-0031 | medium | invalid_format | visits | V123 | visit_id | V123 | 'V123' does not match the pattern ^V\d{5}$ |
| DQ-0032 | medium | invalid_format | visits | VV0789 | visit_id | VV0789 | 'VV0789' does not match the pattern ^V\d{5}$ |

### Data Services (cross-database) (11)

| issue_id | severity | category | table | record_key | field | value | message |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DQ-0059 | high | cross_db_birth_date_mismatch | participants | P0026 | birth_date | 1957-02-28 | Research database has 1957-02-28 but clinical database has 1958-03-05 |
| DQ-0060 | high | cross_db_birth_date_mismatch | participants | P0056 | birth_date | 1951-03-02 | Research database has 1951-03-02 but clinical database has 1952-03-06 |
| DQ-0061 | high | cross_db_birth_date_mismatch | participants | P0095 | birth_date | 1953-12-04 | Research database has 1953-12-04 but clinical database has 1954-12-09 |
| DQ-0062 | high | cross_db_birth_date_mismatch | participants | P0111 | birth_date | 1947-11-24 | Research database has 1947-11-24 but clinical database has 1946-11-19 |
| DQ-0066 | high | cross_db_missing_participant | participants | P0107 | participant_id | P0107 | Participant is in the research database but not in the clinical database |
| DQ-0067 | high | cross_db_missing_participant | participants | P0170 | participant_id | P0170 | Participant is in the research database but not in the clinical database |
| DQ-0063 | high | cross_db_sex_mismatch | participants | P0011 | sex | F | Research database has F but clinical database has M |
| DQ-0064 | high | cross_db_sex_mismatch | participants | P0091 | sex | F | Research database has F but clinical database has M |
| DQ-0065 | high | cross_db_sex_mismatch | participants | P0176 | sex | F | Research database has F but clinical database has M |
| DQ-0068 | medium | cross_db_extra_participant | clinical_participants | P0901 | participant_id | P0901 | Participant is in the clinical database but not in the research database |
| DQ-0069 | medium | cross_db_extra_participant | clinical_participants | P0902 | participant_id | P0902 | Participant is in the clinical database but not in the research database |

## Automatic fixes (audit trail)

| category | count |
| --- | --- |
| date_format_standardized | 6 |
| duplicate_removed | 3 |
| label_standardized | 7 |

Every automatic fix is listed row by row in `issues_log.csv` and the `Auto-fixes` sheet of the Excel report.
