import type { UseQueryResult } from '@tanstack/react-query';

import { useQuery } from '@tanstack/react-query';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

interface QAMetricsSummary {
  projectId: string;
  testCases: {
    total: number;
    byStatus: Record<string, number>;
    byPriority: Record<string, number>;
    automatedCount: number;
    manualCount: number;
    automationPercentage: number;
  };
  testSuites: {
    total: number;
    byStatus: Record<string, number>;
    totalTestCases: number;
  };
  testRuns: {
    total: number;
    byStatus: Record<string, number>;
    byType: Record<string, number>;
    averagePassRate: number;
    averageDurationSeconds: number;
  };
  coverage: {
    totalRequirements: number;
    coveredRequirements: number;
    uncoveredRequirements: number;
    coveragePercentage: number;
    totalMappings: number;
    byType: Record<string, number>;
  };
}

interface PassRateTrend {
  projectId: string;
  days: number;
  trend: {
    date: string;
    totalRuns: number;
    avgPassRate: number;
    totalPassed: number;
    totalFailed: number;
  }[];
}

interface CoverageMetrics {
  projectId: string;
  overall: {
    totalRequirements: number;
    coveredRequirements: number;
    coveragePercentage: number;
  };
  byView: Record<
    string,
    {
      total: number;
      covered: number;
      percentage: number;
    }
  >;
  byType: Record<string, number>;
  gapsCount: number;
  highPriorityGaps: number;
}

interface DefectDensity {
  projectId: string;
  overallDefectDensity: number;
  totalExecutions: number;
  totalFailures: number;
  testCasesWithFailures: number;
  topFailingTests: {
    testCaseId: string;
    totalExecutions: number;
    failureCount: number;
    failureRate: number;
  }[];
}

interface FlakyTests {
  projectId: string;
  markedFlaky: {
    testCaseId: string;
    flakyOccurrences: number;
  }[];
  markedFlakyCount: number;
  potentiallyFlaky: {
    testCaseId: string;
    inconsistentDays: number;
  }[];
  potentiallyFlakyCount: number;
}

interface ExecutionHistory {
  projectId: string;
  days: number;
  runs: {
    id: string;
    runNumber: string;
    name: string;
    status: string;
    runType: string;
    environment?: string | undefined;
    buildNumber?: string | undefined;
    branch?: string | undefined;
    startedAt?: string | undefined;
    completedAt?: string | undefined;
    durationSeconds?: number | undefined;
    totalTests: number;
    passedCount: number;
    failedCount: number;
    passRate?: number | undefined;
  }[];
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && Boolean(value) && !Array.isArray(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  if (isRecord(value)) {
    return value;
  }
  return {};
}

function asArray(value: unknown): unknown[] {
  if (Array.isArray(value)) {
    return value;
  }
  return [];
}

function asNumber(value: unknown, fallback: number): number {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === 'string') {
    const parsed = Number(value);
    if (Number.isFinite(parsed)) {
      return parsed;
    }
  }
  return fallback;
}

function asString(value: unknown, fallback: string): string {
  if (typeof value === 'string') {
    return value;
  }
  return fallback;
}

function asOptionalString(value: unknown): string | undefined {
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
}

function asOptionalNumber(value: unknown): number | undefined {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  return undefined;
}

function asRecordNumberMap(value: unknown): Record<string, number> {
  const rec = asRecord(value);
  const out: Record<string, number> = {};
  for (const [key, entryValue] of Object.entries(rec)) {
    const parsedNumber = asNumber(entryValue, Number.NaN);
    if (Number.isFinite(parsedNumber)) {
      out[key] = parsedNumber;
    }
  }
  return out;
}

function asCoverageByView(value: unknown): CoverageMetrics['byView'] {
  const rec = asRecord(value);
  const out: CoverageMetrics['byView'] = {};
  for (const [key, entryValue] of Object.entries(rec)) {
    const entry = asRecord(entryValue);
    out[key] = {
      covered: asNumber(entry['covered'], 0),
      percentage: asNumber(entry['percentage'], 0),
      total: asNumber(entry['total'], 0),
    };
  }
  return out;
}

function transformSummary(data: Record<string, unknown>): QAMetricsSummary {
  const testCasesData = asRecord(data['test_cases']);
  const testSuitesData = asRecord(data['test_suites']);
  const testRunsData = asRecord(data['test_runs']);
  const coverageData = asRecord(data['coverage']);
  return {
    coverage: {
      byType: asRecordNumberMap(coverageData['by_type']),
      coveragePercentage: asNumber(coverageData['coverage_percentage'], 0),
      coveredRequirements: asNumber(coverageData['covered_requirements'], 0),
      totalMappings: asNumber(coverageData['total_mappings'], 0),
      totalRequirements: asNumber(coverageData['total_requirements'], 0),
      uncoveredRequirements: asNumber(coverageData['uncovered_requirements'], 0),
    },
    projectId: asString(data['project_id'], ''),
    testCases: {
      automatedCount: asNumber(testCasesData['automated_count'], 0),
      automationPercentage: asNumber(testCasesData['automation_percentage'], 0),
      byPriority: asRecordNumberMap(testCasesData['by_priority']),
      byStatus: asRecordNumberMap(testCasesData['by_status']),
      manualCount: asNumber(testCasesData['manual_count'], 0),
      total: asNumber(testCasesData['total'], 0),
    },
    testRuns: {
      averageDurationSeconds: asNumber(testRunsData['average_duration_seconds'], 0),
      averagePassRate: asNumber(testRunsData['average_pass_rate'], 0),
      byStatus: asRecordNumberMap(testRunsData['by_status']),
      byType: asRecordNumberMap(testRunsData['by_type']),
      total: asNumber(testRunsData['total'], 0),
    },
    testSuites: {
      byStatus: asRecordNumberMap(testSuitesData['by_status']),
      total: asNumber(testSuitesData['total'], 0),
      totalTestCases: asNumber(testSuitesData['total_test_cases'], 0),
    },
  };
}

function transformPassRateTrend(data: Record<string, unknown>): PassRateTrend {
  return {
    days: asNumber(data['days'], 0),
    projectId: asString(data['project_id'], ''),
    trend: asArray(data['trend']).map((item: unknown) => {
      const trendItem = asRecord(item);
      return {
        avgPassRate: asNumber(trendItem['avg_pass_rate'], 0),
        date: asString(trendItem['date'], ''),
        totalFailed: asNumber(trendItem['total_failed'], 0),
        totalPassed: asNumber(trendItem['total_passed'], 0),
        totalRuns: asNumber(trendItem['total_runs'], 0),
      };
    }),
  };
}

function transformCoverageMetrics(data: Record<string, unknown>): CoverageMetrics {
  const overall = asRecord(data['overall']);
  return {
    byType: asRecordNumberMap(data['by_type']),
    byView: asCoverageByView(data['by_view']),
    gapsCount: asNumber(data['gaps_count'], 0),
    highPriorityGaps: asNumber(data['high_priority_gaps'], 0),
    overall: {
      coveragePercentage: asNumber(overall['coverage_percentage'], 0),
      coveredRequirements: asNumber(overall['covered_requirements'], 0),
      totalRequirements: asNumber(overall['total_requirements'], 0),
    },
    projectId: asString(data['project_id'], ''),
  };
}

function transformDefectDensity(data: Record<string, unknown>): DefectDensity {
  return {
    overallDefectDensity: asNumber(data['overall_defect_density'], 0),
    projectId: asString(data['project_id'], ''),
    testCasesWithFailures: asNumber(data['test_cases_with_failures'], 0),
    topFailingTests: asArray(data['top_failing_tests']).map((item: unknown) => {
      const topFailingTest = asRecord(item);
      return {
        failureCount: asNumber(topFailingTest['failure_count'], 0),
        failureRate: asNumber(topFailingTest['failure_rate'], 0),
        testCaseId: asString(topFailingTest['test_case_id'], ''),
        totalExecutions: asNumber(topFailingTest['total_executions'], 0),
      };
    }),
    totalExecutions: asNumber(data['total_executions'], 0),
    totalFailures: asNumber(data['total_failures'], 0),
  };
}

function transformFlakyTests(data: Record<string, unknown>): FlakyTests {
  return {
    markedFlaky: asArray(data['marked_flaky']).map((item: unknown) => {
      const flakyItem = asRecord(item);
      return {
        flakyOccurrences: asNumber(flakyItem['flaky_occurrences'], 0),
        testCaseId: asString(flakyItem['test_case_id'], ''),
      };
    }),
    markedFlakyCount: asNumber(data['marked_flaky_count'], 0),
    potentiallyFlaky: asArray(data['potentially_flaky']).map((item: unknown) => {
      const potentiallyFlakyItem = asRecord(item);
      return {
        inconsistentDays: asNumber(potentiallyFlakyItem['inconsistent_days'], 0),
        testCaseId: asString(potentiallyFlakyItem['test_case_id'], ''),
      };
    }),
    potentiallyFlakyCount: asNumber(data['potentially_flaky_count'], 0),
    projectId: asString(data['project_id'], ''),
  };
}

function transformExecutionHistory(data: Record<string, unknown>): ExecutionHistory {
  return {
    days: asNumber(data['days'], 0),
    projectId: asString(data['project_id'], ''),
    runs: asArray(data['runs']).map((run: unknown) => {
      const runRecord = asRecord(run);
      return {
        branch: asOptionalString(runRecord['branch']),
        buildNumber: asOptionalString(runRecord['build_number']),
        completedAt: asOptionalString(runRecord['completed_at']),
        durationSeconds: asOptionalNumber(runRecord['duration_seconds']),
        environment: asOptionalString(runRecord['environment']),
        failedCount: asNumber(runRecord['failed_count'], 0),
        id: asString(runRecord['id'], ''),
        name: asString(runRecord['name'], ''),
        passRate: asOptionalNumber(runRecord['pass_rate']),
        passedCount: asNumber(runRecord['passed_count'], 0),
        runNumber: asString(runRecord['run_number'], ''),
        runType: asString(runRecord['run_type'], ''),
        startedAt: asOptionalString(runRecord['started_at']),
        status: asString(runRecord['status'], ''),
        totalTests: asNumber(runRecord['total_tests'], 0),
      };
    }),
  };
}

async function readJsonRecord(res: Response): Promise<Record<string, unknown>> {
  const json: unknown = await res.json();
  return asRecord(json);
}

async function fetchQAMetricsSummary(projectId: string): Promise<QAMetricsSummary> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/summary?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch QA metrics summary');
  }
  const data = await readJsonRecord(res);
  return transformSummary(data);
}

async function fetchPassRateTrend(projectId: string, days = 30): Promise<PassRateTrend> {
  const res = await fetch(
    `${API_URL}/api/v1/qa/metrics/pass-rate?project_id=${projectId}&days=${days}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch pass rate trend');
  }
  const data = await readJsonRecord(res);
  return transformPassRateTrend(data);
}

async function fetchCoverageMetrics(projectId: string): Promise<CoverageMetrics> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/coverage?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch coverage metrics');
  }
  const data = await readJsonRecord(res);
  return transformCoverageMetrics(data);
}

async function fetchDefectDensity(projectId: string): Promise<DefectDensity> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/defect-density?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch defect density');
  }
  const data = await readJsonRecord(res);
  return transformDefectDensity(data);
}

async function fetchFlakyTests(projectId: string): Promise<FlakyTests> {
  const res = await fetch(`${API_URL}/api/v1/qa/metrics/flaky-tests?project_id=${projectId}`, {
    headers: getAuthHeaders(),
  });
  if (!res.ok) {
    throw new Error('Failed to fetch flaky tests');
  }
  const data = await readJsonRecord(res);
  return transformFlakyTests(data);
}

async function fetchExecutionHistory(projectId: string, days = 7): Promise<ExecutionHistory> {
  const res = await fetch(
    `${API_URL}/api/v1/qa/metrics/execution-history?project_id=${projectId}&days=${days}`,
    { headers: getAuthHeaders() },
  );
  if (!res.ok) {
    throw new Error('Failed to fetch execution history');
  }
  const data = await readJsonRecord(res);
  return transformExecutionHistory(data);
}

function useQAMetricsSummary(projectId: string | undefined): UseQueryResult<QAMetricsSummary> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchQAMetricsSummary(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'summary', projectId],
  });
}

function usePassRateTrend(projectId: string | undefined, days = 30): UseQueryResult<PassRateTrend> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchPassRateTrend(projectId, days);
      return result;
    },
    queryKey: ['qaMetrics', 'passRate', projectId, days],
  });
}

function useCoverageMetrics(projectId: string | undefined): UseQueryResult<CoverageMetrics> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchCoverageMetrics(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'coverage', projectId],
  });
}

function useDefectDensity(projectId: string | undefined): UseQueryResult<DefectDensity> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchDefectDensity(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'defectDensity', projectId],
  });
}

function useFlakyTests(projectId: string | undefined): UseQueryResult<FlakyTests> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchFlakyTests(projectId);
      return result;
    },
    queryKey: ['qaMetrics', 'flakyTests', projectId],
  });
}

function useExecutionHistory(
  projectId: string | undefined,
  days = 7,
): UseQueryResult<ExecutionHistory> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      const result = await fetchExecutionHistory(projectId, days);
      return result;
    },
    queryKey: ['qaMetrics', 'executionHistory', projectId, days],
  });
}

export {
  useCoverageMetrics,
  useDefectDensity,
  useExecutionHistory,
  useFlakyTests,
  usePassRateTrend,
  useQAMetricsSummary,
  type CoverageMetrics,
  type DefectDensity,
  type ExecutionHistory,
  type FlakyTests,
  type PassRateTrend,
  type QAMetricsSummary,
};
