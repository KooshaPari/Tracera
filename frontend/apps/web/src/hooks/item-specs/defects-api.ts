import type {
  DefectSeverity,
  DefectSpec,
  DefectSpecCreate,
  DefectSpecUpdate,
  DefectStatus,
} from './types';

import {
  API_URL,
  appendParam,
  getAuthHeaders,
  getBulkHeaders,
  getJsonAuthHeaders,
  readJson,
} from './constants';

async function fetchDefectSpecs(
  projectId: string,
  options?: {
    severity?: DefectSeverity;
    status?: DefectStatus;
    limit?: number;
    offset?: number;
  },
): Promise<{ specs: DefectSpec[]; total: number }> {
  const params = new URLSearchParams();
  appendParam(params, 'severity', options?.severity);
  appendParam(params, 'status', options?.status);
  appendParam(params, 'limit', options?.limit);
  appendParam(params, 'offset', options?.offset);

  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/defects?${params}`, {
    headers: getBulkHeaders(),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch defect specs: ${res.status} ${errorText}`);
  }
  return readJson<{ specs: DefectSpec[]; total: number }>(res);
}

async function fetchDefectSpec(projectId: string, specId: string): Promise<DefectSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/defects/${specId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch defect spec');
  }
  return readJson<DefectSpec>(res);
}

async function fetchDefectSpecByItem(projectId: string, itemId: string): Promise<DefectSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/defects/by-item/${itemId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch defect spec by item');
  }
  return readJson<DefectSpec>(res);
}

async function createDefectSpec(projectId: string, data: DefectSpecCreate): Promise<DefectSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/defects`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create defect spec');
  }
  return readJson<DefectSpec>(res);
}

async function updateDefectSpec(
  projectId: string,
  specId: string,
  data: DefectSpecUpdate,
): Promise<DefectSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/defects/${specId}`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update defect spec');
  }
  return readJson<DefectSpec>(res);
}

async function deleteDefectSpec(projectId: string, specId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/defects/${specId}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete defect spec');
  }
}

export {
  fetchDefectSpecs,
  fetchDefectSpec,
  fetchDefectSpecByItem,
  createDefectSpec,
  updateDefectSpec,
  deleteDefectSpec,
};
