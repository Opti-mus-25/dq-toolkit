import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from dqkit.generate import generate
from dqkit.pipeline import run_checks
from dqkit.verify import compare, load_manifest

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "rules" / "rules.yaml"
SQL = ROOT / "sql" / "cross_checks.sql"


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_clean_dataset_has_no_issues(self):
        generate(self.tmp / "clean", clean=True)
        result = run_checks(self.tmp / "clean", RULES, SQL)
        self.assertEqual(len(result.issues), 0)

    def test_every_planted_error_is_found_exactly(self):
        manifest_path = self.tmp / "answer_key.csv"
        generate(self.tmp / "dirty", manifest_path)
        result = run_checks(self.tmp / "dirty", RULES, SQL)
        outcome = compare(result.issues, load_manifest(manifest_path))
        self.assertEqual(outcome["planted"], 69)
        self.assertEqual(outcome["missed"], [])
        self.assertEqual(outcome["unexpected"], [])

    def test_changing_the_rules_changes_the_results(self):
        generate(self.tmp / "clean", clean=True)
        rules = yaml.safe_load(RULES.read_text(encoding="utf-8"))
        rules["tables"]["participants"]["fields"]["education_years"]["max"] = 10
        stricter = self.tmp / "stricter.yaml"
        stricter.write_text(yaml.safe_dump(rules), encoding="utf-8")
        result = run_checks(self.tmp / "clean", stricter, SQL)
        self.assertGreater(len(result.issues), 0)
        self.assertEqual(set(result.issues["category"]), {"out_of_range"})
        self.assertEqual(set(result.issues["field"]), {"education_years"})

    def test_missing_data_file_raises_clear_error(self):
        with self.assertRaises(FileNotFoundError):
            run_checks(self.tmp / "nothing_here", RULES, SQL)

    def test_cleaned_output_has_no_duplicate_rows(self):
        generate(self.tmp / "dirty", self.tmp / "key.csv")
        result = run_checks(self.tmp / "dirty", RULES, SQL)
        for table, frame in result.cleaned.items():
            self.assertFalse(frame.duplicated().any(), table)


if __name__ == "__main__":
    unittest.main()
