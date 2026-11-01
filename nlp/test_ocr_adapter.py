"""Tests for nlp/ocr_adapter.py, roadmap Step 36 (OCR -> NLP connection).

Run from the repository root:

    python -m unittest nlp.test_ocr_adapter -v

The nine JSON files in nlp/test_data/ocr_samples/ are exact copies of the
OCR module's real output (feature/neha-ocr, commit d4760d4). Every test uses
a fixed reference date, so results never depend on the day the tests run.
"""

import copy
import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from nlp.ocr_adapter import OCR_SOURCE, OCRRecordError, parse_ocr_file, parse_ocr_record
from nlp.parser import parse_message

SAMPLE_DIR = Path(__file__).with_name("test_data") / "ocr_samples"
SAMPLE_FILES = sorted(SAMPLE_DIR.glob("*.json"))
REF = datetime(2026, 10, 28)


def load(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def make_record(**changes):
    """A small valid OCR record; keyword arguments override fields."""
    record = {
        "source": "notice.png",
        "raw_text": "Submit the DBMS assignment by 5 November 2026",
        "cleaned_text": "Submit the DBMS assignment by 5 November 2026",
        "overall_confidence": 0.9,
        "confidence": [{"text": "Submit the DBMS assignment by 5 November 2026", "score": 0.9}],
    }
    record.update(changes)
    return record


class RealSampleTests(unittest.TestCase):
    def test_all_nine_committed_samples_are_present(self):
        self.assertEqual(len(SAMPLE_FILES), 9)

    def test_every_sample_is_parsed(self):
        for path in SAMPLE_FILES:
            with self.subTest(sample=path.name):
                record = load(path)
                result = parse_ocr_file(path, REF)
                self.assertEqual(set(result), {"task", "ocr"})
                # The adapter gives the parser exactly cleaned_text, nothing more.
                self.assertEqual(
                    result["task"],
                    parse_message(record["cleaned_text"], "Screenshot/OCR", REF),
                )
                self.assertEqual(result["task"]["raw_text"], record["cleaned_text"])

    def test_ocr_details_are_kept_separately(self):
        for path in SAMPLE_FILES:
            with self.subTest(sample=path.name):
                record = load(path)
                ocr = parse_ocr_file(path, REF)["ocr"]
                self.assertEqual(set(ocr), {"image_filename", "overall_confidence", "line_confidences"})
                self.assertEqual(ocr["image_filename"], record["source"])
                self.assertEqual(ocr["overall_confidence"], record["overall_confidence"])
                self.assertEqual(ocr["line_confidences"], record["confidence"])

    def test_known_sample_results(self):
        # screenshot 9: "REGISTER NOW" poster with a date; checked against the parser output.
        result = parse_ocr_file(SAMPLE_DIR / "screenshot 9.json", REF)
        self.assertEqual(result["ocr"]["image_filename"], "screenshot 9.jpeg")
        self.assertEqual(result["ocr"]["overall_confidence"], 0.6024)
        self.assertEqual(len(result["ocr"]["line_confidences"]), 34)
        self.assertEqual(result["task"]["task_title"], "REGISTER NOW")
        self.assertEqual(result["task"]["due_date"], "2026-10-09")


class SourceTests(unittest.TestCase):
    def test_source_is_screenshot_ocr_not_the_filename(self):
        for path in SAMPLE_FILES:
            with self.subTest(sample=path.name):
                result = parse_ocr_file(path, REF)
                self.assertEqual(OCR_SOURCE, "Screenshot/OCR")
                self.assertEqual(result["task"]["source"], "Screenshot/OCR")
                self.assertNotEqual(result["task"]["source"], result["ocr"]["image_filename"])

    def test_filename_is_not_leaked_into_the_task(self):
        result = parse_ocr_record(make_record(source="secret name.png"), REF)
        self.assertNotIn("secret name.png", json.dumps(result["task"]))
        self.assertEqual(result["ocr"]["image_filename"], "secret name.png")


class ReferenceDateTests(unittest.TestCase):
    def test_reference_date_changes_relative_dates(self):
        record = make_record(cleaned_text="Submit the DBMS assignment tomorrow")
        first = parse_ocr_record(record, datetime(2026, 10, 28))["task"]["due_date"]
        second = parse_ocr_record(record, datetime(2026, 11, 5))["task"]["due_date"]
        self.assertEqual(first, "2026-10-29")
        self.assertEqual(second, "2026-11-06")

    def test_date_and_datetime_references_agree(self):
        record = make_record(cleaned_text="Submit the DBMS assignment tomorrow")
        with_date = parse_ocr_record(record, date(2026, 10, 28))
        with_datetime = parse_ocr_record(record, datetime(2026, 10, 28))
        self.assertEqual(with_date, with_datetime)

    def test_reference_date_is_passed_through_unchanged(self):
        record = make_record(cleaned_text="Submit the DBMS assignment tomorrow")
        result = parse_ocr_record(record, datetime(2026, 10, 28))
        self.assertEqual(
            result["task"],
            parse_message(record["cleaned_text"], "Screenshot/OCR", datetime(2026, 10, 28)),
        )

    def test_reference_date_is_optional(self):
        result = parse_ocr_record(make_record())
        self.assertEqual(result["task"]["due_date"], "2026-11-05")


class EmptyTextTests(unittest.TestCase):
    def test_empty_text_with_no_ocr_lines(self):
        record = make_record(raw_text="", cleaned_text="", overall_confidence=None, confidence=[])
        result = parse_ocr_record(record, REF)
        task = result["task"]
        self.assertEqual(task["source"], "Screenshot/OCR")
        self.assertEqual(task["raw_text"], "")
        for field in ("task_title", "task_type", "subject", "due_date", "due_time", "event_datetime"):
            self.assertIsNone(task[field], field)
        self.assertEqual(task["confidence"], 0.0)
        self.assertEqual(result["ocr"]["image_filename"], "notice.png")
        self.assertIsNone(result["ocr"]["overall_confidence"])
        self.assertEqual(result["ocr"]["line_confidences"], [])

    def test_whitespace_only_text(self):
        result = parse_ocr_record(make_record(cleaned_text="  \n \t "), REF)
        self.assertIsNone(result["task"]["task_title"])
        self.assertEqual(result["task"]["confidence"], 0.0)


class MissingFieldTests(unittest.TestCase):
    def test_each_required_field_is_reported_by_name(self):
        for field in ("source", "cleaned_text", "overall_confidence", "confidence"):
            with self.subTest(field=field):
                record = make_record()
                del record[field]
                with self.assertRaises(OCRRecordError) as caught:
                    parse_ocr_record(record, REF)
                self.assertIn(f"missing required field '{field}'", str(caught.exception))

    def test_missing_overall_confidence_is_an_error_but_null_is_allowed(self):
        record = make_record()
        del record["overall_confidence"]
        with self.assertRaises(OCRRecordError):
            parse_ocr_record(record, REF)
        result = parse_ocr_record(make_record(overall_confidence=None), REF)
        self.assertIsNone(result["ocr"]["overall_confidence"])

    def test_record_must_be_a_dictionary(self):
        for bad in (None, "text", ["a"], 5):
            with self.subTest(value=bad):
                with self.assertRaises(OCRRecordError):
                    parse_ocr_record(bad, REF)

    def test_invalid_field_types(self):
        cases = [
            ("source", "", "source"),
            ("source", "   ", "source"),
            ("source", 7, "source"),
            ("cleaned_text", None, "cleaned_text"),
            ("cleaned_text", 12, "cleaned_text"),
            ("confidence", "none", "confidence"),
            ("confidence", None, "confidence"),
        ]
        for field, value, name in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaises(OCRRecordError) as caught:
                    parse_ocr_record(make_record(**{field: value}), REF)
                self.assertIn(f"'{name}'", str(caught.exception))


class InvalidConfidenceTests(unittest.TestCase):
    def test_invalid_overall_confidence(self):
        for bad in (-0.1, 1.1, 2, "0.9", True, False, [0.9], float("nan"), float("inf")):
            with self.subTest(value=bad):
                with self.assertRaises(OCRRecordError) as caught:
                    parse_ocr_record(make_record(overall_confidence=bad), REF)
                self.assertIn("overall_confidence", str(caught.exception))

    def test_boundary_values_are_valid(self):
        for good in (0, 0.0, 1, 1.0, 0.5):
            with self.subTest(value=good):
                result = parse_ocr_record(make_record(overall_confidence=good), REF)
                self.assertEqual(result["ocr"]["overall_confidence"], good)

    def test_invalid_line_scores(self):
        for bad in (-1, 1.5, "0.9", None, True, float("nan")):
            with self.subTest(score=bad):
                lines = [{"text": "ok", "score": 0.9}, {"text": "bad", "score": bad}]
                with self.assertRaises(OCRRecordError) as caught:
                    parse_ocr_record(make_record(confidence=lines), REF)
                self.assertIn("'confidence'[1]", str(caught.exception))

    def test_invalid_line_shapes(self):
        for lines in (["text"], [{"text": "a"}], [{"score": 0.5}], [{"text": 5, "score": 0.5}]):
            with self.subTest(lines=lines):
                with self.assertRaises(OCRRecordError):
                    parse_ocr_record(make_record(confidence=lines), REF)


class ConfidenceSeparationTests(unittest.TestCase):
    def test_nlp_confidence_is_not_the_ocr_confidence(self):
        record = load(SAMPLE_DIR / "screenshot 9.json")
        result = parse_ocr_file(SAMPLE_DIR / "screenshot 9.json", REF)
        self.assertEqual(record["overall_confidence"], 0.6024)
        self.assertEqual(result["task"]["confidence"], 0.5)  # NLP: title + type found
        self.assertEqual(result["ocr"]["overall_confidence"], 0.6024)
        self.assertNotEqual(result["task"]["confidence"], result["ocr"]["overall_confidence"])

    def test_ocr_confidence_never_changes_the_nlp_result(self):
        low = parse_ocr_record(make_record(overall_confidence=0.05), REF)
        high = parse_ocr_record(make_record(overall_confidence=0.99), REF)
        none = parse_ocr_record(make_record(overall_confidence=None), REF)
        self.assertEqual(low["task"], high["task"])
        self.assertEqual(low["task"], none["task"])

    def test_task_keeps_the_shared_contract_keys_only(self):
        expected_keys = set(parse_message("anything", "Screenshot/OCR", REF))
        for path in SAMPLE_FILES:
            with self.subTest(sample=path.name):
                task = parse_ocr_file(path, REF)["task"]
                self.assertEqual(set(task), expected_keys)
                self.assertNotIn("overall_confidence", task)
                self.assertNotIn("line_confidences", task)
                self.assertIsInstance(task["confidence"], float)

    def test_input_record_is_not_modified_and_output_is_a_copy(self):
        record = make_record()
        before = copy.deepcopy(record)
        result = parse_ocr_record(record, REF)
        self.assertEqual(record, before)
        result["ocr"]["line_confidences"][0]["score"] = 0.0
        self.assertEqual(record, before)


class FileLoadingTests(unittest.TestCase):
    def test_invalid_json_file(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "broken.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(OCRRecordError) as caught:
                parse_ocr_file(path, REF)
            self.assertIn("broken.json", str(caught.exception))

    def test_missing_file_is_a_normal_file_error(self):
        with self.assertRaises(FileNotFoundError):
            parse_ocr_file(SAMPLE_DIR / "does not exist.json", REF)

    def test_path_can_be_a_string(self):
        result = parse_ocr_file(str(SAMPLE_DIR / "screenshot 9.json"), REF)
        self.assertEqual(result["ocr"]["image_filename"], "screenshot 9.jpeg")


if __name__ == "__main__":
    unittest.main()
