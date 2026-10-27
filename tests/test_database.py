"""Unit and integration tests for Phase 7 (Step 47): Database & Data Layer.

Verifies:
1. SQLite connection and schema initialization.
2. Insertion and retrieval of structured tasks against the 19-field contract.
3. Strict preservation of NULLs (no invented dates/times/fallbacks).
4. Normalization of due_datetime (only when both date and time are provided).
5. Serialization and decoding of change_information as JSON arrays.
6. Auto-generation of task_id and created_at by SQLite.
7. Enforcement of database constraints (status, confidence, JSON validation, etc.).
8. Lifecycle management of completed_at upon task status transitions.
"""

from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import unittest

from backend.database.connection import get_connection, get_db_path, init_db
from backend.database.repository import (
    CONTRACT_FIELD_ORDER,
    get_all_tasks,
    get_task_by_id,
    insert_task,
    normalize_due_datetime,
    update_task_status,
)

SAMPLE_TASKS_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "samples" / "sample_tasks.json"
)


class BaseDatabaseTestCase(unittest.TestCase):
    """Base test case managing an isolated temporary database for each test."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test_nudge.db")
        init_db(db_path=self.db_path)

    def tearDown(self):
        import gc
        gc.collect()
        self.temp_dir.cleanup()


class TestDatabaseConnection(BaseDatabaseTestCase):
    """Tests for database initialization and connection handling."""

    def test_schema_initialization(self):
        """Verify that tasks table and all 4 indexes are successfully created."""
        con = get_connection(self.db_path)
        try:
            tables = [
                row[0]
                for row in con.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'table'"
                ).fetchall()
            ]
            self.assertIn("tasks", tables)

            indexes = [
                row[0]
                for row in con.execute(
                    "SELECT name FROM sqlite_master WHERE type = 'index'"
                ).fetchall()
            ]
            self.assertIn("idx_tasks_status", indexes)
            self.assertIn("idx_tasks_due_datetime", indexes)
            self.assertIn("idx_tasks_event_datetime", indexes)
            self.assertIn("idx_tasks_subject", indexes)
        finally:
            con.close()

    def test_configurable_db_path(self):
        """Verify explicit db_path and environment variable configuration."""
        custom_path = str(Path(self.temp_dir.name) / "custom.db")
        self.assertEqual(get_db_path(custom_path), custom_path)

        old_env = os.environ.get("NUDGE_DB_PATH")
        try:
            os.environ["NUDGE_DB_PATH"] = custom_path
            self.assertEqual(get_db_path(), custom_path)
        finally:
            if old_env is not None:
                os.environ["NUDGE_DB_PATH"] = old_env
            else:
                os.environ.pop("NUDGE_DB_PATH", None)


class TestTaskInsertionAndRetrieval(BaseDatabaseTestCase):
    """Tests inserting and retrieving tasks using the 19-field shared contract."""

    def test_insert_and_retrieve_all_sample_tasks(self):
        """Insert all 6 sample tasks and verify their contract compliance on retrieval."""
        self.assertTrue(SAMPLE_TASKS_PATH.is_file(), "sample_tasks.json must exist")
        with open(SAMPLE_TASKS_PATH, "r", encoding="utf-8") as f:
            samples = json.load(f)

        self.assertEqual(len(samples), 6)

        inserted_ids = []
        for sample in samples:
            task_id = insert_task(sample, db_path=self.db_path)
            self.assertIsInstance(task_id, int)
            self.assertGreater(task_id, 0)
            inserted_ids.append(task_id)

        # Ensure task_ids are sequential
        self.assertEqual(inserted_ids, [1, 2, 3, 4, 5, 6])

        # Verify retrieval and structure of every sample
        for idx, task_id in enumerate(inserted_ids):
            retrieved = get_task_by_id(task_id, db_path=self.db_path)
            self.assertIsNotNone(retrieved)

            # 1. Exactly the 19 contract keys in the exact contract sequence
            self.assertEqual(list(retrieved.keys()), CONTRACT_FIELD_ORDER)

            # 2. task_id matches generated ID
            self.assertEqual(retrieved["task_id"], task_id)

            # 3. created_at is automatically assigned valid ISO 8601 string
            self.assertIsInstance(retrieved["created_at"], str)
            self.assertRegex(
                retrieved["created_at"],
                r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
            )

            # 4. change_information is always decoded back to a Python list
            self.assertIsInstance(retrieved["change_information"], list)

            # 5. Core NLP fields match input
            expected = samples[idx]
            self.assertEqual(retrieved["task_title"], expected["task_title"])
            self.assertEqual(retrieved["task_type"], expected["task_type"])
            self.assertEqual(retrieved["source"], expected["source"])
            self.assertEqual(retrieved["raw_text"], expected["raw_text"])

        # Specifically check MSG-004 change_information
        msg4 = get_task_by_id(4, db_path=self.db_path)
        self.assertEqual(len(msg4["change_information"]), 1)
        self.assertTrue(msg4["change_information"][0]["is_changed"])
        self.assertEqual(msg4["change_information"][0]["change_type"], "deadline")
        self.assertEqual(
            msg4["change_information"][0]["old_value"], "Wednesday 11:59 PM"
        )
        self.assertEqual(
            msg4["change_information"][0]["new_value"], "Friday, 30th October at 11:59 PM"
        )

        # Check get_all_tasks returns all 6 records
        all_tasks = get_all_tasks(db_path=self.db_path)
        self.assertEqual(len(all_tasks), 6)

    def test_get_nonexistent_task(self):
        """Querying a non-existent task_id returns None without error."""
        result = get_task_by_id(999999, db_path=self.db_path)
        self.assertIsNone(result)


class TestNullPreservationAndDatetime(BaseDatabaseTestCase):
    """Tests ensuring no missing dates, times, or timestamps are invented."""

    def test_null_preservation_across_samples(self):
        """Verify strict NULL preservation for missing temporal and optional fields."""
        with open(SAMPLE_TASKS_PATH, "r", encoding="utf-8") as f:
            samples = json.load(f)

        for sample in samples:
            insert_task(sample, db_path=self.db_path)

        # MSG-002: Date present, but time missing -> due_datetime must be NULL (no 23:59!)
        msg2 = get_task_by_id(2, db_path=self.db_path)
        self.assertEqual(msg2["due_date"], "2026-11-04")
        self.assertIsNone(msg2["due_time"])
        self.assertIsNone(msg2["due_datetime"])
        self.assertIsNone(msg2["event_datetime"])
        self.assertIsNone(msg2["subject"])
        self.assertIsNone(msg2["importance"])
        self.assertIsNone(msg2["estimated_effort"])

        # MSG-003: Scheduled event occurrence -> due_datetime NULL, event_datetime populated
        msg3 = get_task_by_id(3, db_path=self.db_path)
        self.assertIsNone(msg3["due_date"])
        self.assertIsNone(msg3["due_time"])
        self.assertIsNone(msg3["due_datetime"])
        self.assertEqual(msg3["event_datetime"], "2026-10-27T14:00:00")

        # MSG-006: Incomplete temporal info -> all dates/times strictly NULL
        msg6 = get_task_by_id(6, db_path=self.db_path)
        self.assertIsNone(msg6["due_date"])
        self.assertIsNone(msg6["due_time"])
        self.assertIsNone(msg6["due_datetime"])
        self.assertIsNone(msg6["event_datetime"])
        self.assertIsNone(msg6["date_time_expression"])

    def test_normalize_due_datetime_function(self):
        """Directly verify the normalization helper logic."""
        # Both date and time provided
        self.assertEqual(
            normalize_due_datetime("2026-10-15", "17:00"),
            "2026-10-15T17:00:00",
        )
        self.assertEqual(
            normalize_due_datetime("2026-10-15", "17:00:30"),
            "2026-10-15T17:00:30",
        )
        # Explicit due_datetime takes precedence if supplied
        self.assertEqual(
            normalize_due_datetime("2026-10-15", "17:00", "2026-10-15T17:00:00"),
            "2026-10-15T17:00:00",
        )
        # Missing time -> None
        self.assertIsNone(normalize_due_datetime("2026-10-15", None))
        self.assertIsNone(normalize_due_datetime("2026-10-15", ""))
        # Missing date -> None
        self.assertIsNone(normalize_due_datetime(None, "17:00"))
        # Both missing -> None
        self.assertIsNone(normalize_due_datetime(None, None))


class TestConstraintValidation(BaseDatabaseTestCase):
    """Tests verifying database-level constraint enforcement and rejection of invalid data."""

    def test_invalid_status_rejection(self):
        """Inserting a task with an unpermitted status violates CHECK constraint."""
        bad_task = {
            "task_title": "Test Task",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "Sample text",
            "status": "finished",  # Invalid status
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(bad_task, db_path=self.db_path)

    def test_invalid_confidence_rejection(self):
        """Confidence score outside [0.0, 1.0] violates CHECK constraint."""
        task_over = {
            "task_title": "Test Task",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "Sample text",
            "confidence": 1.5,
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(task_over, db_path=self.db_path)

        task_under = {
            "task_title": "Test Task",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "Sample text",
            "confidence": -0.1,
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(task_under, db_path=self.db_path)

    def test_invalid_change_information_rejection(self):
        """Non-JSON text or non-array JSON violates json_valid() / json_type() constraints."""
        # Non-JSON string
        task_bad_json = {
            "task_title": "Test Task",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "Sample text",
            "change_information": "not valid json {",
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(task_bad_json, db_path=self.db_path)

        # Valid JSON, but object instead of array
        task_object_json = {
            "task_title": "Test Task",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "Sample text",
            "change_information": '{"key": "value"}',
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(task_object_json, db_path=self.db_path)

    def test_empty_required_text_rejection(self):
        """Whitespace-only or empty strings for required fields violate length(trim(...)) > 0."""
        # Empty title
        task_empty_title = {
            "task_title": "   ",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "Sample text",
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(task_empty_title, db_path=self.db_path)

        # Empty raw_text
        task_empty_raw = {
            "task_title": "Valid Title",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "",
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(task_empty_raw, db_path=self.db_path)

    def test_negative_effort_rejection(self):
        """Negative estimated effort violates CHECK (estimated_effort >= 0)."""
        task_neg_effort = {
            "task_title": "Test Task",
            "task_type": "assignment",
            "source": "LMS",
            "raw_text": "Sample text",
            "estimated_effort": -2.5,
        }
        with self.assertRaises(sqlite3.IntegrityError):
            insert_task(task_neg_effort, db_path=self.db_path)


class TestStatusLifecycle(BaseDatabaseTestCase):
    """Tests authoritative status management and completed_at transitions."""

    def test_completed_at_lifecycle(self):
        """completed_at is set when transitioning to 'completed' and cleared on reopen."""
        task_id = insert_task(
            {
                "task_title": "Lifecycle Task",
                "task_type": "assignment",
                "source": "LMS",
                "raw_text": "Lifecycle test message",
                "status": "pending",
            },
            db_path=self.db_path,
        )

        initial = get_task_by_id(task_id, db_path=self.db_path)
        self.assertEqual(initial["status"], "pending")
        self.assertIsNone(initial["completed_at"])

        # Transition to completed
        updated = update_task_status(task_id, "completed", db_path=self.db_path)
        self.assertTrue(updated)

        completed_task = get_task_by_id(task_id, db_path=self.db_path)
        self.assertEqual(completed_task["status"], "completed")
        self.assertIsInstance(completed_task["completed_at"], str)
        self.assertRegex(
            completed_task["completed_at"],
            r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$",
        )

        # Reopen to in_progress -> completed_at must be cleared to NULL
        reopened = update_task_status(task_id, "in_progress", db_path=self.db_path)
        self.assertTrue(reopened)

        in_progress_task = get_task_by_id(task_id, db_path=self.db_path)
        self.assertEqual(in_progress_task["status"], "in_progress")
        self.assertIsNone(in_progress_task["completed_at"])

        # Reopen to pending -> completed_at remains NULL
        update_task_status(task_id, "pending", db_path=self.db_path)
        pending_task = get_task_by_id(task_id, db_path=self.db_path)
        self.assertEqual(pending_task["status"], "pending")
        self.assertIsNone(pending_task["completed_at"])

    def test_invalid_status_update_rejection(self):
        """Updating to an invalid status string raises ValueError."""
        task_id = insert_task(
            {
                "task_title": "Test Task",
                "task_type": "assignment",
                "source": "LMS",
                "raw_text": "Sample text",
            },
            db_path=self.db_path,
        )
        with self.assertRaises(ValueError):
            update_task_status(task_id, "unknown_status", db_path=self.db_path)


if __name__ == "__main__":
    unittest.main()
