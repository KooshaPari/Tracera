import type {
  TestResult,
  TestResultStatus,
  TestRun,
  TestRunActivity,
  TestRunStats,
  TestRunStatus,
  TestRunType,
} from '@tracertm/types';

import {
  asRecord,
  getOptionalArray,
  getOptionalBoolean,
  getOptionalNumber,
  getOptionalRecord,
  getOptionalString,
  getOptionalStringArray,
  getRequiredArray,
  getRequiredBoolean,
  getRequiredNumber,
  getRequiredRecord,
  getRequiredString,
  toStringId,
  type JsonRecord,
} from './test-run-guards';

function parseTestRunStatus(value: unknown): TestRunStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'blocked':
      return 'blocked';
    case 'cancelled':
      return 'cancelled';
    case 'failed':
      return 'failed';
    case 'passed':
      return 'passed';
    case 'pending':
      return 'pending';
    case 'running':
      return 'running';
    default:
      throw new Error(`Invalid status value: ${str}`);
  }
}

function parseTestRunType(value: unknown): TestRunType {
  const str = parseRequiredString(value, 'run_type');
  switch (str) {
    case 'automated':
      return 'automated';
    case 'ci_cd':
      return 'ci_cd';
    case 'manual':
      return 'manual';
    case 'scheduled':
      return 'scheduled';
    default:
      throw new Error(`Invalid run_type value: ${str}`);
  }
}

function parseTestResultStatus(value: unknown): TestResultStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'blocked':
      return 'blocked';
    case 'error':
      return 'error';
    case 'failed':
      return 'failed';
    case 'passed':
      return 'passed';
    case 'skipped':
      return 'skipped';
    default:
      throw new Error(`Invalid status value: ${str}`);
  }
}

function parseRequiredString(value: unknown, key: string): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new Error(`Missing or invalid required string field: ${key}`);
  }
  return value;
}

function parseTestRun(input: unknown): TestRun {
  const data = asRecord(input, 'test run');

  return {
    blockedCount: getRequiredNumber(data, 'blocked_count'),
    branch: getOptionalString(data, 'branch'),
    buildNumber: getOptionalString(data, 'build_number'),
    buildUrl: getOptionalString(data, 'build_url'),
    commitSha: getOptionalString(data, 'commit_sha'),
    completedAt: getOptionalString(data, 'completed_at'),
    createdAt: getRequiredString(data, 'created_at'),
    description: getOptionalString(data, 'description'),
    durationSeconds: getOptionalNumber(data, 'duration_seconds'),
    environment: getOptionalString(data, 'environment'),
    errorCount: getRequiredNumber(data, 'error_count'),
    executedBy: getOptionalString(data, 'executed_by'),
    externalRunId: getOptionalString(data, 'external_run_id'),
    failedCount: getRequiredNumber(data, 'failed_count'),
    failureSummary: getOptionalString(data, 'failure_summary'),
    id: toStringId(data['id'], 'id'),
    initiatedBy: getOptionalString(data, 'initiated_by'),
    metadata: getOptionalRecord(data, 'run_metadata'),
    name: getRequiredString(data, 'name'),
    notes: getOptionalString(data, 'notes'),
    passRate: getOptionalNumber(data, 'pass_rate'),
    passedCount: getRequiredNumber(data, 'passed_count'),
    projectId: getRequiredString(data, 'project_id'),
    runNumber: toStringId(data['run_number'], 'run_number'),
    runType: parseTestRunType(data['run_type']),
    scheduledAt: getOptionalString(data, 'scheduled_at'),
    skippedCount: getRequiredNumber(data, 'skipped_count'),
    startedAt: getOptionalString(data, 'started_at'),
    status: parseTestRunStatus(data['status']),
    suiteId: getOptionalString(data, 'suite_id'),
    tags: getOptionalStringArray(data, 'tags'),
    totalTests: getRequiredNumber(data, 'total_tests'),
    updatedAt: getRequiredString(data, 'updated_at'),
    version: getRequiredNumber(data, 'version'),
    webhookId: getOptionalString(data, 'webhook_id'),
  };
}

function parseTestResult(input: unknown): TestResult {
  const data = asRecord(input, 'test result');
  const stepResultsRaw = getOptionalArray(data, 'step_results');

  return {
    actualResult: getOptionalString(data, 'actual_result'),
    attachments: getOptionalStringArray(data, 'attachments'),
    completedAt: getOptionalString(data, 'completed_at'),
    createdAt: getRequiredString(data, 'created_at'),
    createdDefectId: getOptionalString(data, 'created_defect_id'),
    durationSeconds: getOptionalNumber(data, 'duration_seconds'),
    errorMessage: getOptionalString(data, 'error_message'),
    executedBy: getOptionalString(data, 'executed_by'),
    failureReason: getOptionalString(data, 'failure_reason'),
    id: toStringId(data['id'], 'id'),
    isFlaky: getRequiredBoolean(data, 'is_flaky'),
    linkedDefectIds: getOptionalStringArray(data, 'linked_defect_ids'),
    logsUrl: getOptionalString(data, 'logs_url'),
    metadata: getOptionalRecord(data, 'run_metadata'),
    notes: getOptionalString(data, 'notes'),
    retryCount: getRequiredNumber(data, 'retry_count'),
    runId: getRequiredString(data, 'run_id'),
    screenshots: getOptionalStringArray(data, 'screenshots'),
    stackTrace: getOptionalString(data, 'stack_trace'),
    startedAt: getOptionalString(data, 'started_at'),
    status: parseTestResultStatus(data['status']),
    stepResults: parseStepResults(stepResultsRaw),
    testCaseId: getRequiredString(data, 'test_case_id'),
    updatedAt: getRequiredString(data, 'updated_at'),
  };
}

function parseStepResults(stepResultsRaw: unknown[] | undefined): TestResult['stepResults'] {
  if (stepResultsRaw === undefined) {
    return undefined;
  }
  const parsed = stepResultsRaw.map((item: unknown) => {
    const step = asRecord(item, 'step_result');
    return {
      actualResult: getOptionalString(step, 'actual_result'),
      notes: getOptionalString(step, 'notes'),
      status: parseTestResultStatus(step['status']),
      stepNumber: getRequiredNumber(step, 'step_number'),
    };
  });
  return parsed;
}

function parseTestRunActivitiesResponse(input: unknown): {
  runId: string;
  activities: TestRunActivity[];
} {
  const data = asRecord(input, 'activities response');
  const activitiesRaw = getRequiredArray(data, 'activities');
  const activities = activitiesRaw.map((item: unknown): TestRunActivity => {
    const a = asRecord(item, 'activity');
    return {
      activityType: getRequiredString(a, 'activity_type'),
      createdAt: getRequiredString(a, 'created_at'),
      description: getOptionalString(a, 'description'),
      fromValue: getOptionalString(a, 'from_value'),
      id: toStringId(a['id'], 'id'),
      metadata: getOptionalRecord(a, 'run_metadata'),
      performedBy: getOptionalString(a, 'performed_by'),
      runId: getRequiredString(a, 'run_id'),
      toValue: getOptionalString(a, 'to_value'),
    };
  });

  return { activities, runId: getRequiredString(data, 'run_id') };
}

function parseTestRunStats(input: unknown): TestRunStats {
  const data = asRecord(input, 'test run stats');

  return {
    averageDurationSeconds: getOptionalNumber(data, 'average_duration_seconds') ?? 0,
    averagePassRate: getOptionalNumber(data, 'average_pass_rate') ?? 0,
    byStatus: parseNumberMap(getOptionalRecord(data, 'by_status')),
    byType: parseNumberMap(getOptionalRecord(data, 'by_type')),
    projectId: getRequiredString(data, 'project_id'),
    recentRuns: (getOptionalArray(data, 'recent_runs') ?? []).map((item: unknown) =>
      parseTestRun(item),
    ),
    totalRuns: getOptionalNumber(data, 'total_runs') ?? 0,
  };
}

function parseNumberMap(input: JsonRecord | undefined): Record<string, number> {
  if (input === undefined) {
    return {};
  }
  const out: Record<string, number> = {};
  for (const [key, value] of Object.entries(input)) {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      throw new Error(`Invalid number map value for key: ${key}`);
    }
    out[key] = value;
  }
  return out;
}

function parseIdStatusTimestamp(input: unknown): {
  id: string;
  status: string;
  startedAt?: string;
  completedAt?: string;
  passRate?: number;
  isActiveVersion?: boolean;
} {
  const data = asRecord(input, 'response');
  return {
    completedAt: getOptionalString(data, 'completed_at'),
    id: toStringId(data['id'], 'id'),
    isActiveVersion: getOptionalBoolean(data, 'is_active_version'),
    passRate: getOptionalNumber(data, 'pass_rate'),
    startedAt: getOptionalString(data, 'started_at'),
    status: getRequiredString(data, 'status'),
  };
}

function parseIdRunNumber(input: unknown): { id: string; runNumber: string } {
  const data = asRecord(input, 'create response');
  return {
    id: toStringId(data['id'], 'id'),
    runNumber: toStringId(data['run_number'], 'run_number'),
  };
}

function parseIdVersion(input: unknown): { id: string; version: number } {
  const data = asRecord(input, 'update response');
  return {
    id: toStringId(data['id'], 'id'),
    version: getRequiredNumber(data, 'version'),
  };
}

function parseCancelResponse(input: unknown): { id: string; status: string } {
  const data = asRecord(input, 'cancel response');
  return {
    id: toStringId(data['id'], 'id'),
    status: getRequiredString(data, 'status'),
  };
}

function parseBulkSubmitResponse(input: unknown): {
  submitted: number;
  passed: number;
  failed: number;
  runStatus: string;
  passRate: number;
} {
  const data = asRecord(input, 'bulk submit response');
  return {
    failed: getRequiredNumber(data, 'failed'),
    passRate: getRequiredNumber(data, 'pass_rate'),
    passed: getRequiredNumber(data, 'passed'),
    runStatus: getRequiredString(data, 'run_status'),
    submitted: getRequiredNumber(data, 'submitted'),
  };
}

export {
  parseBulkSubmitResponse,
  parseCancelResponse,
  parseIdRunNumber,
  parseIdStatusTimestamp,
  parseIdVersion,
  parseTestResult,
  parseTestRun,
  parseTestRunActivitiesResponse,
  parseTestRunStats,
};
