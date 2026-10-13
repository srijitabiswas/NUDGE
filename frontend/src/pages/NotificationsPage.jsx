import { useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { useTasks } from "../hooks/useTasks";
import TaskDetails from "../components/TaskDetails";

const KIND = {
  risk: { label: "Deadline risk", tag: "tag-danger" },
  change: { label: "Change", tag: "tag-neutral" },
  clash: { label: "Clash", tag: "tag-warning" },
};

export default function NotificationsPage() {
  const { user } = useAuth();
  const { tasks, alerts, readIds, markRead, markAllRead, advanceStatus, loading, error } = useTasks();
  const [filter, setFilter] = useState("all");
  const [openId, setOpenId] = useState(null);

  const unreadCount = alerts.filter((a) => !readIds.includes(a.id)).length;
  const visible = alerts.filter((a) => (filter === "unread" ? !readIds.includes(a.id) : true));
  const prefs = user?.profile?.notifications || {};
  const allOff = prefs.deadlineReminders === false && prefs.changeAlerts === false && prefs.clashAlerts === false;

  return (
    <div className="stack">
      <TaskDetails
        task={tasks.find((t) => t.id === openId) || null}
        onClose={() => setOpenId(null)}
        onAdvance={advanceStatus}
      />

      <div className="page-header row row-between">
        <div>
          <h1>Notifications</h1>
          <p className="muted">{unreadCount} unread · {alerts.length} total</p>
        </div>
        <div className="row">
          <div className="seg" role="group" aria-label="Filter notifications">
            <button className={filter === "all" ? "on" : ""} aria-pressed={filter === "all"} onClick={() => setFilter("all")}>All</button>
            <button className={filter === "unread" ? "on" : ""} aria-pressed={filter === "unread"} onClick={() => setFilter("unread")}>Unread</button>
          </div>
          <button className="btn btn-secondary btn-sm" onClick={markAllRead} disabled={unreadCount === 0}>Mark all read</button>
        </div>
      </div>

      {error && <div className="callout callout-danger" role="alert">{error}</div>}
      {loading && <div className="empty-state">Loading…</div>}

      {allOff && (
        <div className="callout callout-info">
          All alert types are turned off. Change this in <Link to="/settings">Settings</Link>.
        </div>
      )}

      {!loading && visible.length === 0 && (
        <div className="empty-state">
          {filter === "unread" ? "You're all caught up." : "No notifications."}
        </div>
      )}

      <ul className="nt-list">
        {visible.map((a) => {
          const kind = KIND[a.id.split(":")[0]] || { label: "Alert", tag: "tag-neutral" };
          const unread = !readIds.includes(a.id);
          const task = tasks.find((t) => t.id === a.taskId);
          return (
            <li key={a.id} className={`nt-item${unread ? " unread" : ""}`}>
              <div className="nt-body">
                <div className="row nt-head">
                  {unread && <span className="nt-dot" aria-label="Unread" />}
                  <span className={`tag ${kind.tag}`}>{kind.label}</span>
                  <strong>{a.title}</strong>
                </div>
                <p className="nt-text">{a.text}</p>
              </div>
              <div className="row">
                {task && (
                  <button className="btn btn-secondary btn-sm" onClick={() => { markRead([a.id]); setOpenId(task.id); }}>
                    Open task
                  </button>
                )}
                {unread && (
                  <button className="btn btn-ghost btn-sm" onClick={() => markRead([a.id])}>Mark read</button>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}