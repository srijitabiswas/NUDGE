
"""
NUDGE Priority Engine

Calculates explainable priority recommendations from structured task records.
This initial implementation will use rule-based scoring, not trained machine learning.
"""

from datetime import datetime

def parse_datetime(value):
    """
    Convert an ISO 8601 datetime string into a datetime object.

    Return None if the value is missing, invalid, or not a string.
    """

    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(value.strip())
    except ValueError:
        return None



def calculate_deadline_urgency(due_datetime, current_time):
    """
    Return a deadline urgency score from 0 to 100.

    Return None if the deadline is missing or invalid.
    """

    if due_datetime is None or current_time is None:
        return None

    if not isinstance(due_datetime, datetime):
        return None

    if not isinstance(current_time, datetime):
        return None

    # Both timestamps must either include time zones or omit them.
    if (due_datetime.utcoffset() is None) != (
        current_time.utcoffset() is None
    ):
        return None

    time_remaining = due_datetime - current_time

    if time_remaining.total_seconds() < 0:
        return 100

    hours_remaining = time_remaining.total_seconds() / 3600

    if hours_remaining <= 24:
        return 95
    elif hours_remaining <= 72:
        return 75
    elif hours_remaining <= 168:
        return 50
    else:
        return 25


def calculate_importance_score(importance):
    """
    Convert an explicitly provided importance value into a score.

    Return None when the value is missing or unrecognized.
    """

    if not isinstance(importance, str):
        return None

    importance = importance.strip().lower()

    importance_scores = {
        "high": 100,
        "medium": 60,
        "low": 30,
    }

    return importance_scores.get(importance)


def calculate_task_type_score(task_type):
    """
    Convert an explicitly provided task type into a score.

    Return None when the value is missing or unrecognized.
    """

    if not isinstance(task_type, str):
        return None

    task_type = task_type.strip().lower()

    task_type_scores = {
        "exam": 100,
        "assignment": 80,
        "quiz": 65,
        "project": 80,
    }

    return task_type_scores.get(task_type)


def calculate_priority_score(deadline_score, importance_score, task_type_score):
    """
    Combine available signals into a priority score from 0 to 100.

    Missing signals are excluded, and the remaining weights are
    adjusted proportionally. Return None if no signals are available.
    """

    weighted_signals = [
        (deadline_score, 0.50),
        (importance_score, 0.30),
        (task_type_score, 0.20),
    ]

    available_signals = [
        (score, weight)
        for score, weight in weighted_signals
        if isinstance(score, (int, float))
        and not isinstance(score, bool)
        and 0 <= score <= 100
    ]

    if not available_signals:
        return None

    total_weight = sum(weight for _, weight in available_signals)

    priority_score = sum(
        score * weight for score, weight in available_signals
    ) / total_weight

    return round(priority_score, 2)


def get_priority_label(priority_score):
    """
    Convert a priority score into a priority label.

    Return Unavailable when no valid score exists.
    """

    if (
        not isinstance(priority_score, (int, float))
        or isinstance(priority_score, bool)
        or not 0 <= priority_score <= 100
    ):
        return "Unavailable"

    if priority_score >= 70:
        return "High"
    elif priority_score >= 40:
        return "Medium"
    else:
        return "Low"


def generate_priority_recommendation(task, current_time):
    """
    Generate an explainable priority recommendation for one task.

    Expects a task dictionary following the NUDGE shared data contract.
    """

    if not isinstance(task, dict):
        raise TypeError("task must be a dictionary")

    task_id = task.get("task_id")
    status = task.get("status")

    # Completed tasks should not receive active recommendations.
    if isinstance(status, str) and status.strip().lower() == "completed":
        return {
            "task_id": task_id,
            "priority_score": None,
            "priority_label": "Unavailable",
            "priority_reason": "Task is completed; no active priority recommendation is needed.",
        }


    # Calculate deadline urgency for active tasks.
    # Overdue urgency is assigned only to pending tasks.
    deadline_score = None
    normalized_status = (
        status.strip().lower() if isinstance(status, str) else ""
    )

    if normalized_status in ("pending", "in_progress"):
        due_datetime = parse_datetime(task.get("due_datetime"))

        if normalized_status == "pending":
            deadline_score = calculate_deadline_urgency(
                due_datetime,
                current_time,
            )
        elif due_datetime is not None and current_time is not None:
            deadline_score = calculate_deadline_urgency(
                due_datetime,
                current_time,
            )
            if deadline_score == 100:
                deadline_score = None


    importance_score = calculate_importance_score(task.get("importance"))
    task_type_score = calculate_task_type_score(task.get("task_type"))

    priority_score = calculate_priority_score(
        deadline_score,
        importance_score,
        task_type_score,
    )

    priority_label = get_priority_label(priority_score)

    # Explain which available signals contributed to the score.
    reasons = []

    if deadline_score is not None:
        reasons.append(f"deadline urgency score {deadline_score}")

    if importance_score is not None:
        reasons.append(f"importance score {importance_score}")

    if task_type_score is not None:
        reasons.append(f"task-type score {task_type_score}")

    if priority_score is None:
        priority_reason = (
            "Priority is unavailable because no valid scoring signals "
            "were available."
        )
    else:
        priority_reason = (
            f"Priority is {priority_label.lower()} (score {priority_score}), "
            f"based on {', '.join(reasons)}."
        )

    return {
        "task_id": task_id,
        "priority_score": priority_score,
        "priority_label": priority_label,
        "priority_reason": priority_reason,
    }
