import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Field } from "../components/ui";
import { useAuth } from "../hooks/useAuth";
import { DEFAULT_NOTIFICATIONS } from "../utils/profileOptions";
import { validateName } from "../utils/validation";

const NOTIFY_OPTIONS = [
  ["deadlineReminders", "Deadline reminders", "Remind me before tasks are due."],
  ["changeAlerts", "Change alerts", "Tell me when a deadline, date, time or location changes."],
  ["clashAlerts", "Clash alerts", "Warn me when two tasks overlap."],
  ["weeklySummary", "Weekly summary", "Show a weekly summary of my workload."],
];

export default function SettingsPage() {
  const { user, updateAccount, logout } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState(user?.name || "");
  const [nameError, setNameError] = useState("");
  const [notify, setNotify] = useState({ ...DEFAULT_NOTIFICATIONS, ...(user?.profile?.notifications || {}) });
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  async function saveAccount(e) {
    e.preventDefault();
    setMsg(""); setErr("");
    const problem = validateName(name);
    setNameError(problem || "");
    if (problem) { document.getElementById("set-name")?.focus(); return; }
    try {
      await updateAccount({ name: name.trim() });
      setMsg("Account updated.");
    } catch (e2) { setErr(e2.message || "Could not save."); }
  }

  async function saveNotify(e) {
    e.preventDefault();
    setMsg(""); setErr("");
    try {
      await updateAccount({ profile: { notifications: notify } });
      setMsg("Notification settings saved.");
    } catch (e2) { setErr(e2.message || "Could not save."); }
  }

  async function signOut() {
    await logout();
    navigate("/", { replace: true });
  }

  return (
    <div className="stack">
      <div className="page-header">
        <h1>Settings</h1>
        <p className="muted">Manage your account and notifications.</p>
      </div>

      {msg && <div className="callout callout-success" role="status">{msg}</div>}
      {err && <div className="callout callout-danger" role="alert">{err}</div>}

      <form className="card stack" onSubmit={saveAccount} noValidate>
        <h2>Account</h2>
        <div className="form-grid">
          <Field id="set-name" label="Name" value={name} onChange={(e) => setName(e.target.value)} error={nameError} autoComplete="name" />
          <Field id="set-email" label="Email" value={user?.email || ""} readOnly hint="Email can't be changed here." />
        </div>
        <div><button className="btn btn-primary" type="submit">Save account</button></div>
      </form>

      <form className="card stack" onSubmit={saveNotify}>
        <h2>Notifications</h2>
        {NOTIFY_OPTIONS.map(([key, label, hint]) => (
          <label key={key} className="check">
            <input type="checkbox" checked={!!notify[key]} onChange={(e) => setNotify((n) => ({ ...n, [key]: e.target.checked }))} />
            <span><strong>{label}</strong><br /><span className="muted">{hint}</span></span>
          </label>
        ))}
        <div><button className="btn btn-primary" type="submit">Save notifications</button></div>
      </form>

      <section className="card stack">
        <h2>Session</h2>
        <div><button className="btn btn-secondary" onClick={signOut}>Sign out</button></div>
      </section>
    </div>
  );
}