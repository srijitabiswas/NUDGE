// The ONLY file that talks to the data source.
import { sampleTasks, samplePriorities, sampleAnalytics } from "../data/sampleTasks";
import { normalizeTasks, normalizeOne } from "./taskAdapter";
import { request, apiConfigured } from "../lib/apiClient";

// Tasks use the real backend (backend/api.py, Rumana) when VITE_API_BASE_URL is set in
// frontend/.env. Without it the app runs on sample data, so it still works with no backend.
// Parsing, priorities and analytics still use stand-ins: those modules are not connected to the API yet.
export const USING_SAMPLE_DATA = !apiConfigured();

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
let nextId = 1000;

// GET /tasks returns a plain list. No priorities come from the API yet, so none are attached.
export async function fetchTasks() {
  if (!USING_SAMPLE_DATA) return normalizeTasks(await request("/tasks"), []);
  await wait(300);
  return normalizeTasks(sampleTasks, samplePriorities);
}

// Returns { workload, productivity, risks } as produced by Sresthita's module.
// Not available from the API yet, so with the real backend this reports "unavailable".
export async function fetchAnalytics() {
  if (!USING_SAMPLE_DATA) throw new Error("Analytics are not connected to the API yet.");
  await wait(400);
  return JSON.parse(JSON.stringify(sampleAnalytics));
}

export async function updateTaskStatus(id, status) {
  if (!USING_SAMPLE_DATA) {
    await request(`/tasks/${id}/status`, { method: "PATCH", body: { status } });
    return { id, status };
  }
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

// Still the stand-in parser: the NLP module is not exposed through the API yet.
export async function parseMessage(raw_text, source) {
  await wait(400);
  return sampleParse(raw_text, source);
}

// Saves the confirmed task and returns it in the shape the UI uses.
export async function createTask(parsed) {
  if (!USING_SAMPLE_DATA) {
    // The storage layer owns task_id, status, created_at, completed_at and due_datetime.
    const created = await request("/tasks", {
      method: "POST",
      body: {
        task_title: parsed.task_title,
        description: parsed.description || null,
        task_type: parsed.task_type || null,
        subject: parsed.subject || null,
        due_date: parsed.due_date || null,
        due_time: parsed.due_time || null,
        event_datetime: parsed.event_datetime || null,
        date_time_expression: parsed.date_time_expression || null,
        source: parsed.source || "Manual",
        raw_text: parsed.raw_text || parsed.task_title,
        confidence: typeof parsed.confidence === "number" ? parsed.confidence : 1,
        change_information: parsed.change_information || [],
      },
    });
    return normalizeOne(created, null);
  }
  await wait(200);
  const raw = {
    task_id: nextId++,
    task_title: parsed.task_title,
    description: parsed.description,
    task_type: parsed.task_type,
    subject: parsed.subject,
    due_date: parsed.due_date,
    due_time: parsed.due_time,
    // No end-of-day time is invented: without a time, due_datetime stays empty.
    due_datetime: parsed.due_date && parsed.due_time ? `${parsed.due_date}T${parsed.due_time}:00` : null,
    event_datetime: parsed.event_datetime,
    source: parsed.source,
    status: "pending",
    confidence: parsed.confidence,
    change_information: parsed.change_information || [],
  };
  return normalizeOne(raw, null);
}


// Edits a task. The API only accepts the title and the date/time (plus importance and
// effort, which the UI does not edit yet), so type, subject and description are read-only there.
// `task` is the current task, needed to know whether the date belongs to an event.
export async function updateTaskFields(id, fields, task) {
  if (!USING_SAMPLE_DATA) {
    const body = { task_title: fields.title };
    if (task?.event_datetime) {
      if (fields.due_date) {
        body.event_datetime = `${fields.due_date}T${fields.due_time || task.due_time || "00:00"}:00`;
      }
    } else {
      body.due_date = fields.due_date || null;
      body.due_time = fields.due_time || null;
    }
    const updated = await request(`/tasks/${id}`, { method: "PATCH", body });
    return normalizeOne(updated, null);
  }
  await wait(150);
  return { id, ...fields };
}

export async function deleteTask(id) {
  if (!USING_SAMPLE_DATA) {
    await request(`/tasks/${id}`, { method: "DELETE" });
    return { id };
  }
  await wait(150);
  return { id };
}