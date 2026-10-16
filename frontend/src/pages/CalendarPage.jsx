import { useMemo, useState } from "react";
import { useAuth } from "../hooks/useAuth";
import { useTasks } from "../hooks/useTasks";
import TaskDetails from "../components/TaskDetails";
import { sessionsByDay } from "../utils/academics";
import { STATUS_LABEL, getBucket, todayStr } from "../utils/taskUtils";
import {
  addDays, dateKey, dayName, longDate, monthGrid, monthLabel,
  parseKey, startOfWeek, weekLabel, weekdayHeaders,
} from "../utils/calendar";

export default function CalendarPage() {
  const { user } = useAuth();
  const { tasks, loading, error, advanceStatus } = useTasks();
  const weekStart = user?.profile?.preferences?.weekStart || "mon";
  const subjects = useMemo(() => user?.profile?.subjects || [], [user]);

  const [view, setView] = useState("month");
  const [cursor, setCursor] = useState(() => new Date());
  const [selected, setSelected] = useState(todayStr());
  const [openId, setOpenId] = useState(null);

  const today = todayStr();
  const sessions = useMemo(() => sessionsByDay(subjects), [subjects]);

  const tasksByDate = useMemo(() => {
    const map = {};
    tasks.forEach((t) => {
      if (!t.due_date) return;
      (map[t.due_date] ||= []).push(t);
    });
    Object.values(map).forEach((l) => l.sort((a, b) => (a.due_time || "99").localeCompare(b.due_time || "99")));
    return map;
  }, [tasks]);

  const classesOn = (date) => sessions[dayName(date)] || [];

  function move(dir) {
    setCursor((c) => (view === "month" ? new Date(c.getFullYear(), c.getMonth() + dir, 1) : addDays(c, 7 * dir)));
  }
  function goToday() {
    setCursor(new Date());
    setSelected(todayStr());
  }

  const weeks = useMemo(() => monthGrid(cursor.getFullYear(), cursor.getMonth(), weekStart), [cursor, weekStart]);
  const weekDays = useMemo(() => {
    const s = startOfWeek(cursor, weekStart);
    return Array.from({ length: 7 }, (_, i) => addDays(s, i));
  }, [cursor, weekStart]);

  const heading = view === "month" ? monthLabel(cursor) : weekLabel(weekDays[0]);
  const selectedDate = parseKey(selected);
  const selTasks = tasksByDate[selected] || [];
  const selClasses = classesOn(selectedDate);

  const chipClass = (t) => {
    const b = getBucket(t, today);
    return `cal-chip ${b === "done" ? "done" : b === "overdue" ? "overdue" : t.priority_label === "high" ? "high" : ""}`;
  };

  return (
    <div className="stack">
      <TaskDetails
        task={tasks.find((t) => t.id === openId) || null}
        onClose={() => setOpenId(null)}
        onAdvance={advanceStatus}
      />

      <div className="page-header">
        <h1>Calendar</h1>
        <p className="muted">Deadlines and classes in one place.</p>
      </div>

      {error && <div className="callout callout-danger" role="alert">{error}</div>}

      <div className="cal-toolbar">
        <div className="row">
          <button className="btn btn-secondary btn-sm" onClick={() => move(-1)} aria-label={`Previous ${view}`}>‹</button>
          <button className="btn btn-secondary btn-sm" onClick={goToday}>Today</button>
          <button className="btn btn-secondary btn-sm" onClick={() => move(1)} aria-label={`Next ${view}`}>›</button>
        </div>
        <h2 className="cal-heading" aria-live="polite">{heading}</h2>
        <div className="seg" role="group" aria-label="Calendar view">
          <button className={view === "month" ? "on" : ""} aria-pressed={view === "month"} onClick={() => setView("month")}>Month</button>
          <button className={view === "week" ? "on" : ""} aria-pressed={view === "week"} onClick={() => setView("week")}>Week</button>
        </div>
      </div>

      {loading && <div className="empty-state">Loading…</div>}

            {view === "month" && (
        <div className="cal-grid" role="grid" aria-label={heading}>
          {weekdayHeaders(weekStart).map((n) => (
            <div key={n} className="cal-head" role="columnheader">{n}</div>
          ))}
          {weeks.flat().map((d) => {
            const key = dateKey(d);
            const list = tasksByDate[key] || [];
            const cls = classesOn(d);
            const outside = d.getMonth() !== cursor.getMonth();
            return (
              <div
                key={key}
                role="gridcell"
                tabIndex={0}
                className={`cal-cell${outside ? " other" : ""}${key === today ? " today" : ""}${key === selected ? " selected" : ""}`}
                onClick={() => setSelected(key)}
                onKeyDown={(e) => {
                  if ((e.key === "Enter" || e.key === " ") && e.target === e.currentTarget) {
                    e.preventDefault();
                    setSelected(key);
                  }
                }}
                aria-selected={key === selected}
                aria-label={`${longDate(d)}: ${list.length} task${list.length === 1 ? "" : "s"}, ${cls.length} class${cls.length === 1 ? "" : "es"}`}
              >
                <span className="cal-num">{d.getDate()}</span>
                {list.slice(0, 2).map((t) => (
                  <button
                    key={t.id}
                    type="button"
                    className={chipClass(t)}
                    title={t.title}
                    onClick={(e) => {
                      e.stopPropagation();
                      setOpenId(t.id);
                    }}
                  >
                    {t.title}
                  </button>
                ))}
                {list.length > 2 && (
                  <button
                    type="button"
                    className="cal-more"
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelected(key);
                      setTimeout(() => document.getElementById("cal-sel")?.scrollIntoView({ behavior: "smooth", block: "start" }), 0);
                    }}
                  >
                    +{list.length - 2} more · view all
                  </button>
                )}
                {cls.length > 0 && <span className="cal-classes">{cls.length} class{cls.length === 1 ? "" : "es"}</span>}
                {(list.length > 0 || cls.length > 0) && (
                  <span className="cal-count">{list.length + cls.length} item{list.length + cls.length === 1 ? "" : "s"}</span>
                )}
              </div>
            );
          })}
        </div>
      )}

      {view === "week" && (
        <div className="cal-week">
          {weekDays.map((d) => {
            const key = dateKey(d);
            const list = tasksByDate[key] || [];
            const cls = classesOn(d);
            return (
              <section key={key} className={`cal-wday${key === today ? " today" : ""}${key === selected ? " selected" : ""}`}>
                <button className="cal-wdate" onClick={() => setSelected(key)} aria-pressed={key === selected}>
                  {dayName(d)} {d.getDate()}
                </button>
                {cls.map((c) => (
                  <div key={c.id} className="cal-class">
                    <strong>{c.name}</strong>
                    <span>{c.start && c.end ? `${c.start}–${c.end}` : "Time not set"}</span>
                  </div>
                ))}
                {list.map((t) => (
                  <button key={t.id} className={chipClass(t)} onClick={() => setOpenId(t.id)} title={t.title}>
                    {t.due_time ? `${t.due_time} ` : ""}{t.title}
                  </button>
                ))}
                {list.length === 0 && cls.length === 0 && <span className="muted">Free</span>}
              </section>
            );
          })}
        </div>
      )}

      <section className="card stack" aria-labelledby="cal-sel">
        <h2 id="cal-sel">{longDate(selectedDate)}</h2>

        <div>
          <h3>Classes</h3>
          {selClasses.length === 0 ? (
            <p className="muted">No classes.</p>
          ) : (
            <ul className="plain-list">
              {selClasses.map((c) => (
                <li key={c.id}>
                  <strong>{c.name}</strong>
                  <span className="muted"> · {c.start && c.end ? `${c.start}–${c.end}` : "Time not set"}{c.room ? ` · ${c.room}` : ""}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h3>Tasks due</h3>
          {selTasks.length === 0 ? (
            <p className="muted">No tasks due.</p>
          ) : (
            <ul className="plain-list">
              {selTasks.map((t) => (
                <li key={t.id} className="row row-between">
                  <span>
                    <strong className={t.status === "completed" ? "done-title" : ""}>
                      <button type="button" className="link-btn" onClick={() => setOpenId(t.id)}>{t.title}</button>
                    </strong>
                    <span className="muted"> · {t.due_time || "No time"} · {STATUS_LABEL[t.status] || t.status}{t.conflict ? " · Possible clash" : ""}</span>
                  </span>
                  <span className="row">
                    <button className="btn btn-secondary btn-sm" onClick={() => setOpenId(t.id)}>Details</button>
                    <button className="btn btn-secondary btn-sm" onClick={() => advanceStatus(t)}>
                      {t.status === "completed" ? "Reopen" : "Mark done"}
                    </button>
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}