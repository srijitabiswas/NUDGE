import { DAYS } from "./profileOptions";

const JS_DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export function todayName() {
  return JS_DAYS[new Date().getDay()];
}

export function orderedDays(weekStart) {
  return weekStart === "sun" ? ["Sun", ...DAYS.slice(0, 6)] : DAYS;
}

// Matches a task to a subject by subject field or title containing the subject name/code.
export function matchSubject(task, subjects) {
  const hay = `${task.subject || ""} ${task.title}`.toLowerCase();
  return (
    subjects.find((s) => {
      const name = s.name.trim().toLowerCase();
      const code = (s.code || "").trim().toLowerCase();
      return (name && hay.includes(name)) || (code.length >= 2 && hay.includes(code));
    }) || null
  );
}

export function sessionsByDay(subjects) {
  const map = {};
  DAYS.forEach((d) => (map[d] = []));
  subjects.forEach((s) => {
    (s.days || []).forEach((d) => {
      map[d].push({ id: s.id, name: s.name, start: s.start, end: s.end, room: s.room });
    });
  });
  DAYS.forEach((d) => map[d].sort((a, b) => (a.start || "99").localeCompare(b.start || "99")));
  return map;
}

export function scheduleText(s) {
  const days = s.days?.length ? s.days.join(", ") : "";
  const time = s.start && s.end ? `${s.start}–${s.end}` : "";
  return [days, time, s.room].filter(Boolean).join(" · ");
}