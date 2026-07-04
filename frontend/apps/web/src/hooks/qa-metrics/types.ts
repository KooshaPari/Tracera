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

export type {
  CoverageMetrics,
  DefectDensity,
  ExecutionHistory,
  FlakyTests,
  PassRateTrend,
  QAMetricsSummary,
};
