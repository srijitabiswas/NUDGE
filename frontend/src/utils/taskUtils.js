export function cap(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1) : "";
}

export function todayStr() {
  const d = new Date();
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

export function formatDate(str) {
  if (!str) return "No date";
  const [y, m, d] = str.split("-").map(Number);
  return new Date(y, m - 1, d).toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

export const STATUS_LABEL = {
  pending: "Pending",
  in_progress: "In progress",
  completed: "Completed",
};

export const NEXT_STATUS = {
  pending: "completed",
  in_progress: "completed",
  completed: "pending",
};

// "done" | "overdue" | "today" | "upcoming"
export function getBucket(task, today = todayStr()) {
  if (task.status === "completed") return "done";
  if (!task.due_date) return "upcoming";
  if (task.due_date < today) return "overdue";
  if (task.due_date === today) return "today";
  return "upcoming";
}

// Alerts with stable ids so the Notifications page can track read state.
export function buildAlerts(tasks, analytics) {
  const list = [];
  (analytics?.risks || []).forEach((r) => {
    list.push({
      id: `risk:${r.task_id}`,
      type: r.risk_level === "high" ? "danger" : "warning",
      title: r.task_title,
      text: `${r.task_title}: ${(r.risk_reasons || []).join("; ")}`,
      taskId: r.task_id,
    });
  });
  tasks.forEach((t) => {
    if (t.status === "completed") return;
    if (t.change) {
      list.push({
        id: `change:${t.id}`,
        type: "info",
        title: t.title,
        text: `${cap(t.change.type)} changed: ${t.title}`,
        taskId: t.id,
      });
    }
    if (t.conflict) {
      list.push({
        id: `clash:${t.id}`,
        type: "warning",
        title: t.title,
        text: `Possible clash: ${t.title}`,
        taskId: t.id,
      });
    }
  });
  return list;
}