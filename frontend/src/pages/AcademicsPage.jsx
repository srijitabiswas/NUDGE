import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTasks } from "../hooks/useTasks";
import { formatDate, getBucket, todayStr } from "../utils/taskUtils";
import { matchSubject, orderedDays, scheduleText, sessionsByDay, todayName } from "../utils/academics";

export default function AcademicsPage() {
  const { user } = useAuth();
  const { tasks, loading } = useTasks();
  const p = user?.profile || {};
  const subjects = useMemo(() => p.subjects || [], [p.subjects]);
  const today = todayStr();
  const todayDay = todayName();

  const grouped = useMemo(() => {
    const bySubject = new Map(subjects.map((s) => [s.id, []]));
    const unassigned = [];
    tasks.forEach((t) => {
      if (t.status === "completed") return;
      const s = matchSubject(t, subjects);
      if (s) bySubject.get(s.id).push(t);
      else unassigned.push(t);
    });
    return { bySubject, unassigned };
  }, [tasks, subjects]);

  const sessions = useMemo(() => sessionsByDay(subjects), [subjects]);
  const days = orderedDays(p.preferences?.weekStart);
  const todayClasses = sessions[todayDay] || [];
  const hasSchedule = subjects.some((s) => s.days?.length);

  if (!p.completed && subjects.length === 0) {
    return (
      <div className="stack">
        <div className="page-header"><h1>Academics</h1></div>
        <div className="empty-state">
          <p>Add your course details and subjects to see your timetable and subject-wise tasks.</p>
          <Link className="btn btn-primary" to="/profile">Complete profile</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="page-header row row-between">
        <div>
          <h1>Academics</h1>
          <p className="muted">
            {[p.course, p.year && `Year ${p.year}`, p.semester && `Semester ${p.semester}`].filter(Boolean).join(" · ") || "Your courses and subjects"}
          </p>
        </div>
        <Link className="btn btn-secondary" to="/profile">Edit subjects</Link>
      </div>

      <section className="card stack" aria-labelledby="ac-today">
        <h2 id="ac-today">Today's classes ({todayDay})</h2>
        {todayClasses.length === 0 ? (
          <p className="muted">No classes scheduled today.</p>
        ) : (
          <ul className="plain-list">
            {todayClasses.map((c) => (
              <li key={c.id}>
                <strong>{c.name}</strong>
                <span className="muted"> · {c.start && c.end ? `${c.start}–${c.end}` : "Time not set"}{c.room ? ` · ${c.room}` : ""}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="card stack" aria-labelledby="ac-week">
        <h2 id="ac-week">Weekly timetable</h2>
        {!hasSchedule ? (
          <p className="muted">No class days set yet. Add days and times to your subjects in Profile.</p>
        ) : (
          <div className="tt-grid">
            {days.map((d) => (
              <div key={d} className={`tt-day${d === todayDay ? " today" : ""}`}>
                <h3>{d}</h3>
                {sessions[d].length === 0 && <p className="muted tt-empty">—</p>}
                {sessions[d].map((c) => (
                  <div key={c.id} className="tt-slot">
                    <strong>{c.name}</strong>
                    <span>{c.start && c.end ? `${c.start}–${c.end}` : "Time not set"}</span>
                    {c.room && <span>{c.room}</span>}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="stack" aria-labelledby="ac-subjects">
        <h2 id="ac-subjects">Subjects</h2>
        {subjects.length === 0 ? (
          <div className="empty-state">
            <p>No subjects yet.</p>
            <Link className="btn btn-primary" to="/profile">Add subjects</Link>
          </div>
        ) : (
          <div className="subj-grid">
            {subjects.map((s) => {
              const open = grouped.bySubject.get(s.id) || [];
              const overdue = open.filter((t) => getBucket(t, today) === "overdue").length;
              const next = open
                .filter((t) => t.due_date && t.due_date >= today)
                .sort((a, b) => a.due_date.localeCompare(b.due_date))[0];
              return (
                <article key={s.id} className="card subj-card">
                  <h3>{s.name}{s.code ? <span className="muted"> · {s.code}</span> : null}</h3>
                  <p className="muted">{scheduleText(s) || "No schedule set"}</p>
                  <dl className="subj-stats">
                    <div><dt>Open tasks</dt><dd>{loading ? "…" : open.length}</dd></div>
                    <div><dt>Overdue</dt><dd className={overdue ? "text-danger" : ""}>{loading ? "…" : overdue}</dd></div>
                  </dl>
                  <p className="subj-next">
                    {next ? <>Next: <strong>{next.title}</strong> ({formatDate(next.due_date)})</> : "No upcoming deadline"}
                  </p>
                </article>
              );
            })}
          </div>
        )}
        {subjects.length > 0 && (
          <p className="muted">
            Tasks are matched to a subject by its name or code appearing in the task's subject or title. {grouped.unassigned.length} open task(s) have no matching subject.
          </p>
        )}
      </section>
    </div>
  );
}