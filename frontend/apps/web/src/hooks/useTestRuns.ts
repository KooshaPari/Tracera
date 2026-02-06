import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type {
  TestResult,
  TestResultStatus,
  TestRun,
  TestRunActivity,
  TestRunStats,
  TestRunStatus,
  TestRunType,
} from '@tracertm/types';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

// Transform API response (snake_case) to frontend format (camelCase)
function transformTestRun(data: Record<string, unknown>): TestRun {
  return {
    blockedCount: data['blocked_count'] as number,
    branch: data['branch'] as string,
    buildNumber: data['build_number'] as string,
    buildUrl: data['build_url'] as string,
    commitSha: data['commit_sha'] as string,
    completedAt: data['completed_at'] as string,
    createdAt: data['created_at'] as string,
    description: data['description'] as string,
    durationSeconds: data['duration_seconds'] as number,
    environment: data['environment'] as string,
    errorCount: data['error_count'] as number,
    executedBy: data['executed_by'] as string,
    externalRunId: data['external_run_id'] as string,
    failedCount: data['failed_count'] as number,
    failureSummary: data['failure_summary'] as string,
    id: data['id'] as string,
    initiatedBy: data['initiated_by'] as string,
    metadata: data['run_metadata'] as Record<string, unknown>,
    name: data.name as string,
    notes: data['notes'] as string,
    passRate: data['pass_rate'] as number,
    passedCount: data['passed_count'] as number,
    projectId: data['project_id'] as string,
    runNumber: String(data['run_number'] ?? ''),
    runType: data['run_type'] as TestRunType,
    scheduledAt: data['scheduled_at'] as string,
    skippedCount: data['skipped_count'] as number,
    startedAt: data['started_at'] as string,
    status: data.status as TestRunStatus,
    suiteId: data['suite_id'] as string,
    tags: data['tags'] as string[],
    totalTests: data['total_tests'] as number,
    updatedAt: data['updated_at'] as string,
    version: data['version'] as number,
    webhookId: data['webhook_id'] as string,
  };
}

function transformTestResult(data: Record<string, unknown>): TestResult {
  return {
    actualResult: data['actual_result'] as string,
    attachments: data['attachments'] as string[],
    completedAt: data['completed_at'] as string,
    createdAt: data['created_at'] as string,
    createdDefectId: data['created_defect_id'] as string,
    durationSeconds: data['duration_seconds'] as number,
    errorMessage: data['error_message'] as string,
    executedBy: data['executed_by'] as string,
    failureReason: data['failure_reason'] as string,
    id: data['id'] as string,
    isFlaky: data['is_flaky'] as boolean,
    linkedDefectIds: data['linked_defect_ids'] as string[],
    logsUrl: data['logs_url'] as string,
    metadata: data['run_metadata'] as Record<string, unknown>,
    notes: data['notes'] as string,
    retryCount: data['retry_count'] as number,
    runId: data['run_id'] as string,
    screenshots: data['screenshots'] as string[],
    stackTrace: data['stack_trace'] as string,
    startedAt: data['started_at'] as string,
    status: data.status as TestResultStatus,
    stepResults: data['step_results'] as {
      stepNumber: number;
      status: TestResultStatus;
      actualResult?: string;
      notes?: string;
    }[],
    testCaseId: data['test_case_id'] as string,
    updatedAt: data['updated_at'] as string,
  };
}

interface TestRunFilters {
  projectId: string;
  status?: TestRunStatus;
  runType?: TestRunType;
  suiteId?: string;
  environment?: string;
  initiatedBy?: string;
  search?: string;
  skip?: number;
  limit?: number;
}

async function fetchTestRuns(
  filters: TestRunFilters,
): Promise<{ testRuns: TestRun[]; total: number }> {
  const params = new URLSearchParams();
  params.set('project_id', filters.projectId);
  if (filters.status) {
    params.set('status', filters.status);
  }
  if (filters.runType) {
    params.set('run_type', filters.runType);
  }
  if (filters.suiteId) {
    params.set('suite_id', filters.suiteId);
  }
  if (filters.environment) {
    params.set('environment', filters.environment);
  }
  if (filters.initiatedBy) {
    params.set('initiated_by', filters.initiatedBy);
  }
  if (filters.search) {
    params.set('search', filters.search);
  }
  if (filters.skip !== undefined) {
    params.set('skip', String(filters.skip));
  }
  if (filters.limit !== undefined) {
    params.set('limit', String(filters.limit));
  }

  const res = await fetch(`${API_URL}/api/v1/test-runs?${params}`, {
    headers: {
      'X-Bulk-Operation': 'true',
      ...getAuthHeaders(),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch test runs: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    testRuns: (data['test_runs'] || []).map(transformTestRun),
    total: data['total'] || 0,
  };
}

async function fetchTestRun(id: string): Promise<TestRun> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${id}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test run');
  }
  const data = await res.json();
  return transformTestRun(data);
}

interface CreateTestRunData {
  projectId: string;
  name: string;
  description?: string;
  suiteId?: string;
  runType?: TestRunType;
  environment?: string;
  buildNumber?: string;
  buildUrl?: string;
  branch?: string;
  commitSha?: string;
  scheduledAt?: string;
  initiatedBy?: string;
  notes?: string;
  tags?: string[];
  externalRunId?: string;
  metadata?: Record<string, unknown>;
}

async function createTestRun(data: CreateTestRunData): Promise<{ id: string; runNumber: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-runs?project_id=${data['projectId']}`, {
    body: JSON.stringify({
      branch: data['branch'],
      build_number: data['buildNumber'],
      build_url: data['buildUrl'],
      commit_sha: data['commitSha'],
      description: data['description'],
      environment: data['environment'],
      external_run_id: data['externalRunId'],
      initiated_by: data['initiatedBy'],
      metadata: data['metadata'] || {},
      name: data.name,
      notes: data['notes'],
      run_type: data['runType'] || 'manual',
      scheduled_at: data['scheduledAt'],
      suite_id: data['suiteId'],
      tags: data['tags'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create test run');
  }
  const result = await res.json();
  return { id: result['id'], runNumber: result['run_number'] };
}

async function updateTestRun(
  id: string,
  data: Partial<CreateTestRunData>,
): Promise<{ id: string; version: number }> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${id}`, {
    body: JSON.stringify({
      branch: data['branch'],
      build_number: data['buildNumber'],
      build_url: data['buildUrl'],
      commit_sha: data['commitSha'],
      description: data['description'],
      environment: data['environment'],
      metadata: data['metadata'],
      name: data.name,
      notes: data['notes'],
      tags: data['tags'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'PUT',
  });
  if (!res.ok) {
    throw new Error('Failed to update test run');
  }
  return res.json();
}

async function startTestRun(
  id: string,
  executedBy?: string,
): Promise<{ id: string; status: string; startedAt: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${id}/start`, {
    body: JSON.stringify({
      executed_by: executedBy,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to start test run: ${errorText}`);
  }
  const result = await res.json();
  return {
    id: result['id'],
    startedAt: result['started_at'],
    status: result.status,
  };
}

async function completeTestRun(
  id: string,
  failureSummary?: string,
  notes?: string,
): Promise<{
  id: string;
  status: string;
  passRate: number;
  completedAt: string;
}> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${id}/complete`, {
    body: JSON.stringify({
      failure_summary: failureSummary,
      notes,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to complete test run: ${errorText}`);
  }
  const result = await res.json();
  return {
    completedAt: result['completed_at'],
    id: result['id'],
    passRate: result['pass_rate'],
    status: result.status,
  };
}

async function cancelTestRun(id: string, reason?: string): Promise<{ id: string; status: string }> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${id}/cancel`, {
    body: JSON.stringify({
      reason,
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to cancel test run: ${errorText}`);
  }
  return res.json();
}

async function deleteTestRun(id: string): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${id}`, {
    headers: getAuthHeaders(),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete test run');
  }
}

// Test results management
interface SubmitTestResultData {
  testCaseId: string;
  status: TestResultStatus;
  executedBy?: string;
  actualResult?: string;
  failureReason?: string;
  errorMessage?: string;
  stackTrace?: string;
  screenshots?: string[];
  logsUrl?: string;
  attachments?: string[];
  stepResults?: {
    stepNumber: number;
    status: TestResultStatus;
    actualResult?: string;
    notes?: string;
  }[];
  notes?: string;
  isFlaky?: boolean;
  linkedDefectIds?: string[];
  createdDefectId?: string;
  metadata?: Record<string, unknown>;
}

async function submitTestResult(runId: string, data: SubmitTestResultData): Promise<TestResult> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${runId}/results`, {
    body: JSON.stringify({
      actual_result: data['actualResult'],
      attachments: data['attachments'],
      created_defect_id: data['createdDefectId'],
      error_message: data['errorMessage'],
      executed_by: data['executedBy'],
      failure_reason: data['failureReason'],
      is_flaky: data['isFlaky'] || false,
      linked_defect_ids: data['linkedDefectIds'],
      logs_url: data['logsUrl'],
      metadata: data['metadata'],
      notes: data['notes'],
      screenshots: data['screenshots'],
      stack_trace: data['stackTrace'],
      status: data.status,
      step_results: data['stepResults'],
      test_case_id: data['testCaseId'],
    }),
    headers: { 'Content-Type': 'application/json', ...getAuthHeaders() },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to submit test result');
  }
  const result = await res.json();
  return transformTestResult(result);
}

async function submitBulkTestResults(
  runId: string,
  results: SubmitTestResultData[],
): Promise<{
  submitted: number;
  passed: number;
  failed: number;
  runStatus: string;
  passRate: number;
}> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${runId}/results/bulk`, {
    body: JSON.stringify({
      results: results.map((r) => ({
        actual_result: r.actualResult,
        error_message: r.errorMessage,
        executed_by: r.executedBy,
        failure_reason: r.failureReason,
        is_flaky: r.isFlaky || false,
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
  if (!res.ok) {
    throw new Error('Failed to submit bulk test results');
  }
  const result = await res.json();
  return {
    failed: result['failed'],
    passRate: result['pass_rate'],
    passed: result['passed'],
    runStatus: result['run_status'],
    submitted: result['submitted'],
  };
}

async function fetchTestRunResults(runId: string): Promise<TestResult[]> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${runId}/results`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test run results');
  }
  const data = await res.json();
  return (data['results'] || []).map(transformTestResult);
}

async function fetchTestRunActivities(
  runId: string,
  limit = 50,
): Promise<{ runId: string; activities: TestRunActivity[] }> {
  const res = await fetch(`${API_URL}/api/v1/test-runs/${runId}/activities?limit=${limit}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch activities');
  }
  const data = await res.json();
  return {
    activities: ((data['activities'] as unknown[]) || []).map(
      (a: Record<string, unknown>): TestRunActivity => ({
        activityType: a.activity_type as string,
        createdAt: a.created_at as string,
        description: a.description as string,
        fromValue: a.from_value as string,
        id: a.id as string,
        metadata: a.run_metadata as Record<string, unknown>,
        performedBy: a.performed_by as string,
        runId: a.run_id as string,
        toValue: a.to_value as string,
      }),
    ),
    runId: data['run_id'] as string,
  };
}

async function fetchTestRunStats(projectId: string): Promise<TestRunStats> {
  const res = await fetch(`${API_URL}/api/v1/projects/${projectId}/test-runs/stats`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch test run stats');
  }
  const data = await res.json();
  return {
    averageDurationSeconds: data['average_duration_seconds'] || 0,
    averagePassRate: data['average_pass_rate'] || 0,
    byStatus: data['by_status'] || {},
    byType: data['by_type'] || {},
    projectId: data['project_id'],
    recentRuns: (data['recent_runs'] || []).map(transformTestRun),
    totalRuns: data['total_runs'] || 0,
  };
}

// React Query hooks

export function useTestRuns(filters: TestRunFilters) {
  return useQuery({
    enabled: Boolean(filters.projectId),
    queryFn: () => fetchTestRuns(filters),
    queryKey: ['testRuns', JSON.stringify(filters)],
  });
}

export function useTestRun(id: string) {
  return useQuery({
    enabled: Boolean(id),
    queryFn: () => fetchTestRun(id),
    queryKey: ['testRuns', id],
  });
}

export function useCreateTestRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createTestRun,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['testRuns'] });
    },
  });
}

export function useUpdateTestRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CreateTestRunData> }) =>
      updateTestRun(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      queryClient.invalidateQueries({ queryKey: ['testRuns', id] });
    },
  });
}

export function useStartTestRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, executedBy }: { id: string; executedBy?: string }) =>
      startTestRun(id, executedBy),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      queryClient.invalidateQueries({ queryKey: ['testRuns', id] });
      queryClient.invalidateQueries({ queryKey: ['testRunActivities', id] });
    },
  });
}

export function useCompleteTestRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      failureSummary,
      notes,
    }: {
      id: string;
      failureSummary?: string;
      notes?: string;
    }) => completeTestRun(id, failureSummary, notes),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      queryClient.invalidateQueries({ queryKey: ['testRuns', id] });
      queryClient.invalidateQueries({ queryKey: ['testRunActivities', id] });
    },
  });
}

export function useCancelTestRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason?: string }) => cancelTestRun(id, reason),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: ['testRuns'] });
      queryClient.invalidateQueries({ queryKey: ['testRuns', id] });
      queryClient.invalidateQueries({ queryKey: ['testRunActivities', id] });
    },
  });
}

export function useDeleteTestRun() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteTestRun,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['testRuns'] });
    },
  });
}

export function useSubmitTestResult() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ runId, data }: { runId: string; data: SubmitTestResultData }) =>
      submitTestResult(runId, data),
    onSuccess: (_, { runId }) => {
      queryClient.invalidateQueries({ queryKey: ['testRunResults', runId] });
      queryClient.invalidateQueries({ queryKey: ['testRuns', runId] });
    },
  });
}

export function useSubmitBulkTestResults() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ runId, results }: { runId: string; results: SubmitTestResultData[] }) =>
      submitBulkTestResults(runId, results),
    onSuccess: (_, { runId }) => {
      queryClient.invalidateQueries({ queryKey: ['testRunResults', runId] });
      queryClient.invalidateQueries({ queryKey: ['testRuns', runId] });
    },
  });
}

export function useTestRunResults(runId: string) {
  return useQuery({
    enabled: Boolean(runId),
    queryFn: () => fetchTestRunResults(runId),
    queryKey: ['testRunResults', runId],
  });
}

export function useTestRunActivities(runId: string, limit = 50) {
  return useQuery({
    enabled: Boolean(runId),
    queryFn: () => fetchTestRunActivities(runId, limit),
    queryKey: ['testRunActivities', runId, limit],
  });
}

export function useTestRunStats(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: () => fetchTestRunStats(projectId),
    queryKey: ['testRunStats', projectId],
  });
}
