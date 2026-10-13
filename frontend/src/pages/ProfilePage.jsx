import { useState } from "react";
import { Link } from "react-router-dom";
import ProfileForm from "../components/ProfileForm";
import { useAuth } from "../hooks/useAuth";

function Item({ label, value }) {
  return (
    <div>
      <dt className="muted">{label}</dt>
      <dd>{value || "—"}</dd>
    </div>
  );
}

export default function ProfilePage() {
  const { user, updateAccount } = useAuth();
  const p = user?.profile || {};
  const [editing, setEditing] = useState(!p.completed);
  const [saved, setSaved] = useState(false);

  async function save(profile) {
    await updateAccount({ profile: { ...profile, completed: true } });
    setEditing(false);
    setSaved(true);
  }

  return (
    <div className="stack">
      <div className="page-header row row-between">
        <div>
          <h1>Profile</h1>
          <p className="muted">{user?.name} · {user?.email}</p>
        </div>
        {!editing && (
          <button className="btn btn-primary" onClick={() => { setSaved(false); setEditing(true); }}>Edit profile</button>
        )}
      </div>

      {saved && <div className="callout callout-success" role="status">Profile saved.</div>}
      {!p.completed && <div className="callout callout-info">Complete your profile so NUDGE can organise your subjects.</div>}

      {editing ? (
        <ProfileForm
          initial={p}
          submitLabel="Save profile"
          onSubmit={save}
          onCancel={p.completed ? () => setEditing(false) : undefined}
        />
      ) : (
        <>
          <section className="card">
            <h2>Academic details</h2>
            <dl className="profile-grid">
              <Item label="College" value={p.college} />
              <Item label="Department" value={p.department} />
              <Item label="Course" value={p.course} />
              <Item label="Year" value={p.year && `Year ${p.year}`} />
              <Item label="Semester" value={p.semester && `Semester ${p.semester}`} />
              <Item label="Student ID" value={p.studentId} />
            </dl>
          </section>

          <section className="card stack">
            <h2>Subjects and schedule</h2>
            {(p.subjects || []).length === 0 ? (
              <p className="muted">No subjects added.</p>
            ) : (
              <div className="table-wrap">
                <table className="table">
                  <thead>
                    <tr><th>Subject</th><th>Code</th><th>Days</th><th>Time</th><th>Room</th></tr>
                  </thead>
                  <tbody>
                    {p.subjects.map((s) => (
                      <tr key={s.id}>
                        <td>{s.name}</td>
                        <td>{s.code || "—"}</td>
                        <td>{s.days?.length ? s.days.join(", ") : "—"}</td>
                        <td>{s.start && s.end ? `${s.start}–${s.end}` : "—"}</td>
                        <td>{s.room || "—"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <p className="muted">Account name and notification options are in <Link to="/settings">Settings</Link>.</p>
        </>
      )}
    </div>
  );
}