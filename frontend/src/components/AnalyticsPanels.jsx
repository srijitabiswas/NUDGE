import { Link } from "react-router-dom";

function show(value, suffix = "") {
  return value === null || value === undefined ? "Not available" : `${value}${suffix}`;
}

function Metric({ label, value, hint }) {
  return (
    <div className="metric">
      <span className="metric-value">{value}</span>
      <span className="metric-label">{label}</span>
      {hint && <span className="metric-label">{hint}</span>}
    </div>
  );
}

export default function AnalyticsPanels({ analytics, error }) {
  if (error) {
    return (
      <div className="panel">
        <h2>Workload</h2>
        <p className="muted">Could not load analytics.</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="panel">
        <h2>Workload</h2>
        <p className="muted">Loading analytics…</p>
      </div>
    );
  }

  const workload = analytics.workload || {};
  const productivity = analytics.productivity || {};
  const risks = analytics.risks || [];

  const effort =
    workload.known_effort_task_count > 0
      ? `${workload.known_effort_total}`
      : "Not provided";

  return (
    <>
      <div className="panel">
        <h2>Workload</h2>
        <p className="muted small">Your open work right now.</p>
        <div className="metrics">
          <Metric label="Active tasks" value={show(workload.active_task_count)} />
          <Metric label="Overdue" value={show(workload.overdue_task_count)} />
          <Metric label="Due in 7 days" value={show(workload.due_within_7_days_count)} />
          <Metric
            label="Estimated effort"
            value={effort}
            hint={workload.known_effort_task_count > 0 ? "" : "No effort estimates yet"}
          />
        </div>
      </div>

      <div className="panel">
        <h2>Productivity</h2>
        <p className="muted small">Completion rate is completed tasks out of all active and completed tasks, over all time.</p>
        <div className="metrics">
          <Metric label="Completion rate (all time)" value={show(productivity.completion_rate_percent, "%")} />
          <Metric
            label="Total completed"
            value={`${show(productivity.completed_task_count)} of ${show(productivity.total_tasks)}`}
          />
          <Metric label="Completed in the last 7 days" value={show(productivity.completed_within_7_days_count)} />
        </div>
      </div>

      <div className="panel risk-panel">
        <h2>Early risks</h2>
        {risks.length === 0 && <p className="muted">No risks detected.</p>}
        <ul className="risk-list">
          {risks.map((r, i) => (
            <li key={`${r.task_id ?? "overall"}-${i}`} className={`risk-item risk-${r.risk_level}`}>
              <div className="risk-head">
                <strong>{r.task_title || "Untitled"}</strong>
                <span className={`badge risk-pill-${r.risk_level}`}>{r.risk_level}</span>
              </div>
              {(r.risk_reasons || []).map((reason, j) => (
                <p key={j} className="risk-reason">{reason}</p>
              ))}
              {r.task_id !== null && r.task_id !== undefined && (
                <p className="risk-action">
                  Next step: review this task and update its status or date in <Link to="/tasks">My Tasks</Link>.
                </p>
              )}
            </li>
          ))}
        </ul>
        <p className="muted small">These are rule-based signals from deadlines and status, not predictions.</p>
      </div>
    </>
  );
}