import { useEffect, useMemo, useState } from "react";
import { fetchTasks, fetchAnalytics, updateTaskStatus } from "./services/taskService";
import AnalyticsPanels from "./components/AnalyticsPanels";
import Tracker from "./components/Tracker";
import "./App.css";

const FILTERS = [
  { key: "all", label: "All" },
  { key: "today", label: "Today" },
  { key: "upcoming", label: "Upcoming" },
  { key: "overdue", label: "Overdue" },
  { key: "assignment", label: "Assignments" },
  { key: "exam", label: "Exams" },
];

const STATUS_LABEL = {
  pending: "Pending",
  in_progress: "In progress",
  completed: "Completed",
};

const NEXT_STATUS = {
  pending: "completed",
  completed: "pending",
};

function todayStr() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function formatDate(str) {
  if (!str) return "No date";
  const [y, m, d] = str.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
  });
}

function getBucket(task, today) {
  if (task.status === "completed") return "done";
  if (!task.due_date) return "upcoming";
  if (task.due_date < today) return "overdue";
  if (task.due_date === today) return "today";
  return "upcoming";
}

function StatCard({ label, value, tone }) {
  return (
    <div className={`stat-card tone-${tone}`}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function TaskCard({ task, bucket, onAdvance }) {
  return (
    <article className={`task-card bucket-${bucket}`}>
      <div className="task-top">
        <h3 className={task.status === "completed" ? "done-title" : ""}>
          {task.title}
        </h3>
        <span className={`badge priority-${task.priority_label || "none"}`}>
          {task.priority_label || "unrated"}
        </span>
      </div>

      {task.description && <p className="task-desc">{task.description}</p>}

      <div className="task-meta">
        <span className="chip">{task.type}</span>
        <span>
          {formatDate(task.due_date)}
          {task.due_time ? `, ${task.due_time}` : ""}
        </span>
        <span>via {task.source}</span>
        {bucket === "overdue" && <span className="chip chip-danger">Overdue</span>}
      </div>

      {task.change && (
        <p className="note note-change">
          {task.change.type} changed: <s>{task.change.old}</s> →{" "}
          <strong>{task.change.new}</strong>
        </p>
      )}
      {task.conflict && (
        <p className="note note-conflict">Possible clash with another event.</p>
      )}
      {task.priority_reason && (
        <p className="note note-reason">
          Why: {task.priority_reason}
          {typeof task.priority_score === "number" &&
            ` (score ${Math.round(task.priority_score)}/100)`}
        </p>
      )}

      <button
        className={`status-btn status-${task.status}`}
        onClick={() => onAdvance(task)}
        title="Click to change status"
      >
        {STATUS_LABEL[task.status] || task.status}
      </button>
    </article>
  );
}

export default function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
    const [filter, setFilter] = useState("all");
  const [analytics, setAnalytics] = useState(null);
  const [analyticsError, setAnalyticsError] = useState(false);

  useEffect(() => {
    fetchTasks()
      .then(setTasks)
      .catch(() => setError("Could not load tasks. Please try again."))
            .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetchAnalytics()
      .then(setAnalytics)
      .catch(() => setAnalyticsError(true));
  }, []);

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

  const alerts = useMemo(() => {
    const list = [];
    withBucket.forEach(({ task, bucket }) => {
      if (bucket === "overdue")
        list.push({ type: "danger", text: `Overdue: ${task.title}` });
      if (bucket === "today")
        list.push({ type: "warning", text: `Due today: ${task.title}` });
      if (task.change && bucket !== "done")
        list.push({ type: "info", text: `${task.change.type} changed: ${task.title}` });
      if (task.conflict && bucket !== "done")
        list.push({ type: "warning", text: `Possible clash: ${task.title}` });
    });
    return list;
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
    return list.sort(
      (a, b) =>
        (b.task.priority_score || 0) - (a.task.priority_score || 0)
    );
  }, [withBucket, filter]);

  async function handleAdvance(task) {
    const next = NEXT_STATUS[task.status] || "pending";
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, status: next } : t))
    );
    try {
      await updateTaskStatus(task.id, next);
    } catch {
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: task.status } : t))
      );
      setError("Could not update status.");
    }
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>NUDGE</h1>
          <p>From messages to actions</p>
        </div>
        <span className="dev-banner">Sample data</span>
      </header>

      <main className="layout">
        <section className="stats">
          <StatCard label="Due today" value={counts.today} tone="warning" />
          <StatCard label="Upcoming" value={counts.upcoming} tone="primary" />
          <StatCard label="Overdue" value={counts.overdue} tone="danger" />
          <StatCard label="High priority" value={counts.high} tone="danger" />
        </section>

        <section className="main-col">
          {!loading && !error && <Tracker tasks={tasks} />}

          <div className="filters">
            {FILTERS.map((f) => (
              <button
                key={f.key}
                className={`filter-btn ${filter === f.key ? "active" : ""}`}
                onClick={() => setFilter(f.key)}
              >
                {f.label}
              </button>
            ))}
          </div>

          {error && <div className="state state-error">{error}</div>}
          {loading && <div className="state">Loading tasks…</div>}
          {!loading && !error && visible.length === 0 && (
            <div className="state">Nothing here. You're clear.</div>
          )}

          <div className="task-list">
            {visible.map(({ task, bucket }) => (
              <TaskCard
                key={task.id}
                task={task}
                bucket={bucket}
                onAdvance={handleAdvance}
              />
            ))}
          </div>
        </section>

        <aside className="side-col">
          <div className="panel">
            <h2>Alerts</h2>
            {alerts.length === 0 && <p className="muted">No alerts.</p>}
            <ul className="alert-list">
              {alerts.map((a, i) => (
                <li key={i} className={`alert alert-${a.type}`}>
                  {a.text}
                </li>
              ))}
            </ul>
          </div>

          <AnalyticsPanels analytics={analytics} error={analyticsError} />

          <div className="panel">
            <h2>By type</h2>
            <p className="muted">{workload.total} open tasks</p>
            {Object.entries(workload.byType).map(([type, n]) => (
              <div key={type} className="bar-row">
                <span className="bar-label">{type}</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ width: `${(n / workload.total) * 100}%` }}
                  />
                </div>
                <span className="bar-count">{n}</span>
              </div>
            ))}
          </div>
        </aside>
      </main>
    </div>
  );
}