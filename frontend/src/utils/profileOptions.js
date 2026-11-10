export const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
export const YEARS = ["1", "2", "3", "4", "5"];
export const SEMESTERS = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"];
export const REMINDER_LEADS = [
  { value: "1h", label: "1 hour before" },
  { value: "1d", label: "1 day before" },
  { value: "2d", label: "2 days before" },
  { value: "1w", label: "1 week before" },
];
export const WEEK_STARTS = [
  { value: "mon", label: "Monday" },
  { value: "sun", label: "Sunday" },
];

export const DEFAULT_NOTIFICATIONS = {
  deadlineReminders: true,
  changeAlerts: true,
  clashAlerts: true,
  weeklySummary: false,
};

export function newSubjectId() {
  return "s_" + Math.random().toString(36).slice(2, 9);
}

export function emptySubject() {
  return { id: newSubjectId(), name: "", code: "", days: [], start: "", end: "", room: "" };
}

export function profileToForm(profile = {}) {
  return {
    college: profile.college || "",
    department: profile.department || "",
    course: profile.course || "",
    year: profile.year || "",
    semester: profile.semester || "",
    studentId: profile.studentId || "",
    subjects: (profile.subjects || []).map((s) => ({ ...emptySubject(), ...s })),
    reminderLead: profile.preferences?.reminderLead || "1d",
    weekStart: profile.preferences?.weekStart || "mon",
  };
}

export function formToProfile(v) {
  return {
    college: v.college.trim(),
    department: v.department.trim(),
    course: v.course.trim(),
    year: v.year,
    semester: v.semester,
    studentId: v.studentId.trim(),
    subjects: v.subjects.map((s) => ({
      id: s.id,
      name: s.name.trim(),
      code: s.code.trim(),
      days: s.days,
      start: s.start,
      end: s.end,
      room: s.room.trim(),
    })),
    preferences: { reminderLead: v.reminderLead, weekStart: v.weekStart },
  };
}

// Returns { errors: {fieldId: message}, order: [fieldId...] }
export function validateProfile(v) {
  const errors = {};
  const need = (key, label) => {
    if (!String(v[key]).trim()) errors["pf-" + key] = `${label} is required.`;
  };
  need("college", "College");
  need("department", "Department");
  need("course", "Course");
  need("year", "Year");
  need("semester", "Semester");
  if (v.studentId.trim() && !/^[A-Za-z0-9\-/]{3,30}$/.test(v.studentId.trim())) {
    errors["pf-studentId"] = "Use 3–30 letters, numbers, - or /.";
  }
  v.subjects.forEach((s) => {
    if (!s.name.trim()) errors[`pf-sub-${s.id}-name`] = "Subject name is required.";
    if ((s.start && !s.end) || (!s.start && s.end)) {
      errors[`pf-sub-${s.id}-start`] = "Enter both start and end time.";
    } else if (s.start && s.end && s.end <= s.start) {
      errors[`pf-sub-${s.id}-end`] = "End time must be after start time.";
    }
  });
  return errors;
}