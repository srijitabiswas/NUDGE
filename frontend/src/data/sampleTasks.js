// TEMPORARY development data. Shapes copy the real contracts:
// tasks  -> nlp/NLP_INTERFACE.md + storage fields (task_id, due_datetime, status)
// priorities -> ml/INTELLIGENCE_INTERFACE.md (score 0-100, label High/Medium/Low/Unavailable)

const p = (n) => String(n).padStart(2, "0");
const day = (offset) => {
  const d = new Date();
  d.setDate(d.getDate() + offset);
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
};

export const sampleTasks = [
  {
    task_id: 1,
    task_title: "Submit DBMS assignment 3",
    description: "ER diagram and normalization up to BCNF.",
    task_type: "assignment",
    subject: "DBMS",
    due_date: day(0),
    due_time: "23:59",
    due_datetime: `${day(0)}T23:59:00`,
    event_datetime: null,
    source: "WhatsApp",
    status: "pending",
    confidence: 0.94,
    change_information: [
      { is_changed: true, change_type: "deadline", old_value: "Wednesday 11:59 PM", new_value: "Today 11:59 PM" },
    ],
  },
  {
    task_id: 2,
    task_title: "Operating Systems mid-sem exam",
    description: "Units 1 to 3. Room 204.",
    task_type: "exam",
    subject: "Operating Systems",
    due_date: null,
    due_time: null,
    due_datetime: `${day(3)}T10:00:00`,
    event_datetime: `${day(3)}T10:00:00`,
    source: "Screenshot/OCR",
    status: "pending",
    confidence: 0.88,
    change_information: [],
  },
  {
    task_id: 3,
    task_title: "Project review presentation",
    description: "Final year project review with guide.",
    task_type: "event",
    subject: null,
    due_date: null,
    due_time: null,
    due_datetime: `${day(3)}T11:00:00`,
    event_datetime: `${day(3)}T11:00:00`,
    source: "Email",
    status: "pending",
    confidence: 0.81,
    change_information: [],
  },
  {
    task_id: 4,
    task_title: "Computer Networks lab record",
    description: "Experiments 5 to 8.",
    task_type: "assignment",
    subject: "Computer Networks",
    due_date: day(-1),
    due_time: "17:00",
    due_datetime: `${day(-1)}T17:00:00`,
    event_datetime: null,
    source: "LMS",
    status: "pending",
    confidence: 0.9,
    change_information: [],
  },
  {
    task_id: 5,
    task_title: "Fill internship eligibility form",
    description: null,
    task_type: "other",
    subject: null,
    due_date: day(6),
    due_time: null,
    due_datetime: null,
    event_datetime: null,
    source: "Email",
    status: "pending",
    confidence: 0.72,
    change_information: [],
  },
  {
    task_id: 6,
    task_title: "AI/ML quiz 2",
    description: "Regression and classification basics.",
    task_type: "quiz",
    subject: "AI/ML",
    due_date: day(8),
    due_time: "14:00",
    due_datetime: `${day(8)}T14:00:00`,
    event_datetime: `${day(8)}T14:00:00`,
    source: "WhatsApp",
    status: "pending",
    confidence: 0.85,
    change_information: [
      { is_changed: true, change_type: "date", old_value: "Friday", new_value: "Next Monday" },
    ],
  },
  {
    task_id: 7,
    task_title: "Submit seminar report",
    description: "Final PDF to the department office.",
    task_type: "assignment",
    subject: null,
    due_date: day(-4),
    due_time: "16:00",
    due_datetime: `${day(-4)}T16:00:00`,
    event_datetime: null,
    source: "Notice",
    status: "completed",
    confidence: 0.92,
    change_information: [],
  },
];

export const samplePriorities = [
  { task_id: 1, priority_score: 91.0, priority_label: "High", priority_reason: "Due within 24 hours; assignment." },
  { task_id: 2, priority_score: 87.5, priority_label: "High", priority_reason: "Exam due in 3 days." },
  { task_id: 3, priority_score: 75.0, priority_label: "High", priority_reason: "Due in 3 days." },
  { task_id: 4, priority_score: 90.0, priority_label: "High", priority_reason: "Overdue and still pending." },
  { task_id: 5, priority_score: null, priority_label: "Unavailable", priority_reason: "No valid deadline or task type signal." },
  { task_id: 6, priority_score: 40.0, priority_label: "Medium", priority_reason: "Due in more than 7 days; quiz." },
  { task_id: 7, priority_score: null, priority_label: "Unavailable", priority_reason: "Task is completed; no active priority recommendation is needed." },
];


// TEMPORARY. Shapes copy ml/intelligence_metrics.py outputs exactly.
// Values are what those functions return for the sample tasks above.
export const sampleAnalytics = {
  workload: {
    active_task_count: 6,
    overdue_task_count: 1,
    due_within_7_days_count: 3,
    known_effort_task_count: 0,
    known_effort_total: null,
    effort_unit: null,
  },
  productivity: {
    total_tasks: 7,
    completed_task_count: 1,
    active_task_count: 6,
    completion_rate_percent: 14.29,
    completed_within_7_days_count: 0,
  },
  risks: [
    {
      task_id: 4,
      task_title: "Computer Networks lab record",
      risk_level: "high",
      risk_reasons: ["Deadline has passed"],
    },
    {
      task_id: 1,
      task_title: "Submit DBMS assignment 3",
      risk_level: "medium",
      risk_reasons: ["Deadline is within 24 hours"],
    },
    {
      task_id: null,
      task_title: "Overall workload",
      risk_level: "medium",
      risk_reasons: ["6 active tasks; review workload"],
    },
  ],
};