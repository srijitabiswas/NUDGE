import { useMemo } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTasks } from "../hooks/useTasks";
import AnalyticsPanels from "../components/AnalyticsPanels";
import BarList from "../components/BarList";
import { cap, getBucket, todayStr } from "../utils/taskUtils";
import { addDays, dateKey, dayName } from "../utils/calendar";
import { matchSubject } from "../utils/academics";

function countBy(list, keyFn, order) {
  const map = {};
  list.forEach((t) => {
    const k = keyFn(t);
    map[k] = (map[k] || 0) + 1;
  });
  const keys = order || Object.keys(map).sort((a, b) => map[b] - map[a]);
  return keys.map((k) => ({ label: k, value: map[k] || 0 }));
}

export default function AnalyticsPage() {
  const { user } = useAuth();
  const { tasks, analytics, analyticsError, loading, error } = useTasks();
  const subjects = useMemo(() => user?.profile?.subjects || [], [user]);
  const today = todayStr();

  const data = useMemo(() => {
    const open = tasks.filter((t) => t.status !== "completed");
    const overdue = open.filter((t) => getBucket(t, today) === "overdue").length;

    const status = [
      { label: "Pending", value: tasks.filter((t) => t.status === "pending").length },
      { label: "In progress", value: tasks.filter((t) => t.status === "in_progress").length },
      { label: "Completed", value: tasks.filter((t) => t.status === "completed").length, tone: "ok" },
      { label: "Overdue (open)", value: overdue, tone: "danger" },
    ];

    const type = countBy(open, (t) => cap(t.type));

    const prio = [
      { label: "High", value: open.filter((t) => t.priority_label === "high").length, tone: "danger" },
      { label: "Medium", value: open.filter((t) => t.priority_label === "medium").length, tone: "warn" },
      { label: "Low", value: open.filter((t) => t.priority_label === "low").length },
      { label: "Unrated", value: open.filter((t) => !t.priority_label).length },
    ];

    const subject = countBy(open, (t) => matchSubject(t, subjects)?.name || "No subject");

    const start = new Date();
    const week = Array.from({ length: 7 }, (_, i) => {
      const d = addDays(start, i);
      const key = dateKey(d);
      return {
        label: i === 0 ? "Today" : `${dayName(d)} ${d.getDate()}`,
        value: open.filter((t) => t.due_date === key).length,
      };
    });
    const weekMax = Math.max(1, ...week.map((w) => w.value));

    return { open: open.length, overdue, status, type, prio, subject, week, weekMax };
  }, [tasks, subjects, today]);
    const noSubject = data.subject.find((s) => s.label === "No subject")?.value || 0;

  return (
    <div className="stack">
      <div className="page-header row row-between">
        <div>
          <h1>Analytics</h1>
          <p className="muted">Your workload and progress at a glance.</p>
        </div>
      </div>

      {error && <div className="callout callout-danger" role="alert">{error}</div>}
      {loading && <div className="empty-state">Loading…</div>}

      {!loading && tasks.length === 0 && (
        <div className="empty-state">
          <p>No tasks yet, so there is nothing to analyse.</p>
          <Link className="btn btn-primary" to="/add-information">Add information</Link>
        </div>
      )}

      {tasks.length > 0 && (
        <>
          <section className="card stack" aria-labelledby="an-week">
            <h2 id="an-week">Open deadlines, next 7 days</h2>
            <div className="an-cols" role="img" aria-label={data.week.map((w) => `${w.label}: ${w.value}`).join(", ")}>
              {data.week.map((w) => (
                <div key={w.label} className="an-col">
                  <span className="an-col-value">{w.value}</span>
                  <span className="an-col-bar" style={{ height: `${(w.value / data.weekMax) * 100}%` }} />
                  <span className="an-col-label">{w.label}</span>
                </div>
              ))}
            </div>
            <p className="muted">{data.open} open task(s), {data.overdue} overdue.</p>
          </section>

          <div className="grid-2">
            <section className="card stack" aria-labelledby="an-status">
              <h2 id="an-status">By status</h2>
                            <p className="muted small">Where every task stands in your workflow.</p>
              <BarList items={data.status} />
            </section>
            <section className="card stack" aria-labelledby="an-prio">
              <h2 id="an-prio">Open tasks by priority</h2>
              <BarList items={data.prio} />
            </section>
            <section className="card stack" aria-labelledby="an-type">
              <h2 id="an-type">Open tasks by type</h2>
              <BarList items={data.type} />
            </section>
                        <section className="card stack" aria-labelledby="an-subject">
              <h2 id="an-subject">Open tasks by subject</h2>
              <BarList items={data.subject} />
              {noSubject > 0 && (
                <p className="hint-box">
                  {noSubject} open task{noSubject === 1 ? " has" : "s have"} no subject.{" "}
                  {subjects.length === 0 ? (
                    <>Add your subjects in <Link to="/profile">Profile</Link> so tasks group automatically.</>
                  ) : (
                    <>Set a subject when editing them in <Link to="/tasks">My Tasks</Link>.</>
                  )}
                </p>
              )}
            </section>
          </div>
        </>
      )}

      <section className="stack" aria-labelledby="an-module">
        <h2 id="an-module">Workload, productivity and early risks</h2>
        <p className="muted">From the analytics module. Charts above are computed in the browser from your tasks.</p>
        <div className="an-panels">
          <AnalyticsPanels analytics={analytics} error={analyticsError} />
        </div>
      </section>
    </div>
  );
}