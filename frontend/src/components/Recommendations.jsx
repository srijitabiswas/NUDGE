import { useMemo } from "react";

function formatDate(str) {
  if (!str) return "No date";
  const [y, m, d] = str.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export default function Recommendations({ tasks, risks }) {
  const { picks, unrated } = useMemo(() => {
    const riskById = new Map(
      (risks || [])
        .filter((r) => r.task_id !== null && r.task_id !== undefined)
        .map((r) => [r.task_id, r])
    );
    const active = tasks.filter((t) => t.status !== "completed");
    const rated = active
      .filter((t) => typeof t.priority_score === "number")
      .sort((a, b) => b.priority_score - a.priority_score)
      .slice(0, 3)
      .map((t) => ({ task: t, risk: riskById.get(t.id) || null }));
    return {
      picks: rated,
      unrated: active.filter((t) => typeof t.priority_score !== "number").length,
    };
  }, [tasks, risks]);

  return (
    <div className="panel">
      <h2>Focus next</h2>

      {picks.length === 0 && <p className="muted">Nothing to focus on right now.</p>}

      <ol className="focus-list">
        {picks.map(({ task, risk }, i) => (
          <li key={task.id} className="focus-item">
            <span className="focus-num">{i + 1}</span>
            <div className="focus-body">
              <strong>{task.title}</strong>
              <span className="focus-sub">
                {formatDate(task.due_date)}
                {task.due_time ? `, ${task.due_time}` : ""} · score {Math.round(task.priority_score)}/100
              </span>
              {task.priority_reason && <span className="focus-sub">{task.priority_reason}</span>}
              {risk && (
                <span className={`badge risk-pill-${risk.risk_level}`}>
                  {risk.risk_level} risk
                </span>
              )}
            </div>
          </li>
        ))}
      </ol>

      {unrated > 0 && (
        <p className="muted small">
          {unrated} task{unrated === 1 ? " has" : "s have"} no priority yet (missing deadline or type).
        </p>
      )}
    </div>
  );
}