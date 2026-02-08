import { useQuery } from '@tanstack/react-query';
import type { UseQueryResult } from '@tanstack/react-query';

import { client } from '@/api/client';

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:4000';

// ==================== Types ====================

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
    environment?: string;
    buildNumber?: string;
    branch?: string;
    startedAt?: string;
    completedAt?: string;
    durationSeconds?: number;
    totalTests: number;
    passedCount: number;
    failedCount: number;
    passRate?: number;
  }[];
}

// ==================== Transform Functions ====================

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
  for (const [k, v] of Object.entries(rec)) {
    const n = asNumber(v, Number.NaN);
    if (Number.isFinite(n)) {
      out[k] = n;
    }
  }
  return out;
}

function transformSummary(data: Record<string, unknown>): QAMetricsSummary {
  const tc = asRecord(data['test_cases']);
  const ts = asRecord(data['test_suites']);
  const tr = asRecord(data['test_runs']);
  const cov = asRecord(data['coverage']);
  return {
    coverage: {
      byType: asRecordNumberMap(cov['by_type']),
      coveragePercentage: asNumber(cov['coverage_percentage'], 0),
      coveredRequirements: asNumber(cov['covered_requirements'], 0),
      totalMappings: asNumber(cov['total_mappings'], 0),
      totalRequirements: asNumber(cov['total_requirements'], 0),
      uncoveredRequirements: asNumber(cov['uncovered_requirements'], 0),
    },
    projectId: asString(data['project_id'], ''),
    testCases: {
      automatedCount: asNumber(tc['automated_count'], 0),
      automationPercentage: asNumber(tc['automation_percentage'], 0),
      byPriority: asRecordNumberMap(tc['by_priority']),
      byStatus: asRecordNumberMap(tc['by_status']),
      manualCount: asNumber(tc['manual_count'], 0),
      total: asNumber(tc['total'], 0),
    },
    testRuns: {
      averageDurationSeconds: asNumber(tr['average_duration_seconds'], 0),
      averagePassRate: asNumber(tr['average_pass_rate'], 0),
      byStatus: asRecordNumberMap(tr['by_status']),
      byType: asRecordNumberMap(tr['by_type']),
      total: asNumber(tr['total'], 0),
    },
    testSuites: {
      byStatus: asRecordNumberMap(ts['by_status']),
      total: asNumber(ts['total'], 0),
      totalTestCases: asNumber(ts['total_test_cases'], 0),
    },
  };
}

function transformPassRateTrend(data: Record<string, unknown>): PassRateTrend {
  return {
    days: asNumber(data['days'], 0),
    projectId: asString(data['project_id'], ''),
    trend: asArray(data['trend']).map((item: unknown) => {
      const i = asRecord(item);
      return {
        avgPassRate: asNumber(i['avg_pass_rate'], 0),
        date: asString(i['date'], ''),
        totalFailed: asNumber(i['total_failed'], 0),
        totalPassed: asNumber(i['total_passed'], 0),
        totalRuns: asNumber(i['total_runs'], 0),
      };
    }),
  };
}

function transformCoverageMetrics(data: Record<string, unknown>): CoverageMetrics {
  const overall = asRecord(data['overall']);
  return {
    byType: asRecordNumberMap(data['by_type']),
    byView: asRecord(data['by_view']) as CoverageMetrics['byView'],
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
      const i = asRecord(item);
      return {
        failureCount: asNumber(i['failure_count'], 0),
        failureRate: asNumber(i['failure_rate'], 0),
        testCaseId: asString(i['test_case_id'], ''),
        totalExecutions: asNumber(i['total_executions'], 0),
      };
    }),
    totalExecutions: asNumber(data['total_executions'], 0),
    totalFailures: asNumber(data['total_failures'], 0),
  };
}

function transformFlakyTests(data: Record<string, unknown>): FlakyTests {
  return {
    markedFlaky: asArray(data['marked_flaky']).map((item: unknown) => {
      const i = asRecord(item);
      return {
        flakyOccurrences: asNumber(i['flaky_occurrences'], 0),
        testCaseId: asString(i['test_case_id'], ''),
      };
    }),
    markedFlakyCount: asNumber(data['marked_flaky_count'], 0),
    potentiallyFlaky: asArray(data['potentially_flaky']).map((item: unknown) => {
      const i = asRecord(item);
      return {
        inconsistentDays: asNumber(i['inconsistent_days'], 0),
        testCaseId: asString(i['test_case_id'], ''),
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
      const r = asRecord(run);
      return {
        branch: asOptionalString(r['branch']),
        buildNumber: asOptionalString(r['build_number']),
        completedAt: asOptionalString(r['completed_at']),
        durationSeconds: asOptionalNumber(r['duration_seconds']),
        environment: asOptionalString(r['environment']),
        failedCount: asNumber(r['failed_count'], 0),
        id: asString(r['id'], ''),
        name: asString(r['name'], ''),
        passRate: asOptionalNumber(r['pass_rate']),
        passedCount: asNumber(r['passed_count'], 0),
        runNumber: asString(r['run_number'], ''),
        runType: asString(r['run_type'], ''),
        startedAt: asOptionalString(r['started_at']),
        status: asString(r['status'], ''),
        totalTests: asNumber(r['total_tests'], 0),
      };
    }),
  };
}

// ==================== Fetch Functions ====================

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

// ==================== Hooks ====================

function useQAMetricsSummary(
  projectId: string | undefined,
): UseQueryResult<QAMetricsSummary, Error> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      return fetchQAMetricsSummary(projectId);
    },
    queryKey: ['qaMetrics', 'summary', projectId],
  });
}

function usePassRateTrend(
  projectId: string | undefined,
  days = 30,
): UseQueryResult<PassRateTrend, Error> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      return fetchPassRateTrend(projectId, days);
    },
    queryKey: ['qaMetrics', 'passRate', projectId, days],
  });
}

function useCoverageMetrics(projectId: string | undefined): UseQueryResult<CoverageMetrics, Error> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      return fetchCoverageMetrics(projectId);
    },
    queryKey: ['qaMetrics', 'coverage', projectId],
  });
}

function useDefectDensity(projectId: string | undefined): UseQueryResult<DefectDensity, Error> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      return fetchDefectDensity(projectId);
    },
    queryKey: ['qaMetrics', 'defectDensity', projectId],
  });
}

function useFlakyTests(projectId: string | undefined): UseQueryResult<FlakyTests, Error> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      return fetchFlakyTests(projectId);
    },
    queryKey: ['qaMetrics', 'flakyTests', projectId],
  });
}

function useExecutionHistory(
  projectId: string | undefined,
  days = 7,
): UseQueryResult<ExecutionHistory, Error> {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => {
      if (projectId === undefined) {
        throw new Error('projectId is required');
      }
      return fetchExecutionHistory(projectId, days);
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
};

export type {
  CoverageMetrics,
  DefectDensity,
  ExecutionHistory,
  FlakyTests,
  PassRateTrend,
  QAMetricsSummary,
};
