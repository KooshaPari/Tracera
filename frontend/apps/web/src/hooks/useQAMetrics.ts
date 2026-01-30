import { useQuery } from "@tanstack/react-query";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// ==================== Types ====================

export interface QAMetricsSummary {
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

export interface PassRateTrend {
	projectId: string;
	days: number;
	trend: Array<{
		date: string;
		totalRuns: number;
		avgPassRate: number;
		totalPassed: number;
		totalFailed: number;
	}>;
}

export interface CoverageMetrics {
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

export interface DefectDensity {
	projectId: string;
	overallDefectDensity: number;
	totalExecutions: number;
	totalFailures: number;
	testCasesWithFailures: number;
	topFailingTests: Array<{
		testCaseId: string;
		totalExecutions: number;
		failureCount: number;
		failureRate: number;
	}>;
}

export interface FlakyTests {
	projectId: string;
	markedFlaky: Array<{
		testCaseId: string;
		flakyOccurrences: number;
	}>;
	markedFlakyCount: number;
	potentiallyFlaky: Array<{
		testCaseId: string;
		inconsistentDays: number;
	}>;
	potentiallyFlakyCount: number;
}

export interface ExecutionHistory {
	projectId: string;
	days: number;
	runs: Array<{
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
	}>;
}

// ==================== Transform Functions ====================

function transformSummary(data: any): QAMetricsSummary {
	return {
		projectId: data.project_id,
		testCases: {
			total: data.test_cases?.total || 0,
			byStatus: data.test_cases?.by_status || {},
			byPriority: data.test_cases?.by_priority || {},
			automatedCount: data.test_cases?.automated_count || 0,
			manualCount: data.test_cases?.manual_count || 0,
			automationPercentage: data.test_cases?.automation_percentage || 0,
		},
		testSuites: {
			total: data.test_suites?.total || 0,
			byStatus: data.test_suites?.by_status || {},
			totalTestCases: data.test_suites?.total_test_cases || 0,
		},
		testRuns: {
			total: data.test_runs?.total || 0,
			byStatus: data.test_runs?.by_status || {},
			byType: data.test_runs?.by_type || {},
			averagePassRate: data.test_runs?.average_pass_rate || 0,
			averageDurationSeconds: data.test_runs?.average_duration_seconds || 0,
		},
		coverage: {
			totalRequirements: data.coverage?.total_requirements || 0,
			coveredRequirements: data.coverage?.covered_requirements || 0,
			uncoveredRequirements: data.coverage?.uncovered_requirements || 0,
			coveragePercentage: data.coverage?.coverage_percentage || 0,
			totalMappings: data.coverage?.total_mappings || 0,
			byType: data.coverage?.by_type || {},
		},
	};
}

function transformPassRateTrend(data: any): PassRateTrend {
	return {
		projectId: data.project_id,
		days: data.days,
		trend: (data.trend || []).map((item: any) => ({
			date: item.date,
			totalRuns: item.total_runs,
			avgPassRate: item.avg_pass_rate,
			totalPassed: item.total_passed,
			totalFailed: item.total_failed,
		})),
	};
}

function transformCoverageMetrics(data: any): CoverageMetrics {
	return {
		projectId: data.project_id,
		overall: {
			totalRequirements: data.overall?.total_requirements || 0,
			coveredRequirements: data.overall?.covered_requirements || 0,
			coveragePercentage: data.overall?.coverage_percentage || 0,
		},
		byView: data.by_view || {},
		byType: data.by_type || {},
		gapsCount: data.gaps_count || 0,
		highPriorityGaps: data.high_priority_gaps || 0,
	};
}

function transformDefectDensity(data: any): DefectDensity {
	return {
		projectId: data.project_id,
		overallDefectDensity: data.overall_defect_density || 0,
		totalExecutions: data.total_executions || 0,
		totalFailures: data.total_failures || 0,
		testCasesWithFailures: data.test_cases_with_failures || 0,
		topFailingTests: (data.top_failing_tests || []).map((item: any) => ({
			testCaseId: item.test_case_id,
			totalExecutions: item.total_executions,
			failureCount: item.failure_count,
			failureRate: item.failure_rate,
		})),
	};
}

function transformFlakyTests(data: any): FlakyTests {
	return {
		projectId: data.project_id,
		markedFlaky: (data.marked_flaky || []).map((item: any) => ({
			testCaseId: item.test_case_id,
			flakyOccurrences: item.flaky_occurrences,
		})),
		markedFlakyCount: data.marked_flaky_count || 0,
		potentiallyFlaky: (data.potentially_flaky || []).map((item: any) => ({
			testCaseId: item.test_case_id,
			inconsistentDays: item.inconsistent_days,
		})),
		potentiallyFlakyCount: data.potentially_flaky_count || 0,
	};
}

function transformExecutionHistory(data: any): ExecutionHistory {
	return {
		projectId: data.project_id,
		days: data.days,
		runs: (data.runs || []).map((run: any) => ({
			id: run.id,
			runNumber: run.run_number,
			name: run.name,
			status: run.status,
			runType: run.run_type,
			environment: run.environment,
			buildNumber: run.build_number,
			branch: run.branch,
			startedAt: run.started_at,
			completedAt: run.completed_at,
			durationSeconds: run.duration_seconds,
			totalTests: run.total_tests,
			passedCount: run.passed_count,
			failedCount: run.failed_count,
			passRate: run.pass_rate,
		})),
	};
}

// ==================== Fetch Functions ====================

async function fetchQAMetricsSummary(
	projectId: string,
): Promise<QAMetricsSummary> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/summary?project_id=${projectId}`,
	);
	if (!res.ok) throw new Error("Failed to fetch QA metrics summary");
	const data = await res.json();
	return transformSummary(data);
}

async function fetchPassRateTrend(
	projectId: string,
	days: number = 30,
): Promise<PassRateTrend> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/pass-rate?project_id=${projectId}&days=${days}`,
	);
	if (!res.ok) throw new Error("Failed to fetch pass rate trend");
	const data = await res.json();
	return transformPassRateTrend(data);
}

async function fetchCoverageMetrics(
	projectId: string,
): Promise<CoverageMetrics> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/coverage?project_id=${projectId}`,
	);
	if (!res.ok) throw new Error("Failed to fetch coverage metrics");
	const data = await res.json();
	return transformCoverageMetrics(data);
}

async function fetchDefectDensity(projectId: string): Promise<DefectDensity> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/defect-density?project_id=${projectId}`,
	);
	if (!res.ok) throw new Error("Failed to fetch defect density");
	const data = await res.json();
	return transformDefectDensity(data);
}

async function fetchFlakyTests(projectId: string): Promise<FlakyTests> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/flaky-tests?project_id=${projectId}`,
	);
	if (!res.ok) throw new Error("Failed to fetch flaky tests");
	const data = await res.json();
	return transformFlakyTests(data);
}

async function fetchExecutionHistory(
	projectId: string,
	days: number = 7,
): Promise<ExecutionHistory> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/execution-history?project_id=${projectId}&days=${days}`,
	);
	if (!res.ok) throw new Error("Failed to fetch execution history");
	const data = await res.json();
	return transformExecutionHistory(data);
}

// ==================== Hooks ====================

export function useQAMetricsSummary(projectId: string | undefined) {
	return useQuery({
		queryKey: ["qaMetrics", "summary", projectId],
		queryFn: () => fetchQAMetricsSummary(projectId!),
		enabled: !!projectId,
	});
}

export function usePassRateTrend(
	projectId: string | undefined,
	days: number = 30,
) {
	return useQuery({
		queryKey: ["qaMetrics", "passRate", projectId, days],
		queryFn: () => fetchPassRateTrend(projectId!, days),
		enabled: !!projectId,
	});
}

export function useCoverageMetrics(projectId: string | undefined) {
	return useQuery({
		queryKey: ["qaMetrics", "coverage", projectId],
		queryFn: () => fetchCoverageMetrics(projectId!),
		enabled: !!projectId,
	});
}

export function useDefectDensity(projectId: string | undefined) {
	return useQuery({
		queryKey: ["qaMetrics", "defectDensity", projectId],
		queryFn: () => fetchDefectDensity(projectId!),
		enabled: !!projectId,
	});
}

export function useFlakyTests(projectId: string | undefined) {
	return useQuery({
		queryKey: ["qaMetrics", "flakyTests", projectId],
		queryFn: () => fetchFlakyTests(projectId!),
		enabled: !!projectId,
	});
}

export function useExecutionHistory(
	projectId: string | undefined,
	days: number = 7,
) {
	return useQuery({
		queryKey: ["qaMetrics", "executionHistory", projectId, days],
		queryFn: () => fetchExecutionHistory(projectId!, days),
		enabled: !!projectId,
	});
}
