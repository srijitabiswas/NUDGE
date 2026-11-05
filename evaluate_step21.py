
import sys
from pathlib import Path
from openpyxl import load_workbook
from datetime import datetime

from nlp.parser import parse_message, extract_date


DATASET_PATH = (
    Path(__file__).parent
    / "data"
    / "samples"
    / "NUDGE_NLP_Step21_Representative_Dataset.xlsx"
)


def normalize(value):
    """Normalize empty spreadsheet cells for comparison."""
    if value is None:
        return None

    value = str(value).strip()

    if not value or value.lower() in {"none", "null", "n/a"}:
        return None

    return value


def main():
    if not DATASET_PATH.exists():
        print(f"Dataset not found: {DATASET_PATH}")
        sys.exit(1)

    workbook = load_workbook(DATASET_PATH, data_only=True)
    sheet = workbook["Test Dataset"]

    rows = sheet.iter_rows(values_only=True)
    headers = [str(header).strip() for header in next(rows)]

    cases = [
        dict(zip(headers, row))
        for row in rows
        if row[0] is not None
    ]

    fields_to_check = {
        "task_title": "expected_task_title",
        "task_type": "expected_task_type",
        "subject": "expected_subject",
        "due_date": "expected_due_date",
        "due_time": "expected_due_time",
        "event_datetime": "expected_event_datetime",
    }

    total_checks = 0
    passed_checks = 0

    print(f"\nLoaded {len(cases)} test cases.\n")

    for case in cases:
        case_id = case["case_id"]
        raw_message = case["raw_message"]
        source = case["source"]

        result = parse_message(
    str(raw_message),
    str(source),
    reference_date=datetime(2026, 10, 28)
)

        case_passed = True
        failures = []

        for parser_field, expected_field in fields_to_check.items():
            expected = normalize(case.get(expected_field))
            actual = normalize(result.get(parser_field))

            total_checks += 1

            if actual == expected:
                passed_checks += 1
            else:
                case_passed = False
                failures.append(
                    f"  {parser_field}: expected={expected!r}, "
                    f"actual={actual!r}"
                )

        status = "PASS" if case_passed else "FAIL"
        print(f"[{status}] {case_id}")

        for failure in failures:
            print(failure)

    print("\n========== BASELINE SUMMARY ==========")
    print(f"Test cases: {len(cases)}")
    print(f"Field checks passed: {passed_checks}/{total_checks}")
    print(f"Field checks failed: {total_checks - passed_checks}/{total_checks}")

    if total_checks:
        accuracy = passed_checks / total_checks * 100
        print(f"Field-level match rate: {accuracy:.2f}%")

    print("\nThis is the baseline. No parser code was changed.")


if __name__ == "__main__":
    main()
