// The ONLY file that talks to the data source.
// Later we replace the bodies of these functions with real API calls.
import { sampleTasks, samplePriorities } from "../data/sampleTasks";
import { normalizeTasks } from "./taskAdapter";

export async function fetchTasks() {
  await new Promise((resolve) => setTimeout(resolve, 300));
  return normalizeTasks(sampleTasks, samplePriorities);
}

export async function updateTaskStatus(id, status) {
  await new Promise((resolve) => setTimeout(resolve, 100));
  return { id, status };
}