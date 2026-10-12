
import unittest
from datetime import datetime, timedelta

from ml.intelligence_metrics import (
    calculate_workload,
    calculate_productivity,
    detect_early_risks,
)


class TestIntelligenceMetrics(unittest.TestCase):

    def setUp(self):
        self.now = datetime(2026, 10, 12, 10, 0, 0)

    def test_workload_counts_active_tasks(self):
        tasks = [
            {"task_id": 1, "status": "pending",
             "due_datetime": "2026-10-11T10:00:00",
             "estimated_effort": 2},
            {"task_id": 2, "status": "in_progress",
             "due_datetime": "2026-10-15T10:00:00",
             "estimated_effort": 3},
            {"task_id": 3, "status": "completed",
             "estimated_effort": 5},
        ]

        result = calculate_workload(tasks, self.now)

        self.assertEqual(result["active_task_count"], 2)
        self.assertEqual(result["overdue_task_count"], 1)
        self.assertEqual(result["due_within_7_days_count"], 1)
        self.assertEqual(result["known_effort_total"], 5)

    def test_missing_effort_is_not_invented(self):
        result = calculate_workload(
            [{"status": "pending"}], self.now
        )

        self.assertEqual(result["known_effort_task_count"], 0)
        self.assertIsNone(result["known_effort_total"])

    def test_productivity_counts_completed_tasks(self):
        tasks = [
            {"status": "completed",
             "completed_at": "2026-10-10T10:00:00"},
            {"status": "pending"},
            {"status": "in_progress"},
        ]

        result = calculate_productivity(tasks, self.now)

        self.assertEqual(result["total_tasks"], 3)
        self.assertEqual(result["completed_task_count"], 1)
        self.assertEqual(result["active_task_count"], 2)
        self.assertAlmostEqual(result["completion_rate_percent"], 33.33)
        self.assertEqual(result["completed_within_7_days_count"], 1)

    def test_empty_productivity_dataset(self):
        result = calculate_productivity([], self.now)

        self.assertEqual(result["total_tasks"], 0)
        self.assertIsNone(result["completion_rate_percent"])

    def test_overdue_task_gets_high_risk(self):
        tasks = [{
            "task_id": 10,
            "task_title": "Assignment",
            "status": "pending",
            "due_datetime": "2026-10-11T10:00:00",
        }]

        risks = detect_early_risks(tasks, self.now)

        self.assertEqual(len(risks), 1)
        self.assertEqual(risks[0]["risk_level"], "high")

    def test_completed_task_gets_no_deadline_risk(self):
        tasks = [{
            "task_id": 11,
            "status": "completed",
            "due_datetime": "2026-10-11T10:00:00",
        }]

        self.assertEqual(detect_early_risks(tasks, self.now), [])

    def test_invalid_deadline_does_not_crash(self):
        tasks = [{
            "task_id": 12,
            "status": "pending",
            "due_datetime": "not-a-date",
        }]

        self.assertEqual(detect_early_risks(tasks, self.now), [])


if __name__ == "__main__":
    unittest.main()
