import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	TestResult,
	TestResultStatus,
	TestRun,
	TestRunActivity,
	TestRunStats,
	TestRunStatus,
	TestRunType,
} from "@tracertm/types";
import { getAuthHeaders } from "@/api/client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformTestRun(data: any): TestRun {
	return {
		id: data.id,
		runNumber: data.run_number,
		projectId: data.project_id,
		suiteId: data.suite_id,
		name: data.name,
		description: data.description,
		status: data.status,
		runType: data.run_type,
		environment: data.environment,
		buildNumber: data.build_number,
		buildUrl: data.build_url,
		branch: data.branch,
		commitSha: data.commit_sha,
		scheduledAt: data.scheduled_at,
		startedAt: data.started_at,
		completedAt: data.completed_at,
		durationSeconds: data.duration_seconds,
		initiatedBy: data.initiated_by,
		executedBy: data.executed_by,
		totalTests: data.total_tests,
		passedCount: data.passed_count,
		failedCount: data.failed_count,
		skippedCount: data.skipped_count,
		blockedCount: data.blocked_count,
		errorCount: data.error_count,
		passRate: data.pass_rate,
		notes: data.notes,
		failureSummary: data.failure_summary,
		tags: data.tags,
		externalRunId: data.external_run_id,
		webhookId: data.webhook_id,
		metadata: data.run_metadata,
		version: data.version,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

function transformTestResult(data: any): TestResult {
	return {
		id: data.id,
		runId: data.run_id,
		testCaseId: data.test_case_id,
		status: data.status,
		startedAt: data.started_at,
		completedAt: data.completed_at,
		durationSeconds: data.duration_seconds,
		executedBy: data.executed_by,
		actualResult: data.actual_result,
		failureReason: data.failure_reason,
		errorMessage: data.error_message,
		stackTrace: data.stack_trace,
		screenshots: data.screenshots,
		logsUrl: data.logs_url,
		attachments: data.attachments,
		stepResults: data.step_results,
		linkedDefectIds: data.linked_defect_ids,
		createdDefectId: data.created_defect_id,
		retryCount: data.retry_count,
		isFlaky: data.is_flaky,
		notes: data.notes,
		metadata: data.run_metadata,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
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
	params.set("project_id", filters.projectId);
	if (filters.status) params.set("status", filters.status);
	if (filters.runType) params.set("run_type", filters.runType);
	if (filters.suiteId) params.set("suite_id", filters.suiteId);
	if (filters.environment) params.set("environment", filters.environment);
	if (filters.initiatedBy) params.set("initiated_by", filters.initiatedBy);
	if (filters.search) params.set("search", filters.search);
	if (filters.skip !== undefined) params.set("skip", String(filters.skip));
	if (filters.limit !== undefined) params.set("limit", String(filters.limit));

	const res = await fetch(`${API_URL}/api/v1/test-runs?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...getAuthHeaders(),
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch test runs: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		testRuns: (data.test_runs || []).map(transformTestRun),
		total: data.total || 0,
	};
}

async function fetchTestRun(id: string): Promise<TestRun> {
	const res = await fetch(`${API_URL}/api/v1/test-runs/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch test run");
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

async function createTestRun(
	data: CreateTestRunData,
): Promise<{ id: string; runNumber: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/test-runs?project_id=${data.projectId}`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify({
				name: data.name,
				description: data.description,
				suite_id: data.suiteId,
				run_type: data.runType || "manual",
				environment: data.environment,
				build_number: data.buildNumber,
				build_url: data.buildUrl,
				branch: data.branch,
				commit_sha: data.commitSha,
				scheduled_at: data.scheduledAt,
				initiated_by: data.initiatedBy,
				notes: data.notes,
				tags: data.tags,
				external_run_id: data.externalRunId,
				metadata: data.metadata || {},
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to create test run");
	const result = await res.json();
	return { id: result.id, runNumber: result.run_number };
}

async function updateTestRun(
	id: string,
	data: Partial<CreateTestRunData>,
): Promise<{ id: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/test-runs/${id}`, {
		method: "PUT",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			name: data.name,
			description: data.description,
			environment: data.environment,
			build_number: data.buildNumber,
			build_url: data.buildUrl,
			branch: data.branch,
			commit_sha: data.commitSha,
			notes: data.notes,
			tags: data.tags,
			metadata: data.metadata,
		}),
	});
	if (!res.ok) throw new Error("Failed to update test run");
	return res.json();
}

async function startTestRun(
	id: string,
	executedBy?: string,
): Promise<{ id: string; status: string; startedAt: string }> {
	const res = await fetch(`${API_URL}/api/v1/test-runs/${id}/start`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			executed_by: executedBy,
		}),
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to start test run: ${errorText}`);
	}
	const result = await res.json();
	return {
		id: result.id,
		status: result.status,
		startedAt: result.started_at,
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
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			failure_summary: failureSummary,
			notes,
		}),
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to complete test run: ${errorText}`);
	}
	const result = await res.json();
	return {
		id: result.id,
		status: result.status,
		passRate: result.pass_rate,
		completedAt: result.completed_at,
	};
}

async function cancelTestRun(
	id: string,
	reason?: string,
): Promise<{ id: string; status: string }> {
	const res = await fetch(`${API_URL}/api/v1/test-runs/${id}/cancel`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			reason,
		}),
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to cancel test run: ${errorText}`);
	}
	return res.json();
}

async function deleteTestRun(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/test-runs/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete test run");
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
	stepResults?: Array<{
		stepNumber: number;
		status: TestResultStatus;
		actualResult?: string;
		notes?: string;
	}>;
	notes?: string;
	isFlaky?: boolean;
	linkedDefectIds?: string[];
	createdDefectId?: string;
	metadata?: Record<string, unknown>;
}

async function submitTestResult(
	runId: string,
	data: SubmitTestResultData,
): Promise<TestResult> {
	const res = await fetch(`${API_URL}/api/v1/test-runs/${runId}/results`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			test_case_id: data.testCaseId,
			status: data.status,
			executed_by: data.executedBy,
			actual_result: data.actualResult,
			failure_reason: data.failureReason,
			error_message: data.errorMessage,
			stack_trace: data.stackTrace,
			screenshots: data.screenshots,
			logs_url: data.logsUrl,
			attachments: data.attachments,
			step_results: data.stepResults,
			notes: data.notes,
			is_flaky: data.isFlaky || false,
			linked_defect_ids: data.linkedDefectIds,
			created_defect_id: data.createdDefectId,
			metadata: data.metadata,
		}),
	});
	if (!res.ok) throw new Error("Failed to submit test result");
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
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			results: results.map((r) => ({
				test_case_id: r.testCaseId,
				status: r.status,
				executed_by: r.executedBy,
				actual_result: r.actualResult,
				failure_reason: r.failureReason,
				error_message: r.errorMessage,
				stack_trace: r.stackTrace,
				screenshots: r.screenshots,
				logs_url: r.logsUrl,
				notes: r.notes,
				is_flaky: r.isFlaky || false,
			})),
		}),
	});
	if (!res.ok) throw new Error("Failed to submit bulk test results");
	const result = await res.json();
	return {
		submitted: result.submitted,
		passed: result.passed,
		failed: result.failed,
		runStatus: result.run_status,
		passRate: result.pass_rate,
	};
}

async function fetchTestRunResults(runId: string): Promise<TestResult[]> {
	const res = await fetch(`${API_URL}/api/v1/test-runs/${runId}/results`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch test run results");
	const data = await res.json();
	return (data.results || []).map(transformTestResult);
}

async function fetchTestRunActivities(
	runId: string,
	limit = 50,
): Promise<{ runId: string; activities: TestRunActivity[] }> {
	const res = await fetch(
		`${API_URL}/api/v1/test-runs/${runId}/activities?limit=${limit}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch activities");
	const data = await res.json();
	return {
		runId: data.run_id,
		activities: (data.activities || []).map((a: any) => ({
			id: a.id,
			runId: a.run_id,
			activityType: a.activity_type,
			fromValue: a.from_value,
			toValue: a.to_value,
			description: a.description,
			performedBy: a.performed_by,
			metadata: a.run_metadata,
			createdAt: a.created_at,
		})),
	};
}

async function fetchTestRunStats(projectId: string): Promise<TestRunStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/test-runs/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch test run stats");
	const data = await res.json();
	return {
		projectId: data.project_id,
		totalRuns: data.total_runs || 0,
		byStatus: data.by_status || {},
		byType: data.by_type || {},
		averagePassRate: data.average_pass_rate || 0,
		averageDurationSeconds: data.average_duration_seconds || 0,
		recentRuns: (data.recent_runs || []).map(transformTestRun),
	};
}

// React Query hooks

export function useTestRuns(filters: TestRunFilters) {
	return useQuery({
		queryKey: ["testRuns", filters],
		queryFn: () => fetchTestRuns(filters),
		enabled: !!filters.projectId,
	});
}

export function useTestRun(id: string) {
	return useQuery({
		queryKey: ["testRuns", id],
		queryFn: () => fetchTestRun(id),
		enabled: !!id,
	});
}

export function useCreateTestRun() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createTestRun,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["testRuns"] });
		},
	});
}

export function useUpdateTestRun() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			data,
		}: {
			id: string;
			data: Partial<CreateTestRunData>;
		}) => updateTestRun(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testRuns"] });
			queryClient.invalidateQueries({ queryKey: ["testRuns", id] });
		},
	});
}

export function useStartTestRun() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, executedBy }: { id: string; executedBy?: string }) =>
			startTestRun(id, executedBy),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testRuns"] });
			queryClient.invalidateQueries({ queryKey: ["testRuns", id] });
			queryClient.invalidateQueries({ queryKey: ["testRunActivities", id] });
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
			queryClient.invalidateQueries({ queryKey: ["testRuns"] });
			queryClient.invalidateQueries({ queryKey: ["testRuns", id] });
			queryClient.invalidateQueries({ queryKey: ["testRunActivities", id] });
		},
	});
}

export function useCancelTestRun() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, reason }: { id: string; reason?: string }) =>
			cancelTestRun(id, reason),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testRuns"] });
			queryClient.invalidateQueries({ queryKey: ["testRuns", id] });
			queryClient.invalidateQueries({ queryKey: ["testRunActivities", id] });
		},
	});
}

export function useDeleteTestRun() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteTestRun,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["testRuns"] });
		},
	});
}

export function useSubmitTestResult() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			runId,
			data,
		}: {
			runId: string;
			data: SubmitTestResultData;
		}) => submitTestResult(runId, data),
		onSuccess: (_, { runId }) => {
			queryClient.invalidateQueries({ queryKey: ["testRunResults", runId] });
			queryClient.invalidateQueries({ queryKey: ["testRuns", runId] });
		},
	});
}

export function useSubmitBulkTestResults() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			runId,
			results,
		}: {
			runId: string;
			results: SubmitTestResultData[];
		}) => submitBulkTestResults(runId, results),
		onSuccess: (_, { runId }) => {
			queryClient.invalidateQueries({ queryKey: ["testRunResults", runId] });
			queryClient.invalidateQueries({ queryKey: ["testRuns", runId] });
		},
	});
}

export function useTestRunResults(runId: string) {
	return useQuery({
		queryKey: ["testRunResults", runId],
		queryFn: () => fetchTestRunResults(runId),
		enabled: !!runId,
	});
}

export function useTestRunActivities(runId: string, limit = 50) {
	return useQuery({
		queryKey: ["testRunActivities", runId, limit],
		queryFn: () => fetchTestRunActivities(runId, limit),
		enabled: !!runId,
	});
}

export function useTestRunStats(projectId: string) {
	return useQuery({
		queryKey: ["testRunStats", projectId],
		queryFn: () => fetchTestRunStats(projectId),
		enabled: !!projectId,
	});
}
