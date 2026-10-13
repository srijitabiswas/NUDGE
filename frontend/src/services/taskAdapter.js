// Converts the real backend/NLP/ML shapes into the shape the UI uses.
// If a teammate renames a field, this is the only file to change.

function splitDateTime(value) {
  if (!value) return ["", ""];
  const s = String(value);
  return [s.slice(0, 10), s.length >= 16 ? s.slice(11, 16) : ""];
}

function toMinutes(t) {
  if (!t) return null;
  const [h, m] = t.split(":").map(Number);
  return h * 60 + m;
}

export function normalizeOne(task, priority) {
  const [dtDate, dtTime] = splitDateTime(task.event_datetime || task.due_datetime);
  const change = (task.change_information || []).find((c) => c.is_changed);
  const label = priority?.priority_label;

  return {
    id: task.task_id,
    title: task.task_title || "Untitled task",
    description: task.description || "",
    type: task.task_type || "other",
    subject: task.subject || "",
    due_date: task.due_date || dtDate,
    due_time: task.due_time || dtTime,
    source: task.source || "Unknown",
    status: task.status || "pending",
    confidence: task.confidence,
    priority_label: label && label !== "Unavailable" ? label.toLowerCase() : null,
    priority_score: typeof priority?.priority_score === "number" ? priority.priority_score : null,
    priority_reason: priority?.priority_reason || "",
    change: change
      ? { type: change.change_type, old: change.old_value, new: change.new_value }
      : null,
    conflict: false,
  };
}

// Conflict = two active tasks on the same date with times less than 2 hours apart.
export function markConflicts(tasks) {
  return tasks.map((t) => {
    const a = toMinutes(t.due_time);
    const conflict =
      t.status !== "completed" &&
      a !== null &&
      tasks.some((o) => {
        const b = toMinutes(o.due_time);
        return (
          o.id !== t.id &&
          o.status !== "completed" &&
          b !== null &&
          o.due_date === t.due_date &&
          Math.abs(a - b) < 120
        );
      });
    return { ...t, conflict };
  });
}

export function normalizeTasks(tasks, priorities) {
  const byId = new Map((priorities || []).map((p) => [p.task_id, p]));
  return markConflicts(tasks.map((t) => normalizeOne(t, byId.get(t.task_id))));
}