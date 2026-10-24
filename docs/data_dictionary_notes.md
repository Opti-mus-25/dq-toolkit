# Data dictionary notes

`python -m dqkit dictionary` writes `output/data_dictionary.csv` from `rules/rules.yaml`, so the dictionary and the checks cannot drift apart.

The file uses the standard REDCap data dictionary column headers (Variable / Field Name, Form Name, Field Type, Field Label, Choices, Text Validation Type, Min, Max, Identifier?, Required Field?, and so on). It has not been uploaded to a live REDCap project, so treat it as a draft layout.

Mapping from rules to dictionary:

| Rules file | Dictionary |
| --- | --- |
| type: int | text field, validation `integer`, with min and max |
| type: date | text field, validation `date_ymd`, with min and max, Identifier? = y |
| type: category | radio field, choices from `choices` or `allowed` |
| type: string with pattern | text field, pattern recorded in Field Annotation |
| required: true | Required Field? = y |
| form | Form Name (lowercase, underscores) |

Notes:

- REDCap needs unique variable names across a project, so repeated IDs (for example participant_id in several tables) appear once, under the first form that uses them.
- The clinical database table is excluded because it represents a separate system.
- Date fields are marked as identifiers because dates are a common identifier category in privacy rules.
