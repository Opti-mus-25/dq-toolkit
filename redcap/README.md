# REDCap demo test

This folder records a hands-on test of the toolkit's data dictionary in REDCap. It used the free three-day REDCap demo server and fake data only. No real participants are involved.

## What was done

1. Ran `python -m dqkit dictionary` to export `output/data_dictionary.csv` from `rules/rules.yaml`.
2. Created an empty practice project in the REDCap demo (Practice / Just for fun).
3. Uploaded the file on the project's Data Dictionary page. REDCap reported no errors or warnings and found 14 fields, which matches the toolkit: 5 in Participant Enrollment, 3 in Study Visit and 6 in Cognitive Screen.
4. Committed the dictionary. The Online Designer then showed the three forms.
5. Entered a value of 40 in Years of education. REDCap showed an alert that the value is outside the suggested range (0 to 25), which matches the toolkit's `out_of_range` rule. REDCap calls the value "admissible", so it treats the range as a soft warning.
6. Entered a few fake practice records and completed the three forms for the first one.
7. Exported all data as CSV.

## Files

| File | What it shows |
| --- | --- |
| `redcap_demo_export.csv` | The data exported from REDCap (fake data) |
| `02_range_warning.png` | The warning for an education value of 40 |

## What this does and does not show

- It shows the dictionary imports cleanly and that REDCap applies the ranges the rules describe. The range check is a soft warning, so a value like 40 can still be saved, while the toolkit reports it as an issue for review.
- REDCap does not enforce the ID pattern (`P` followed by four digits). The dictionary stores it only as a field annotation, so the toolkit catches badly formatted IDs that REDCap would accept.
- It was a three-day demo on a shared server, not a real study, and it did not involve user permissions, surveys, longitudinal events or HIPAA data.
