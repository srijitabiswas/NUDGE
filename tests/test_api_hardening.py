"""Extra tests for backend/api.py (the Flask API): storage-owned fields on
create, date/time format checks, protected fields on edit, JSON errors and
the delete response.

This is a separate file so the existing tests/test_api.py and
tests/test_api_extra.py are not touched.
"""

import os
import tempfile
import unittest

from backend.api import create_app
from backend.database.connection import init_db

ORIGIN = "http://localhost:5173"


def task(**extra):
    data = {
        "task_title": "Submit DBMS assignment 3",
        "task_type": "assignment",
        "source": "WhatsApp",
        "raw_text": "Submit DBMS assignment 3 by 12 November.",
        "confidence": 0.9,
        "due_date": "2026-11-12",
    }
    data.update(extra)
    return data


class HardeningTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "test.db")
        init_db(db_path=self.db)
        self.client = create_app(self.db).test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def create(self, **extra):
        response = self.client.post("/tasks", json=task(**extra))
        self.assertEqual(response.status_code, 201, response.get_data(as_text=True))
        return response.get_json()

    # ---- create: storage-owned fields
    def test_create_ignores_client_chosen_storage_fields(self):
        body = self.create(due_datetime="2030-01-01T23:59:00", status="completed",
                           created_at="1999-01-01T00:00:00",
                           completed_at="1999-01-02T00:00:00", task_id=999)
        self.assertNotEqual(body["task_id"], 999)
        self.assertIsNone(body["due_datetime"])
        self.assertEqual(body["status"], "pending")
        self.assertNotEqual(body["created_at"], "1999-01-01T00:00:00")
        self.assertIsNone(body["completed_at"])

    def test_create_accepts_a_full_parser_object_with_null_storage_fields(self):
        body = self.create(task_id=None, created_at=None, completed_at=None,
                           due_datetime=None, status="pending", due_time=None)
        self.assertIsNone(body["due_datetime"])

    def test_create_date_and_time_still_derive_due_datetime(self):
        self.assertEqual(self.create(due_time="17:00")["due_datetime"], "2026-11-12T17:00:00")

    def test_create_date_only_keeps_time_and_datetime_null(self):
        body = self.create()
        self.assertEqual(body["due_date"], "2026-11-12")
        self.assertIsNone(body["due_time"])
        self.assertIsNone(body["due_datetime"])

    # ---- create: format checks
    def test_create_rejects_invalid_date_and_time_formats(self):
        bad_values = [{"due_date": "tomorrow"}, {"due_date": "2026-13-45"}, {"due_date": "2026-1-5"},
                      {"due_time": "5pm"}, {"due_time": "25:00"}, {"due_time": 17},
                      {"event_datetime": "next monday"}, {"event_datetime": "2026-11-12"}]
        for extra in bad_values:
            with self.subTest(extra=extra):
                response = self.client.post("/tasks", json=task(**extra))
                self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/tasks").get_json(), [])

    def test_create_accepts_null_and_blank_optional_dates(self):
        for extra in ({"due_date": None}, {"due_date": ""}, {"due_time": None}, {"event_datetime": None}):
            with self.subTest(extra=extra):
                self.assertEqual(self.client.post("/tasks", json=task(**extra)).status_code, 201)

    def test_create_accepts_valid_event_datetime(self):
        body = self.create(due_date=None, task_type="event", event_datetime="2026-11-20T09:00:00")
        self.assertEqual(body["event_datetime"], "2026-11-20T09:00:00")
        self.assertIsNone(body["due_datetime"])

    # ---- edit: protected fields
    def test_edit_rejects_every_protected_field_and_changes_nothing(self):
        created = self.create()
        task_id = created["task_id"]
        protected = ["task_id", "status", "due_datetime", "created_at", "completed_at", "source",
                     "raw_text", "confidence", "date_time_expression", "change_information"]
        for field in protected:
            with self.subTest(field=field):
                response = self.client.patch(f"/tasks/{task_id}", json={field: "x"})
                self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get(f"/tasks/{task_id}").get_json(), created)

    def test_edit_mixing_valid_and_protected_fields_changes_nothing(self):
        created = self.create()
        response = self.client.patch(f"/tasks/{created['task_id']}",
                                     json={"task_title": "Changed", "source": "x"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get(f"/tasks/{created['task_id']}").get_json(), created)

    # ---- JSON errors
    def test_unknown_route_is_a_json_404(self):
        for path in ("/nothing", "/tasks/abc", "/api/tasks"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 404)
                self.assertEqual(response.content_type, "application/json")
                self.assertIn("error", response.get_json())

    def test_wrong_method_is_a_json_405_with_allow_header(self):
        response = self.client.put("/tasks", json={})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content_type, "application/json")
        self.assertIn("POST", response.headers["Allow"])
        self.assertIn("GET", response.headers["Allow"])

    # ---- delete response
    def test_delete_response_uses_task_id(self):
        task_id = self.create()["task_id"]
        response = self.client.delete(f"/tasks/{task_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"task_id": task_id, "deleted": True})

    # ---- CORS and content type stay as approved
    def test_only_the_frontend_origin_gets_cors_headers(self):
        allowed = self.client.get("/tasks", headers={"Origin": ORIGIN})
        self.assertEqual(allowed.headers.get("Access-Control-Allow-Origin"), ORIGIN)
        for origin in ("http://evil.example", "http://127.0.0.1:5173", "null"):
            with self.subTest(origin=origin):
                other = self.client.get("/tasks", headers={"Origin": origin})
                self.assertIsNone(other.headers.get("Access-Control-Allow-Origin"))

    def test_post_with_wrong_content_type_does_not_create_a_task(self):
        response = self.client.post("/tasks", data="{}", content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/tasks").get_json(), [])


if __name__ == "__main__":
    unittest.main()
