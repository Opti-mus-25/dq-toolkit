import argparse
import sys
from pathlib import Path

from .generate import generate
from .pipeline import run_checks
from .report import (
    write_cleaned,
    write_dictionary,
    write_issues_csv,
    write_markdown,
    write_xlsx,
)
from .verify import compare, load_manifest

ROOT = Path(__file__).resolve().parents[2]


def build_parser():
    parser = argparse.ArgumentParser(prog="dqkit", description="Rules-driven data quality checker")
    commands = parser.add_subparsers(dest="command", required=True)

    gen = commands.add_parser("generate", help="Create the synthetic dataset")
    gen.add_argument("--out", default=str(ROOT / "data" / "raw"))
    gen.add_argument("--answer-key", default=str(ROOT / "data" / "answer_key" / "planted_errors.csv"))
    gen.add_argument("--clean", action="store_true", help="Create a dataset with no planted errors")

    check = commands.add_parser("check", help="Clean, validate, and report")
    check.add_argument("--data", default=str(ROOT / "data" / "raw"))
    check.add_argument("--rules", default=str(ROOT / "rules" / "rules.yaml"))
    check.add_argument("--sql", default=str(ROOT / "sql" / "cross_checks.sql"))
    check.add_argument("--out", default=str(ROOT / "output"))
    check.add_argument("--answer-key", default=None, help="Compare results with a planted-error answer key")
    check.add_argument("--fail-on-issues", action="store_true", help="Exit with code 1 if any issue needs review")

    dictionary = commands.add_parser("dictionary", help="Export a REDCap-style data dictionary")
    dictionary.add_argument("--rules", default=str(ROOT / "rules" / "rules.yaml"))
    dictionary.add_argument("--out", default=str(ROOT / "output" / "data_dictionary.csv"))
    return parser


def command_generate(args):
    manifest = generate(args.out, None if args.clean else args.answer_key, clean=args.clean)
    print(f"Wrote synthetic data to {args.out} with {len(manifest)} planted errors")
    return 0


def command_check(args):
    result = run_checks(args.data, args.rules, args.sql)
    out = Path(args.out)
    write_cleaned(result.cleaned, result.rules, out / "cleaned")
    write_issues_csv(result.issues, out / "issues_log.csv")
    write_xlsx(result.issues, out / "discrepancy_report.xlsx")
    write_markdown(result.issues, result.raw_counts, result.cleaned, out / "discrepancy_report.md")
    review = int((result.issues["action"] == "needs_review").sum())
    fixed = int((result.issues["action"] == "auto_fixed").sum())
    print(f"{review} issues need review, {fixed} fixes applied automatically. Reports in {out}")
    if args.answer_key:
        outcome = compare(result.issues, load_manifest(args.answer_key))
        print(f"Answer key: {outcome['planted']} planted, {outcome['found']} reported")
        for item in outcome["missed"]:
            print(f"  MISSED: {item}")
        for item in outcome["unexpected"]:
            print(f"  UNEXPECTED: {item}")
        if not outcome["exact_match"]:
            return 1
        print("Exact match with the answer key")
    if args.fail_on_issues and review:
        return 1
    return 0


def command_dictionary(args):
    from .rules import load_rules

    write_dictionary(load_rules(args.rules), args.out)
    print(f"Wrote data dictionary to {args.out}")
    return 0


def main(argv=None):
    args = build_parser().parse_args(argv)
    handlers = {"generate": command_generate, "check": command_check, "dictionary": command_dictionary}
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
