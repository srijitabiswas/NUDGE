"""Ingestion layer: parsed NLP / OCR output -> database (roadmap Step 47).

This module takes the dictionaries produced by the NLP parser (and by the OCR
adapter) and stores them through ``insert_task``. It does NOT import any NLP
or OCR code, so it works on plain dictionaries.

What it does
- Skips general notices and incomplete records and says why. A skip is never
  silent: every call returns a result dictionary with ``status`` and, for a
  skip, a ``reason_code`` and a human-readable ``reason``.
- ``category`` ("task", "event" or "general_notice") is optional. When it is
  not given, the decision is made from the record's own fields.
- OCR confidence is stored in a separate ``ocr_metadata`` table. The ``tasks``
  table and the ``insert_task`` contract are not changed. The NLP
  ``confidence`` stays in ``tasks.confidence`` and is never mixed with OCR.
- The database owns ``task_id`` and ``created_at``. If the input carries them,
  they are ignored.

Result dictionary
    {"status": "inserted" | "skipped",
     "task_id": int | None,
     "reason_code": str | None,
     "reason": str | None,
     "warnings": [str, ...]}
    OCR results also carry "ocr_stored": bool.

Unexpected database errors (for example a failed write) are NOT turned into
skips. They are raised, so a real failure is never hidden.
"""

from __future__ import annotations

import json
import math
import sqlite3
from typing import Any, Dict, Optional

from backend.database.connection import get_connection
from backend.database.repository import VALID_STATUSES, insert_task

VALID_CATEGORIES = ("task", "event", "general_notice")

# Owned by the storage layer. Input values for these are ignored.
STORAGE_OWNED_FIELDS = ("task_id", "created_at")

OCR_METADATA_DDL = """
CREATE TABLE IF NOT EXISTS ocr_metadata (
    ocr_id              INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id             INTEGER NOT NULL UNIQUE
                        REFERENCES tasks(task_id) ON DELETE CASCADE,
    image_filename      TEXT NOT NULL CHECK (length(trim(image_filename)) > 0),
    overall_confidence  REAL
                        CHECK (overall_confidence IS NULL
                               OR (overall_confidence >= 0.0 AND overall_confidence <= 1.0)),
    line_confidences    TEXT NOT NULL DEFAULT '[]'
                        CHECK (json_valid(line_confidences)
                               AND json_type(line_confidences) = 'array'),
    created_at          TEXT NOT NULL
                        DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime'))
)
"""


# ---------------------------------------------------------------- helpers

def _skip(code: str, reason: str) -> Dict[str, Any]:
    return {
        "status": "skipped",
        "task_id": None,
        "reason_code": code,
        "reason": reason,
        "warnings": [],
    }


def _is_score(value: Any) -> bool:
    """True for a real number from 0 to 1. Booleans, NaN and infinity are not."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False
    return math.isfinite(value) and 0 <= value <= 1


def _nonempty_str(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _check_task(task: Any, category: Optional[str]):
    """Return (reason_code, reason) if the task must be skipped, else None."""
    if not isinstance(task, dict):
        return "invalid_input", "Task must be a dictionary."

    if category is not None and category not in VALID_CATEGORIES:
        return (
            "invalid_category",
            f"Unknown category {category!r}. Allowed: {VALID_CATEGORIES}.",
        )
    if category == "general_notice":
        return (
            "general_notice",
            "Category is 'general_notice'; it is not stored as a task.",
        )

    if not _nonempty_str(task.get("task_title")):
        return (
            "missing_task_title",
            "task_title is missing or empty. This usually means a general "
            "notice or a non-actionable message.",
        )
    if not _nonempty_str(task.get("task_type")):
        return (
            "missing_task_type",
            "task_type is missing or empty. This usually means a general "
            "notice or a non-actionable message.",
        )
    if not _nonempty_str(task.get("source")):
        return "missing_source", "source is missing or empty."
    if not _nonempty_str(task.get("raw_text")):
        return "missing_raw_text", "raw_text is missing or empty."

    confidence = task.get("confidence")
    if confidence is not None and not _is_score(confidence):
        return (
            "invalid_confidence",
            f"confidence must be null or a number from 0 to 1, got {confidence!r}.",
        )

    status = task.get("status")
    if status and status not in VALID_STATUSES:
        return (
            "invalid_status",
            f"status {status!r} is not one of {VALID_STATUSES}.",
        )

    effort = task.get("estimated_effort")
    if effort is not None:
        if (isinstance(effort, bool) or not isinstance(effort, (int, float))
                or not math.isfinite(effort) or effort < 0):
            return (
                "invalid_estimated_effort",
                f"estimated_effort must be null or a number >= 0, got {effort!r}.",
            )

    change_info = task.get("change_information")
    if change_info is not None and not isinstance(change_info, (list, tuple)):
        return (
            "invalid_change_information",
            "change_information must be null or a list.",
        )

    event_dt = task.get("event_datetime")
    if event_dt is not None and not isinstance(event_dt, str):
        return "invalid_event_datetime", "event_datetime must be null or a string."

    return None


def _check_ocr(ocr: Any):
    """Return (reason_code, reason) if OCR details are invalid, else None."""
    if not isinstance(ocr, dict):
        return "invalid_ocr_metadata", "'ocr' must be a dictionary."
    if not _nonempty_str(ocr.get("image_filename")):
        return "invalid_ocr_metadata", "ocr.image_filename must be a non-empty string."

    overall = ocr.get("overall_confidence")
    if overall is not None and not _is_score(overall):
        return (
            "invalid_ocr_metadata",
            f"ocr.overall_confidence must be null or a number from 0 to 1, got {overall!r}.",
        )

    lines = ocr.get("line_confidences")
    if not isinstance(lines, list):
        return "invalid_ocr_metadata", "ocr.line_confidences must be a list."
    for index, item in enumerate(lines):
        if not isinstance(item, dict) or not isinstance(item.get("text"), str):
            return (
                "invalid_ocr_metadata",
                f"ocr.line_confidences[{index}] needs a string 'text'.",
            )
        if not _is_score(item.get("score")):
            return (
                "invalid_ocr_metadata",
                f"ocr.line_confidences[{index}].score must be a number from 0 to 1.",
            )
    return None


def _warnings(task: Dict[str, Any], category: Optional[str]):
    warnings = []
    if category == "event" and not task.get("event_datetime"):
        warnings.append("Category is 'event' but event_datetime is empty.")
    return warnings


def _storable(task: Dict[str, Any]) -> Dict[str, Any]:
    """Copy of the task without the fields the database generates itself."""
    return {k: v for k, v in task.items() if k not in STORAGE_OWNED_FIELDS}


def ensure_ocr_metadata_table(connection: sqlite3.Connection) -> None:
    """Create the ocr_metadata table if it does not exist yet."""
    connection.execute(OCR_METADATA_DDL)
    connection.commit()


def _insert_ocr_row(connection: sqlite3.Connection, task_id: int, ocr: Dict[str, Any]) -> None:
    connection.execute(
        "INSERT INTO ocr_metadata "
        "(task_id, image_filename, overall_confidence, line_confidences) "
        "VALUES (?, ?, ?, ?)",
        (
            task_id,
            ocr["image_filename"],
            ocr.get("overall_confidence"),
            json.dumps(
                [{"text": i["text"], "score": i["score"]} for i in ocr["line_confidences"]],
                ensure_ascii=False,
            ),
        ),
    )
    connection.commit()


# ------------------------------------------------------------- public API

def ingest_task(
    task: Dict[str, Any],
    category: Optional[str] = None,
    db_path: Optional[str] = None,
    connection: Optional[sqlite3.Connection] = None,
) -> Dict[str, Any]:
    """Store one parsed task/event, or skip it with a clear reason."""
    problem = _check_task(task, category)
    if problem:
        return _skip(*problem)

    owns_connection = connection is None
    con = connection or get_connection(db_path)
    try:
        task_id = insert_task(_storable(task), connection=con)
    finally:
        if owns_connection:
            con.close()

    return {
        "status": "inserted",
        "task_id": task_id,
        "reason_code": None,
        "reason": None,
        "warnings": _warnings(task, category),
    }


def ingest_ocr_result(
    result: Dict[str, Any],
    category: Optional[str] = None,
    db_path: Optional[str] = None,
    connection: Optional[sqlite3.Connection] = None,
) -> Dict[str, Any]:
    """Store an OCR adapter result ``{"task": ..., "ocr": ...}``.

    The task goes into ``tasks`` and the OCR details go into ``ocr_metadata``.
    Both are checked before anything is written. If writing the OCR row fails
    after the task was saved, the task is removed again and the error is raised,
    so a task is never left without its OCR details.
    """
    if (not isinstance(result, dict) or not isinstance(result.get("task"), dict)
            or "ocr" not in result):
        return _skip(
            "invalid_input",
            "OCR result must be a dictionary with 'task' and 'ocr'.",
        )

    task, ocr = result["task"], result["ocr"]

    problem = _check_task(task, category) or _check_ocr(ocr)
    if problem:
        skipped = _skip(*problem)
        skipped["ocr_stored"] = False
        return skipped

    owns_connection = connection is None
    con = connection or get_connection(db_path)
    try:
        ensure_ocr_metadata_table(con)
        task_id = insert_task(_storable(task), connection=con)
        try:
            _insert_ocr_row(con, task_id, ocr)
        except Exception:
            con.rollback()
            con.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
            con.commit()
            raise
    finally:
        if owns_connection:
            con.close()

    return {
        "status": "inserted",
        "task_id": task_id,
        "reason_code": None,
        "reason": None,
        "warnings": _warnings(task, category),
        "ocr_stored": True,
    }


def get_ocr_metadata(
    task_id: int,
    db_path: Optional[str] = None,
    connection: Optional[sqlite3.Connection] = None,
) -> Optional[Dict[str, Any]]:
    """Return the OCR details stored for a task, or None if there are none."""
    owns_connection = connection is None
    con = connection or get_connection(db_path)
    try:
        ensure_ocr_metadata_table(con)
        row = con.execute(
            "SELECT task_id, image_filename, overall_confidence, line_confidences "
            "FROM ocr_metadata WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "task_id": row[0],
            "image_filename": row[1],
            "overall_confidence": row[2],
            "line_confidences": json.loads(row[3]),
        }
    finally:
        if owns_connection:
            con.close()
