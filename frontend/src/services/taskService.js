// The ONLY file that talks to the data source.
// Later we replace the bodies of these functions with real API calls.
import { sampleTasks, samplePriorities, sampleAnalytics } from "../data/sampleTasks";
import { normalizeTasks } from "./taskAdapter";

export async function fetchTasks() {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return normalizeTasks(sampleTasks, samplePriorities);
}

// Returns { workload, productivity, risks } as produced by Sresthita's module.
export async function fetchAnalytics() {
  await new Promise((resolve) => setTimeout(resolve, 400));
  return JSON.parse(JSON.stringify(sampleAnalytics));
}

export async function updateTaskStatus(id, status) {
  await new Promise((resolve) => setTimeout(resolve, 100));
  return { id, status };
}