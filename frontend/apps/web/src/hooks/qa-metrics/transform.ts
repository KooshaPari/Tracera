import type {
  CoverageMetrics,
  DefectDensity,
  ExecutionHistory,
  FlakyTests,
  PassRateTrend,
  QAMetricsSummary,
} from './types';

import {
  asArray,
  asCoverageByView,
  asNumber,
  asOptionalNumber,
  asOptionalString,
  asRecord,
  asRecordNumberMap,
  asString,
} from './coerce';

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

export {
  transformCoverageMetrics,
  transformDefectDensity,
  transformExecutionHistory,
  transformFlakyTests,
  transformPassRateTrend,
  transformSummary,
};
