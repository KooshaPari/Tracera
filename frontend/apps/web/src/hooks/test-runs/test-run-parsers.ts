import type {
  TestResult,
  TestResultStatus,
  TestRun,
  TestRunActivity,
  TestRunStats,
  TestRunStatus,
  TestRunType,
} from '@tracertm/types';

import { testRunGuards } from './test-run-guards';

function parseTestRunStatus(value: unknown): TestRunStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'blocked': {
      return 'blocked';
    }
    case 'cancelled': {
      return 'cancelled';
    }
    case 'failed': {
      return 'failed';
    }
    case 'passed': {
      return 'passed';
    }
    case 'pending': {
      return 'pending';
    }
    case 'running': {
      return 'running';
    }
    default: {
      throw new Error(`Invalid status value: ${str}`);
    }
  }
}

function parseTestRunType(value: unknown): TestRunType {
  const str = parseRequiredString(value, 'run_type');
  switch (str) {
    case 'automated': {
      return 'automated';
    }
    case 'ci_cd': {
      return 'ci_cd';
    }
    case 'manual': {
      return 'manual';
    }
    case 'scheduled': {
      return 'scheduled';
    }
    default: {
      throw new Error(`Invalid run_type value: ${str}`);
    }
  }
}

function parseTestResultStatus(value: unknown): TestResultStatus {
  const str = parseRequiredString(value, 'status');
  switch (str) {
    case 'blocked': {
      return 'blocked';
    }
    case 'error': {
      return 'error';
    }
    case 'failed': {
      return 'failed';
    }
    case 'passed': {
      return 'passed';
    }
    case 'skipped': {
      return 'skipped';
    }
    default: {
      throw new Error(`Invalid status value: ${str}`);
    }
  }
}

function parseRequiredString(value: unknown, key: string): string {
  if (typeof value !== 'string' || value.length === 0) {
    throw new TypeError(`Missing or invalid required string field: ${key}`);
  }
  return value;
}

function parseTestRun(input: unknown): TestRun {
  const data = testRunGuards.asRecord(input, 'test run');

  return {
    blockedCount: testRunGuards.getRequiredNumber(data, 'blocked_count'),
    branch: testRunGuards.getOptionalString(data, 'branch'),
    buildNumber: testRunGuards.getOptionalString(data, 'build_number'),
    buildUrl: testRunGuards.getOptionalString(data, 'build_url'),
    commitSha: testRunGuards.getOptionalString(data, 'commit_sha'),
    completedAt: testRunGuards.getOptionalString(data, 'completed_at'),
    createdAt: testRunGuards.getRequiredString(data, 'created_at'),
    description: testRunGuards.getOptionalString(data, 'description'),
    durationSeconds: testRunGuards.getOptionalNumber(data, 'duration_seconds'),
    environment: testRunGuards.getOptionalString(data, 'environment'),
    errorCount: testRunGuards.getRequiredNumber(data, 'error_count'),
    executedBy: testRunGuards.getOptionalString(data, 'executed_by'),
    externalRunId: testRunGuards.getOptionalString(data, 'external_run_id'),
    failedCount: testRunGuards.getRequiredNumber(data, 'failed_count'),
    failureSummary: testRunGuards.getOptionalString(data, 'failure_summary'),
    id: testRunGuards.toStringId(data['id'], 'id'),
    initiatedBy: testRunGuards.getOptionalString(data, 'initiated_by'),
    metadata: testRunGuards.getOptionalRecord(data, 'run_metadata'),
    name: testRunGuards.getRequiredString(data, 'name'),
    notes: testRunGuards.getOptionalString(data, 'notes'),
    passRate: testRunGuards.getOptionalNumber(data, 'pass_rate'),
    passedCount: testRunGuards.getRequiredNumber(data, 'passed_count'),
    projectId: testRunGuards.getRequiredString(data, 'project_id'),
    runNumber: testRunGuards.toStringId(data['run_number'], 'run_number'),
    runType: parseTestRunType(data['run_type']),
    scheduledAt: testRunGuards.getOptionalString(data, 'scheduled_at'),
    skippedCount: testRunGuards.getRequiredNumber(data, 'skipped_count'),
    startedAt: testRunGuards.getOptionalString(data, 'started_at'),
    status: parseTestRunStatus(data['status']),
    suiteId: testRunGuards.getOptionalString(data, 'suite_id'),
    tags: testRunGuards.getOptionalStringArray(data, 'tags'),
    totalTests: testRunGuards.getRequiredNumber(data, 'total_tests'),
    updatedAt: testRunGuards.getRequiredString(data, 'updated_at'),
    version: testRunGuards.getRequiredNumber(data, 'version'),
    webhookId: testRunGuards.getOptionalString(data, 'webhook_id'),
  };
}

function parseTestResult(input: unknown): TestResult {
  const data = testRunGuards.asRecord(input, 'test result');
  const stepResultsRaw = testRunGuards.getOptionalArray(data, 'step_results');

  return {
    actualResult: testRunGuards.getOptionalString(data, 'actual_result'),
    attachments: testRunGuards.getOptionalStringArray(data, 'attachments'),
    completedAt: testRunGuards.getOptionalString(data, 'completed_at'),
    createdAt: testRunGuards.getRequiredString(data, 'created_at'),
    createdDefectId: testRunGuards.getOptionalString(data, 'created_defect_id'),
    durationSeconds: testRunGuards.getOptionalNumber(data, 'duration_seconds'),
    errorMessage: testRunGuards.getOptionalString(data, 'error_message'),
    executedBy: testRunGuards.getOptionalString(data, 'executed_by'),
    failureReason: testRunGuards.getOptionalString(data, 'failure_reason'),
    id: testRunGuards.toStringId(data['id'], 'id'),
    isFlaky: testRunGuards.getRequiredBoolean(data, 'is_flaky'),
    linkedDefectIds: testRunGuards.getOptionalStringArray(data, 'linked_defect_ids'),
    logsUrl: testRunGuards.getOptionalString(data, 'logs_url'),
    metadata: testRunGuards.getOptionalRecord(data, 'run_metadata'),
    notes: testRunGuards.getOptionalString(data, 'notes'),
    retryCount: testRunGuards.getRequiredNumber(data, 'retry_count'),
    runId: testRunGuards.getRequiredString(data, 'run_id'),
    screenshots: testRunGuards.getOptionalStringArray(data, 'screenshots'),
    stackTrace: testRunGuards.getOptionalString(data, 'stack_trace'),
    startedAt: testRunGuards.getOptionalString(data, 'started_at'),
    status: parseTestResultStatus(data['status']),
    stepResults: parseStepResults(stepResultsRaw),
    testCaseId: testRunGuards.getRequiredString(data, 'test_case_id'),
    updatedAt: testRunGuards.getRequiredString(data, 'updated_at'),
  };
}

function parseStepResults(stepResultsRaw: unknown[] | undefined): TestResult['stepResults'] {
  if (stepResultsRaw === undefined) {
    return undefined;
  }
  return stepResultsRaw.map((item: unknown) => {
    const step = testRunGuards.asRecord(item, 'step_result');
    return {
      actualResult: testRunGuards.getOptionalString(step, 'actual_result'),
      notes: testRunGuards.getOptionalString(step, 'notes'),
      status: parseTestResultStatus(step['status']),
      stepNumber: testRunGuards.getRequiredNumber(step, 'step_number'),
    };
  });
}

function parseTestRunActivitiesResponse(input: unknown): {
  runId: string;
  activities: TestRunActivity[];
} {
  const data = testRunGuards.asRecord(input, 'activities response');
  const activitiesRaw = testRunGuards.getRequiredArray(data, 'activities');
  const activities = activitiesRaw.map((item: unknown): TestRunActivity => {
    const a = testRunGuards.asRecord(item, 'activity');
    return {
      activityType: testRunGuards.getRequiredString(a, 'activity_type'),
      createdAt: testRunGuards.getRequiredString(a, 'created_at'),
      description: testRunGuards.getOptionalString(a, 'description'),
      fromValue: testRunGuards.getOptionalString(a, 'from_value'),
      id: testRunGuards.toStringId(a['id'], 'id'),
      metadata: testRunGuards.getOptionalRecord(a, 'run_metadata'),
      performedBy: testRunGuards.getOptionalString(a, 'performed_by'),
      runId: testRunGuards.getRequiredString(a, 'run_id'),
      toValue: testRunGuards.getOptionalString(a, 'to_value'),
    };
  });

  return { activities, runId: testRunGuards.getRequiredString(data, 'run_id') };
}

function parseTestRunStats(input: unknown): TestRunStats {
  const data = testRunGuards.asRecord(input, 'test run stats');

  return {
    averageDurationSeconds: testRunGuards.getOptionalNumber(data, 'average_duration_seconds') ?? 0,
    averagePassRate: testRunGuards.getOptionalNumber(data, 'average_pass_rate') ?? 0,
    byStatus: parseNumberMap(testRunGuards.getOptionalRecord(data, 'by_status')),
    byType: parseNumberMap(testRunGuards.getOptionalRecord(data, 'by_type')),
    projectId: testRunGuards.getRequiredString(data, 'project_id'),
    recentRuns: (testRunGuards.getOptionalArray(data, 'recent_runs') ?? []).map((item: unknown) =>
      parseTestRun(item),
    ),
    totalRuns: testRunGuards.getOptionalNumber(data, 'total_runs') ?? 0,
  };
}

function parseNumberMap(input: Record<string, unknown> | undefined): Record<string, number> {
  if (input === undefined) {
    return {};
  }
  const out: Record<string, number> = {};
  for (const [key, value] of Object.entries(input)) {
    if (typeof value !== 'number' || !Number.isFinite(value)) {
      throw new TypeError(`Invalid number map value for key: ${key}`);
    }
    out[key] = value;
  }
  return out;
}

function parseIdStatusTimestamp(input: unknown): {
  id: string;
  status: string;
  startedAt?: string | undefined;
  completedAt?: string | undefined;
  passRate?: number | undefined;
  isActiveVersion?: boolean | undefined;
} {
  const data = testRunGuards.asRecord(input, 'response');
  return {
    completedAt: testRunGuards.getOptionalString(data, 'completed_at'),
    id: testRunGuards.toStringId(data['id'], 'id'),
    isActiveVersion: testRunGuards.getOptionalBoolean(data, 'is_active_version'),
    passRate: testRunGuards.getOptionalNumber(data, 'pass_rate'),
    startedAt: testRunGuards.getOptionalString(data, 'started_at'),
    status: testRunGuards.getRequiredString(data, 'status'),
  };
}

function parseIdRunNumber(input: unknown): { id: string; runNumber: string } {
  const data = testRunGuards.asRecord(input, 'create response');
  return {
    id: testRunGuards.toStringId(data['id'], 'id'),
    runNumber: testRunGuards.toStringId(data['run_number'], 'run_number'),
  };
}

function parseIdVersion(input: unknown): { id: string; version: number } {
  const data = testRunGuards.asRecord(input, 'update response');
  return {
    id: testRunGuards.toStringId(data['id'], 'id'),
    version: testRunGuards.getRequiredNumber(data, 'version'),
  };
}

function parseCancelResponse(input: unknown): { id: string; status: string } {
  const data = testRunGuards.asRecord(input, 'cancel response');
  return {
    id: testRunGuards.toStringId(data['id'], 'id'),
    status: testRunGuards.getRequiredString(data, 'status'),
  };
}

function parseBulkSubmitResponse(input: unknown): {
  submitted: number;
  passed: number;
  failed: number;
  runStatus: string;
  passRate: number;
} {
  const data = testRunGuards.asRecord(input, 'bulk submit response');
  return {
    failed: testRunGuards.getRequiredNumber(data, 'failed'),
    passRate: testRunGuards.getRequiredNumber(data, 'pass_rate'),
    passed: testRunGuards.getRequiredNumber(data, 'passed'),
    runStatus: testRunGuards.getRequiredString(data, 'run_status'),
    submitted: testRunGuards.getRequiredNumber(data, 'submitted'),
  };
}

const testRunParsers = {
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
  testRunParsers,
};
