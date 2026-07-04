import type { TestResult, TestRun, TestRunActivity, TestRunStats } from '@tracertm/types';

import { client } from '@/api/client';

import type { CreateTestRunData, SubmitTestResultData, TestRunFilters } from './test-run-types';

import { testRunGuards } from './test-run-guards';
import { testRunParsers } from './test-run-parsers';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

interface TestRunsResponse {
  testRuns: TestRun[];
  total: number;
}

interface BulkSubmitResponse {
  submitted: number;
  passed: number;
  failed: number;
  runStatus: string;
  passRate: number;
}

async function fetchJson(url: string, init?: RequestInit): Promise<unknown> {
  const res = await fetch(url, init);
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Request failed: ${res.status} ${errorText}`);
  }
  const data: unknown = await res.json();
  return data;
}

function buildTestRunsParams(filters: TestRunFilters): URLSearchParams {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);

  const stringParams: { key: string; value: string | undefined }[] = [
    { key: 'status', value: filters.status },
    { key: 'run_type', value: filters.runType },
    { key: 'suite_id', value: filters.suiteId },
    { key: 'environment', value: filters.environment },
    { key: 'initiated_by', value: filters.initiatedBy },
    { key: 'search', value: filters.search },
  ];

  for (const { key, value } of stringParams) {
    if (value !== undefined && value.length > 0) {
      params.set(key, value);
    }
  }

  if (filters.skip !== undefined) {
    params.set('skip', String(filters.skip));
  }
  if (filters.limit !== undefined) {
    params.set('limit', String(filters.limit));
  }

  return params;
}

async function fetchTestRuns(filters: TestRunFilters): Promise<TestRunsResponse> {
  const params = buildTestRunsParams(filters);
  const json = await fetchJson(`${API_URL}/api/v1/test-runs?${params.toString()}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });

  const data = testRunGuards.asRecord(json, 'test runs response');
  const rawRuns = testRunGuards.getOptionalArray(data, 'test_runs') ?? [];
  const total = testRunGuards.getOptionalNumber(data, 'total') ?? 0;
  return {
    testRuns: rawRuns.map((item: unknown) => testRunParsers.parseTestRun(item)),
    total,
  };
}

async function fetchTestRun(id: string): Promise<TestRun> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${id}`, {
    headers: getAuthHeaders(),
  });
  return testRunParsers.parseTestRun(json);
}

async function createTestRun(data: CreateTestRunData): Promise<{ id: string; runNumber: string }> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs?project_id=${data.projectId}`, {
    body: JSON.stringify({
      branch: data.branch,
      build_number: data.buildNumber,
      build_url: data.buildUrl,
      commit_sha: data.commitSha,
      description: data.description,
      environment: data.environment,
      external_run_id: data.externalRunId,
      initiated_by: data.initiatedBy,
      metadata: data.metadata ?? {},
      name: data.name,
      notes: data.notes,
      run_type: data.runType ?? 'manual',
      scheduled_at: data.scheduledAt,
      suite_id: data.suiteId,
      tags: data.tags,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return testRunParsers.parseIdRunNumber(json);
}

async function updateTestRun(
  id: string,
  data: Partial<CreateTestRunData>,
): Promise<{ id: string; version: number }> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${id}`, {
    body: JSON.stringify({
      branch: data.branch,
      build_number: data.buildNumber,
      build_url: data.buildUrl,
      commit_sha: data.commitSha,
      description: data.description,
      environment: data.environment,
      metadata: data.metadata,
      name: data.name,
      notes: data.notes,
      tags: data.tags,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  return testRunParsers.parseIdVersion(json);
}

async function startTestRun(
  id: string,
  executedBy?: string,
): Promise<{ id: string; status: string; startedAt?: string | undefined }> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${id}/start`, {
    body: JSON.stringify({ executed_by: executedBy }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  const parsed = testRunParsers.parseIdStatusTimestamp(json);
  return { id: parsed.id, startedAt: parsed.startedAt, status: parsed.status };
}

async function completeTestRun(
  id: string,
  failureSummary?: string,
  notes?: string,
): Promise<{
  id: string;
  status: string;
  passRate?: number | undefined;
  completedAt?: string | undefined;
}> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${id}/complete`, {
    body: JSON.stringify({ failure_summary: failureSummary, notes }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  const parsed = testRunParsers.parseIdStatusTimestamp(json);
  return {
    completedAt: parsed.completedAt,
    id: parsed.id,
    passRate: parsed.passRate,
    status: parsed.status,
  };
}

async function cancelTestRun(id: string, reason?: string): Promise<{ id: string; status: string }> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${id}/cancel`, {
    body: JSON.stringify({ reason }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return testRunParsers.parseCancelResponse(json);
}

async function deleteTestRun(id: string): Promise<void> {
  await fetchJson(`${API_URL}/api/v1/test-runs/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
}

async function submitTestResult(runId: string, data: SubmitTestResultData): Promise<TestResult> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${runId}/results`, {
    body: JSON.stringify({
      actual_result: data.actualResult,
      attachments: data.attachments,
      created_defect_id: data.createdDefectId,
      error_message: data.errorMessage,
      executed_by: data.executedBy,
      failure_reason: data.failureReason,
      is_flaky: data.isFlaky ?? false,
      linked_defect_ids: data.linkedDefectIds,
      logs_url: data.logsUrl,
      metadata: data.metadata,
      notes: data.notes,
      screenshots: data.screenshots,
      stack_trace: data.stackTrace,
      status: data.status,
      step_results: data.stepResults,
      test_case_id: data.testCaseId,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return testRunParsers.parseTestResult(json);
}

async function submitBulkTestResults(
  runId: string,
  results: SubmitTestResultData[],
): Promise<BulkSubmitResponse> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${runId}/results/bulk`, {
    body: JSON.stringify({
      results: results.map((r) => ({
        actual_result: r.actualResult,
        error_message: r.errorMessage,
        executed_by: r.executedBy,
        failure_reason: r.failureReason,
        is_flaky: r.isFlaky ?? false,
        logs_url: r.logsUrl,
        notes: r.notes,
        screenshots: r.screenshots,
        stack_trace: r.stackTrace,
        status: r.status,
        test_case_id: r.testCaseId,
      })),
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  return testRunParsers.parseBulkSubmitResponse(json);
}

async function fetchTestRunResults(runId: string): Promise<TestResult[]> {
  const json = await fetchJson(`${API_URL}/api/v1/test-runs/${runId}/results`, {
    headers: getAuthHeaders(),
  });
  const data = testRunGuards.asRecord(json, 'test run results response');
  const rawResults = testRunGuards.getOptionalArray(data, 'results') ?? [];
  return rawResults.map((item: unknown) => testRunParsers.parseTestResult(item));
}

async function fetchTestRunActivities(
  runId: string,
  limit: number,
): Promise<{ runId: string; activities: TestRunActivity[] }> {
  const json = await fetchJson(
    `${API_URL}/api/v1/test-runs/${runId}/activities?limit=${String(limit)}`,
    {
      headers: getAuthHeaders(),
    },
  );
  return testRunParsers.parseTestRunActivitiesResponse(json);
}

async function fetchTestRunStats(projectId: string): Promise<TestRunStats> {
  const json = await fetchJson(`${API_URL}/api/v1/projects/${projectId}/test-runs/stats`, {
    headers: getAuthHeaders(),
  });
  return testRunParsers.parseTestRunStats(json);
}

const testRunApi = {
  cancelTestRun,
  completeTestRun,
  createTestRun,
  deleteTestRun,
  fetchTestRun,
  fetchTestRunActivities,
  fetchTestRunResults,
  fetchTestRunStats,
  fetchTestRuns,
  startTestRun,
  submitBulkTestResults,
  submitTestResult,
  updateTestRun,
};

export {
  cancelTestRun,
  completeTestRun,
  createTestRun,
  deleteTestRun,
  fetchTestRun,
  fetchTestRunActivities,
  fetchTestRunResults,
  fetchTestRunStats,
  fetchTestRuns,
  startTestRun,
  submitBulkTestResults,
  submitTestResult,
  testRunApi,
  type BulkSubmitResponse,
  type TestRunsResponse,
  updateTestRun,
};
