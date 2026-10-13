// The ONLY file that talks to the data source.
import { sampleTasks, samplePriorities, sampleAnalytics } from "../data/sampleTasks";
import { normalizeTasks, normalizeOne } from "./taskAdapter";

// Set to false once the real API exists and the functions below are implemented.
export const USING_SAMPLE_DATA = true;

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
function notConnected() {
  throw new Error("Real API is not connected yet.");
}
let nextId = 1000;

export async function fetchTasks() {
  if (!USING_SAMPLE_DATA) notConnected();
  await wait(300);
  return normalizeTasks(sampleTasks, samplePriorities);
}

// Returns { workload, productivity, risks } as produced by Sresthita's module.
export async function fetchAnalytics() {
  if (!USING_SAMPLE_DATA) notConnected();
  await wait(400);
  return JSON.parse(JSON.stringify(sampleAnalytics));
}

export async function updateTaskStatus(id, status) {
  if (!USING_SAMPLE_DATA) notConnected();
  await wait(100);
  return { id, status };
}

// ---- Message -> structured task -------------------------------------------
// Output shape follows nlp/NLP_INTERFACE.md. The sample version below is a
// TEMPORARY stand-in for Prakriti's parser, only for testing the UI flow.

const MONTHS = [
  "january", "february", "march", "april", "may", "june",
  "july", "august", "september", "october", "november", "december",
];
const pad = (n) => String(n).padStart(2, "0");
const fmt = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

function sampleParse(raw_text, source) {
  const text = raw_text.trim();
  const lower = text.toLowerCase();

  let task_type = "other";
  if (/\b(exam|viva|mid-?sem|end-?sem)\b/.test(lower)) task_type = "exam";
  else if (/\bquiz\b/.test(lower)) task_type = "quiz";
  else if (/\b(assignment|submit|submission|report)\b/.test(lower)) task_type = "assignment";
  else if (/\bproject\b/.test(lower)) task_type = "project";
  else if (/\b(meeting|event|workshop)\b/.test(lower)) task_type = "event";

  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  let due_date = null;
  let expr = null;

  if (/\btomorrow\b/.test(lower)) {
    due_date = fmt(new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1));
    expr = "tomorrow";
  } else if (/\btoday\b/.test(lower)) {
    due_date = fmt(today);
    expr = "today";
  } else {
    const m = lower.match(new RegExp(`(\\d{1,2})(?:st|nd|rd|th)?\\s+(${MONTHS.join("|")})`));
    if (m) {
      const month = MONTHS.indexOf(m[2]);
      let candidate = new Date(today.getFullYear(), month, Number(m[1]));
      if (candidate < today) candidate = new Date(today.getFullYear() + 1, month, Number(m[1]));
      due_date = fmt(candidate);
      expr = m[0];
    }
  }

  let due_time = null;
  const t = lower.match(/(\d{1,2})(?::(\d{2}))?\s*(am|pm)/);
  if (t) {
    const hour = (Number(t[1]) % 12) + (t[3] === "pm" ? 12 : 0);
    due_time = `${pad(hour)}:${t[2] || "00"}`;
    expr = expr ? `${expr} ${t[0]}` : t[0];
  }

  return {
    task_title: text.split(/[.\n]/)[0].slice(0, 80) || "Untitled task",
    description: null,
    task_type,
    subject: null,
    due_date,
    due_time,
    event_datetime: null,
    source,
    raw_text,
    date_time_expression: expr,
    confidence: 0.5,
    change_information: [],
  };
}

export async function parseMessage(raw_text, source) {
  if (!USING_SAMPLE_DATA) notConnected();
  await wait(400);
  return sampleParse(raw_text, source);
}

// Saves the confirmed task and returns it in the shape the UI uses.
export async function createTask(parsed) {
  if (!USING_SAMPLE_DATA) notConnected();
  await wait(200);
  const raw = {
    task_id: nextId++,
    task_title: parsed.task_title,
    description: parsed.description,
    task_type: parsed.task_type,
    subject: parsed.subject,
    due_date: parsed.due_date,
    due_time: parsed.due_time,
    due_datetime: parsed.due_date
      ? `${parsed.due_date}T${parsed.due_time || "23:59"}:00`
      : null,
    event_datetime: parsed.event_datetime,
    source: parsed.source,
    status: "pending",
    confidence: parsed.confidence,
    change_information: parsed.change_information || [],
  };
  return normalizeOne(raw, null);
}