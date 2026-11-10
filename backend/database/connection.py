"""Database connection management for NUDGE.

Provides functions to obtain configured SQLite connections and initialize
the database schema from schema.sql.
"""

from __future__ import annotations

import os
from pathlib import Path
import sqlite3
from typing import Optional

# Path to the NUDGE root directory (two levels up from backend/database)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"
DEFAULT_DB_FILE = PROJECT_ROOT / "data" / "nudge.db"


def get_db_path(db_path: Optional[str] = None) -> str:
    """Resolve the SQLite database path.

    Precedence:
    1. Explicit `db_path` argument if provided.
    2. `NUDGE_DB_PATH` environment variable if set.
    3. Default path at `data/nudge.db` relative to project root.
    """
    if db_path is not None:
        return db_path
    env_path = os.environ.get("NUDGE_DB_PATH")
    if env_path:
        return env_path
    return str(DEFAULT_DB_FILE)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Create and return a configured SQLite connection.

    - Enables dictionary/row access via sqlite3.Row.
    - Enables foreign key constraint enforcement.
    - Creates parent directories automatically for disk-backed databases.
    """
    resolved_path = get_db_path(db_path)

    # Ensure parent directory exists for file-based databases
    if resolved_path != ":memory:":
        parent_dir = Path(resolved_path).parent
        parent_dir.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(resolved_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def init_db(
    db_path: Optional[str] = None,
    schema_path: Optional[str | Path] = None,
) -> None:
    """Initialize the SQLite database using the formal schema.sql definition.

    Executes schema DDL statements to create tables and indexes if they do not exist.
    """
    target_schema = Path(schema_path) if schema_path else DEFAULT_SCHEMA_PATH
    if not target_schema.is_file():
        raise FileNotFoundError(f"Schema file not found at: {target_schema}")

    schema_sql = target_schema.read_text(encoding="utf-8")

    connection = get_connection(db_path)
    try:
        connection.executescript(schema_sql)
        connection.commit()
    finally:
        connection.close()
