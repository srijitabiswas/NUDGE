import { useState } from "react";
import { Field } from "./ui";
import {
  DAYS, YEARS, SEMESTERS, REMINDER_LEADS, WEEK_STARTS,
  emptySubject, profileToForm, formToProfile, validateProfile,
} from "../utils/profileOptions";

export default function ProfileForm({ initial, submitLabel = "Save", onSubmit, onCancel, extraAction }) {
  const [v, setV] = useState(() => profileToForm(initial));
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");

  const set = (key) => (e) => setV((p) => ({ ...p, [key]: e.target.value }));
  const setSubject = (id, patch) =>
    setV((p) => ({ ...p, subjects: p.subjects.map((s) => (s.id === id ? { ...s, ...patch } : s)) }));
  const toggleDay = (id, day) =>
    setV((p) => ({
      ...p,
      subjects: p.subjects.map((s) =>
        s.id === id
          ? { ...s, days: s.days.includes(day) ? s.days.filter((d) => d !== day) : [...s.days, day] }
          : s
      ),
    }));

  async function handleSubmit(e) {
    e.preventDefault();
    setFormError("");
    const errs = validateProfile(v);
    setErrors(errs);
    const firstId = Object.keys(errs)[0];
    if (firstId) {
      document.getElementById(firstId)?.focus();
      return;
    }
    setSaving(true);
    try {
      await onSubmit(formToProfile(v));
    } catch (err) {
      setFormError(err.message || "Could not save. Try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="stack">
      {formError && <div className="callout callout-danger" role="alert">{formError}</div>}

      <section className="card stack" aria-labelledby="pf-academic">
        <h2 id="pf-academic">Academic details</h2>
        <div className="form-grid">
          <Field id="pf-college" label="College" value={v.college} onChange={set("college")} error={errors["pf-college"]} autoComplete="organization" />
          <Field id="pf-department" label="Department" value={v.department} onChange={set("department")} error={errors["pf-department"]} />
          <Field id="pf-course" label="Course" hint="e.g. B.Tech Computer Science" value={v.course} onChange={set("course")} error={errors["pf-course"]} />
          <Field id="pf-studentId" label="Student ID (optional)" value={v.studentId} onChange={set("studentId")} error={errors["pf-studentId"]} />
          <Field id="pf-year" as="select" label="Year" value={v.year} onChange={set("year")} error={errors["pf-year"]}>
            <option value="">Select year</option>
            {YEARS.map((y) => <option key={y} value={y}>Year {y}</option>)}
          </Field>
          <Field id="pf-semester" as="select" label="Semester" value={v.semester} onChange={set("semester")} error={errors["pf-semester"]}>
            <option value="">Select semester</option>
            {SEMESTERS.map((s) => <option key={s} value={s}>Semester {s}</option>)}
          </Field>
        </div>
      </section>

      <section className="card stack" aria-labelledby="pf-subjects">
        <div className="row row-between">
          <h2 id="pf-subjects">Subjects and weekly schedule</h2>
          <button type="button" className="btn btn-secondary btn-sm" onClick={() => setV((p) => ({ ...p, subjects: [...p.subjects, emptySubject()] }))}>
            + Add subject
          </button>
        </div>
        {v.subjects.length === 0 && <p className="muted">No subjects yet. Add the subjects you study this semester.</p>}
        {v.subjects.map((s, i) => (
          <fieldset key={s.id} className="subject-box">
            <legend>Subject {i + 1}</legend>
            <div className="form-grid">
              <Field id={`pf-sub-${s.id}-name`} label="Name" value={s.name} onChange={(e) => setSubject(s.id, { name: e.target.value })} error={errors[`pf-sub-${s.id}-name`]} />
              <Field id={`pf-sub-${s.id}-code`} label="Code (optional)" value={s.code} onChange={(e) => setSubject(s.id, { code: e.target.value })} />
              <Field id={`pf-sub-${s.id}-start`} type="time" label="Start time" value={s.start} onChange={(e) => setSubject(s.id, { start: e.target.value })} error={errors[`pf-sub-${s.id}-start`]} />
              <Field id={`pf-sub-${s.id}-end`} type="time" label="End time" value={s.end} onChange={(e) => setSubject(s.id, { end: e.target.value })} error={errors[`pf-sub-${s.id}-end`]} />
              <Field id={`pf-sub-${s.id}-room`} label="Room (optional)" value={s.room} onChange={(e) => setSubject(s.id, { room: e.target.value })} />
            </div>
            <div className="day-picker" role="group" aria-label={`Days for subject ${i + 1}`}>
              {DAYS.map((d) => (
                <label key={d} className={"day-chip" + (s.days.includes(d) ? " on" : "")}>
                  <input type="checkbox" checked={s.days.includes(d)} onChange={() => toggleDay(s.id, d)} />
                  {d}
                </label>
              ))}
            </div>
            <button type="button" className="btn btn-ghost btn-sm" onClick={() => setV((p) => ({ ...p, subjects: p.subjects.filter((x) => x.id !== s.id) }))}>
              Remove subject
            </button>
          </fieldset>
        ))}
      </section>

      <section className="card stack" aria-labelledby="pf-prefs">
        <h2 id="pf-prefs">Preferences</h2>
        <div className="form-grid">
          <Field id="pf-reminderLead" as="select" label="Default reminder" value={v.reminderLead} onChange={set("reminderLead")}>
            {REMINDER_LEADS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </Field>
          <Field id="pf-weekStart" as="select" label="Week starts on" value={v.weekStart} onChange={set("weekStart")}>
            {WEEK_STARTS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </Field>
        </div>
      </section>

      <div className="row">
        <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? "Saving…" : submitLabel}</button>
        {onCancel && <button type="button" className="btn btn-secondary" onClick={onCancel}>Cancel</button>}
        {extraAction}
      </div>
    </form>
  );
}