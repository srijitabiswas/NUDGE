
import unittest
from datetime import datetime, timedelta

from priority_engine import (
    calculate_deadline_urgency,
    calculate_importance_score,
    calculate_task_type_score,
    calculate_priority_score,
    get_priority_label,
    generate_priority_recommendation,
)


class TestPriorityEngine(unittest.TestCase):

    def test_deadline_within_24_hours(self):
        now = datetime(2026, 10, 12, 10, 0)
        deadline = now + timedelta(hours=12)

        self.assertEqual(
            calculate_deadline_urgency(deadline, now),
            95
        )

    def test_overdue_pending_deadline(self):
        now = datetime(2026, 10, 12, 10, 0)
        deadline = now - timedelta(hours=2)

        self.assertEqual(
            calculate_deadline_urgency(deadline, now),
            100
        )

    def test_missing_deadline(self):
        now = datetime(2026, 10, 12, 10, 0)

        self.assertIsNone(
            calculate_deadline_urgency(None, now)
        )

    def test_importance_mapping(self):
        self.assertEqual(calculate_importance_score("High"), 100)
        self.assertEqual(calculate_importance_score("Medium"), 60)
        self.assertEqual(calculate_importance_score("Low"), 30)

    def test_importance_is_case_insensitive(self):
        self.assertEqual(calculate_importance_score("  hIgH "), 100)

    def test_unknown_importance(self):
        self.assertIsNone(calculate_importance_score("Critical"))

    def test_task_type_mapping(self):
        self.assertEqual(calculate_task_type_score("Exam"), 100)
        self.assertEqual(calculate_task_type_score("Assignment"), 80)
        self.assertEqual(calculate_task_type_score("Quiz"), 65)
        self.assertEqual(calculate_task_type_score("Project"), 80)

    def test_unknown_task_type(self):
        self.assertIsNone(calculate_task_type_score("Workshop"))

    def test_weighted_priority_score(self):
        self.assertEqual(
            calculate_priority_score(100, 60, 80),
            84.0
        )

    def test_missing_signal_weights_are_normalized(self):
        self.assertEqual(
            calculate_priority_score(100, None, 80),
            94.29
        )

    def test_no_available_signals(self):
        self.assertIsNone(
            calculate_priority_score(None, None, None)
        )

    def test_invalid_score_is_rejected(self):
        self.assertIsNone(
            calculate_priority_score(150, None, None)
        )

    def test_priority_labels(self):
        self.assertEqual(get_priority_label(85), "High")
        self.assertEqual(get_priority_label(60), "Medium")
        self.assertEqual(get_priority_label(25), "Low")
        self.assertEqual(get_priority_label(None), "Unavailable")

    def test_priority_label_boundaries(self):
        self.assertEqual(get_priority_label(39.99), "Low")
        self.assertEqual(get_priority_label(40), "Medium")
        self.assertEqual(get_priority_label(69.99), "Medium")
        self.assertEqual(get_priority_label(70), "High")

    def test_completed_task_has_no_active_recommendation(self):
        task = {
            "task_id": "T3",
            "status": "completed",
            "importance": "High",
            "task_type": "Exam",
        }
        now = datetime(2026, 10, 12, 10, 0)

        result = generate_priority_recommendation(task, now)

        self.assertIsNone(result["priority_score"])
        self.assertEqual(result["priority_label"], "Unavailable")

    def test_task_with_no_scoring_signals(self):
        task = {
            "task_id": "T4",
            "status": "pending",
        }
        now = datetime(2026, 10, 12, 10, 0)

        result = generate_priority_recommendation(task, now)

        self.assertIsNone(result["priority_score"])
        self.assertEqual(result["priority_label"], "Unavailable")


    def test_in_progress_task_with_upcoming_deadline_gets_urgency(self):
        now = datetime(2026, 10, 12, 10, 0)
        task = {
            "task_id": "T5",
            "status": "in_progress",
            "due_datetime": (now + timedelta(hours=12)).isoformat(),
        }

        result = generate_priority_recommendation(task, now)

        self.assertEqual(result["priority_score"], 95.0)
        self.assertIn("deadline urgency score 95", result["priority_reason"])

    def test_in_progress_overdue_task_does_not_get_pending_overdue_score(self):
        now = datetime(2026, 10, 12, 10, 0)
        task = {
            "task_id": "T6",
            "status": "in_progress",
            "due_datetime": (now - timedelta(hours=2)).isoformat(),
        }

        result = generate_priority_recommendation(task, now)

        self.assertIsNone(result["priority_score"])
        self.assertEqual(result["priority_label"], "Unavailable")

    def test_distant_deadline(self):
        now = datetime(2026, 10, 12, 10, 0)
        deadline = now + timedelta(days=10)

        self.assertEqual(
            calculate_deadline_urgency(deadline, now),
            25
        )

    def test_invalid_deadline_does_not_get_urgency(self):
        now = datetime(2026, 10, 12, 10, 0)
        task = {
            "task_id": "T7",
            "status": "pending",
            "due_datetime": "not-a-valid-date",
        }

        result = generate_priority_recommendation(task, now)

        self.assertIsNone(result["priority_score"])
        self.assertEqual(result["priority_label"], "Unavailable")

    def test_recommendation_contains_required_output_fields(self):
        now = datetime(2026, 10, 12, 10, 0)
        task = {
            "task_id": "T8",
            "status": "pending",
            "due_datetime": (now + timedelta(hours=12)).isoformat(),
        }

        result = generate_priority_recommendation(task, now)

        self.assertEqual(
            set(result.keys()),
            {
                "task_id",
                "priority_score",
                "priority_label",
                "priority_reason",
            }
        )
        self.assertEqual(result["task_id"], "T8")
        self.assertIsInstance(result["priority_reason"], str)
        self.assertTrue(result["priority_reason"])


if __name__ == "__main__":
    unittest.main()
