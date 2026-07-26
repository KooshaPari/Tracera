import type { TestResultStatus, TestSpec, TestSpecCreate, TestSpecUpdate, TestType } from './types';

import {
  API_URL,
  DEFAULT_FLAKY_LIMIT,
  DEFAULT_FLAKY_THRESHOLD,
  DEFAULT_QUARANTINED_LIMIT,
  appendParam,
  getAuthHeaders,
  getBulkHeaders,
  getJsonAuthHeaders,
  readJson,
} from './constants';

interface TestRunPayload {
  status: TestResultStatus;
  durationMs: number;
  errorMessage?: string;
  environment?: string;
}

async function fetchTestSpecs(
  projectId: string,
  options?: {
    testType?: TestType;
    isQuarantined?: boolean;
    limit?: number;
    offset?: number;
  },
): Promise<{ specs: TestSpec[]; total: number }> {
  const params = new URLSearchParams();
  appendParam(params, 'test_type', options?.testType);
  appendParam(params, 'is_quarantined', options?.isQuarantined);
  appendParam(params, 'limit', options?.limit);
  appendParam(params, 'offset', options?.offset);

  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tests?${params}`, {
    headers: getBulkHeaders(),
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch test specs: ${res.status} ${errorText}`);
  }
  return readJson<{ specs: TestSpec[]; total: number }>(res);
}

async function fetchTestSpec(projectId: string, specId: string): Promise<TestSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test spec');
  }
  return readJson<TestSpec>(res);
}

async function fetchTestSpecByItem(projectId: string, itemId: string): Promise<TestSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tests/by-item/${itemId}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch test spec by item');
  }
  return readJson<TestSpec>(res);
}

async function fetchFlakyTests(
  projectId: string,
  threshold = DEFAULT_FLAKY_THRESHOLD,
  limit = DEFAULT_FLAKY_LIMIT,
): Promise<{ specs: TestSpec[]; total: number }> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tests/flaky?threshold=${threshold}&limit=${limit}`,
    { headers: getBulkHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch flaky tests');
  }
  return readJson<{ specs: TestSpec[]; total: number }>(res);
}

async function fetchQuarantinedTests(
  projectId: string,
  limit = DEFAULT_QUARANTINED_LIMIT,
): Promise<{ specs: TestSpec[]; total: number }> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tests/quarantined?limit=${limit}`,
    { headers: getBulkHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch quarantined tests');
  }
  return readJson<{ specs: TestSpec[]; total: number }>(res);
}

async function fetchTestHealthReport(projectId: string): Promise<{
  total_tests: number;
  flaky_count: number;
  quarantined_count: number;
  total_runs: number;
  pass_rate: number;
  average_duration_ms: number;
  health_score: number;
}> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tests/health-report`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch test health report');
  }
  return readJson<{
    total_tests: number;
    flaky_count: number;
    quarantined_count: number;
    total_runs: number;
    pass_rate: number;
    average_duration_ms: number;
    health_score: number;
  }>(res);
}

async function createTestSpec(projectId: string, data: TestSpecCreate): Promise<TestSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tests`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create test spec');
  }
  return readJson<TestSpec>(res);
}

async function updateTestSpec(
  projectId: string,
  specId: string,
  data: TestSpecUpdate,
): Promise<TestSpec> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}`, {
    body: JSON.stringify(data),
    headers: getJsonAuthHeaders(),
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update test spec');
  }
  return readJson<TestSpec>(res);
}

async function deleteTestSpec(projectId: string, specId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete test spec');
  }
}

async function recordTestRun(
  projectId: string,
  specId: string,
  payload: TestRunPayload,
): Promise<TestSpec> {
  const params = new URLSearchParams({
    duration_ms: String(payload.durationMs),
    status: payload.status,
  });
  if (typeof payload.errorMessage === 'string' && payload.errorMessage.length > 0) {
    params.append('error_message', payload.errorMessage);
  }
  if (typeof payload.environment === 'string' && payload.environment.length > 0) {
    params.append('environment', payload.environment);
  }

  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}/record-run?${params}`,
    { headers: getAuthHeaders(), method: 'POST' },
  );
  if (!res.ok) {
    throw new Error('Failed to record test run');
  }
  return readJson<TestSpec>(res);
}

async function quarantineTest(
  projectId: string,
  specId: string,
  reason: string,
): Promise<TestSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}/quarantine?reason=${encodeURIComponent(reason)}`,
    { headers: getAuthHeaders(), method: 'POST' },
  );
  if (!res.ok) {
    throw new Error('Failed to quarantine test');
  }
  return readJson<TestSpec>(res);
}

async function unquarantineTest(projectId: string, specId: string): Promise<TestSpec> {
  const res = await fetch(
    `${API_URL}/api/v1/projects/${projectId}/item-specs/tests/${specId}/unquarantine`,
    { headers: getAuthHeaders(), method: 'POST' },
  );
  if (!res.ok) {
    throw new Error('Failed to unquarantine test');
  }
  return readJson<TestSpec>(res);
}

export type { TestRunPayload };
export {
  fetchTestSpecs,
  fetchTestSpec,
  fetchTestSpecByItem,
  fetchFlakyTests,
  fetchQuarantinedTests,
  fetchTestHealthReport,
  createTestSpec,
  updateTestSpec,
  deleteTestSpec,
  recordTestRun,
  quarantineTest,
  unquarantineTest,
};
