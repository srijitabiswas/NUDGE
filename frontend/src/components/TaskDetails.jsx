import { useEffect } from "react";

const STATUS_LABEL = { pending: "Pending", completed: "Completed", in_progress: "In progress" };
const NEXT_LABEL = { pending: "Mark completed", completed: "Mark pending", in_progress: "Mark completed" };

function longDate(str) {
  if (!str) return "No date";
  const [y, m, d] = str.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-IN", {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function Row({ label, children }) {
  return (
    <div className="detail-row">
      <span className="detail-label">{label}</span>
      <span className="detail-value">{children}</span>
    </div>
  );
}

export default function TaskDetails({ task, onClose, onAdvance }) {
  useEffect(() => {
    if (!task) return undefined;
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [task, onClose]);

  if (!task) return null;

  const scored = typeof task.priority_score === "number";

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal"
        role="dialog"
        aria-modal="true"
        aria-label={task.title}
        onClick={(e) => e.stopPropagation()}
      >
        <button className="modal-close" onClick={onClose} aria-label="Close">
          ×
        </button>

        <h2 className="modal-title">{task.title}</h2>
        <p className="muted">{task.description || "No description provided."}</p>

        <div className="detail-grid">
          <Row label="Type">{task.type}</Row>
          <Row label="Subject">{task.subject || "Not detected"}</Row>
          <Row label="Due date">{longDate(task.due_date)}</Row>
          <Row label="Due time">{task.due_time || "Not specified"}</Row>
          <Row label="Source">{task.source}</Row>
          <Row label="Status">{STATUS_LABEL[task.status] || task.status}</Row>
          <Row label="Detection confidence">
            {typeof task.confidence === "number" ? `${Math.round(task.confidence * 100)}%` : "N/A"}
          </Row>
          <Row label="Priority">
            {task.priority_label
              ? `${task.priority_label}${scored ? ` (${Math.round(task.priority_score)}/100)` : ""}`
              : "Not scored yet"}
          </Row>
        </div>

        {task.priority_reason && <p className="note note-reason">Why: {task.priority_reason}</p>}

        {task.change && (
          <p className="note note-change">
            {task.change.type.charAt(0).toUpperCase() + task.change.type.slice(1)} changed:{" "}
            <s>{task.change.old}</s> → <strong>{task.change.new}</strong>
          </p>
        )}

        {task.conflict && (
          <p className="note note-conflict">Possible clash with another task on the same day.</p>
        )}

        <div className="modal-actions">
          <button className="primary-btn" onClick={() => onAdvance(task)}>
            {NEXT_LABEL[task.status] || "Update status"}
          </button>
          <button className="ghost-btn" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}