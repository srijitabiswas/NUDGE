import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTasks } from "../hooks/useTasks";
import { useAuth } from "../hooks/useAuth";
import { USING_SAMPLE_DATA } from "../services/taskService";
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

function StatCard({ label, value, tone }) {
  return (
    <div className={`stat-card tone-${tone}`}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
    </div>
  );
}

function TaskCard({ task, bucket, onAdvance, onOpen }) {
  return (
    <article className={`task-card bucket-${bucket}`}>
      <div className="task-top">
        <h3 className={task.status === "completed" ? "done-title" : ""}>{task.title}</h3>
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
          {cap(task.change.type)} changed: <s>{task.change.old}</s> → <strong>{task.change.new}</strong>
        </p>
      )}
      {task.conflict && <p className="note note-conflict">Possible clash with another event.</p>}
      {task.priority_reason && (
        <p className="note note-reason">
          Why: {task.priority_reason}
          {typeof task.priority_score === "number" && ` (score ${Math.round(task.priority_score)}/100)`}
        </p>
      )}

      <div className="card-actions">
        <button className={`status-btn status-${task.status}`} onClick={() => onAdvance(task)} title="Click to change status">
          {STATUS_LABEL[task.status] || task.status}
        </button>
        <button className="status-btn" onClick={onOpen}>
          Details
        </button>
      </div>
    </article>
  );
}

export default function DashboardPage() {
  const { user } = useAuth();
  const { tasks, analytics, loading, error, analyticsError, alerts, addTask, advanceStatus } = useTasks();
  const [filter, setFilter] = useState("all");
  const [selectedId, setSelectedId] = useState(null);

  const today = todayStr();
  const firstName = (user?.name || "").split(" ")[0];

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

      <div className="page-header row row-between">
        <div>
          <h1>{firstName ? `Welcome back, ${firstName}` : "Dashboard"}</h1>
          <p className="muted">Here is what needs your attention.</p>
        </div>
        {USING_SAMPLE_DATA && <span className="dev-banner">Sample data</span>}
      </div>

      {user && !user.profile?.completed && (
        <div className="callout callout-info">
          Your profile is incomplete. <Link to="/profile">Complete it</Link> so NUDGE can organise your subjects.
        </div>
      )}

      <div className="layout">
        <section className="stats">
          <StatCard label="Due today" value={counts.today} tone="warning" />
          <StatCard label="Upcoming" value={counts.upcoming} tone="primary" />
          <StatCard label="Overdue" value={counts.overdue} tone="danger" />
          <StatCard label="High priority" value={counts.high} tone="danger" />
        </section>

        <section className="main-col">
          <AddMessage onConfirm={addTask} />

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

          {error && <div className="state state-error" role="alert">{error}</div>}
          {loading && <div className="state">Loading tasks…</div>}
          {!loading && !error && visible.length === 0 && <div className="state">Nothing here. You're clear.</div>}

          <div className="task-list">
            {visible.map(({ task, bucket }) => (
              <TaskCard
                key={task.id}
                task={task}
                bucket={bucket}
                onAdvance={advanceStatus}
                onOpen={() => setSelectedId(task.id)}
              />
            ))}
          </div>
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