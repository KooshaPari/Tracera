import type { TaskSpec, TaskSpecCreate, TaskSpecUpdate, TaskStatus } from './types';

import {
  API_URL,
  appendParam,
  getAuthHeaders,
  getBulkHeaders,
  getJsonAuthHeaders,
  readJson,
} from './constants';

async function fetchTaskSpecs(
  projectId: string,
  options?: {
    status?: TaskStatus;
    storyId?: string;
    limit?: number;
    offset?: number;
  },
): Promise<{ specs: TaskSpec[]; total: number }> {
  const params = new URLSearchParams();
  appendParam(params, 'status', options?.status);
  appendParam(params, 'story_id', options?.storyId);
  appendParam(params, 'limit', options?.limit);
  appendParam(params, 'offset', options?.offset);

  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks?${params}`, {
    headers: getBulkHeaders(),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch task specs: ${res.status} ${errorText}`);
  }
  return readJson<{ specs: TaskSpec[]; total: number }>(res);
}

async function fetchTaskSpec(projectId: string, specId: string): Promise<TaskSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/${specId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch task spec');
  }
  return readJson<TaskSpec>(res);
}

async function fetchTaskSpecByItem(projectId: string, itemId: string): Promise<TaskSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/by-item/${itemId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch task spec by item');
  }
  return readJson<TaskSpec>(res);
}

async function createTaskSpec(projectId: string, data: TaskSpecCreate): Promise<TaskSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create task spec');
  }
  return readJson<TaskSpec>(res);
}

async function updateTaskSpec(
  projectId: string,
  specId: string,
  data: TaskSpecUpdate,
): Promise<TaskSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/${specId}`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update task spec');
  }
  return readJson<TaskSpec>(res);
}

async function deleteTaskSpec(projectId: string, specId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tasks/${specId}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete task spec');
  }
}

export {
  fetchTaskSpecs,
  fetchTaskSpec,
  fetchTaskSpecByItem,
  createTaskSpec,
  updateTaskSpec,
  deleteTaskSpec,
};
