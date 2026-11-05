"""Tests for backend/database/build_database.py (Steps 46-47).

The snapshot files here are small hand-made examples in the same shape that
data/samples/real/make_snapshots.py writes. They test the builder, not the
parser. Values are copied from the Step 21 dataset where possible.
"""

import contextlib
import io
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.database.build_database import main  # noqa: E402


def blank_task(**changes):
    task = {
        "task_id": None, "task_title": None, "description": None, "task_type": None,
        "subject": None, "due_date": None, "due_time": None, "due_datetime": None,
        "event_datetime": None, "status": "pending", "importance": None,
        "estimated_effort": None, "source": "LMS", "raw_text": "x",
        "date_time_expression": None, "confidence": 0.9, "change_information": [],
        "created_at": None, "completed_at": None,
    }
    task.update(changes)
    return task


def message_records():
    return [
        {"case_id": "NLP-01", "expected_category": "task", "category": "task",
         "task": blank_task(task_title="Submit Machine Learning Assignment 2",
                            task_type="assignment", due_date="2026-11-05", due_time="17:00",
                            raw_text="Please submit Machine Learning Assignment 2 by 5 November 2026 at 5:00 PM.")},
        {"case_id": "NLP-16", "expected_category": "task", "category": "task",
         "task": blank_task(task_title="Submit internship report", task_type=None,
                            due_date="2026-11-20", raw_text="Submit internship report by 20 November.")},
        {"case_id": "NLP-19", "expected_category": "general_notice", "category": "general_notice",
         "task": blank_task(source="University Notice",
                            raw_text="Notice: the library will remain closed on 2 November 2026.")},
    ]


def ocr_records():
    return [{
        "image": "screenshot 9.jpeg", "category": "event",
        "task": blank_task(task_title="IEEE invited talk", task_type="event",
                           event_datetime="2026-10-09T20:00:00", source="Screenshot/OCR",
                           raw_text="IEEE invited talk 9th October 8:00 PM", confidence=0.8),
        "ocr": {"image_filename": "screenshot 9.jpeg", "overall_confidence": 0.6024,
                "line_confidences": [{"text": "REGISTER NOW", "score": 0.91}]},
    }]


class BuildDatabaseTests(unittest.TestCase):

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.root = Path(self.folder.name)
        self.parser_file = self.root / "parser_snapshot.json"
        self.ocr_file = self.root / "ocr_snapshot.json"
        self.db = str(self.root / "built.db")
        self.export = self.root / "export" / "tasks.json"
        self.parser_file.write_text(json.dumps(
            {"_meta": {"parser_commit": "abc123"}, "records": message_records()}), encoding="utf-8")
        self.ocr_file.write_text(json.dumps(
            {"_meta": {"parser_commit": "abc123"}, "records": ocr_records()}), encoding="utf-8")

    def tearDown(self):
        self.folder.cleanup()

    def run_main(self, *extra):
        args = ["--db-path", self.db, "--parser-snapshot", str(self.parser_file),
                "--ocr-snapshot", str(self.ocr_file), *extra]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(args)
        return code, out.getvalue(), err.getvalue()

    def rows(self, sql):
        con = sqlite3.connect(self.db)
        try:
            return con.execute(sql).fetchall()
        finally:
            con.close()

    def test_builds_database_from_both_snapshots(self):
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        titles = [r[0] for r in self.rows("SELECT task_title FROM tasks ORDER BY task_id")]
        self.assertEqual(titles, ["Submit Machine Learning Assignment 2",
                                  "Submit internship report", "IEEE invited talk"])
        self.assertIn("Inserted: 3   Skipped: 1", out)

    def test_null_task_type_task_is_stored(self):
        self.run_main()
        row = self.rows("SELECT task_type FROM tasks WHERE task_title = 'Submit internship report'")
        self.assertEqual(row, [(None,)])

    def test_general_notice_is_skipped_with_reason(self):
        _, out, _ = self.run_main()
        self.assertIn("skipped because general_notice: 1", out)

    def test_ocr_confidence_goes_to_separate_table(self):
        self.run_main()
        meta = self.rows("SELECT image_filename, overall_confidence FROM ocr_metadata")
        self.assertEqual(meta, [("screenshot 9.jpeg", 0.6024)])
        conf = self.rows("SELECT confidence FROM tasks WHERE task_title = 'IEEE invited talk'")
        self.assertEqual(conf, [(0.8,)])

    def test_export_contains_tasks_and_ocr_details(self):
        code, _, _ = self.run_main("--export", str(self.export))
        self.assertEqual(code, 0)
        payload = json.loads(self.export.read_text(encoding="utf-8"))
        self.assertEqual(payload["_meta"]["task_count"], 3)
        self.assertEqual(payload["_meta"]["parser_snapshot"]["parser_commit"], "abc123")
        by_title = {t["task_title"]: t for t in payload["tasks"]}
        self.assertIsNone(by_title["Submit internship report"]["ocr"])
        self.assertEqual(by_title["IEEE invited talk"]["ocr"]["overall_confidence"], 0.6024)
        self.assertIn("task_id", by_title["IEEE invited talk"])

    def test_refuses_database_that_already_has_tasks(self):
        self.assertEqual(self.run_main()[0], 0)
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("already contains 3 tasks", err)
        self.assertEqual(self.rows("SELECT COUNT(*) FROM tasks"), [(3,)])

    def test_bad_snapshot_returns_error_and_creates_no_database(self):
        self.parser_file.write_text("not json", encoding="utf-8")
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("Cannot read parser snapshot", err)
        self.assertFalse(Path(self.db).exists())

    def test_snapshot_without_records_list_is_rejected(self):
        self.parser_file.write_text(json.dumps({"records": "nope"}), encoding="utf-8")
        self.assertEqual(self.run_main()[0], 2)

    def test_missing_explicit_ocr_snapshot_is_an_error(self):
        self.ocr_file.unlink()
        code, _, err = self.run_main()
        self.assertEqual(code, 2)
        self.assertIn("Cannot read OCR snapshot", err)

    def test_malformed_record_is_reported_not_crashed(self):
        self.parser_file.write_text(json.dumps(
            {"records": ["oops", {"case_id": "X", "task": None}]}), encoding="utf-8")
        code, out, _ = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("skipped because invalid_input: 2", out)


if __name__ == "__main__":
    unittest.main()
