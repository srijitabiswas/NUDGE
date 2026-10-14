import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useTasks } from "../hooks/useTasks";
import { cap, formatDate, getBucket, todayStr, STATUS_LABEL } from "../utils/taskUtils";
import AddMessage from "../components/AddMessage";
import TaskDetails from "../components/TaskDetails";
import "../App.css";

const MAX_ROWS = 5;

function dueText(task) {
  return `${formatDate(task.due_date)}${task.due_time ? `, ${task.due_time}` : ""}`;
}

function dueValue(t) {
  return t.due_date ? `${t.due_date}T${t.due_time || "23:59"}` : "9999";
}

function Summary({ label, value, tone }) {
  return (
    <div className={`sum tone-${tone}`}>
      <span className="sum-value">{value}</span>
      <span className="sum-label">{label}</span>
    </div>
  );
}

function PriorityBadge({ label }) {
  if (label !== "high" && label !== "medium") return null;
  return <span className={`badge priority-${label}`}>{label}</span>;
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
        <h3>
          <button className="link-btn" onClick={onOpen}>{task.title}</button>
        </h3>
        <p className="drow-meta">
          {cap(task.type)} · {dueText(task)}
          {bucket === "overdue" && <span className="drow-flag"> · Overdue</span>}
          {bucket === "today" && <span className="drow-today"> · Due today</span>}
        </p>
      </div>

      <div className="drow-side">
        <PriorityBadge label={task.priority_label} />
      </div>
    </li>
  );
}

export default function DashboardPage() {
  const { tasks, analytics, loading, error, alerts, addTask, advanceStatus } = useTasks();
  const [selectedId, setSelectedId] = useState(null);

  const today = todayStr();

  const withBucket = useMemo(
    () => tasks.map((t) => ({ task: t, bucket: getBucket(t, today) })),
    [tasks, today]
  );

  const counts = useMemo(() => {
    const c = { today: 0, upcoming: 0, overdue: 0 };
    withBucket.forEach(({ bucket }) => {
      if (bucket === "today") c.today++;
      if (bucket === "upcoming") c.upcoming++;
      if (bucket === "overdue") c.overdue++;
    });
    return c;
  }, [withBucket]);

  // Top recommendation from the existing priority output
  const focus = useMemo(() => {
    const rated = tasks
      .filter((t) => t.status !== "completed" && typeof t.priority_score === "number")
      .sort((a, b) => b.priority_score - a.priority_score);
    if (rated.length === 0) return null;
    const risk = (analytics?.risks || []).find((r) => r.task_id === rated[0].id) || null;
    return { task: rated[0], bucket: getBucket(rated[0], today), risk };
  }, [tasks, analytics, today]);

  // Today's list: overdue + due today (priority first), then a few upcoming
  const { rows, coming } = useMemo(() => {
    const urgent = withBucket
      .filter(({ bucket }) => bucket === "today" || bucket === "overdue")
      .sort((a, b) => (b.task.priority_score || 0) - (a.task.priority_score || 0))
      .slice(0, MAX_ROWS);
    const room = urgent.length === 0 ? 3 : MAX_ROWS - urgent.length;
    const next = withBucket
      .filter(({ bucket }) => bucket === "upcoming")
      .sort((a, b) => dueValue(a.task).localeCompare(dueValue(b.task)))
      .slice(0, Math.max(0, room));
    return { rows: urgent, coming: next };
  }, [withBucket]);

  // Only genuinely urgent alerts, never repeating the focus task
  const urgentAlerts = useMemo(
    () => alerts.filter((a) => a.type === "danger" && a.taskId !== focus?.task.id).slice(0, 2),
    [alerts, focus]
  );

  const attention = counts.today + counts.overdue;
  const dateLabel = new Date().toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" });
  const subtitle =
    attention === 0
      ? "Nothing urgent right now."
      : `${attention} task${attention === 1 ? " needs" : "s need"} your attention today.`;

  return (
    <div className="stack dash">
      <TaskDetails
        task={tasks.find((t) => t.id === selectedId) || null}
        onClose={() => setSelectedId(null)}
        onAdvance={advanceStatus}
      />

      <div className="page-header">
        <h1>Dashboard</h1>
        <p className="dash-sub">
          {dateLabel} · {subtitle}
        </p>
      </div>

      {focus && (
        <section className="focus-hero" aria-labelledby="focus-title">
          <div className="focus-hero-main">
            <p className="eyebrow">Focus next</p>
            <h2 id="focus-title">{focus.task.title}</h2>
            <p className="focus-hero-meta">
              {focus.bucket === "overdue" ? "Overdue · " : focus.bucket === "today" ? "Due today · " : "Due "}
              {dueText(focus.task)} · {cap(focus.task.type)}
              {typeof focus.task.priority_score === "number" && ` · score ${Math.round(focus.task.priority_score)}/100`}
            </p>
            {focus.task.priority_reason && <p className="focus-hero-reason">{focus.task.priority_reason}</p>}
            <div className="focus-hero-tags">
              {focus.task.priority_label && (
                <span className={`badge priority-${focus.task.priority_label}`}>{focus.task.priority_label} priority</span>
              )}
              {focus.risk && <span className={`badge risk-pill-${focus.risk.risk_level}`}>{focus.risk.risk_level} risk</span>}
            </div>
          </div>
          <button className="btn btn-primary" onClick={() => setSelectedId(focus.task.id)}>
            View task
          </button>
        </section>
      )}

      <section className="sum-grid" aria-label="Summary">
        <Summary label="Due today" value={counts.today} tone="warning" />
        <Summary label="Upcoming" value={counts.upcoming} tone="primary" />
        <Summary label="Overdue" value={counts.overdue} tone="danger" />
      </section>

      <div className="dash-grid">
        <section className="panel list-panel dash-tasks" aria-labelledby="today-title">
          <div className="list-head">
            <h2 id="today-title">Today's tasks</h2>
            <Link to="/tasks" className="view-all">View all →</Link>
          </div>

          {error && <div className="state state-error" role="alert">{error}</div>}
          {loading && <div className="state">Loading tasks…</div>}
          {!loading && !error && rows.length === 0 && <div className="state">Nothing due today. You're clear.</div>}

          {rows.length > 0 && (
            <ul className="drow-list">
              {rows.map(({ task, bucket }) => (
                <TaskRow key={task.id} task={task} bucket={bucket} onAdvance={advanceStatus} onOpen={() => setSelectedId(task.id)} />
              ))}
            </ul>
          )}

          {coming.length > 0 && (
            <>
              <h3 className="list-sub">Coming up</h3>
              <ul className="drow-list">
                {coming.map(({ task, bucket }) => (
                  <TaskRow key={task.id} task={task} bucket={bucket} onAdvance={advanceStatus} onOpen={() => setSelectedId(task.id)} />
                ))}
              </ul>
            </>
          )}
        </section>

        <aside className="dash-side">
          {urgentAlerts.length > 0 && (
            <section className="urgent" aria-labelledby="urgent-title">
              <h2 id="urgent-title">Needs attention</h2>
              <ul>
                {urgentAlerts.map((a) => (
                  <li key={a.id}>
                    {tasks.some((t) => t.id === a.taskId) ? (
                      <button className="link-btn" onClick={() => setSelectedId(a.taskId)}>{a.text}</button>
                    ) : (
                      a.text
                    )}
                  </li>
                ))}
              </ul>
              {alerts.length > urgentAlerts.length && (
                <Link to="/notifications" className="view-all">All notifications →</Link>
              )}
            </section>
          )}

          <AddMessage onConfirm={addTask} compact />
        </aside>
      </div>
    </div>
  );
}