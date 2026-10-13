import { useEffect, useState } from "react";
import { Field } from "./ui";

const TYPES = ["assignment", "exam", "quiz", "project", "event", "task", "other"];

export default function TaskForm({ initial, onSubmit, onCancel }) {
  const editing = !!initial;
  const [v, setV] = useState({
    title: initial?.title || "",
    description: initial?.description || "",
    type: initial?.type || "assignment",
    subject: initial?.subject || "",
    due_date: initial?.due_date || "",
    due_time: initial?.due_time || "",
  });
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");

  useEffect(() => {
    document.getElementById("tf-title")?.focus();
  }, []);

  const set = (k) => (e) => setV((p) => ({ ...p, [k]: e.target.value }));

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError("");
    const errs = {};
    if (!v.title.trim()) errs["tf-title"] = "Title is required.";
    else if (v.title.trim().length > 120) errs["tf-title"] = "Keep the title under 120 characters.";
    if (v.due_time && !v.due_date) errs["tf-date"] = "Add a date for this time.";
    setErrors(errs);
    const first = Object.keys(errs)[0];
    if (first) {
      document.getElementById(first)?.focus();
      return;
    }
    setSaving(true);
    try {
      await onSubmit({
        title: v.title.trim(),
        description: v.description.trim(),
        type: v.type,
        subject: v.subject.trim(),
        due_date: v.due_date,
        due_time: v.due_time,
      });
    } catch (err) {
      setFormError(err.message || "Could not save the task.");
      setSaving(false);
    }
  }

  return (
    <form className="card stack" onSubmit={handleSubmit} noValidate aria-label={editing ? "Edit task" : "Add task"}>
      <h2>{editing ? "Edit task" : "Add task"}</h2>
      {formError && <div className="callout callout-danger" role="alert">{formError}</div>}
      <div className="form-grid">
        <Field id="tf-title" label="Title" value={v.title} onChange={set("title")} error={errors["tf-title"]} />
        <Field id="tf-type" as="select" label="Type" value={v.type} onChange={set("type")}>
          {TYPES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
        </Field>
        <Field id="tf-subject" label="Subject (optional)" value={v.subject} onChange={set("subject")} />
        <Field id="tf-date" type="date" label="Due date" value={v.due_date} onChange={set("due_date")} error={errors["tf-date"]} />
        <Field id="tf-time" type="time" label="Due time (optional)" value={v.due_time} onChange={set("due_time")} />
      </div>
      <Field id="tf-desc" as="textarea" rows={3} label="Description (optional)" value={v.description} onChange={set("description")} />
      <div className="row">
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Saving…" : editing ? "Save changes" : "Add task"}
        </button>
        <button type="button" className="btn btn-secondary" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}