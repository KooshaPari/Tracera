import { z } from 'zod';

import type {
  AutomationStatus,
  TestCase,
  TestCaseActivity,
  TestCasePriority,
  TestCaseStats,
  TestCaseStatus,
  TestCaseType,
  TestStep,
} from '@tracertm/types';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

const submitReviewResponseSchema = z.object({
  id: z.string(),
  reviewed_by: z.string(),
  status: z.string(),
});

const approveTestCaseResponseSchema = z.object({
  approved_by: z.string(),
  id: z.string(),
  status: z.string(),
});

const deprecateTestCaseResponseSchema = z.object({
  id: z.string(),
  status: z.string(),
});

const testCaseActivitiesResponseSchema = z.object({
  activities: z.array(z.record(z.string(), z.unknown())).optional(),
  test_case_id: z.string(),
});

const testCaseListSchema = z.object({
  test_cases: z.array(z.record(z.string(), z.unknown())).optional(),
  total: z.number().optional(),
});

const testCaseResponseSchema = z.record(z.string(), z.unknown());

const createTestCaseResponseSchema = z.object({
  id: z.string(),
  test_case_number: z.string(),
});

const updateTestCaseResponseSchema = z.object({
  id: z.string(),
  version: z.number(),
});

const transitionStatusResponseSchema = z.object({
  id: z.string(),
  status: z.string(),
  version: z.number(),
});

const testCaseStatsSchema = z.object({
  by_automation_status: z.record(z.string(), z.unknown()).optional(),
  by_priority: z.record(z.string(), z.unknown()).optional(),
  by_status: z.record(z.string(), z.unknown()).optional(),
  by_type: z.record(z.string(), z.unknown()).optional(),
  execution_summary: z
    .object({
      total_failed: z.number().optional(),
      total_passed: z.number().optional(),
      total_runs: z.number().optional(),
    })
    .optional(),
  project_id: z.string(),
  total: z.number().optional(),
});

interface TestCaseFilters {
  projectId: string;
  status?: TestCaseStatus;
  testType?: TestCaseType;
  priority?: TestCasePriority;
  automationStatus?: AutomationStatus;
  category?: string;
  assignedTo?: string;
  search?: string;
}

interface CreateTestCaseData {
  projectId: string;
  title: string;
  description?: string;
  objective?: string;
  testType?: TestCaseType;
  priority?: TestCasePriority;
  category?: string;
  tags?: string[];
  preconditions?: string;
  testSteps?: TestStep[];
  expectedResult?: string;
  postconditions?: string;
  testData?: Record<string, unknown>;
  automationStatus?: AutomationStatus;
  automationScriptPath?: string;
  automationFramework?: string;
  automationNotes?: string;
  estimatedDurationMinutes?: number;
  assignedTo?: string;
  metadata?: Record<string, unknown>;
}

interface TestCaseListResult {
  testCases: TestCase[];
  total: number;
}

interface TestCaseActivitiesResult {
  testCaseId: string;
  activities: TestCaseActivity[];
}

const DEFAULT_AUTOMATION_STATUS: AutomationStatus = 'not_automated';
const DEFAULT_PRIORITY: TestCasePriority = 'medium';
const DEFAULT_TEST_TYPE: TestCaseType = 'functional';
const DEFAULT_METADATA: Record<string, unknown> = {};
const DEFAULT_STATS_TOTAL = 0;

async function readJson<TData>(response: Response, schema: z.ZodType<TData>): Promise<TData> {
  const data: unknown = await response.json();
  return schema.parse(data);
}

function getString(value: unknown, fallback = ''): string {
  if (typeof value === 'string') {
    return value;
  }
  return fallback;
}

function getNumber(value: unknown, fallback = 0): number {
  if (typeof value === 'number') {
    return value;
  }
  return fallback;
}

function getRecord(value: unknown): Record<string, unknown> | undefined {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return undefined;
  }
  return value as Record<string, unknown>;
}

function parseNumberRecord(value: unknown): Record<string, number> {
  const record = getRecord(value);
  if (!record) {
    return {};
  }
  return Object.fromEntries(Object.entries(record).map(([key, entry]) => [key, getNumber(entry)]));
}

function isRecord(value: unknown): value is Record<string, unknown> {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return false;
  }
  return true;
}

function buildStepPayload(step: TestStep): Record<string, unknown> {
  return {
    action: step.action,
    expected_result: step.expectedResult,
    step_number: step.stepNumber,
    test_data: step.testData,
  };
}

function buildTestSteps(steps?: TestStep[]): Record<string, unknown>[] | undefined {
  if (!steps) {
    return undefined;
  }
  return steps.map((step) => buildStepPayload(step));
}

function buildCreatePayload(data: CreateTestCaseData): Record<string, unknown> {
  const payload: Record<string, unknown> = {
    assigned_to: data.assignedTo,
    automation_framework: data.automationFramework,
    automation_notes: data.automationNotes,
    automation_script_path: data.automationScriptPath,
    category: data.category,
    description: data.description,
    estimated_duration_minutes: data.estimatedDurationMinutes,
    expected_result: data.expectedResult,
    objective: data.objective,
    postconditions: data.postconditions,
    preconditions: data.preconditions,
    tags: data.tags,
    test_data: data.testData,
    title: data.title,
  };

  const automationStatus = data.automationStatus ?? DEFAULT_AUTOMATION_STATUS;
  payload['automation_status'] = automationStatus;

  const priority = data.priority ?? DEFAULT_PRIORITY;
  payload['priority'] = priority;

  const testType = data.testType ?? DEFAULT_TEST_TYPE;
  payload['test_type'] = testType;

  const metadata = data.metadata ?? DEFAULT_METADATA;
  payload['metadata'] = metadata;

  const testSteps = buildTestSteps(data.testSteps);
  if (testSteps) {
    payload['test_steps'] = testSteps;
  }

  return payload;
}

function applyUpdate(payload: Record<string, unknown>, key: string, value: unknown): void {
  if (value !== undefined) {
    payload[key] = value;
  }
}

function buildUpdatePayload(data: Partial<CreateTestCaseData>): Record<string, unknown> {
  const payload: Record<string, unknown> = {};

  applyUpdate(payload, 'title', data.title);
  applyUpdate(payload, 'description', data.description);
  applyUpdate(payload, 'objective', data.objective);
  applyUpdate(payload, 'test_type', data.testType);
  applyUpdate(payload, 'priority', data.priority);
  applyUpdate(payload, 'category', data.category);
  applyUpdate(payload, 'tags', data.tags);
  applyUpdate(payload, 'preconditions', data.preconditions);
  applyUpdate(payload, 'expected_result', data.expectedResult);
  applyUpdate(payload, 'postconditions', data.postconditions);
  applyUpdate(payload, 'test_data', data.testData);
  applyUpdate(payload, 'automation_status', data.automationStatus);
  applyUpdate(payload, 'automation_script_path', data.automationScriptPath);
  applyUpdate(payload, 'automation_framework', data.automationFramework);
  applyUpdate(payload, 'automation_notes', data.automationNotes);
  applyUpdate(payload, 'estimated_duration_minutes', data.estimatedDurationMinutes);
  applyUpdate(payload, 'assigned_to', data.assignedTo);
  applyUpdate(payload, 'metadata', data.metadata);

  const testSteps = buildTestSteps(data.testSteps);
  if (testSteps) {
    payload['test_steps'] = testSteps;
  }

  return payload;
}

function transformTestCase(data: Record<string, unknown>): TestCase {
  const rawSteps = Array.isArray(data['test_steps']) ? data['test_steps'] : [];
  const stepRecords = rawSteps.filter((step) => isRecord(step));
  const testSteps = stepRecords.map((step, index) => ({
    action: getString(step['action']),
    expectedResult: getString(step['expected_result']),
    stepNumber: getNumber(step['step_number'], index + 1),
    testData: getString(step['test_data']),
  }));

  return {
    approvedAt: data['approved_at'],
    approvedBy: data['approved_by'],
    assignedTo: data['assigned_to'],
    automationFramework: data['automation_framework'],
    automationNotes: data['automation_notes'],
    automationScriptPath: data['automation_script_path'],
    automationStatus: data['automation_status'],
    category: data['category'],
    createdAt: data['created_at'],
    createdBy: data['created_by'],
    deprecatedAt: data['deprecated_at'],
    deprecationReason: data['deprecation_reason'],
    description: data['description'],
    estimatedDurationMinutes: data['estimated_duration_minutes'],
    expectedResult: data['expected_result'],
    failCount: data['fail_count'] ?? 0,
    id: data['id'],
    lastExecutedAt: data['last_executed_at'],
    lastExecutionResult: data['last_execution_result'],
    metadata: data['metadata'],
    objective: data['objective'],
    passCount: data['pass_count'] ?? 0,
    postconditions: data['postconditions'],
    preconditions: data['preconditions'],
    priority: data['priority'],
    projectId: data['project_id'],
    reviewedAt: data['reviewed_at'],
    reviewedBy: data['reviewed_by'],
    status: data['status'],
    tags: data['tags'],
    testCaseNumber: data['test_case_number'],
    testData: data['test_data'],
    testSteps,
    testType: data['test_type'],
    title: data['title'],
    totalExecutions: data['total_executions'] ?? 0,
    updatedAt: data['updated_at'],
    version: data['version'],
  } as TestCase;
}

async function fetchTestCases(filters: TestCaseFilters): Promise<TestCaseListResult> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.testType) {
    params.set('test_type', filters.testType);
  }
  if (filters.priority) {
    params.set('priority', filters.priority);
  }
  if (filters.automationStatus) {
    params.set('automation_status', filters.automationStatus);
  }
  if (filters.category) {
    params.set('category', filters.category);
  }
  if (filters.assignedTo) {
    params.set('assigned_to', filters.assignedTo);
  }
  if (filters.search) {
    params.set('search', filters.search);
  }

  const res = await fetch(`${API_URL}/api/v1/test-cases?${params.toString()}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch test cases: ${res.status} ${errorText}`);
  }
  const data = await readJson(res, testCaseListSchema);
  const testCases = data.test_cases ?? [];
  return {
    testCases: testCases.map((testCase) => transformTestCase(testCase)),
    total: data.total ?? DEFAULT_STATS_TOTAL,
  };
}

async function fetchTestCase(id: string): Promise<TestCase> {
  const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test case');
  }
  const data = await readJson(res, testCaseResponseSchema);
  return transformTestCase(data);
}

async function createTestCase(
  data: CreateTestCaseData,
): Promise<{ id: string; testCaseNumber: string }> {
  const payload = buildCreatePayload(data);
  const res = await fetch(`${API_URL}/api/v1/test-cases?project_id=${data.projectId}`, {
    body: JSON.stringify(payload),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create test case');
  }
  const result = await readJson(res, createTestCaseResponseSchema);
  return { id: result.id, testCaseNumber: result.test_case_number };
}

async function updateTestCase(
  id: string,
  data: Partial<CreateTestCaseData>,
): Promise<{ id: string; version: number }> {
  const payload = buildUpdatePayload(data);
  const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
    body: JSON.stringify(payload),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  if (!res.ok) {
    throw new Error('Failed to update test case');
  }
  return readJson(res, updateTestCaseResponseSchema);
}

async function transitionTestCaseStatus(
  id: string,
  newStatus: TestCaseStatus,
  reason?: string,
): Promise<{ id: string; status: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/status`, {
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
  return readJson(res, transitionStatusResponseSchema);
}

async function submitTestCaseForReview(
  id: string,
  reviewer: string,
  notes?: string,
): Promise<{ id: string; status: string; reviewedBy: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/submit-review`, {
    body: JSON.stringify({
      notes,
      reviewer,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to submit for review');
  }
  const result = await readJson(res, submitReviewResponseSchema);
  return {
    id: result.id,
    reviewedBy: result.reviewed_by,
    status: result.status,
  };
}

async function approveTestCase(
  id: string,
  notes?: string,
): Promise<{ id: string; status: string; approvedBy: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/approve`, {
    body: JSON.stringify({
      approved: true,
      notes,
      reviewer: '',
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to approve test case');
  }
  const result = await readJson(res, approveTestCaseResponseSchema);
  return {
    approvedBy: result.approved_by,
    id: result.id,
    status: result.status,
  };
}

async function deprecateTestCase(
  id: string,
  reason: string,
  replacementTestCaseId?: string,
): Promise<{ id: string; status: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/deprecate`, {
    body: JSON.stringify({
      reason,
      replacement_test_case_id: replacementTestCaseId,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to deprecate test case');
  }
  return readJson(res, deprecateTestCaseResponseSchema);
}

async function deleteTestCase(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete test case');
  }
}

async function fetchTestCaseActivities(
  testCaseId: string,
  limit: number,
): Promise<TestCaseActivitiesResult> {
  const res = await fetch(`${API_URL}/api/v1/test-cases/${testCaseId}/activities?limit=${limit}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch activities');
  }
  const data = await readJson(res, testCaseActivitiesResponseSchema);
  const activities = data.activities ?? [];
  return {
    activities: activities.map((activity) => ({
      activityType: getString(activity['activity_type']),
      createdAt: getString(activity['created_at']),
      description: getString(activity['description']),
      fromValue: getString(activity['from_value']),
      id: getString(activity['id']),
      metadata: getRecord(activity['metadata']),
      performedBy: getString(activity['performed_by']),
      testCaseId: getString(activity['test_case_id']),
      toValue: getString(activity['to_value']),
    })),
    testCaseId: data.test_case_id,
  };
}

async function fetchTestCaseStats(projectId: string): Promise<TestCaseStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/test-cases/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test case stats');
  }
  const data = await readJson(res, testCaseStatsSchema);
  return {
    byAutomationStatus: parseNumberRecord(data.by_automation_status),
    byPriority: parseNumberRecord(data.by_priority),
    byStatus: parseNumberRecord(data.by_status),
    byType: parseNumberRecord(data.by_type),
    executionSummary: {
      totalFailed: data.execution_summary?.total_failed ?? DEFAULT_STATS_TOTAL,
      totalPassed: data.execution_summary?.total_passed ?? DEFAULT_STATS_TOTAL,
      totalRuns: data.execution_summary?.total_runs ?? DEFAULT_STATS_TOTAL,
    },
    projectId: data.project_id,
    total: data.total ?? DEFAULT_STATS_TOTAL,
  };
}

const testCasesApi = {
  approveTestCase,
  createTestCase,
  deleteTestCase,
  deprecateTestCase,
  fetchTestCase,
  fetchTestCaseActivities,
  fetchTestCaseStats,
  fetchTestCases,
  submitTestCaseForReview,
  transitionTestCaseStatus,
  updateTestCase,
};

export default testCasesApi;
export type { CreateTestCaseData, TestCaseActivitiesResult, TestCaseFilters, TestCaseListResult };
