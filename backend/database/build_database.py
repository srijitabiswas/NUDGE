"""Build a populated NUDGE database from saved parser/OCR snapshots (Steps 46-47).

It reads the two snapshot files made by data/samples/real/make_snapshots.py,
stores every record through the ingestion layer, prints what was stored and
what was skipped (with the reason), and can export the stored tasks as JSON
for the dashboard.

It does not import any NLP or OCR code, so it does not need spaCy.

Run from the repository root:

    python -m backend.database.build_database --db-path data/nudge_real.db ^
        --export data/processed/tasks_export.json

Rules
- --db-path is required, so nothing is written to a default location by accident.
- The database must be empty. A second run into the same file is refused,
  because it would store every task twice.
- Exit code 0 = built, 2 = refused or invalid input.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.database.connection import get_connection, init_db
from backend.database.ingest import get_ocr_metadata, ingest_ocr_result, ingest_task
from backend.database.repository import get_all_tasks

REAL_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "samples" / "real"
DEFAULT_PARSER_SNAPSHOT = REAL_DATA_DIR / "parser_snapshot.json"
DEFAULT_OCR_SNAPSHOT = REAL_DATA_DIR / "ocr_snapshot.json"


class BuildError(ValueError):
    """Raised for invalid input or a refused build."""


def load_snapshot(path: Path, kind: str) -> Tuple[Dict[str, Any], List[Any]]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BuildError(f"Cannot read {kind} snapshot {path}: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise BuildError(f"{kind} snapshot must be an object with a 'records' list.")
    meta = data.get("_meta")
    return (meta if isinstance(meta, dict) else {}), data["records"]


def atomic_write_json(path: Path, payload: Dict[str, Any]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=path.name + ".", suffix=".tmp", delete=False,
        ) as handle:
            temp_name = handle.name
            handle.write(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        temp_name = None
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def _store_records(con, records, kind) -> List[Dict[str, Any]]:
    rows = []
    for index, record in enumerate(records, 1):
        if not isinstance(record, dict):
            rows.append({"kind": kind, "label": f"record {index}", "category": None,
                         "expected": None, "status": "skipped",
                         "reason_code": "invalid_input", "task_id": None})
            continue
        category = record.get("category")
        if kind == "message":
            label = record.get("case_id") or f"record {index}"
            result = ingest_task(record.get("task"), category=category, connection=con)
        else:
            label = record.get("image") or f"record {index}"
            result = ingest_ocr_result(
                {"task": record.get("task"), "ocr": record.get("ocr")},
                category=category, connection=con,
            )
        rows.append({
            "kind": kind, "label": str(label), "category": category,
            "expected": record.get("expected_category"),
            "status": result["status"], "reason_code": result["reason_code"],
            "task_id": result["task_id"],
        })
    return rows



def build(db_path: str, parser_snapshot: Path, ocr_snapshot: Optional[Path],
          export_path: Optional[Path] = None) -> Dict[str, Any]:
    parser_meta, parser_records = load_snapshot(parser_snapshot, "parser")
    ocr_meta, ocr_records = ({}, [])
    if ocr_snapshot is not None:
        ocr_meta, ocr_records = load_snapshot(ocr_snapshot, "OCR")

    target = Path(db_path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        try:
            existing_con = sqlite3.connect(str(target))
            try:
                tables = {row[0] for row in existing_con.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )}
                task_count = existing_con.execute(
                    "SELECT COUNT(*) FROM tasks"
                ).fetchone()[0] if "tasks" in tables else 0
                ocr_count = existing_con.execute(
                    "SELECT COUNT(*) FROM ocr_metadata"
                ).fetchone()[0] if "ocr_metadata" in tables else 0
            finally:
                existing_con.close()
        except sqlite3.Error as exc:
            raise BuildError(f"Cannot inspect existing database {target}: {exc}") from exc

        if task_count or ocr_count:
            raise BuildError(
                f"Database {target} already contains {task_count} tasks "
                f"and {ocr_count} OCR records. Use a new --db-path."
            )

    temp_handle = tempfile.NamedTemporaryFile(
        prefix=target.stem + ".build_", suffix=".db",
        dir=str(target.parent), delete=False
    )
    temp_path = Path(temp_handle.name)
    temp_handle.close()
    con = None

    try:
        init_db(str(temp_path))
        con = get_connection(str(temp_path))
        rows = _store_records(con, parser_records, "message")
        rows += _store_records(con, ocr_records, "ocr")

        if export_path is not None:
            tasks = get_all_tasks(connection=con)
            for task in tasks:
                task["ocr"] = get_ocr_metadata(task["task_id"], connection=con)
            atomic_write_json(Path(export_path), {
                "_meta": {
                    "generated_on": date.today().isoformat(),
                    "task_count": len(tasks),
                    "note": "Tasks follow the 19-field contract. 'ocr' is filled only for screenshot tasks, otherwise null.",
                    "parser_snapshot": parser_meta,
                    "ocr_snapshot": ocr_meta,
                },
                "tasks": tasks,
            })

        con.close()
        con = None
        os.replace(str(temp_path), str(target))
        return {"rows": rows}

    finally:
        if con is not None:
            con.close()
        for suffix in ("", "-wal", "-shm"):
            leftover = Path(str(temp_path) + suffix)
            if leftover.exists():
                leftover.unlink()

def print_summary(rows: List[Dict[str, Any]]) -> None:
    for row in rows:
        print(f'{row["kind"]:8} {row["label"]:30} {str(row["category"] or "-"):15} '
              f'{row["status"]:9} {row["reason_code"] or "":22} {row["task_id"] or ""}')
    inserted = [r for r in rows if r["status"] == "inserted"]
    skipped = [r for r in rows if r["status"] == "skipped"]
    print()
    print(f"Inserted: {len(inserted)}   Skipped: {len(skipped)}   Total: {len(rows)}")
    reasons = Counter(r["reason_code"] for r in skipped)
    for reason, count in sorted(reasons.items()):
        print(f"  skipped because {reason}: {count}")
    differing = [r["label"] for r in rows if r["expected"] and r["category"] != r["expected"]]
    print("Category differs from the dataset's expected category:",
          differing if differing else "none")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build a NUDGE database from saved snapshots.")
    parser.add_argument("--db-path", required=True, help="database file to create (must be new or empty)")
    parser.add_argument("--parser-snapshot", default=None)
    parser.add_argument("--ocr-snapshot", default=None)
    parser.add_argument("--export", default=None, help="write the stored tasks to this JSON file")
    args = parser.parse_args(argv)

    parser_path = Path(args.parser_snapshot) if args.parser_snapshot else DEFAULT_PARSER_SNAPSHOT
    if args.ocr_snapshot:
        ocr_path = Path(args.ocr_snapshot)
    elif DEFAULT_OCR_SNAPSHOT.is_file():
        ocr_path = DEFAULT_OCR_SNAPSHOT
    else:
        ocr_path = None
        print("Note: no OCR snapshot found, so only message records are loaded.")

    try:
        result = build(args.db_path, parser_path, ocr_path,
                       Path(args.export) if args.export else None)
    except (BuildError, OSError, sqlite3.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print_summary(result["rows"])
    print(f"Database: {args.db_path}")
    if args.export:
        print(f"Export:   {args.export}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
