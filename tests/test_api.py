import os
import tempfile
import unittest

from backend.api import create_app
from backend.database.connection import init_db


def base_task(**extra):
    task = {
        "task_title": "Submit Test Assignment",
        "source": "LMS",
        "raw_text": "Submit the test assignment.",
        "confidence": 0.9,
    }
    task.update(extra)
    return task


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "test.db")
        init_db(db_path=self.db)
        self.client = create_app(self.db).test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def test_list_starts_empty(self):
        res = self.client.get("/tasks")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), [])

    def test_post_with_date_and_time_sets_due_datetime(self):
        res = self.client.post("/tasks", json=base_task(due_date="2026-11-10", due_time="17:00"))
        self.assertEqual(res.status_code, 201)
        body = res.get_json()
        self.assertEqual(body["due_datetime"], "2026-11-10T17:00:00")
        self.assertEqual(body["status"], "pending")

    def test_post_date_only_keeps_due_datetime_null(self):
        res = self.client.post("/tasks", json=base_task(due_date="2026-11-10"))
        self.assertEqual(res.status_code, 201)
        self.assertIsNone(res.get_json()["due_datetime"])

    def test_event_datetime_is_not_used_as_deadline(self):
        res = self.client.post("/tasks", json=base_task(event_datetime="2026-11-12T10:00:00"))
        body = res.get_json()
        self.assertIsNone(body["due_datetime"])
        self.assertEqual(body["event_datetime"], "2026-11-12T10:00:00")

    def test_client_cannot_choose_task_id(self):
        res = self.client.post("/tasks", json=base_task(task_id=999))
        self.assertNotEqual(res.get_json()["task_id"], 999)

    def test_post_missing_required_field_is_400(self):
        res = self.client.post("/tasks", json={"task_title": "No source"})
        self.assertEqual(res.status_code, 400)

    def test_post_non_json_is_400(self):
        res = self.client.post("/tasks", data="hello")
        self.assertEqual(res.status_code, 400)

    def test_get_one_and_missing(self):
        new_id = self.client.post("/tasks", json=base_task()).get_json()["task_id"]
        self.assertEqual(self.client.get(f"/tasks/{new_id}").status_code, 200)
        self.assertEqual(self.client.get("/tasks/9999").status_code, 404)

    def test_complete_sets_completed_at_and_reopen_clears_it(self):
        new_id = self.client.post("/tasks", json=base_task()).get_json()["task_id"]
        done = self.client.patch(f"/tasks/{new_id}/status", json={"status": "completed"}).get_json()
        self.assertEqual(done["status"], "completed")
        self.assertIsNotNone(done["completed_at"])
        reopened = self.client.patch(f"/tasks/{new_id}/status", json={"status": "pending"}).get_json()
        self.assertIsNone(reopened["completed_at"])

    def test_cancelled_status_is_accepted(self):
        new_id = self.client.post("/tasks", json=base_task()).get_json()["task_id"]
        res = self.client.patch(f"/tasks/{new_id}/status", json={"status": "cancelled"})
        self.assertEqual(res.get_json()["status"], "cancelled")

    def test_bad_status_is_400_and_unknown_task_is_404(self):
        new_id = self.client.post("/tasks", json=base_task()).get_json()["task_id"]
        self.assertEqual(self.client.patch(f"/tasks/{new_id}/status", json={"status": "overdue"}).status_code, 400)
        self.assertEqual(self.client.patch("/tasks/9999/status", json={"status": "completed"}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
