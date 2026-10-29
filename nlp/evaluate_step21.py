"""Score nlp/parser.py against the Step 21 representative dataset.

Run from the repository root:

    python -m nlp.evaluate_step21                     # uses nlp/test_data/step21_dataset.json
    python -m nlp.evaluate_step21 --xlsx FILE.xlsx    # reads the original Excel file
                                                      # (needs: pip install openpyxl)

Each case is checked on 6 parser fields (title, type, subject, due date,
due time, event datetime), so 25 cases give 150 field checks. The message
category (task / event / general_notice) is checked as a 7th, separate value.
Blank expected values mean null: the parser must not guess them.

The exit code is 0 when every check passes and 1 otherwise.
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from nlp.parser import classify_message_category, parse_message

DEFAULT_DATASET = Path(__file__).with_name("test_data") / "step21_dataset.json"
REFERENCE_DATE = datetime(2026, 10, 28)  # fixed by the dataset's Read Me sheet
FIELDS = ["task_title", "task_type", "subject", "due_date", "due_time", "event_datetime"]


def _normalise(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def load_json(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)["cases"]


def load_xlsx(path):
    import openpyxl  # imported here so the JSON route needs no extra package

    sheet = openpyxl.load_workbook(path, data_only=True)["Test Dataset"]
    header = [cell.value for cell in sheet[1]]
    cases = []
    for row in sheet.iter_rows(min_row=2, values_only=True):
        record = dict(zip(header, row))
        cases.append({
            "case_id": record["case_id"],
            "source": record["source"],
            "raw_message": record["raw_message"],
            "expected": {
                field: _normalise(record[f"expected_{field}"]) for field in FIELDS
            },
            "expected_category": record["expected_category"],
        })
    return cases


def evaluate(cases):
    """Return (summary, failures). Each failure is (case_id, field, expected, actual)."""
    field_checks = field_passed = full_cases = category_passed = 0
    failures = []

    for case in cases:
        result = parse_message(case["raw_message"], case["source"], REFERENCE_DATE)
        case_ok = True

        for field in FIELDS:
            field_checks += 1
            expected = _normalise(case["expected"][field])
            actual = _normalise(result[field])
            if actual == expected:
                field_passed += 1
            else:
                case_ok = False
                failures.append((case["case_id"], field, expected, actual))

        category = classify_message_category(case["raw_message"], REFERENCE_DATE)
        if category == case["expected_category"]:
            category_passed += 1
        else:
            case_ok = False
            failures.append((case["case_id"], "category", case["expected_category"], category))

        full_cases += case_ok

    summary = {
        "cases": len(cases),
        "cases_fully_passing": full_cases,
        "field_checks": field_checks,
        "field_checks_passing": field_passed,
        "category_checks_passing": category_passed,
    }
    return summary, failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--xlsx", help="read the original Excel dataset instead of the JSON file")
    args = parser.parse_args(argv)

    cases = load_xlsx(args.xlsx) if args.xlsx else load_json(DEFAULT_DATASET)
    summary, failures = evaluate(cases)

    print(f"Cases fully passing:    {summary['cases_fully_passing']}/{summary['cases']}")
    print(f"Field checks passing:   {summary['field_checks_passing']}/{summary['field_checks']}")
    print(f"Category checks passing: {summary['category_checks_passing']}/{summary['cases']}")
    for case_id, field, expected, actual in failures:
        print(f"FAIL {case_id} {field}: expected {expected!r}, got {actual!r}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
