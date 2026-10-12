import { useMemo } from "react";

const EXAM_TYPES = ["exam", "quiz"];
const ASSIGNMENT_TYPES = ["assignment", "project"];

function daysUntil(dateStr) {
  if (!dateStr) return null;
  const [y, m, d] = dateStr.split("-").map(Number);
  const target = new Date(y, m - 1, d);
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  return Math.round((target - today) / 86400000);
}

function countdown(days) {
  if (days === null) return { text: "No deadline", tone: "none" };
  if (days < 0)
    return { text: `${Math.abs(days)} day${Math.abs(days) === 1 ? "" : "s"} overdue`, tone: "danger" };
  if (days === 0) return { text: "Due today", tone: "warning" };
  if (days === 1) return { text: "Tomorrow", tone: "warning" };
  return { text: `In ${days} days`, tone: days <= 3 ? "warning" : "ok" };
}

function formatDate(str) {
  if (!str) return "No date";
  const [y, m, d] = str.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function TrackerColumn({ title, items, completedCount }) {
  return (
    <div className="panel tracker-col">
      <h2>
        {title} <span className="tracker-count">{items.length}</span>
      </h2>

      {items.length === 0 && <p className="muted">Nothing pending.</p>}

      <ul className="tracker-list">
        {items.map(({ task, days }) => {
          const c = countdown(days);
          return (
            <li key={task.id} className="tracker-item">
              <div className="tracker-main">
                <strong>{task.title}</strong>
                <span className="tracker-sub">
                  {task.subject ? `${task.subject} · ` : ""}
                  {formatDate(task.due_date)}
                  {task.due_time ? `, ${task.due_time}` : ""}
                </span>
              </div>
              <div className="tracker-side">
                <span className={`count-pill count-${c.tone}`}>{c.text}</span>
                {task.priority_label && (
                  <span className={`badge priority-${task.priority_label}`}>
                    {task.priority_label}
                  </span>
                )}
              </div>
            </li>
          );
        })}
      </ul>

      {completedCount > 0 && <p className="muted small">{completedCount} completed</p>}
    </div>
  );
}

export default function Tracker({ tasks }) {
  const { exams, assignments, examsDone, assignmentsDone } = useMemo(() => {
    const build = (types) => {
      const mine = tasks.filter((t) => types.includes(t.type));
      const active = mine
        .filter((t) => t.status !== "completed")
        .map((t) => ({ task: t, days: daysUntil(t.due_date) }))
        .sort((a, b) => {
          if (a.days === null) return 1;
          if (b.days === null) return -1;
          return a.days - b.days;
        });
      return { active, done: mine.length - active.length };
    };
    const e = build(EXAM_TYPES);
    const a = build(ASSIGNMENT_TYPES);
    return {
      exams: e.active,
      examsDone: e.done,
      assignments: a.active,
      assignmentsDone: a.done,
    };
  }, [tasks]);

  return (
    <section className="tracker">
      <TrackerColumn title="Exams & quizzes" items={exams} completedCount={examsDone} />
      <TrackerColumn title="Assignments & projects" items={assignments} completedCount={assignmentsDone} />
    </section>
  );
}