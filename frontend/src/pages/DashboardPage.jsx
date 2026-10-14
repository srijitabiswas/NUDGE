import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTasks } from "../hooks/useTasks";
import { useAuth } from "../hooks/useAuth";
import { cap, formatDate, getBucket, todayStr, STATUS_LABEL } from "../utils/taskUtils";
import AddMessage from "../components/AddMessage";
import TaskDetails from "../components/TaskDetails";
import AnalyticsPanels from "../components/AnalyticsPanels";
import Tracker from "../components/Tracker";
import Recommendations from "../components/Recommendations";
import "../App.css";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "today", label: "Today" },
  { key: "upcoming", label: "Upcoming" },
  { key: "overdue", label: "Overdue" },
  { key: "assignment", label: "Assignments" },
  { key: "exam", label: "Exams" },
];

function Stat({ label, value, tone }) {
  return (
    <div className={`stat tone-${tone}`}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function TaskRow({ task, bucket, onAdvance, onOpen }) {
  const label = STATUS_LABEL[task.status] || task.status;
  return (
    <li className={`drow bucket-${bucket}`}>
      <button
        className={`status-btn status-${task.status}`}
        onClick={() => onAdvance(task)}
        aria-label={`Status ${label}. Change status for ${task.title}`}
      >
        {label}
      </button>

      <div className="drow-main">
        <h3 className={task.status === "completed" ? "done-title" : ""}>{task.title}</h3>
        <p className="drow-meta">
          {cap(task.type)} · {formatDate(task.due_date)}
          {task.due_time ? `, ${task.due_time}` : ""} · via {task.source}
          {bucket === "overdue" && <span className="drow-flag"> · Overdue</span>}
        </p>
        {task.change && (
          <p className="drow-note">
            {cap(task.change.type)} changed: <s>{task.change.old}</s> → <strong>{task.change.new}</strong>
          </p>
        )}
        {task.conflict && <p className="drow-note">Possible clash with another event.</p>}
        {task.priority_reason && (
          <p className="drow-note">
            Why: {task.priority_reason}
            {typeof task.priority_score === "number" && ` (score ${Math.round(task.priority_score)}/100)`}
          </p>
        )}
      </div>

      <div className="drow-side">
        <span className={`badge priority-${task.priority_label || "none"}`}>
          {task.priority_label || "unrated"}
        </span>
        <button className="btn btn-secondary btn-sm" onClick={onOpen}>Details</button>
      </div>
    </li>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { tasks, analytics, loading, error, analyticsError, alerts, addTask, advanceStatus } = useTasks();
  const [filter, setFilter] = useState("all");
  const [selectedId, setSelectedId] = useState(null);

  const today = todayStr();

  const withBucket = useMemo(
    () => tasks.map((t) => ({ task: t, bucket: getBucket(t, today) })),
    [tasks, today]
  );

  const counts = useMemo(() => {
    const c = { today: 0, upcoming: 0, overdue: 0, high: 0 };
    withBucket.forEach(({ task, bucket }) => {
      if (bucket === "today") c.today++;
      if (bucket === "upcoming") c.upcoming++;
      if (bucket === "overdue") c.overdue++;
      if (bucket !== "done" && task.priority_label === "high") c.high++;
    });
    return c;
  }, [withBucket]);

  const workload = useMemo(() => {
    const open = withBucket.filter(({ bucket }) => bucket !== "done");
    const byType = {};
    open.forEach(({ task }) => {
      byType[task.type] = (byType[task.type] || 0) + 1;
    });
    return { total: open.length, byType };
  }, [withBucket]);

  const visible = useMemo(() => {
    const list = withBucket.filter(({ task, bucket }) => {
      if (filter === "all") return true;
      if (filter === "assignment" || filter === "exam") return task.type === filter;
      return bucket === filter;
    });
    return list.sort((a, b) => (b.task.priority_score || 0) - (a.task.priority_score || 0));
  }, [withBucket, filter]);

  return (
    <div className="stack">
      <TaskDetails
        task={tasks.find((t) => t.id === selectedId) || null}
        onClose={() => setSelectedId(null)}
        onAdvance={advanceStatus}
      />

      <div className="page-header">
        <h1>Dashboard</h1>
      </div>

      {user && !user.profile?.completed && (
        <div className="callout callout-info">
          Your profile is incomplete. <Link to="/profile">Complete it</Link> so NUDGE can organise your subjects.
        </div>
      )}

      <div className="layout">
        <section className="stats statbar" aria-label="Summary">
          <Stat label="Due today" value={counts.today} tone="warning" />
          <Stat label="Upcoming" value={counts.upcoming} tone="primary" />
          <Stat label="Overdue" value={counts.overdue} tone="danger" />
          <Stat label="High priority" value={counts.high} tone="danger" />
        </section>

        <section className="main-col">
          <AddMessage onConfirm={addTask} />

          <div className="panel list-panel">
            <div className="list-head">
              <h2>Your tasks</h2>
              <div className="filters" role="group" aria-label="Filter tasks">
                {FILTERS.map((f) => (
                  <button
                    key={f.key}
                    className={`filter-btn ${filter === f.key ? "active" : ""}`}
                    aria-pressed={filter === f.key}
                    onClick={() => setFilter(f.key)}
                  >
                    {f.label}
                  </button>
                ))}
              </div>
            </div>

            {error && <div className="state state-error" role="alert">{error}</div>}
            {loading && <div className="state">Loading tasks…</div>}
            {!loading && !error && visible.length === 0 && <div className="state">Nothing here. You're clear.</div>}

            <ul className="drow-list">
              {visible.map(({ task, bucket }) => (
                <TaskRow
                  key={task.id}
                  task={task}
                  bucket={bucket}
                  onAdvance={advanceStatus}
                  onOpen={() => setSelectedId(task.id)}
                />
              ))}
            </ul>
          </div>

          {!loading && !error && <Tracker tasks={tasks} />}
        </section>

        <aside className="side-col">
          <Recommendations tasks={tasks} risks={analytics?.risks} />

          <div className="panel">
            <h2>Alerts</h2>
            {alerts.length === 0 && <p className="muted">No alerts.</p>}
            <ul className="alert-list">
              {alerts.map((a) => (
                <li key={a.id} className={`alert alert-${a.type}`}>
                  {a.text}
                </li>
              ))}
            </ul>
            {alerts.length > 0 && <Link to="/notifications">View all notifications</Link>}
          </div>

          <AnalyticsPanels analytics={analytics} error={analyticsError} />

          <div className="panel">
            <h2>By type</h2>
            <p className="muted">{workload.total} open tasks</p>
            {Object.entries(workload.byType).map(([type, n]) => (
              <div key={type} className="bar-row">
                <span className="bar-label">{type}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(n / workload.total) * 100}%` }} />
                </div>
                <span className="bar-count">{n}</span>
              </div>
            ))}
          </div>
        </aside>
      </div>
    </div>
  );
}