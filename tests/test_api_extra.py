import os
import tempfile
import unittest

from backend.api import ALLOWED_ORIGIN, create_app
from backend.database.connection import init_db


def base_task(**extra):
    task = {"task_title": "Edit Me", "source": "LMS",
            "raw_text": "Edit me.", "confidence": 0.9}
    task.update(extra)
    return task


class ApiExtraTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = os.path.join(self.tmp.name, "test.db")
        init_db(db_path=self.db)
        self.client = create_app(self.db).test_client()

    def tearDown(self):
        self.tmp.cleanup()

    def new_id(self, **extra):
        return self.client.post("/tasks", json=base_task(**extra)).get_json()["task_id"]

    def test_cors_allows_only_frontend_origin(self):
        res = self.client.get("/tasks", headers={"Origin": ALLOWED_ORIGIN})
        self.assertEqual(res.headers["Access-Control-Allow-Origin"], ALLOWED_ORIGIN)
        self.assertEqual(res.headers["Access-Control-Allow-Credentials"], "true")
        self.assertIn("DELETE", res.headers["Access-Control-Allow-Methods"])
        other = self.client.get("/tasks", headers={"Origin": "http://evil.example"})
        self.assertNotIn("Access-Control-Allow-Origin", other.headers)

    def test_preflight_options(self):
        res = self.client.options("/tasks/1", headers={"Origin": ALLOWED_ORIGIN})
        self.assertEqual(res.headers["Access-Control-Allow-Origin"], ALLOWED_ORIGIN)

    def test_patch_title_and_recompute_due_datetime(self):
        tid = self.new_id()
        res = self.client.patch(f"/tasks/{tid}", json={
            "task_title": "New Title", "due_date": "2026-11-12", "due_time": "09:30"})
        body = res.get_json()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(body["task_title"], "New Title")
        self.assertEqual(body["due_datetime"], "2026-11-12T09:30:00")

    def test_patch_cannot_change_status(self):
        tid = self.new_id()
        res = self.client.patch(f"/tasks/{tid}", json={"status": "completed"})
        self.assertEqual(res.status_code, 400)

    def test_patch_unknown_field_empty_body_and_non_json_are_400(self):
        tid = self.new_id()
        self.assertEqual(self.client.patch(f"/tasks/{tid}", json={"colour": "red"}).status_code, 400)
        self.assertEqual(self.client.patch(f"/tasks/{tid}", json={}).status_code, 400)
        self.assertEqual(self.client.patch(f"/tasks/{tid}", data="hello").status_code, 400)

    def test_patch_bad_date_is_400(self):
        tid = self.new_id()
        res = self.client.patch(f"/tasks/{tid}", json={"due_date": "not-a-date", "due_time": "17:00"})
        self.assertEqual(res.status_code, 400)

    def test_patch_missing_task_is_404(self):
        self.assertEqual(self.client.patch("/tasks/9999", json={"task_title": "x"}).status_code, 404)

    def test_delete_then_get_is_404(self):
        tid = self.new_id()
        self.assertEqual(self.client.delete(f"/tasks/{tid}").status_code, 200)
        self.assertEqual(self.client.get(f"/tasks/{tid}").status_code, 404)

    def test_delete_missing_task_is_404(self):
        self.assertEqual(self.client.delete("/tasks/9999").status_code, 404)

    def test_oversize_body_is_413(self):
        res = self.client.post("/tasks", json=base_task(raw_text="x" * 200000))
        self.assertEqual(res.status_code, 413)


if __name__ == "__main__":
    unittest.main()
