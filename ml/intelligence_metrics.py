
from datetime import datetime, timedelta


def _parse_datetime(value):
    """Parse an ISO datetime string safely."""
    if not isinstance(value, str) or not value.strip():
        return None

    try:
        return datetime.fromisoformat(value.strip())
    except ValueError:
        return None


def _now(current_time):
    """Use the supplied time or the system's current local time."""
    return current_time if current_time is not None else datetime.now()


def _active(task):
    """Tasks that have not been completed or cancelled."""
    status = str(task.get("status") or "pending").strip().lower()
    return status in ("pending", "in_progress", "in progress")


def calculate_workload(tasks, current_time=None):
    """
    Summarize active tasks and their deadlines.
    Estimated effort is summed only when its value is numeric.
    No effort value or unit is invented.
    """
    now = _now(current_time)
    active_tasks = [t for t in tasks if _active(t)]

    overdue = 0
    due_within_7_days = 0
    effort_values = []

    for task in active_tasks:
        deadline = _parse_datetime(task.get("due_datetime"))

        if deadline is not None:
            try:
                remaining = deadline - now

                if remaining.total_seconds() < 0:
                    overdue += 1
                elif remaining <= timedelta(days=7):
                    due_within_7_days += 1
            except TypeError:
                # Avoid comparing incompatible timezone-aware/naive times.
                pass

        effort = task.get("estimated_effort")

        if isinstance(effort, (int, float)) and not isinstance(effort, bool):
            if effort >= 0:
                effort_values.append(effort)

    return {
        "active_task_count": len(active_tasks),
        "overdue_task_count": overdue,
        "due_within_7_days_count": due_within_7_days,
        "known_effort_task_count": len(effort_values),
        "known_effort_total": sum(effort_values) if effort_values else None,
        "effort_unit": None,
    }


def calculate_productivity(tasks, current_time=None):
    """
    Calculate basic task-completion metrics.
    Completion rate uses tasks with known active/completed status.
    """
    now = _now(current_time)
    completed = 0
    active = 0
    completed_this_week = 0

    for task in tasks:
        status = str(task.get("status") or "pending").strip().lower()

        if status == "completed":
            completed += 1
            completed_at = _parse_datetime(task.get("completed_at"))

            if completed_at is not None:
                try:
                    age = now - completed_at
                    if timedelta(0) <= age <= timedelta(days=7):
                        completed_this_week += 1
                except TypeError:
                    pass
        elif status in ("pending", "in_progress", "in progress"):
            active += 1

    known_status_count = completed + active
    completion_rate = (
        round(completed / known_status_count * 100, 2)
        if known_status_count else None
    )

    return {
        "total_tasks": len(tasks),
        "completed_task_count": completed,
        "active_task_count": active,
        "completion_rate_percent": completion_rate,
        "completed_within_7_days_count": completed_this_week,
    }


def detect_early_risks(tasks, current_time=None):
    """
    Transparent rule-based risk signals, not a trained ML prediction.
    Only active tasks are assessed.
    """
    now = _now(current_time)
    risks = []

    for task in tasks:
        if not _active(task):
            continue

        deadline = _parse_datetime(task.get("due_datetime"))
        reasons = []

        if deadline is not None:
            try:
                remaining = deadline - now

                if remaining.total_seconds() < 0:
                    reasons.append("Deadline has passed")
                elif remaining <= timedelta(hours=24):
                    reasons.append("Deadline is within 24 hours")
            except TypeError:
                reasons.append("Deadline could not be compared safely")

        if reasons:
            risks.append({
                "task_id": task.get("task_id"),
                "task_title": task.get("task_title", ""),
                "risk_level": (
                    "high" if "Deadline has passed" in reasons
                    else "medium"
                ),
                "risk_reasons": reasons,
            })

    active_count = sum(1 for task in tasks if _active(task))

    # Explicit heuristic threshold; not a validated risk threshold.
    if active_count >= 5:
        risks.append({
            "task_id": None,
            "task_title": "Overall workload",
            "risk_level": "medium",
            "risk_reasons": [
                f"{active_count} active tasks; review workload"
            ],
        })

    return risks
