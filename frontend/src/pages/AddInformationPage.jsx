import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Field } from "../components/ui";
import { parseMessage } from "../services/taskService";
import { useAuth } from "../hooks/useAuth";
import { useTasks } from "../hooks/useTasks";
import { cap, formatDate } from "../utils/taskUtils";
import { matchSubject } from "../utils/academics";

const SOURCES = ["WhatsApp", "Email", "LMS", "Notice", "Manual input", "Other"];
const TYPES = ["assignment", "exam", "quiz", "project", "event", "announcement", "notice", "other"];
const STEPS = ["Detect", "Review", "Confirm"];

export default function AddInformationPage() {
  const { user } = useAuth();
  const { tasks, addTask } = useTasks();
  const subjects = useMemo(() => user?.profile?.subjects || [], [user]);

  const [stage, setStage] = useState("detect"); // detect | review | done
  const [text, setText] = useState("");
  const [source, setSource] = useState("WhatsApp");
  const [draft, setDraft] = useState(null);
  const [errors, setErrors] = useState({});
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [saved, setSaved] = useState(null);

  const stepIndex = stage === "detect" ? 0 : stage === "review" ? 1 : 2;
  const setField = (k, v) => setDraft((d) => ({ ...d, [k]: v }));

  async function handleDetect(e) {
    e.preventDefault();
    setMessage("");
    if (!text.trim()) {
      setErrors({ "ai-text": "Paste a message or notice first." });
      document.getElementById("ai-text")?.focus();
      return;
    }
    setErrors({});
    setBusy(true);
    try {
      const parsed = await parseMessage(text, source);
      const match = matchSubject({ title: parsed.task_title, subject: parsed.subject }, subjects);
      setDraft({ ...parsed, subject: parsed.subject || match?.name || "" });
      setStage("review");
    } catch (err) {
      setMessage(err.message || "Could not read this message.");
    } finally {
      setBusy(false);
    }
  }

  const duplicate = useMemo(() => {
    if (!draft) return null;
    const title = draft.task_title.trim().toLowerCase();
    if (!title) return null;
    return tasks.find((t) => t.title.trim().toLowerCase() === title && (t.due_date || "") === (draft.due_date || "")) || null;
  }, [draft, tasks]);

  async function handleConfirm(e) {
    e.preventDefault();
    setMessage("");
    const errs = {};
    if (!draft.task_title.trim()) errs["ai-title"] = "Title is required.";
    if (draft.due_time && !draft.due_date) errs["ai-date"] = "Add a date for this time.";
    setErrors(errs);
    const first = Object.keys(errs)[0];
    if (first) {
      document.getElementById(first)?.focus();
      return;
    }
    setBusy(true);
    try {
      const created = await addTask({
        ...draft,
        task_title: draft.task_title.trim(),
        description: draft.description?.trim() || null,
        subject: draft.subject?.trim() || null,
        due_date: draft.due_date || null,
        due_time: draft.due_time || null,
      });
      setSaved(created);
      setStage("done");
    } catch (err) {
      setMessage(err.message || "Could not save the task.");
    } finally {
      setBusy(false);
    }
  }

  function reset() {
    setText("");
    setDraft(null);
    setErrors({});
    setMessage("");
    setSaved(null);
    setStage("detect");
  }

  const changes = (draft?.change_information || []).filter((c) => c.is_changed);
  const lowConfidence = draft && (draft.confidence || 0) < 0.6;
  const subjectNames = subjects.map((s) => s.name);
  const subjectOptions = draft?.subject && !subjectNames.includes(draft.subject) ? [draft.subject, ...subjectNames] : subjectNames;

  return (
    <div className="stack">
      <div className="page-header">
        <h1>Add Information</h1>
        <p className="muted">Turn a message or notice into a task. You always review before anything is saved.</p>
      </div>

      <ol className="stepper" aria-label="Progress">
        {STEPS.map((s, i) => (
          <li key={s} className={i < stepIndex ? "done" : i === stepIndex ? "current" : ""} aria-current={i === stepIndex ? "step" : undefined}>
            <span className="step-num">{i + 1}</span> {s}
          </li>
        ))}
      </ol>

      {message && <div className="callout callout-danger" role="alert">{message}</div>}

      {stage === "detect" && (
        <form className="card stack" onSubmit={handleDetect} noValidate>
          <Field
            id="ai-text"
            as="textarea"
            rows={6}
            maxLength={5000}
            label="Message or notice"
            hint="Paste text from WhatsApp, email, your LMS or a notice board."
            value={text}
            onChange={(e) => setText(e.target.value)}
            error={errors["ai-text"]}
          />
          <div className="form-grid">
            <Field id="ai-source" as="select" label="Source" value={source} onChange={(e) => setSource(e.target.value)}>
              {SOURCES.map((s) => <option key={s}>{s}</option>)}
            </Field>
          </div>
          <div className="row">
            <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? "Reading…" : "Detect task"}</button>
            <button type="button" className="btn btn-secondary" disabled title="Needs the OCR module to be connected">
              Upload screenshot (needs OCR)
            </button>
          </div>
        </form>
      )}

      {stage === "review" && draft && (
        <form className="card stack" onSubmit={handleConfirm} noValidate>
          <div>
            <h2>Review what was detected</h2>
            <p className="muted">
              Source: {draft.source}
              {draft.date_time_expression ? ` · Found date/time: “${draft.date_time_expression}”` : ""}
              {` · Confidence ${Math.round((draft.confidence || 0) * 100)}%`}
            </p>
          </div>

          {lowConfidence && <div className="callout callout-warning">Low confidence. Check every field carefully.</div>}
          {!draft.due_date && <div className="callout callout-info">No date was detected. You can add one below or save without it.</div>}
          {duplicate && <div className="callout callout-warning">A task with the same title and date already exists ("{duplicate.title}"). Confirming will add another.</div>}
          {changes.length > 0 && (
            <div className="callout callout-info">
              Change detected:{" "}
              {changes.map((c, i) => (
                <span key={i}>{cap(c.change_type)}: <s>{c.old_value}</s> → <strong>{c.new_value}</strong>{i < changes.length - 1 ? "; " : ""}</span>
              ))}
            </div>
          )}

          <div className="form-grid">
            <Field id="ai-title" label="Title" value={draft.task_title} onChange={(e) => setField("task_title", e.target.value)} error={errors["ai-title"]} />
            <Field id="ai-type" as="select" label="Type" value={draft.task_type} onChange={(e) => setField("task_type", e.target.value)}>
              {TYPES.map((t) => <option key={t} value={t}>{cap(t)}</option>)}
            </Field>
            <Field id="ai-subject" as="select" label="Subject" value={draft.subject || ""} onChange={(e) => setField("subject", e.target.value)}>
              <option value="">None</option>
              {subjectOptions.map((s) => <option key={s} value={s}>{s}</option>)}
            </Field>
            <Field id="ai-date" type="date" label="Due date" value={draft.due_date || ""} onChange={(e) => setField("due_date", e.target.value)} error={errors["ai-date"]} />
            <Field id="ai-time" type="time" label="Due time" value={draft.due_time || ""} onChange={(e) => setField("due_time", e.target.value)} />
          </div>
          <Field id="ai-desc" as="textarea" rows={3} label="Description (optional)" value={draft.description || ""} onChange={(e) => setField("description", e.target.value)} />

          <details>
            <summary>Original message</summary>
            <p className="orig-text">{draft.raw_text}</p>
          </details>

          <div className="row">
            <button type="submit" className="btn btn-primary" disabled={busy}>{busy ? "Saving…" : "Confirm and save task"}</button>
            <button type="button" className="btn btn-secondary" onClick={() => { setStage("detect"); setMessage(""); }} disabled={busy}>Back</button>
            <button type="button" className="btn btn-ghost" onClick={reset} disabled={busy}>Discard</button>
          </div>
        </form>
      )}

      {stage === "done" && saved && (
        <section className="card stack" role="status">
          <h2>Task saved</h2>
          <p>
            <strong>{saved.title}</strong>
            {saved.due_date ? ` · due ${formatDate(saved.due_date)}${saved.due_time ? `, ${saved.due_time}` : ""}` : " · no due date"}
          </p>
          <div className="row">
            <Link className="btn btn-primary" to="/tasks">View in My Tasks</Link>
            <button className="btn btn-secondary" onClick={reset}>Add another</button>
          </div>
        </section>
      )}
    </div>
  );
}