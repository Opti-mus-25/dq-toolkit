from pathlib import Path

import yaml


def load_rules(path):
    """Read the rules file that defines every table, field, and check."""
    with open(Path(path), "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)
