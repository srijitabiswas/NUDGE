function show(value, suffix = "") {
  return value === null || value === undefined ? "N/A" : `${value}${suffix}`;
}

function Metric({ label, value }) {
  return (
    <div className="metric">
      <span className="metric-value">{value}</span>
      <span className="metric-label">{label}</span>
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
        <div className="metrics">
          <Metric label="Active tasks" value={show(workload.active_task_count)} />
          <Metric label="Overdue" value={show(workload.overdue_task_count)} />
          <Metric label="Due in 7 days" value={show(workload.due_within_7_days_count)} />
          <Metric label="Estimated effort" value={effort} />
        </div>
      </div>

      <div className="panel">
        <h2>Productivity</h2>
        <div className="metrics">
          <Metric
            label="Completion rate"
            value={show(productivity.completion_rate_percent, "%")}
          />
          <Metric
            label="Completed (of all)"
            value={`${show(productivity.completed_task_count)} / ${show(productivity.total_tasks)}`}
          />
          <Metric
            label="Done in last 7 days"
            value={show(productivity.completed_within_7_days_count)}
          />
        </div>
      </div>

      <div className="panel">
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
            </li>
          ))}
        </ul>
        <p className="muted small">Rule-based signals, not predictions.</p>
      </div>
    </>
  );
}