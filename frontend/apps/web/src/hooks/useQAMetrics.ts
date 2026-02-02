import { useQuery } from "@tanstack/react-query";
import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

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

function obj(v: unknown): Record<string, unknown> {
	return (typeof v === "object" && v !== null ? v : {}) as Record<string, unknown>;
}
function arr(v: unknown): unknown[] {
	return Array.isArray(v) ? v : [];
}

function transformSummary(data: Record<string, unknown>): QAMetricsSummary {
	const tc = obj(data['test_cases']);
	const ts = obj(data['test_suites']);
	const tr = obj(data['test_runs']);
	const cov = obj(data['coverage']);
	return {
		projectId: (data['project_id'] ?? "") as string,
		testCases: {
			total: (tc['total'] as number) || 0,
			byStatus: (tc['by_status'] as Record<string, number>) || {},
			byPriority: (tc['by_priority'] as Record<string, number>) || {},
			automatedCount: (tc['automated_count'] as number) || 0,
			manualCount: (tc['manual_count'] as number) || 0,
			automationPercentage: (tc['automation_percentage'] as number) || 0,
		},
		testSuites: {
			total: (ts['total'] as number) || 0,
			byStatus: (ts['by_status'] as Record<string, number>) || {},
			totalTestCases: (ts['total_test_cases'] as number) || 0,
		},
		testRuns: {
			total: (tr['total'] as number) || 0,
			byStatus: (tr['by_status'] as Record<string, number>) || {},
			byType: (tr['by_type'] as Record<string, number>) || {},
			averagePassRate: (tr['average_pass_rate'] as number) || 0,
			averageDurationSeconds: (tr['average_duration_seconds'] as number) || 0,
		},
		coverage: {
			totalRequirements: (cov['total_requirements'] as number) || 0,
			coveredRequirements: (cov['covered_requirements'] as number) || 0,
			uncoveredRequirements: (cov['uncovered_requirements'] as number) || 0,
			coveragePercentage: (cov['coverage_percentage'] as number) || 0,
			totalMappings: (cov['total_mappings'] as number) || 0,
			byType: (cov['by_type'] as Record<string, number>) || {},
		},
	};
}

function transformPassRateTrend(data: Record<string, unknown>): PassRateTrend {
	return {
		projectId: (data['project_id'] ?? "") as string,
		days: (data['days'] ?? 0) as number,
		trend: arr(data['trend']).map((item: unknown) => {
			const i = obj(item);
			return {
				date: (i['date'] ?? "") as string,
				totalRuns: (i['total_runs'] ?? 0) as number,
				avgPassRate: (i['avg_pass_rate'] ?? 0) as number,
				totalPassed: (i['total_passed'] ?? 0) as number,
				totalFailed: (i['total_failed'] ?? 0) as number,
			};
		}),
	};
}

function transformCoverageMetrics(data: Record<string, unknown>): CoverageMetrics {
	const overall = obj(data['overall']);
	return {
		projectId: (data['project_id'] ?? "") as string,
		overall: {
			totalRequirements: (overall['total_requirements'] as number) || 0,
			coveredRequirements: (overall['covered_requirements'] as number) || 0,
			coveragePercentage: (overall['coverage_percentage'] as number) || 0,
		},
		byView: (data['by_view'] as CoverageMetrics['byView']) || {},
		byType: (data['by_type'] as Record<string, number>) || {},
		gapsCount: (data['gaps_count'] as number) ?? 0,
		highPriorityGaps: (data['high_priority_gaps'] as number) ?? 0,
	};
}

function transformDefectDensity(data: Record<string, unknown>): DefectDensity {
	return {
		projectId: (data['project_id'] ?? "") as string,
		overallDefectDensity: (data['overall_defect_density'] as number) ?? 0,
		totalExecutions: (data['total_executions'] as number) ?? 0,
		totalFailures: (data['total_failures'] as number) ?? 0,
		testCasesWithFailures: (data['test_cases_with_failures'] as number) ?? 0,
		topFailingTests: arr(data['top_failing_tests']).map((item: unknown) => {
			const i = obj(item);
			return {
				testCaseId: (i['test_case_id'] ?? "") as string,
				totalExecutions: (i['total_executions'] ?? 0) as number,
				failureCount: (i['failure_count'] ?? 0) as number,
				failureRate: (i['failure_rate'] ?? 0) as number,
			};
		}),
	};
}

function transformFlakyTests(data: Record<string, unknown>): FlakyTests {
	return {
		projectId: (data['project_id'] ?? "") as string,
		markedFlaky: arr(data['marked_flaky']).map((item: unknown) => {
			const i = obj(item);
			return {
				testCaseId: (i['test_case_id'] ?? "") as string,
				flakyOccurrences: (i['flaky_occurrences'] ?? 0) as number,
			};
		}),
		markedFlakyCount: (data['marked_flaky_count'] as number) ?? 0,
		potentiallyFlaky: arr(data['potentially_flaky']).map((item: unknown) => {
			const i = obj(item);
			return {
				testCaseId: (i['test_case_id'] ?? "") as string,
				inconsistentDays: (i['inconsistent_days'] ?? 0) as number,
			};
		}),
		potentiallyFlakyCount: (data['potentially_flaky_count'] as number) ?? 0,
	};
}

function transformExecutionHistory(data: Record<string, unknown>): ExecutionHistory {
	return {
		projectId: (data['project_id'] ?? "") as string,
		days: (data['days'] ?? 0) as number,
		runs: arr(data['runs']).map((run: unknown) => {
			const r = obj(run);
			return {
				id: (r['id'] ?? "") as string,
				runNumber: (r['run_number'] ?? "") as string,
				name: (r['name'] ?? "") as string,
				status: (r['status'] ?? "") as string,
				runType: (r['run_type'] ?? "") as string,
				environment: r['environment'] as string | undefined,
				buildNumber: r['build_number'] as string | undefined,
				branch: r['branch'] as string | undefined,
				startedAt: r['started_at'] as string | undefined,
				completedAt: r['completed_at'] as string | undefined,
				durationSeconds: r['duration_seconds'] as number | undefined,
				totalTests: (r['total_tests'] ?? 0) as number,
				passedCount: (r['passed_count'] ?? 0) as number,
				failedCount: (r['failed_count'] ?? 0) as number,
				passRate: r['pass_rate'] as number | undefined,
			};
		}),
	};
}

// ==================== Fetch Functions ====================

async function fetchQAMetricsSummary(
	projectId: string,
): Promise<QAMetricsSummary> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/summary?project_id=${projectId}`,
		{ headers: getAuthHeaders() },
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
		{ headers: getAuthHeaders() },
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
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch coverage metrics");
	const data = await res.json();
	return transformCoverageMetrics(data);
}

async function fetchDefectDensity(projectId: string): Promise<DefectDensity> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/defect-density?project_id=${projectId}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch defect density");
	const data = await res.json();
	return transformDefectDensity(data);
}

async function fetchFlakyTests(projectId: string): Promise<FlakyTests> {
	const res = await fetch(
		`${API_URL}/api/v1/qa/metrics/flaky-tests?project_id=${projectId}`,
		{ headers: getAuthHeaders() },
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
		{ headers: getAuthHeaders() },
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
