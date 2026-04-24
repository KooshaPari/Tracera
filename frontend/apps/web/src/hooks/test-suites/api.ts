import type {
  TestSuite,
  TestSuiteActivity,
  TestSuiteStats,
  TestSuiteStatus,
  TestSuiteTestCase,
} from '@tracertm/types';

import { client } from '@/api/client';

import { asJsonObject, getOptionalArray, getOptionalNumber, getString } from './decoders';
import {
  decodeTestSuite,
  decodeTestSuiteActivity,
  decodeTestSuiteStats,
  decodeTestSuiteTestCase,
} from './normalize';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

interface TestSuiteFilters {
  projectId: string;
  status?: TestSuiteStatus;
  category?: string;
  parentId?: string;
  owner?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

interface CreateTestSuiteData {
  projectId: string;
  name: string;
  description?: string;
  objective?: string;
  parentId?: string;
  orderIndex?: number;
  category?: string;
  tags?: string[];
  isParallelExecution?: boolean;
  estimatedDurationMinutes?: number;
  requiredEnvironment?: string;
  environmentVariables?: Record<string, string>;
  setupInstructions?: string;
  teardownInstructions?: string;
  owner?: string;
  responsibleTeam?: string;
  metadata?: Record<string, unknown>;
}

interface AddTestCaseToSuiteInput {
  suiteId: string;
  testCaseId: string;
  orderIndex?: number;
  isMandatory?: boolean;
  skipReason?: string;
  customParameters?: Record<string, unknown>;
}

function hasNonEmptyString(value: string | undefined): value is string {
  return value !== undefined && value !== '';
}

function buildTestSuiteQueryParams(filters: TestSuiteFilters): URLSearchParams {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);

  if (filters.status !== undefined) {
    params.set('status', filters.status);
  }
  if (hasNonEmptyString(filters.category)) {
    params.set('category', filters.category);
  }
  if (filters.parentId !== undefined) {
    params.set('parent_id', filters.parentId);
  }
  if (hasNonEmptyString(filters.owner)) {
    params.set('owner', filters.owner);
  }
  if (hasNonEmptyString(filters.search)) {
    params.set('search', filters.search);
  }
  if (filters.skip !== undefined) {
    params.set('skip', String(filters.skip));
  }
  if (filters.limit !== undefined) {
    params.set('limit', String(filters.limit));
  }
  return params;
}

async function readJson(res: Response): Promise<unknown> {
  const data: unknown = await res.json();
  return data;
}

async function fetchTestSuites(
  filters: TestSuiteFilters,
): Promise<{ testSuites: TestSuite[]; total: number }> {
  const params = buildTestSuiteQueryParams(filters);
  const res = await fetch(`${API_URL}/api/v1/test-suites?${params}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch test suites: ${res.status} ${errorText}`);
  }

  const raw = await readJson(res);
  const obj = asJsonObject(raw, 'TestSuitesResponse');
  const suitesRaw = getOptionalArray(obj, 'test_suites') ?? [];
  const total = getOptionalNumber(obj, 'total') ?? 0;

  return {
    testSuites: suitesRaw.map((value: unknown) => decodeTestSuite(value)),
    total,
  };
}

async function fetchTestSuite(id: string): Promise<TestSuite> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test suite');
  }

  const raw = await readJson(res);
  return decodeTestSuite(raw);
}

async function createTestSuite(
  data: CreateTestSuiteData,
): Promise<{ id: string; suiteNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites?project_id=${data.projectId}`, {
    body: JSON.stringify({
      category: data.category,
      description: data.description,
      environment_variables: data.environmentVariables,
      estimated_duration_minutes: data.estimatedDurationMinutes,
      is_parallel_execution: data.isParallelExecution ?? false,
      metadata: data.metadata ?? {},
      name: data.name,
      objective: data.objective,
      order_index: data.orderIndex ?? 0,
      owner: data.owner,
      parent_id: data.parentId,
      required_environment: data.requiredEnvironment,
      responsible_team: data.responsibleTeam,
      setup_instructions: data.setupInstructions,
      tags: data.tags,
      teardown_instructions: data.teardownInstructions,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create test suite');
  }

  const raw = await readJson(res);
  const obj = asJsonObject(raw, 'CreateTestSuiteResponse');
  return {
    id: getString(obj, 'id'),
    suiteNumber: getString(obj, 'suite_number'),
  };
}

async function updateTestSuite(
  id: string,
  data: Partial<CreateTestSuiteData>,
): Promise<{ id: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
    body: JSON.stringify({
      category: data.category,
      description: data.description,
      environment_variables: data.environmentVariables,
      estimated_duration_minutes: data.estimatedDurationMinutes,
      is_parallel_execution: data.isParallelExecution,
      metadata: data.metadata,
      name: data.name,
      objective: data.objective,
      order_index: data.orderIndex,
      owner: data.owner,
      parent_id: data.parentId,
      required_environment: data.requiredEnvironment,
      responsible_team: data.responsibleTeam,
      setup_instructions: data.setupInstructions,
      tags: data.tags,
      teardown_instructions: data.teardownInstructions,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  if (!res.ok) {
    throw new Error('Failed to update test suite');
  }

  const raw = await readJson(res);
  const obj = asJsonObject(raw, 'UpdateTestSuiteResponse');
  return {
    id: getString(obj, 'id'),
    version: getOptionalNumber(obj, 'version') ?? 0,
  };
}

async function transitionTestSuiteStatus(
  id: string,
  newStatus: TestSuiteStatus,
  reason?: string,
): Promise<{ id: string; status: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}/status`, {
    body: JSON.stringify({
      new_status: newStatus,
      reason,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to transition status: ${errorText}`);
  }

  const raw = await readJson(res);
  const obj = asJsonObject(raw, 'TransitionTestSuiteStatusResponse');
  return {
    id: getString(obj, 'id'),
    status: getString(obj, 'status'),
    version: getOptionalNumber(obj, 'version') ?? 0,
  };
}

async function deleteTestSuite(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete test suite');
  }
}

async function addTestCaseToSuite(input: AddTestCaseToSuiteInput): Promise<TestSuiteTestCase> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${input.suiteId}/test-cases`, {
    body: JSON.stringify({
      custom_parameters: input.customParameters,
      is_mandatory: input.isMandatory !== false,
      order_index: input.orderIndex ?? 0,
      skip_reason: input.skipReason,
      test_case_id: input.testCaseId,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to add test case to suite');
  }

  const raw = await readJson(res);
  return decodeTestSuiteTestCase(raw);
}

async function removeTestCaseFromSuite(suiteId: string, testCaseId: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/test-cases/${testCaseId}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to remove test case from suite');
  }
}

async function fetchSuiteTestCases(suiteId: string): Promise<TestSuiteTestCase[]> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/test-cases`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch suite test cases');
  }

  const raw = await readJson(res);
  const obj = asJsonObject(raw, 'SuiteTestCasesResponse');
  const testCasesRaw = getOptionalArray(obj, 'test_cases') ?? [];
  return testCasesRaw.map((value: unknown) => decodeTestSuiteTestCase(value));
}

async function reorderSuiteTestCases(suiteId: string, testCaseIds: string[]): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/test-cases/reorder`, {
    body: JSON.stringify({
      ordered_test_case_ids: testCaseIds,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to reorder test cases');
  }
}

async function fetchTestSuiteActivities(
  suiteId: string,
  limit = 50,
): Promise<{ suiteId: string; activities: TestSuiteActivity[] }> {
  const res = await fetch(`${API_URL}/api/v1/test-suites/${suiteId}/activities?limit=${limit}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch activities');
  }

  const raw = await readJson(res);
  const obj = asJsonObject(raw, 'TestSuiteActivitiesResponse');
  const activitiesRaw = getOptionalArray(obj, 'activities') ?? [];
  return {
    activities: activitiesRaw.map((value: unknown) => decodeTestSuiteActivity(value)),
    suiteId: getString(obj, 'suite_id'),
  };
}

async function fetchTestSuiteStats(projectId: string): Promise<TestSuiteStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/test-suites/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test suite stats');
  }

  const raw = await readJson(res);
  return decodeTestSuiteStats(raw);
}

const testSuitesApi = {
  addTestCaseToSuite,
  createTestSuite,
  deleteTestSuite,
  fetchSuiteTestCases,
  fetchTestSuite,
  fetchTestSuiteActivities,
  fetchTestSuiteStats,
  fetchTestSuites,
  reorderSuiteTestCases,
  removeTestCaseFromSuite,
  transitionTestSuiteStatus,
  updateTestSuite,
} as const;

export type { AddTestCaseToSuiteInput, CreateTestSuiteData, TestSuiteFilters };

export {
  addTestCaseToSuite,
  createTestSuite,
  deleteTestSuite,
  fetchSuiteTestCases,
  fetchTestSuite,
  fetchTestSuiteActivities,
  fetchTestSuiteStats,
  fetchTestSuites,
  reorderSuiteTestCases,
  removeTestCaseFromSuite,
  testSuitesApi,
  transitionTestSuiteStatus,
  updateTestSuite,
};
