import pandas as pd

COLUMNS = [
    "action",
    "severity",
    "category",
    "table",
    "record_key",
    "field",
    "value",
    "message",
    "route_to",
]


class IssueLog:
    """Collects every problem found, with severity and who should resolve it."""

    def __init__(self, categories):
        self.categories = categories
        self.rows = []

    def add(self, category, table, record_key, field, value, message, action="needs_review"):
        info = self.categories.get(category, {})
        self.rows.append(
            {
                "action": action,
                "severity": info.get("severity", "medium"),
                "category": category,
                "table": table,
                "record_key": "" if record_key is None or pd.isna(record_key) else str(record_key),
                "field": field,
                "value": "" if value is None or pd.isna(value) else str(value),
                "message": message,
                "route_to": info.get("route_to", "Data Services"),
            }
        )

    def frame(self):
        frame = pd.DataFrame(self.rows, columns=COLUMNS)
        frame.insert(0, "issue_id", [f"DQ-{number:04d}" for number in range(1, len(frame) + 1)])
        return frame
