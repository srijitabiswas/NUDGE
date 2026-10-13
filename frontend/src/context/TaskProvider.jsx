import { useCallback, useEffect, useMemo, useState } from "react";
import {
  fetchTasks, fetchAnalytics, updateTaskStatus, createTask, updateTaskFields, deleteTask,
} from "../services/taskService";
import { markConflicts } from "../services/taskAdapter";
import { buildAlerts, NEXT_STATUS } from "../utils/taskUtils";
import { useAuth } from "../hooks/useAuth";
import { TaskContext } from "./taskContext";

const readKey = (uid) => `nudge.demo.read.${uid}`;

function loadRead(uid) {
  try {
    return JSON.parse(localStorage.getItem(readKey(uid))) || [];
  } catch {
    return [];
  }
}

function saveRead(uid, ids) {
  try {
    localStorage.setItem(readKey(uid), JSON.stringify(ids));
  } catch {
    /* storage unavailable: read state lasts for this session only */
  }
}

function Inner({ uid, children }) {
  const [tasks, setTasks] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(!!uid);
  const [error, setError] = useState("");
  const [analyticsError, setAnalyticsError] = useState(false);
  const [readIds, setReadIds] = useState(() => (uid ? loadRead(uid) : []));

  useEffect(() => {
    if (!uid) return undefined;
    let cancelled = false;
    fetchTasks()
      .then((t) => !cancelled && setTasks(t))
      .catch(() => !cancelled && setError("Could not load tasks. Please try again."))
      .finally(() => !cancelled && setLoading(false));
    fetchAnalytics()
      .then((a) => !cancelled && setAnalytics(a))
      .catch(() => !cancelled && setAnalyticsError(true));
    return () => {
      cancelled = true;
    };
  }, [uid]);

  const addTask = useCallback(async (parsed) => {
    const created = await createTask(parsed);
    setTasks((prev) => markConflicts([...prev, created]));
    return created;
  }, []);

  // fields: { title, description, type, subject, due_date, due_time }
  const editTask = useCallback(async (id, fields) => {
    await updateTaskFields(id, fields);
    setTasks((prev) => markConflicts(prev.map((t) => (t.id === id ? { ...t, ...fields } : t))));
  }, []);

  const removeTask = useCallback(async (id) => {
    await deleteTask(id);
    setTasks((prev) => markConflicts(prev.filter((t) => t.id !== id)));
  }, []);

  const setStatus = useCallback(async (task, next) => {
    setTasks((prev) => markConflicts(prev.map((t) => (t.id === task.id ? { ...t, status: next } : t))));
    try {
      await updateTaskStatus(task.id, next);
    } catch {
      setTasks((prev) => markConflicts(prev.map((t) => (t.id === task.id ? { ...t, status: task.status } : t))));
      setError("Could not update status.");
    }
  }, []);

  const advanceStatus = useCallback(
    (task) => setStatus(task, NEXT_STATUS[task.status] || "pending"),
    [setStatus]
  );

  const alerts = useMemo(() => buildAlerts(tasks, analytics), [tasks, analytics]);
  const unread = useMemo(() => alerts.filter((a) => !readIds.includes(a.id)).length, [alerts, readIds]);

  const markRead = useCallback(
    (ids) => {
      setReadIds((prev) => {
        const next = Array.from(new Set([...prev, ...ids]));
        if (uid) saveRead(uid, next);
        return next;
      });
    },
    [uid]
  );
  const markAllRead = useCallback(() => markRead(alerts.map((a) => a.id)), [markRead, alerts]);

  const value = useMemo(
    () => ({
      tasks, analytics, loading, error, analyticsError,
      alerts, unread, readIds, markRead, markAllRead,
      addTask, editTask, removeTask, setStatus, advanceStatus,
      dismissError: () => setError(""),
    }),
    [tasks, analytics, loading, error, analyticsError, alerts, unread, readIds, markRead, markAllRead, addTask, editTask, removeTask, setStatus, advanceStatus]
  );

  return <TaskContext.Provider value={value}>{children}</TaskContext.Provider>;
}

// Keyed by user id so one account's data never carries over to the next sign-in.
export default function TaskProvider({ children }) {
  const { user } = useAuth();
  const uid = user?.id || null;
  return (
    <Inner key={uid || "signed-out"} uid={uid}>
      {children}
    </Inner>
  );
}