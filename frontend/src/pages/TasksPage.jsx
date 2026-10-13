import { useMemo, useState } from "react";
import { useTasks } from "../hooks/useTasks";
import { USING_SAMPLE_DATA } from "../services/taskService";
import TaskDetails from "../components/TaskDetails";
import TaskForm from "../components/TaskForm";
import { cap, formatDate, getBucket, todayStr, STATUS_LABEL } from "../utils/taskUtils";

const SORTS = [
  { key: "priority", label: "Priority (high first)" },
  { key: "due", label: "Due date (soonest)" },
  { key: "title", label: "Title (A–Z)" },
];

function dueValue(t) {
  return t.due_date ? `${t.due_date}T${t.due_time || "23:59"}` : "9999";
}

export default function TasksPage() {
  const { tasks, loading, error, addTask, editTask, removeTask, setStatus, advanceStatus } = useTasks();
  const [search, setSearch] = useState("");
  const [status, setStatusFilter] = useState("all");
  const [type, setType] = useState("all");
  const [priority, setPriority] = useState("all");
  const [sort, setSort] = useState("priority");
  const [form, setForm] = useState(null); // null | { task: Task|null }
  const [selectedId, setSelectedId] = useState(null);
  const [confirmId, setConfirmId] = useState(null);
  const [actionError, setActionError] = useState("");

  const today = todayStr();
  const types = useMemo(() => Array.from(new Set(tasks.map((t) => t.type))).sort(), [tasks]);

  const visible = useMemo(() => {
    const q = search.trim().toLowerCase();
    const list = tasks.filter((t) => {
      if (q && !`${t.title} ${t.description} ${t.subject}`.toLowerCase().includes(q)) return false;
      if (status === "overdue") {
        if (getBucket(t, today) !== "overdue") return false;
      } else if (status !== "all" && t.status !== status) return false;
      if (type !== "all" && t.type !== type) return false;
      if (priority === "unrated") {
        if (t.priority_label) return false;
      } else if (priority !== "all" && t.priority_label !== priority) return false;
      return true;
    });
    return list.sort((a, b) => {
      if (sort === "title") return a.title.localeCompare(b.title);
      if (sort === "due") return dueValue(a).localeCompare(dueValue(b));
      return (b.priority_score || 0) - (a.priority_score || 0);
    });
  }, [tasks, search, status, type, priority, sort, today]);

  const filtersActive = search || status !== "all" || type !== "all" || priority !== "all";

  function clearFilters() {
    setSearch("");
    setStatusFilter("all");
    setType("all");
    setPriority("all");
  }

  async function handleSubmit(fields) {
    if (form.task) {
      await editTask(form.task.id, fields);
    } else {
      await addTask({
        task_title: fields.title,
        description: fields.description || null,
        task_type: fields.type,
        subject: fields.subject || null,
        due_date: fields.due_date || null,
        due_time: fields.due_time || null,
        event_datetime: null,
        source: "Manual",
        confidence: 1,
        change_information: [],
      });
    }
    setForm(null);
  }

  async function handleDelete(id) {
    setActionError("");
    try {
      await removeTask(id);
      setConfirmId(null);
      if (selectedId === id) setSelectedId(null);
    } catch (e) {
      setActionError(e.message || "Could not delete the task.");
    }
  }

  return (
    <div className="stack">
      <TaskDetails
        task={tasks.find((t) => t.id === selectedId) || null}
        onClose={() => setSelectedId(null)}
        onAdvance={advanceStatus}
      />

      <div className="page-header row row-between">
        <div>
          <h1>My Tasks</h1>
          <p className="muted">
            {tasks.length} total{USING_SAMPLE_DATA ? " · sample data" : ""}
          </p>
        </div>
        {!form && (
          <button className="btn btn-primary" onClick={() => setForm({ task: null })}>+ Add task</button>
        )}
      </div>

      {form && (
        <TaskForm
          key={form.task ? form.task.id : "new"}
          initial={form.task}
          onSubmit={handleSubmit}
          onCancel={() => setForm(null)}
        />
      )}

      <section className="card stack" aria-label="Search and filters">
        <div className="form-grid">
          <div className="field">
            <label htmlFor="tk-search">Search</label>
            <input id="tk-search" className="input" type="search" placeholder="Title, description or subject" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
          <div className="field">
            <label htmlFor="tk-status">Status</label>
            <select id="tk-status" className="input" value={status} onChange={(e) => setStatusFilter(e.target.value)}>
              <option value="all">All</option>
              <option value="pending">Pending</option>
              <option value="in_progress">In progress</option>
              <option value="completed">Completed</option>
              <option value="overdue">Overdue</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="tk-type">Type</label>
            <select id="tk-type" className="input" value={type} onChange={(e) => setType(e.target.value)}>
              <option value="all">All</option>
              {types.map((t) => <option key={t} value={t}>{cap(t)}</option>)}
            </select>
          </div>
          <div className="field">
            <label htmlFor="tk-priority">Priority</label>
            <select id="tk-priority" className="input" value={priority} onChange={(e) => setPriority(e.target.value)}>
              <option value="all">All</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
              <option value="unrated">Unrated</option>
            </select>
          </div>
          <div className="field">
            <label htmlFor="tk-sort">Sort by</label>
            <select id="tk-sort" className="input" value={sort} onChange={(e) => setSort(e.target.value)}>
              {SORTS.map((s) => <option key={s.key} value={s.key}>{s.label}</option>)}
            </select>
          </div>
        </div>
        <div className="row row-between">
          <span className="muted" role="status">Showing {visible.length} of {tasks.length}</span>
          {filtersActive && <button className="btn btn-ghost btn-sm" onClick={clearFilters}>Clear filters</button>}
        </div>
      </section>

      {(error || actionError) && <div className="callout callout-danger" role="alert">{error || actionError}</div>}
      {loading && <div className="empty-state">Loading tasks…</div>}
      {!loading && !error && tasks.length === 0 && (
        <div className="empty-state">No tasks yet. Add one here or use Add Information.</div>
      )}
      {!loading && tasks.length > 0 && visible.length === 0 && (
        <div className="empty-state">No tasks match your filters.</div>
      )}

      <ul className="tk-list">
        {visible.map((t) => {
          const bucket = getBucket(t, today);
          return (
            <li key={t.id} className={`tk-item bucket-${bucket}`}>
              <div className="tk-main">
                <div className="row tk-title-row">
                  <h3 className={t.status === "completed" ? "done-title" : ""}>{t.title}</h3>
                  <span className="tag tag-neutral">{cap(t.type)}</span>
                  {t.priority_label && <span className={`tag tag-${t.priority_label}`}>{cap(t.priority_label)}</span>}
                  {bucket === "overdue" && <span className="tag tag-danger">Overdue</span>}
                  {t.conflict && <span className="tag tag-warning">Clash</span>}
                </div>
                <p className="muted tk-meta">
                  {formatDate(t.due_date)}{t.due_time ? `, ${t.due_time}` : ""}
                  {t.subject ? ` · ${t.subject}` : ""} · via {t.source}
                </p>
                {t.description && <p className="tk-desc">{t.description}</p>}
              </div>

              <div className="tk-actions">
                <label className="sr-only" htmlFor={`st-${t.id}`}>Status for {t.title}</label>
                <select id={`st-${t.id}`} className="input" value={t.status} onChange={(e) => setStatus(t, e.target.value)}>
                  {Object.entries(STATUS_LABEL).map(([k, label]) => <option key={k} value={k}>{label}</option>)}
                </select>
                <button className="btn btn-secondary btn-sm" onClick={() => setSelectedId(t.id)}>Details</button>
                <button className="btn btn-secondary btn-sm" onClick={() => { setForm({ task: t }); window.scrollTo({ top: 0, behavior: "smooth" }); }}>Edit</button>
                {confirmId === t.id ? (
                  <span className="row">
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(t.id)}>Confirm delete</button>
                    <button className="btn btn-ghost btn-sm" onClick={() => setConfirmId(null)}>Cancel</button>
                  </span>
                ) : (
                  <button className="btn btn-ghost btn-sm" onClick={() => setConfirmId(t.id)} aria-label={`Delete ${t.title}`}>Delete</button>
                )}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}