import type {
  TestSuite,
  TestSuiteActivity,
  TestSuiteStats,
  TestSuiteTestCase,
} from '@tracertm/types';

import {
  asJsonObject,
  getBoolean,
  getNumber,
  getOptionalNumber,
  getOptionalRecord,
  getOptionalRecordOfNumber,
  getOptionalRecordOfString,
  getOptionalString,
  getOptionalStringArray,
  getString,
  getTestSuiteStatus,
} from './decoders';

function decodeTestSuite(value: unknown): TestSuite {
  const obj = asJsonObject(value, 'TestSuite');
  return {
    automatedCount: getNumber(obj, 'automated_count'),
    category: getOptionalString(obj, 'category'),
    createdAt: getString(obj, 'created_at'),
    description: getOptionalString(obj, 'description'),
    environmentVariables: getOptionalRecordOfString(obj, 'environment_variables'),
    estimatedDurationMinutes: getOptionalNumber(obj, 'estimated_duration_minutes'),
    id: getString(obj, 'id'),
    isParallelExecution: getBoolean(obj, 'is_parallel_execution'),
    lastRunAt: getOptionalString(obj, 'last_run_at'),
    lastRunStatus: getOptionalString(obj, 'last_run_status'),
    manualCount: getNumber(obj, 'manual_count'),
    metadata: getOptionalRecord(obj, 'suite_metadata'),
    name: getString(obj, 'name'),
    objective: getOptionalString(obj, 'objective'),
    orderIndex: getNumber(obj, 'order_index'),
    owner: getOptionalString(obj, 'owner'),
    parentId: getOptionalString(obj, 'parent_id'),
    passRate: getOptionalNumber(obj, 'pass_rate'),
    projectId: getString(obj, 'project_id'),
    requiredEnvironment: getOptionalString(obj, 'required_environment'),
    responsibleTeam: getOptionalString(obj, 'responsible_team'),
    setupInstructions: getOptionalString(obj, 'setup_instructions'),
    status: getTestSuiteStatus(obj, 'status'),
    suiteNumber: getString(obj, 'suite_number'),
    tags: getOptionalStringArray(obj, 'tags'),
    teardownInstructions: getOptionalString(obj, 'teardown_instructions'),
    totalTestCases: getNumber(obj, 'total_test_cases'),
    updatedAt: getString(obj, 'updated_at'),
    version: getNumber(obj, 'version'),
  };
}

function decodeTestSuiteTestCase(value: unknown): TestSuiteTestCase {
  const obj = asJsonObject(value, 'TestSuiteTestCase');
  return {
    createdAt: getString(obj, 'created_at'),
    customParameters: getOptionalRecord(obj, 'custom_parameters'),
    id: getString(obj, 'id'),
    isMandatory: getBoolean(obj, 'is_mandatory'),
    orderIndex: getNumber(obj, 'order_index'),
    skipReason: getOptionalString(obj, 'skip_reason'),
    suiteId: getString(obj, 'suite_id'),
    testCaseId: getString(obj, 'test_case_id'),
  };
}

function decodeTestSuiteActivity(value: unknown): TestSuiteActivity {
  const obj = asJsonObject(value, 'TestSuiteActivity');
  return {
    activityType: getString(obj, 'activity_type'),
    createdAt: getString(obj, 'created_at'),
    description: getOptionalString(obj, 'description'),
    fromValue: getOptionalString(obj, 'from_value'),
    id: getString(obj, 'id'),
    metadata: getOptionalRecord(obj, 'activity_metadata'),
    performedBy: getOptionalString(obj, 'performed_by'),
    suiteId: getString(obj, 'suite_id'),
    toValue: getOptionalString(obj, 'to_value'),
  };
}

function decodeTestSuiteStats(value: unknown): TestSuiteStats {
  const obj = asJsonObject(value, 'TestSuiteStats');
  return {
    automatedTestCases: getOptionalNumber(obj, 'automated_test_cases') ?? 0,
    byCategory: getOptionalRecordOfNumber(obj, 'by_category') ?? {},
    byStatus: getOptionalRecordOfNumber(obj, 'by_status') ?? {},
    projectId: getString(obj, 'project_id'),
    total: getOptionalNumber(obj, 'total') ?? 0,
    totalTestCases: getOptionalNumber(obj, 'total_test_cases') ?? 0,
  };
}

export { decodeTestSuite, decodeTestSuiteActivity, decodeTestSuiteStats, decodeTestSuiteTestCase };
