import json
import tempfile
import unittest
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evaluations.evaluate_ocr import load_and_validate, build_report, main


class TestOCREvaluation(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.ocr_dir = self.root / "output"
        self.ocr_dir.mkdir()
        self.gt_path = self.root / "ground_truth.json"
        self.report_path = self.root / "report.md"

    def tearDown(self):
        self.temp.cleanup()

    def write_dataset(self, cases):
        self.gt_path.write_text(json.dumps({"cases": cases}), encoding="utf-8")

    def write_output(self, source, raw_text=None, confidence=None, overall=0.8):
        if confidence is None:
            confidence = [
                {"text": "hello", "score": 0.7},
                {"text": "world", "score": 0.9}
            ]
        if raw_text is None:
            raw_text = "\n".join(region["text"] for region in confidence)

        output = {
            "source": source,
            "raw_text": raw_text,
            "confidence": confidence,
            "overall_confidence": overall
        }
        (self.ocr_dir / (Path(source).stem + ".json")).write_text(
            json.dumps(output), encoding="utf-8"
        )

    def case(self, source="image.jpeg", reference="hello world"):
        return {"id": "case1", "source": source, "reference_text": reference}

    def validate(self):
        return load_and_validate(self.gt_path, self.ocr_dir)

    def test_valid_output(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg")
        self.assertEqual(len(self.validate()), 1)

    def test_mismatched_raw_text(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg", raw_text="unrelated text")
        with self.assertRaises(ValueError):
            self.validate()

    def test_mismatched_overall_confidence(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg", overall=0.5)
        with self.assertRaises(ValueError):
            self.validate()

    def test_empty_raw_text_with_nonempty_regions(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg", raw_text="")
        with self.assertRaises(ValueError):
            self.validate()

    def test_nonempty_raw_text_with_empty_regions(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg", raw_text="hello world", confidence=[], overall=None)
        with self.assertRaises(ValueError):
            self.validate()

    def test_empty_regions_require_null_overall_confidence(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg", raw_text="", confidence=[], overall=0.0)
        with self.assertRaises(ValueError):
            self.validate()

    def test_empty_output_scores_one_hundred_percent_error(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg", raw_text="", confidence=[], overall=None)
        report = build_report(self.validate())
        self.assertIn("| image.jpeg | 1.0000 | 1.0000 | N/A | 0 |", report)

    def test_source_with_forward_slash_rejected(self):
        self.write_dataset([self.case(source="folder/image.jpeg")])
        with self.assertRaisesRegex(ValueError, "safe filename"):
            self.validate()

    def test_source_with_backslash_rejected(self):
        self.write_dataset([self.case(source="folder\\image.jpeg")])
        with self.assertRaisesRegex(ValueError, "safe filename"):
            self.validate()

    def test_case_insensitive_duplicate_sources_rejected(self):
        cases = [
            self.case(source="Image.jpeg"),
            {"id": "case2", "source": "image.JPEG", "reference_text": "hello world"}
        ]
        self.write_dataset(cases)
        self.write_output("Image.jpeg")
        with self.assertRaisesRegex(ValueError, "duplicate source filename"):
            self.validate()

    def test_dot_source_rejected(self):
        self.write_dataset([self.case(source=".")])
        with self.assertRaisesRegex(ValueError, "safe filename"):
            self.validate()

    def test_dot_dot_source_rejected(self):
        self.write_dataset([self.case(source="..")])
        with self.assertRaisesRegex(ValueError, "safe filename"):
            self.validate()

    def test_existing_report_unchanged_after_validation_failure(self):
        self.write_dataset([self.case()])
        self.write_output("image.jpeg", raw_text="incorrect")
        original = b"Existing report must remain unchanged.\r\n"
        self.report_path.write_bytes(original)

        arguments = [
            "evaluate_ocr.py",
            "--ocr-dir", str(self.ocr_dir),
            "--ground-truth", str(self.gt_path),
            "--report", str(self.report_path)
        ]
        with patch.object(sys, "argv", arguments):
            result = main()

        self.assertEqual(result, 2)
        self.assertEqual(self.report_path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
