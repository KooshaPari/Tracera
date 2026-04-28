import type { EpicSpec, EpicSpecCreate, EpicSpecUpdate, EpicStatus } from './types';

import {
  API_URL,
  appendParam,
  getAuthHeaders,
  getBulkHeaders,
  getJsonAuthHeaders,
  readJson,
} from './constants';

async function fetchEpicSpecs(
  projectId: string,
  options?: {
    status?: EpicStatus;
    limit?: number;
    offset?: number;
  },
): Promise<{ specs: EpicSpec[]; total: number }> {
  const params = new URLSearchParams();
  appendParam(params, 'status', options?.status);
  appendParam(params, 'limit', options?.limit);
  appendParam(params, 'offset', options?.offset);

  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/epics?${params}`, {
    headers: getBulkHeaders(),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch epic specs: ${res.status} ${errorText}`);
  }
  return readJson<{ specs: EpicSpec[]; total: number }>(res);
}

async function fetchEpicSpec(projectId: string, specId: string): Promise<EpicSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/epics/${specId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch epic spec');
  }
  return readJson<EpicSpec>(res);
}

async function fetchEpicSpecByItem(projectId: string, itemId: string): Promise<EpicSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/epics/by-item/${itemId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch epic spec by item');
  }
  return readJson<EpicSpec>(res);
}

async function createEpicSpec(projectId: string, data: EpicSpecCreate): Promise<EpicSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/epics`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create epic spec');
  }
  return readJson<EpicSpec>(res);
}

async function updateEpicSpec(
  projectId: string,
  specId: string,
  data: EpicSpecUpdate,
): Promise<EpicSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/epics/${specId}`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update epic spec');
  }
  return readJson<EpicSpec>(res);
}

async function deleteEpicSpec(projectId: string, specId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/epics/${specId}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete epic spec');
  }
}

export {
  fetchEpicSpecs,
  fetchEpicSpec,
  fetchEpicSpecByItem,
  createEpicSpec,
  updateEpicSpec,
  deleteEpicSpec,
};
