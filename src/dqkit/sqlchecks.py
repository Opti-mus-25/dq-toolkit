import re
import sqlite3
from pathlib import Path


def parse_sql_file(path):
    """Split the SQL file into named checks, each with a category and target table."""
    text = Path(path).read_text(encoding="utf-8")
    checks = []
    for chunk in re.split(r"(?m)^-- name:\s*", text)[1:]:
        lines = chunk.splitlines()
        meta = {}
        body = []
        for line in lines[1:]:
            match = re.match(r"--\s*(category|table):\s*(.+)", line)
            if match:
                meta[match.group(1)] = match.group(2).strip()
            else:
                body.append(line)
        checks.append(
            {
                "name": lines[0].strip(),
                "category": meta["category"],
                "table": meta["table"],
                "sql": "\n".join(body).strip().rstrip(";"),
            }
        )
    return checks


def run_sql_checks(tables, sql_path, log):
    """Load the cleaned tables into an in-memory database and run each SQL check."""
    connection = sqlite3.connect(":memory:")
    try:
        for name, df in tables.items():
            prepared = df.astype(object).where(df.notna(), None)
            prepared.to_sql(name, connection, index=False)
        for check in parse_sql_file(sql_path):
            cursor = connection.execute(check["sql"])
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                log.add(
                    check["category"],
                    check["table"],
                    record["record_key"],
                    record["field"],
                    record["value"],
                    record["message"],
                )
    finally:
        connection.close()
