"""Tests for backend/database/ingest.py (roadmap Step 47).

Fixtures are shaped like the NLP contract and like Prakriti's OCR adapter
result. Values come from her Step 21 dataset (expected values and raw
messages) and from the OCR report numbers. They are NOT captured parser
output. Assumptions are marked "ASSUMPTION".
"""

import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.database import ingest  # noqa: E402
from backend.database.ingest import (  # noqa: E402
    get_ocr_metadata,
    ingest_ocr_result,
    ingest_task,
)
from backend.database.repository import get_task_by_id  # noqa: E402

SCHEMA = ROOT / "backend" / "database" / "schema.sql"


def make_connection():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    return con


def task_with_date_and_time():
    # From Step 21 dataset case NLP-01 (expected values + raw message).
    return {
        "task_id": None,
        "task_title": "Submit Machine Learning Assignment 2",
        "description": None,
        "task_type": "assignment",
        "subject": "Machine Learning",
        "due_date": "2026-11-05",
        "due_time": "17:00",
        "due_datetime": None,
        "event_datetime": None,
        "status": "pending",
        "importance": None,
        "estimated_effort": None,
        "source": "LMS",
        "raw_text": "Please submit Machine Learning Assignment 2 on Moodle "
                    "by 5 November 2026 at 5:00 PM.",
        "date_time_expression": "5 November 2026 at 5:00 PM",
        "confidence": 0.9,  # ASSUMPTION: confidence value is not from the dataset
        "change_information": [],
        "created_at": None,
        "completed_at": None,
    }


def task_with_date_only():
    # From Step 21 dataset case NLP-02. ASSUMPTION: due_date 2026-11-07 is
    # what "7 November" resolves to with reference date 2026-10-28.
    task = task_with_date_and_time()
    task.update({
        "task_title": "Submit Data Structures assignment",
        "subject": "Data Structures",
        "due_date": "2026-11-07",
        "due_time": None,
        "source": "WhatsApp",
        "raw_text": "Reminder: Data Structures assignment is due on 7 November.",
        "date_time_expression": "7 November",
    })
    return task


def general_notice():
    # From the Step 21 dataset: library closure notice, all fields null.
    return {
        "task_id": None,
        "task_title": None,
        "description": None,
        "task_type": None,
        "subject": None,
        "due_date": None,
        "due_time": None,
        "due_datetime": None,
        "event_datetime": None,
        "status": "pending",
        "importance": None,
        "estimated_effort": None,
        "source": "University Notice",
        "raw_text": "Notice: the library will remain closed on 2 November "
                    "2026 for maintenance.",
        "date_time_expression": None,
        "confidence": 0.0,
        "change_information": [],
        "created_at": None,
        "completed_at": None,
    }


def event_task():
    # ASSUMPTION: no event case was visible to me. Shape follows the contract.
    task = task_with_date_and_time()
    task.update({
        "task_title": "Capstone viva voce",
        "task_type": "event",
        "subject": None,
        "due_date": None,
        "due_time": None,
        "event_datetime": "2026-11-20T09:00:00",
        "source": "University Notice",
        "raw_text": "Viva voce will be held on 20 November 2026 at 9:00 AM.",
        "date_time_expression": "20 November 2026 at 9:00 AM",
    })
    return task


def ocr_result(overall=0.6024):
    # Shape from nlp/ocr_adapter.py. Values trimmed from the screenshot 9
    # report row (overall 0.6024). ASSUMPTION: the three lines are invented.
    task = task_with_date_and_time()
    task.update({"source": "Screenshot/OCR", "confidence": 0.8})
    return {
        "task": task,
        "ocr": {
            "image_filename": "screenshot 9.jpeg",
            "overall_confidence": overall,
            "line_confidences": [
                {"text": "REGISTER NOW", "score": 0.91},
                {"text": "9th October", "score": 0.55},
                {"text": "8:00 PM", "score": 0.35},
            ],
        },
    }


class IngestTaskTests(unittest.TestCase):

    def setUp(self):
        self.con = make_connection()

    def tearDown(self):
        self.con.close()

    def count(self, table="tasks"):
        return self.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_task_with_date_and_time_is_inserted_and_due_datetime_derived(self):
        result = ingest_task(task_with_date_and_time(), connection=self.con)
        self.assertEqual(result["status"], "inserted")
        stored = get_task_by_id(result["task_id"], connection=self.con)
        self.assertEqual(stored["due_datetime"], "2026-11-05T17:00:00")
        self.assertEqual(stored["task_title"], "Submit Machine Learning Assignment 2")

    def test_date_only_task_keeps_due_datetime_null(self):
        result = ingest_task(task_with_date_only(), connection=self.con)
        stored = get_task_by_id(result["task_id"], connection=self.con)
        self.assertEqual(stored["due_date"], "2026-11-07")
        self.assertIsNone(stored["due_datetime"])

    def test_works_without_category(self):
        result = ingest_task(task_with_date_and_time(), connection=self.con)
        self.assertEqual(result["status"], "inserted")

    def test_works_with_task_category(self):
        result = ingest_task(task_with_date_and_time(), category="task", connection=self.con)
        self.assertEqual(result["status"], "inserted")

    def test_notice_without_category_is_skipped_with_reason(self):
        result = ingest_task(general_notice(), connection=self.con)
        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["reason_code"], "missing_task_title")
        self.assertTrue(result["reason"])
        self.assertIsNone(result["task_id"])
        self.assertEqual(self.count(), 0)

    def test_general_notice_category_skips_even_if_title_present(self):
        result = ingest_task(
            task_with_date_and_time(), category="general_notice", connection=self.con
        )
        self.assertEqual(result["reason_code"], "general_notice")
        self.assertEqual(self.count(), 0)

    def test_unknown_category_is_skipped(self):
        result = ingest_task(task_with_date_and_time(), category="homework", connection=self.con)
        self.assertEqual(result["reason_code"], "invalid_category")
        self.assertEqual(self.count(), 0)

    def test_missing_required_fields_are_skipped_with_specific_codes(self):
        cases = {
            "task_title": "missing_task_title",
            "source": "missing_source",
            "raw_text": "missing_raw_text",
        }
        for field, code in cases.items():
            with self.subTest(field=field):
                task = task_with_date_and_time()
                task[field] = None
                self.assertEqual(ingest_task(task, connection=self.con)["reason_code"], code)
        self.assertEqual(self.count(), 0)

    def test_whitespace_only_title_is_skipped(self):
        task = task_with_date_and_time()
        task["task_title"] = "   "
        self.assertEqual(ingest_task(task, connection=self.con)["status"], "skipped")

    def test_non_dict_input_is_skipped_not_crashed(self):
        for bad in (None, "text", 5, ["a"]):
            with self.subTest(bad=bad):
                self.assertEqual(
                    ingest_task(bad, connection=self.con)["reason_code"], "invalid_input"
                )

    def test_invalid_confidence_is_skipped(self):
        for bad in (1.5, -0.1, True, float("nan"), "0.9"):
            with self.subTest(bad=bad):
                task = task_with_date_and_time()
                task["confidence"] = bad
                self.assertEqual(
                    ingest_task(task, connection=self.con)["reason_code"], "invalid_confidence"
                )
        self.assertEqual(self.count(), 0)

    def test_null_confidence_is_stored_as_zero(self):
        task = task_with_date_and_time()
        task["confidence"] = None
        result = ingest_task(task, connection=self.con)
        self.assertEqual(get_task_by_id(result["task_id"], connection=self.con)["confidence"], 0.0)

    def test_invalid_status_and_effort_are_skipped(self):
        task = task_with_date_and_time()
        task["status"] = "done"
        self.assertEqual(ingest_task(task, connection=self.con)["reason_code"], "invalid_status")
        task = task_with_date_and_time()
        task["estimated_effort"] = -2
        self.assertEqual(
            ingest_task(task, connection=self.con)["reason_code"], "invalid_estimated_effort"
        )

    def test_event_is_stored_with_event_datetime_and_no_due_datetime(self):
        result = ingest_task(event_task(), category="event", connection=self.con)
        self.assertEqual(result["status"], "inserted")
        self.assertEqual(result["warnings"], [])
        stored = get_task_by_id(result["task_id"], connection=self.con)
        self.assertEqual(stored["event_datetime"], "2026-11-20T09:00:00")
        self.assertIsNone(stored["due_datetime"])

    def test_event_without_event_datetime_is_stored_with_warning(self):
        task = event_task()
        task["event_datetime"] = None
        result = ingest_task(task, category="event", connection=self.con)
        self.assertEqual(result["status"], "inserted")
        self.assertEqual(len(result["warnings"]), 1)

    def test_storage_owned_fields_are_ignored(self):
        task = task_with_date_and_time()
        task["task_id"] = 999
        task["created_at"] = "1999-01-01T00:00:00"
        result = ingest_task(task, connection=self.con)
        self.assertNotEqual(result["task_id"], 999)
        stored = get_task_by_id(result["task_id"], connection=self.con)
        self.assertNotEqual(stored["created_at"], "1999-01-01T00:00:00")

    def test_null_task_type_is_stored_as_null(self):
        # Shape of Step 21 case NLP-03 from the parser run: title, date and
        # time present, task_type null. ASSUMPTION: source and raw_text are
        # invented; only the title, date and time were seen.
        task = task_with_date_and_time()
        task.update({
            "task_title": "Submit DBMS lab record",
            "task_type": None,
            "subject": None,
            "due_date": "2026-10-28",
            "due_time": "18:00",
            "raw_text": "Submit the DBMS lab record by 6 PM today.",
        })
        result = ingest_task(task, connection=self.con)
        self.assertEqual(result["status"], "inserted")
        stored = get_task_by_id(result["task_id"], connection=self.con)
        self.assertIsNone(stored["task_type"])
        self.assertEqual(stored["due_datetime"], "2026-10-28T18:00:00")

    def test_blank_task_type_is_stored_as_null(self):
        for blank in ("", "   "):
            with self.subTest(blank=blank):
                task = task_with_date_and_time()
                task["task_type"] = blank
                result = ingest_task(task, connection=self.con)
                self.assertEqual(result["status"], "inserted")
                stored = get_task_by_id(result["task_id"], connection=self.con)
                self.assertIsNone(stored["task_type"])

    def test_non_string_task_type_is_skipped(self):
        for bad in (123, True, []):
            with self.subTest(bad=bad):
                task = task_with_date_and_time()
                task["task_type"] = bad
                self.assertEqual(
                    ingest_task(task, connection=self.con)["reason_code"],
                    "invalid_task_type",
                )

    def test_missing_title_still_skipped_when_type_is_null(self):
        result = ingest_task(general_notice(), connection=self.con)
        self.assertEqual(result["reason_code"], "missing_task_title")

    def test_new_database_file_is_created_with_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            db_path = str(Path(folder) / "new.db")
            result = ingest_task(task_with_date_and_time(), db_path=db_path)
            self.assertEqual(result["status"], "inserted")
            stored = get_task_by_id(result["task_id"], db_path=db_path)
            self.assertEqual(stored["task_title"], "Submit Machine Learning Assignment 2")

    def test_ocr_result_works_on_a_new_database_file(self):
        with tempfile.TemporaryDirectory() as folder:
            db_path = str(Path(folder) / "new_ocr.db")
            result = ingest_ocr_result(ocr_result(), db_path=db_path)
            self.assertEqual(result["status"], "inserted")
            meta = get_ocr_metadata(result["task_id"], db_path=db_path)
            self.assertEqual(meta["overall_confidence"], 0.6024)


class IngestOcrTests(unittest.TestCase):

    def setUp(self):
        self.con = make_connection()

    def tearDown(self):
        self.con.close()

    def count(self, table):
        ingest.ensure_ocr_metadata_table(self.con)
        return self.con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    def test_ocr_result_stores_task_and_metadata(self):
        result = ingest_ocr_result(ocr_result(), connection=self.con)
        self.assertEqual(result["status"], "inserted")
        self.assertTrue(result["ocr_stored"])
        meta = get_ocr_metadata(result["task_id"], connection=self.con)
        self.assertEqual(meta["image_filename"], "screenshot 9.jpeg")
        self.assertEqual(meta["overall_confidence"], 0.6024)
        self.assertEqual(len(meta["line_confidences"]), 3)
        self.assertEqual(meta["line_confidences"][0]["text"], "REGISTER NOW")

    def test_nlp_confidence_and_ocr_confidence_stay_separate(self):
        result = ingest_ocr_result(ocr_result(), connection=self.con)
        stored = get_task_by_id(result["task_id"], connection=self.con)
        meta = get_ocr_metadata(result["task_id"], connection=self.con)
        self.assertEqual(stored["confidence"], 0.8)
        self.assertEqual(meta["overall_confidence"], 0.6024)

    def test_null_overall_confidence_is_stored_as_null(self):
        result = ingest_ocr_result(ocr_result(overall=None), connection=self.con)
        self.assertIsNone(get_ocr_metadata(result["task_id"], connection=self.con)["overall_confidence"])

    def test_empty_ocr_text_notice_is_skipped_and_nothing_stored(self):
        record = {
            "task": general_notice(),
            "ocr": {"image_filename": "blank.png", "overall_confidence": None,
                    "line_confidences": []},
        }
        result = ingest_ocr_result(record, connection=self.con)
        self.assertEqual(result["status"], "skipped")
        self.assertFalse(result["ocr_stored"])
        self.assertEqual(self.count("tasks"), 0)
        self.assertEqual(self.count("ocr_metadata"), 0)

    def test_invalid_ocr_metadata_skips_before_any_write(self):
        record = ocr_result()
        record["ocr"]["line_confidences"][1]["score"] = 1.5
        result = ingest_ocr_result(record, connection=self.con)
        self.assertEqual(result["reason_code"], "invalid_ocr_metadata")
        self.assertEqual(self.count("tasks"), 0)

    def test_malformed_ocr_results_are_skipped(self):
        for bad in (None, {}, {"task": general_notice()}, {"task": "x", "ocr": {}}):
            with self.subTest(bad=bad):
                self.assertEqual(
                    ingest_ocr_result(bad, connection=self.con)["reason_code"], "invalid_input"
                )

    def test_failed_metadata_write_removes_the_task_and_raises(self):
        with patch.object(ingest, "_insert_ocr_row", side_effect=sqlite3.OperationalError("boom")):
            with self.assertRaises(sqlite3.OperationalError):
                ingest_ocr_result(ocr_result(), connection=self.con)
        self.assertEqual(self.count("tasks"), 0)
        self.assertEqual(self.count("ocr_metadata"), 0)

    def test_get_ocr_metadata_returns_none_for_plain_task(self):
        result = ingest_task(task_with_date_and_time(), connection=self.con)
        self.assertIsNone(get_ocr_metadata(result["task_id"], connection=self.con))

    def test_tasks_schema_is_unchanged_by_ocr_ingest(self):
        before = [r[1] for r in self.con.execute("PRAGMA table_info(tasks)")]
        ingest_ocr_result(ocr_result(), connection=self.con)
        after = [r[1] for r in self.con.execute("PRAGMA table_info(tasks)")]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
