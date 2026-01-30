import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	TestCase,
	TestCaseStatus,
	TestCaseType,
	TestCasePriority,
	AutomationStatus,
	TestCaseActivity,
	TestStep,
	TestCaseStats,
} from "@tracertm/types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformTestCase(data: any): TestCase {
	return {
		id: data.id,
		testCaseNumber: data.test_case_number,
		projectId: data.project_id,
		title: data.title,
		description: data.description,
		objective: data.objective,
		status: data.status,
		testType: data.test_type,
		priority: data.priority,
		category: data.category,
		tags: data.tags,
		preconditions: data.preconditions,
		testSteps: data.test_steps?.map((step: any) => ({
			stepNumber: step.step_number,
			action: step.action,
			expectedResult: step.expected_result,
			testData: step.test_data,
		})),
		expectedResult: data.expected_result,
		postconditions: data.postconditions,
		testData: data.test_data,
		automationStatus: data.automation_status,
		automationScriptPath: data.automation_script_path,
		automationFramework: data.automation_framework,
		automationNotes: data.automation_notes,
		estimatedDurationMinutes: data.estimated_duration_minutes,
		createdBy: data.created_by,
		assignedTo: data.assigned_to,
		reviewedBy: data.reviewed_by,
		approvedBy: data.approved_by,
		reviewedAt: data.reviewed_at,
		approvedAt: data.approved_at,
		deprecatedAt: data.deprecated_at,
		deprecationReason: data.deprecation_reason,
		lastExecutedAt: data.last_executed_at,
		lastExecutionResult: data.last_execution_result,
		totalExecutions: data.total_executions || 0,
		passCount: data.pass_count || 0,
		failCount: data.fail_count || 0,
		metadata: data.metadata,
		version: data.version,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

interface TestCaseFilters {
	projectId: string;
	status?: TestCaseStatus;
	testType?: TestCaseType;
	priority?: TestCasePriority;
	automationStatus?: AutomationStatus;
	category?: string;
	assignedTo?: string;
	search?: string;
}

async function fetchTestCases(
	filters: TestCaseFilters,
): Promise<{ testCases: TestCase[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.status) params.set("status", filters.status);
	if (filters.testType) params.set("test_type", filters.testType);
	if (filters.priority) params.set("priority", filters.priority);
	if (filters.automationStatus)
		params.set("automation_status", filters.automationStatus);
	if (filters.category) params.set("category", filters.category);
	if (filters.assignedTo) params.set("assigned_to", filters.assignedTo);
	if (filters.search) params.set("search", filters.search);

	const res = await fetch(`${API_URL}/api/v1/test-cases?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch test cases: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		testCases: (data.test_cases || []).map(transformTestCase),
		total: data.total || 0,
	};
}

async function fetchTestCase(id: string): Promise<TestCase> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`);
	if (!res.ok) throw new Error("Failed to fetch test case");
	const data = await res.json();
	return transformTestCase(data);
}

interface CreateTestCaseData {
	projectId: string;
	title: string;
	description?: string;
	objective?: string;
	testType?: TestCaseType;
	priority?: TestCasePriority;
	category?: string;
	tags?: string[];
	preconditions?: string;
	testSteps?: TestStep[];
	expectedResult?: string;
	postconditions?: string;
	testData?: Record<string, unknown>;
	automationStatus?: AutomationStatus;
	automationScriptPath?: string;
	automationFramework?: string;
	automationNotes?: string;
	estimatedDurationMinutes?: number;
	assignedTo?: string;
	metadata?: Record<string, unknown>;
}

async function createTestCase(
	data: CreateTestCaseData,
): Promise<{ id: string; testCaseNumber: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/test-cases?project_id=${data.projectId}`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({
				title: data.title,
				description: data.description,
				objective: data.objective,
				test_type: data.testType || "functional",
				priority: data.priority || "medium",
				category: data.category,
				tags: data.tags,
				preconditions: data.preconditions,
				test_steps: data.testSteps?.map((step) => ({
					step_number: step.stepNumber,
					action: step.action,
					expected_result: step.expectedResult,
					test_data: step.testData,
				})),
				expected_result: data.expectedResult,
				postconditions: data.postconditions,
				test_data: data.testData,
				automation_status: data.automationStatus || "not_automated",
				automation_script_path: data.automationScriptPath,
				automation_framework: data.automationFramework,
				automation_notes: data.automationNotes,
				estimated_duration_minutes: data.estimatedDurationMinutes,
				assigned_to: data.assignedTo,
				metadata: data.metadata || {},
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to create test case");
	const result = await res.json();
	return { id: result.id, testCaseNumber: result.test_case_number };
}

async function updateTestCase(
	id: string,
	data: Partial<CreateTestCaseData>,
): Promise<{ id: string; version: number }> {
	const body: Record<string, unknown> = {};

	if (data.title !== undefined) body["title"] = data.title;
	if (data.description !== undefined) body["description"] = data.description;
	if (data.objective !== undefined) body["objective"] = data.objective;
	if (data.testType !== undefined) body["test_type"] = data.testType;
	if (data.priority !== undefined) body["priority"] = data.priority;
	if (data.category !== undefined) body["category"] = data.category;
	if (data.tags !== undefined) body["tags"] = data.tags;
	if (data.preconditions !== undefined)
		body["preconditions"] = data.preconditions;
	if (data.testSteps !== undefined) {
		body["test_steps"] = data.testSteps.map((step) => ({
			step_number: step.stepNumber,
			action: step.action,
			expected_result: step.expectedResult,
			test_data: step.testData,
		}));
	}
	if (data.expectedResult !== undefined)
		body["expected_result"] = data.expectedResult;
	if (data.postconditions !== undefined)
		body["postconditions"] = data.postconditions;
	if (data.testData !== undefined) body["test_data"] = data.testData;
	if (data.automationStatus !== undefined)
		body["automation_status"] = data.automationStatus;
	if (data.automationScriptPath !== undefined)
		body["automation_script_path"] = data.automationScriptPath;
	if (data.automationFramework !== undefined)
		body["automation_framework"] = data.automationFramework;
	if (data.automationNotes !== undefined)
		body["automation_notes"] = data.automationNotes;
	if (data.estimatedDurationMinutes !== undefined)
		body["estimated_duration_minutes"] = data.estimatedDurationMinutes;
	if (data.assignedTo !== undefined) body["assigned_to"] = data.assignedTo;
	if (data.metadata !== undefined) body["metadata"] = data.metadata;

	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
		method: "PUT",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(body),
	});
	if (!res.ok) throw new Error("Failed to update test case");
	return res.json();
}

async function transitionTestCaseStatus(
	id: string,
	newStatus: TestCaseStatus,
	reason?: string,
): Promise<{ id: string; status: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/status`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			new_status: newStatus,
			reason,
		}),
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to transition status: ${errorText}`);
	}
	return res.json();
}

async function submitTestCaseForReview(
	id: string,
	reviewer: string,
	notes?: string,
): Promise<{ id: string; status: string; reviewedBy: string }> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/submit-review`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			reviewer,
			notes,
		}),
	});
	if (!res.ok) throw new Error("Failed to submit for review");
	const result = await res.json();
	return {
		id: result.id,
		status: result.status,
		reviewedBy: result.reviewed_by,
	};
}

async function approveTestCase(
	id: string,
	notes?: string,
): Promise<{ id: string; status: string; approvedBy: string }> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/approve`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			reviewer: "", // Will be filled by backend from claims
			notes,
			approved: true,
		}),
	});
	if (!res.ok) throw new Error("Failed to approve test case");
	const result = await res.json();
	return {
		id: result.id,
		status: result.status,
		approvedBy: result.approved_by,
	};
}

async function deprecateTestCase(
	id: string,
	reason: string,
	replacementTestCaseId?: string,
): Promise<{ id: string; status: string }> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/deprecate`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({
			reason,
			replacement_test_case_id: replacementTestCaseId,
		}),
	});
	if (!res.ok) throw new Error("Failed to deprecate test case");
	return res.json();
}

async function deleteTestCase(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
		method: "DELETE",
	});
	if (!res.ok) throw new Error("Failed to delete test case");
}

async function fetchTestCaseActivities(
	testCaseId: string,
	limit = 50,
): Promise<{ testCaseId: string; activities: TestCaseActivity[] }> {
	const res = await fetch(
		`${API_URL}/api/v1/test-cases/${testCaseId}/activities?limit=${limit}`,
	);
	if (!res.ok) throw new Error("Failed to fetch activities");
	const data = await res.json();
	return {
		testCaseId: data.test_case_id,
		activities: (data.activities || []).map((a: any) => ({
			id: a.id,
			testCaseId: a.test_case_id,
			activityType: a.activity_type,
			fromValue: a.from_value,
			toValue: a.to_value,
			description: a.description,
			performedBy: a.performed_by,
			metadata: a.metadata,
			createdAt: a.created_at,
		})),
	};
}

async function fetchTestCaseStats(projectId: string): Promise<TestCaseStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/test-cases/stats`,
	);
	if (!res.ok) throw new Error("Failed to fetch test case stats");
	const data = await res.json();
	return {
		projectId: data.project_id,
		total: data.total || 0,
		byStatus: data.by_status || {},
		byType: data.by_type || {},
		byPriority: data.by_priority || {},
		byAutomationStatus: data.by_automation_status || {},
		executionSummary: {
			totalRuns: data.execution_summary?.total_runs || 0,
			totalPassed: data.execution_summary?.total_passed || 0,
			totalFailed: data.execution_summary?.total_failed || 0,
		},
	};
}

// React Query hooks

export function useTestCases(filters: TestCaseFilters) {
	return useQuery({
		queryKey: ["testCases", filters],
		queryFn: () => fetchTestCases(filters),
		enabled: !!filters.projectId,
	});
}

export function useTestCase(id: string) {
	return useQuery({
		queryKey: ["testCases", id],
		queryFn: () => fetchTestCase(id),
		enabled: !!id,
	});
}

export function useCreateTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createTestCase,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["testCases"] });
			queryClient.invalidateQueries({ queryKey: ["testCaseStats"] });
		},
	});
}

export function useUpdateTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			data,
		}: {
			id: string;
			data: Partial<CreateTestCaseData>;
		}) => updateTestCase(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testCases"] });
			queryClient.invalidateQueries({ queryKey: ["testCases", id] });
		},
	});
}

export function useTransitionTestCaseStatus() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			newStatus,
			reason,
		}: {
			id: string;
			newStatus: TestCaseStatus;
			reason?: string;
		}) => transitionTestCaseStatus(id, newStatus, reason),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testCases"] });
			queryClient.invalidateQueries({ queryKey: ["testCases", id] });
			queryClient.invalidateQueries({ queryKey: ["testCaseActivities", id] });
			queryClient.invalidateQueries({ queryKey: ["testCaseStats"] });
		},
	});
}

export function useSubmitTestCaseForReview() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			reviewer,
			notes,
		}: {
			id: string;
			reviewer: string;
			notes?: string;
		}) => submitTestCaseForReview(id, reviewer, notes),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testCases"] });
			queryClient.invalidateQueries({ queryKey: ["testCases", id] });
			queryClient.invalidateQueries({ queryKey: ["testCaseStats"] });
		},
	});
}

export function useApproveTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
			approveTestCase(id, notes),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testCases"] });
			queryClient.invalidateQueries({ queryKey: ["testCases", id] });
			queryClient.invalidateQueries({ queryKey: ["testCaseActivities", id] });
			queryClient.invalidateQueries({ queryKey: ["testCaseStats"] });
		},
	});
}

export function useDeprecateTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			reason,
			replacementTestCaseId,
		}: {
			id: string;
			reason: string;
			replacementTestCaseId?: string;
		}) => deprecateTestCase(id, reason, replacementTestCaseId),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testCases"] });
			queryClient.invalidateQueries({ queryKey: ["testCases", id] });
			queryClient.invalidateQueries({ queryKey: ["testCaseStats"] });
		},
	});
}

export function useDeleteTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteTestCase,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["testCases"] });
			queryClient.invalidateQueries({ queryKey: ["testCaseStats"] });
		},
	});
}

export function useTestCaseActivities(testCaseId: string, limit = 50) {
	return useQuery({
		queryKey: ["testCaseActivities", testCaseId, limit],
		queryFn: () => fetchTestCaseActivities(testCaseId, limit),
		enabled: !!testCaseId,
	});
}

export function useTestCaseStats(projectId: string) {
	return useQuery({
		queryKey: ["testCaseStats", projectId],
		queryFn: () => fetchTestCaseStats(projectId),
		enabled: !!projectId,
	});
}
