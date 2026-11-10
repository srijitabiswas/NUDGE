const pad = (n) => String(n).padStart(2, "0");
const NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

export const dateKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

export function parseKey(k) {
  const [y, m, d] = k.split("-").map(Number);
  return new Date(y, m - 1, d);
}

export const addDays = (d, n) => new Date(d.getFullYear(), d.getMonth(), d.getDate() + n);
export const dayName = (d) => NAMES[d.getDay()];

export function startOfWeek(d, weekStart) {
  const first = weekStart === "sun" ? 0 : 1;
  return addDays(d, -((d.getDay() - first + 7) % 7));
}

export function weekdayHeaders(weekStart) {
  return weekStart === "sun" ? NAMES : [...NAMES.slice(1), NAMES[0]];
}

export function monthGrid(year, month, weekStart) {
  const last = new Date(year, month + 1, 0);
  let cur = startOfWeek(new Date(year, month, 1), weekStart);
  const weeks = [];
  do {
    weeks.push(Array.from({ length: 7 }, (_, i) => addDays(cur, i)));
    cur = addDays(cur, 7);
  } while (cur <= last);
  return weeks;
}

export function monthLabel(d) {
  return d.toLocaleDateString("en-IN", { month: "long", year: "numeric" });
}

export function weekLabel(start) {
  const end = addDays(start, 6);
  const f = (d) => d.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
  return `${f(start)} – ${f(end)} ${end.getFullYear()}`;
}

export function longDate(d) {
  return d.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
}