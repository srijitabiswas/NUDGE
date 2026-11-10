"""Phase A API: a thin Flask layer over backend/database/repository.py."""
import os
import sqlite3
from datetime import datetime

from flask import Flask, jsonify, request

from backend.database.connection import get_db_path
from backend.database.repository import (
    delete_task,
    get_all_tasks,
    get_task_by_id,
    insert_task,
    update_task_fields,
    update_task_status,
)

VALID_STATUSES = {"pending", "in_progress", "completed", "cancelled"}
ALLOWED_ORIGIN = "http://localhost:5173"
MAX_BODY_BYTES = 64 * 1024
# Owned by the storage layer: a client may send them (a full parser object has
# them as nulls) but they are ignored on create.
CREATE_IGNORED_FIELDS = ("task_id", "created_at", "completed_at", "due_datetime", "status")
EDITABLE_FIELDS = {
    "task_title", "due_date", "due_time", "event_datetime",
    "importance", "estimated_effort",
}


def _matches_format(text, formats):
    for fmt in formats:
        try:
            if datetime.strptime(text, fmt).strftime(fmt) == text:
                return True
        except ValueError:
            continue
    return False


def _bad_format(data):
    """Return an error message if a date/time field has an invalid format."""
    checks = (
        ("due_date", ("%Y-%m-%d",)),
        ("due_time", ("%H:%M", "%H:%M:%S")),
        ("event_datetime", ("%Y-%m-%dT%H:%M:%S",)),
    )
    for field, formats in checks:
        value = data.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        if not isinstance(value, str) or not _matches_format(value, formats):
            return f"{field} has an invalid format"
    return None


def create_app(db_path=None):
    app = Flask(__name__)
    path = get_db_path(db_path)
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Database not found at {path}. Build it first with "
            "backend.database.build_database --db-path <file>."
        )
    app.config["DB_PATH"] = path
    app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_BYTES

    @app.after_request
    def add_cors(response):
        # The frontend sends credentials: "include", so "*" is not allowed.
        if request.headers.get("Origin") == ALLOWED_ORIGIN:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type"
            response.headers["Access-Control-Allow-Methods"] = (
                "GET, POST, PATCH, DELETE, OPTIONS"
            )
            response.headers["Vary"] = "Origin"
        return response

    def error(message, code):
        return jsonify({"error": message}), code

    @app.errorhandler(413)
    def too_large(_exc):
        return error(f"Request body too large (max {MAX_BODY_BYTES} bytes)", 413)

    @app.errorhandler(404)
    def not_found(_exc):
        return error("Not found", 404)

    @app.errorhandler(405)
    def method_not_allowed(exc):
        response = jsonify({"error": "Method not allowed"})
        response.status_code = 405
        if getattr(exc, "valid_methods", None):
            response.headers["Allow"] = ", ".join(sorted(exc.valid_methods))
        return response

    @app.get("/tasks")
    def list_tasks():
        return jsonify(get_all_tasks(db_path=app.config["DB_PATH"]))

    @app.get("/tasks/<int:task_id>")
    def one_task(task_id):
        task = get_task_by_id(task_id, db_path=app.config["DB_PATH"])
        if task is None:
            return error("Task not found", 404)
        return jsonify(task)

    @app.post("/tasks")
    def add_task():
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return error("Request body must be a JSON object", 400)
        for field in CREATE_IGNORED_FIELDS:  # owned by the storage layer
            data.pop(field, None)
        bad = _bad_format(data)
        if bad:
            return error(bad, 400)
        try:
            new_id = insert_task(data, db_path=app.config["DB_PATH"])
        except (ValueError, TypeError, KeyError, sqlite3.IntegrityError) as exc:
            return error(str(exc), 400)
        return jsonify(get_task_by_id(new_id, db_path=app.config["DB_PATH"])), 201

    @app.patch("/tasks/<int:task_id>")
    def edit_task(task_id):
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not data:
            return error("Request body must be a non-empty JSON object", 400)
        if "status" in data:
            return error("Use PATCH /tasks/<id>/status to change status", 400)
        unknown = sorted(set(data) - EDITABLE_FIELDS)
        if unknown:
            return error(f"Fields not editable: {unknown}", 400)
        try:
            found = update_task_fields(task_id, data, db_path=app.config["DB_PATH"])
        except (ValueError, TypeError, KeyError, sqlite3.IntegrityError) as exc:
            return error(str(exc), 400)
        if not found:
            return error("Task not found", 404)
        return jsonify(get_task_by_id(task_id, db_path=app.config["DB_PATH"]))

    @app.delete("/tasks/<int:task_id>")
    def remove_task(task_id):
        if not delete_task(task_id, db_path=app.config["DB_PATH"]):
            return error("Task not found", 404)
        return jsonify({"task_id": task_id, "deleted": True})

    @app.patch("/tasks/<int:task_id>/status")
    def change_status(task_id):
        data = request.get_json(silent=True)
        status = data.get("status") if isinstance(data, dict) else None
        if status not in VALID_STATUSES:
            return error(f"status must be one of {sorted(VALID_STATUSES)}", 400)
        if not update_task_status(task_id, status, db_path=app.config["DB_PATH"]):
            return error("Task not found", 404)
        return jsonify(get_task_by_id(task_id, db_path=app.config["DB_PATH"]))

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=8000)
