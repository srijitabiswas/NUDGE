import { useState } from "react";
import { Link } from "react-router-dom";
import { parseMessage } from "../services/taskService";

const SOURCES = ["WhatsApp", "Email", "LMS", "Notice", "Manual input", "Other"];
const TYPES = ["assignment", "exam", "quiz", "project", "event", "announcement", "notice", "other"];

export default function AddMessage({ onConfirm, compact = false }) {
  const [text, setText] = useState("");
  const [source, setSource] = useState("WhatsApp");
  const [stage, setStage] = useState("idle"); // idle | parsing | review | saving
  const [draft, setDraft] = useState(null);
  const [error, setError] = useState("");

  async function handleParse() {
    if (!text.trim()) return;
    setError("");
    setStage("parsing");
    try {
      setDraft(await parseMessage(text, source));
      setStage("review");
    } catch (e) {
      setError(e.message || "Could not read this message.");
      setStage("idle");
    }
  }

  async function handleConfirm() {
    setStage("saving");
    try {
      await onConfirm({
        ...draft,
        task_title: draft.task_title.trim() || "Untitled task",
        due_date: draft.due_date || null,
        due_time: draft.due_time || null,
      });
      setText("");
      setDraft(null);
      setStage("idle");
    } catch (e) {
      setError(e.message || "Could not save the task.");
      setStage("review");
    }
  }

  function handleDiscard() {
    setDraft(null);
    setStage("idle");
  }

  function setField(key, value) {
    setDraft((d) => ({ ...d, [key]: value }));
  }

  return (
    <div className={`panel add-box ${compact ? "compact" : ""}`}>
      <h2>{compact ? "Quick add" : "Add a message"}</h2>
      {compact && stage === "idle" && <p className="muted small">Paste a message to turn it into a task.</p>}

      {stage !== "review" && stage !== "saving" && (
        <>
          <textarea
            className="add-text"
            aria-label="Message to turn into a task"
            rows={compact ? 2 : 3}
            placeholder="Paste a message, notice or announcement…"
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <div className="add-row">
            <select aria-label="Message source" value={source} onChange={(e) => setSource(e.target.value)}>
              {SOURCES.map((s) => (
                <option key={s}>{s}</option>
              ))}
            </select>
            <button className="primary-btn" onClick={handleParse} disabled={!text.trim() || stage === "parsing"}>
              {stage === "parsing" ? "Reading…" : "Detect task"}
            </button>
            {!compact && (
              <button className="ghost-btn" disabled title="Needs the OCR module to be connected">
                Upload screenshot (soon)
              </button>
            )}
          </div>
        </>
      )}

      {(stage === "review" || stage === "saving") && draft && (
        <div className="review">
          <p className="muted">
            Check what was detected, fix anything wrong, then confirm.
            {draft.date_time_expression && <> Found: “{draft.date_time_expression}”.</>}{" "}
            Confidence {Math.round((draft.confidence || 0) * 100)}%.
          </p>

          <label>
            Title
            <input value={draft.task_title} onChange={(e) => setField("task_title", e.target.value)} />
          </label>

          <div className="review-grid">
            <label>
              Type
              <select value={draft.task_type} onChange={(e) => setField("task_type", e.target.value)}>
                {TYPES.map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </label>
            <label>
              Due date
              <input type="date" value={draft.due_date || ""} onChange={(e) => setField("due_date", e.target.value)} />
            </label>
            <label>
              Due time
              <input type="time" value={draft.due_time || ""} onChange={(e) => setField("due_time", e.target.value)} />
            </label>
          </div>

          <div className="add-row">
            <button className="primary-btn" onClick={handleConfirm} disabled={stage === "saving"}>
              {stage === "saving" ? "Saving…" : "Confirm task"}
            </button>
            <button className="ghost-btn" onClick={handleDiscard} disabled={stage === "saving"}>
              Discard
            </button>
          </div>
        </div>
      )}

      {error && <p className="add-error" role="alert">{error}</p>}

      {compact && (
        <Link to="/add-information" className="view-all">Open full Add Information →</Link>
      )}
    </div>
  );
}