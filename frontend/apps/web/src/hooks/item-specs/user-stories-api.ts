import type {
  UserStorySpec,
  UserStorySpecCreate,
  UserStorySpecUpdate,
  UserStoryStatus,
} from './types';

import {
  API_URL,
  appendParam,
  getAuthHeaders,
  getBulkHeaders,
  getJsonAuthHeaders,
  readJson,
} from './constants';

async function fetchUserStorySpecs(
  projectId: string,
  options?: {
    status?: UserStoryStatus;
    epicId?: string;
    limit?: number;
    offset?: number;
  },
): Promise<{ specs: UserStorySpec[]; total: number }> {
  const params = new URLSearchParams();
  appendParam(params, 'status', options?.status);
  appendParam(params, 'epic_id', options?.epicId);
  appendParam(params, 'limit', options?.limit);
  appendParam(params, 'offset', options?.offset);

  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories?${params}`,
    { headers: getBulkHeaders() },
  );
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch user story specs: ${res.status} ${errorText}`);
  }
  return readJson<{ specs: UserStorySpec[]; total: number }>(res);
}

async function fetchUserStorySpec(projectId: string, specId: string): Promise<UserStorySpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/${specId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch user story spec');
  }
  return readJson<UserStorySpec>(res);
}

async function fetchUserStorySpecByItem(projectId: string, itemId: string): Promise<UserStorySpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/by-item/${itemId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch user story spec by item');
  }
  return readJson<UserStorySpec>(res);
}

async function createUserStorySpec(
  projectId: string,
  data: UserStorySpecCreate,
): Promise<UserStorySpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create user story spec');
  }
  return readJson<UserStorySpec>(res);
}

async function updateUserStorySpec(
  projectId: string,
  specId: string,
  data: UserStorySpecUpdate,
): Promise<UserStorySpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/${specId}`,
    {
      body: JSON.stringify(data),
      headers: getJsonAuthHeaders(),
      method: 'PATCH',
    },
  );
  if (!res.ok) {
    throw new Error('Failed to update user story spec');
  }
  return readJson<UserStorySpec>(res);
}

async function deleteUserStorySpec(projectId: string, specId: string): Promise<void> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/user-stories/${specId}`,
    { headers: getAuthHeaders(), method: 'DELETE' },
  );
  if (!res.ok) {
    throw new Error('Failed to delete user story spec');
  }
}

export {
  fetchUserStorySpecs,
  fetchUserStorySpec,
  fetchUserStorySpecByItem,
  createUserStorySpec,
  updateUserStorySpec,
  deleteUserStorySpec,
};
