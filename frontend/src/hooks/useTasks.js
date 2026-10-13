import { useContext } from "react";
import { TaskContext } from "../context/taskContext";

export function useTasks() {
  const ctx = useContext(TaskContext);
  if (!ctx) throw new Error("useTasks must be used inside <TaskProvider>");
  return ctx;
}