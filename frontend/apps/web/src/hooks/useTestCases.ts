import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	AutomationStatus,
	TestCase,
	TestCaseActivity,
	TestCasePriority,
	TestCaseStats,
	TestCaseStatus,
	TestCaseType,
	TestStep,
} from "@tracertm/types";
import { client } from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformTestCase(data: Record<string, unknown>): TestCase {
	return {
		approvedAt: data["approved_at"],
		approvedBy: data["approved_by"],
		assignedTo: data["assigned_to"],
		automationFramework: data["automation_framework"],
		automationNotes: data["automation_notes"],
		automationScriptPath: data["automation_script_path"],
		automationStatus: data["automation_status"],
		category: data["category"],
		createdAt: data["created_at"],
		createdBy: data["created_by"],
		deprecatedAt: data["deprecated_at"],
		deprecationReason: data["deprecation_reason"],
		description: data["description"],
		estimatedDurationMinutes: data["estimated_duration_minutes"],
		expectedResult: data["expected_result"],
		failCount: data["fail_count"] || 0,
		id: data["id"],
		lastExecutedAt: data["last_executed_at"],
		lastExecutionResult: data["last_execution_result"],
		metadata: data["metadata"],
		objective: data["objective"],
		passCount: data["pass_count"] || 0,
		postconditions: data["postconditions"],
		preconditions: data["preconditions"],
		priority: data["priority"],
		projectId: data["project_id"],
		reviewedAt: data["reviewed_at"],
		reviewedBy: data["reviewed_by"],
		status: data.status,
		tags: data["tags"],
		testCaseNumber: data["test_case_number"],
		testData: data["test_data"],
		testSteps: data["test_steps"]?.map((step: any) => ({
			action: step.action,
			expectedResult: step.expected_result,
			stepNumber: step.step_number,
			testData: step.test_data,
		})),
		testType: data["test_type"],
		title: data["title"],
		totalExecutions: data["total_executions"] || 0,
		updatedAt: data["updated_at"],
		version: data["version"],
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
	if (filters.status) {
		params.set("status", filters.status);
	}
	if (filters.testType) {
		params.set("test_type", filters.testType);
	}
	if (filters.priority) {
		params.set("priority", filters.priority);
	}
	if (filters.automationStatus) {
		params.set("automation_status", filters.automationStatus);
	}
	if (filters.category) {
		params.set("category", filters.category);
	}
	if (filters.assignedTo) {
		params.set("assigned_to", filters.assignedTo);
	}
	if (filters.search) {
		params.set("search", filters.search);
	}

	const res = await fetch(`${API_URL}/api/v1/test-cases?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...getAuthHeaders(),
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch test cases: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		testCases: (data["test_cases"] || []).map(transformTestCase),
		total: data["total"] || 0,
	};
}

async function fetchTestCase(id: string): Promise<TestCase> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) {
		throw new Error("Failed to fetch test case");
	}
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
		`${API_URL}/api/v1/test-cases?project_id=${data["projectId"]}`,
		{
			body: JSON.stringify({
				assigned_to: data["assignedTo"],
				automation_framework: data["automationFramework"],
				automation_notes: data["automationNotes"],
				automation_script_path: data["automationScriptPath"],
				automation_status: data["automationStatus"] || "not_automated",
				category: data["category"],
				description: data["description"],
				estimated_duration_minutes: data["estimatedDurationMinutes"],
				expected_result: data["expectedResult"],
				metadata: data["metadata"] || {},
				objective: data["objective"],
				postconditions: data["postconditions"],
				preconditions: data["preconditions"],
				priority: data["priority"] || "medium",
				tags: data["tags"],
				test_data: data["testData"],
				test_steps: data["testSteps"]?.map((step) => ({
					action: step.action,
					expected_result: step.expectedResult,
					step_number: step.stepNumber,
					test_data: step.testData,
				})),
				test_type: data["testType"] || "functional",
				title: data["title"],
			}),
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			method: "POST",
		},
	);
	if (!res.ok) {
		throw new Error("Failed to create test case");
	}
	const result = await res.json();
	return { id: result["id"], testCaseNumber: result["test_case_number"] };
}

async function updateTestCase(
	id: string,
	data: Partial<CreateTestCaseData>,
): Promise<{ id: string; version: number }> {
	const body: Record<string, unknown> = {};

	if (data["title"] !== undefined) {
		body["title"] = data["title"];
	}
	if (data["description"] !== undefined) {
		body["description"] = data["description"];
	}
	if (data["objective"] !== undefined) {
		body["objective"] = data["objective"];
	}
	if (data["testType"] !== undefined) {
		body["test_type"] = data["testType"];
	}
	if (data["priority"] !== undefined) {
		body["priority"] = data["priority"];
	}
	if (data["category"] !== undefined) {
		body["category"] = data["category"];
	}
	if (data["tags"] !== undefined) {
		body["tags"] = data["tags"];
	}
	if (data["preconditions"] !== undefined) {
		body["preconditions"] = data["preconditions"];
	}
	if (data["testSteps"] !== undefined) {
		body["test_steps"] = data["testSteps"].map((step) => ({
			action: step.action,
			expected_result: step.expectedResult,
			step_number: step.stepNumber,
			test_data: step.testData,
		}));
	}
	if (data["expectedResult"] !== undefined) {
		body["expected_result"] = data["expectedResult"];
	}
	if (data["postconditions"] !== undefined) {
		body["postconditions"] = data["postconditions"];
	}
	if (data["testData"] !== undefined) {
		body["test_data"] = data["testData"];
	}
	if (data["automationStatus"] !== undefined) {
		body["automation_status"] = data["automationStatus"];
	}
	if (data["automationScriptPath"] !== undefined) {
		body["automation_script_path"] = data["automationScriptPath"];
	}
	if (data["automationFramework"] !== undefined) {
		body["automation_framework"] = data["automationFramework"];
	}
	if (data["automationNotes"] !== undefined) {
		body["automation_notes"] = data["automationNotes"];
	}
	if (data["estimatedDurationMinutes"] !== undefined) {
		body["estimated_duration_minutes"] = data["estimatedDurationMinutes"];
	}
	if (data["assignedTo"] !== undefined) {
		body["assigned_to"] = data["assignedTo"];
	}
	if (data["metadata"] !== undefined) {
		body["metadata"] = data["metadata"];
	}

	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
		body: JSON.stringify(body),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "PUT",
	});
	if (!res.ok) {
		throw new Error("Failed to update test case");
	}
	return res.json();
}

async function transitionTestCaseStatus(
	id: string,
	newStatus: TestCaseStatus,
	reason?: string,
): Promise<{ id: string; status: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/status`, {
		body: JSON.stringify({
			new_status: newStatus,
			reason,
		}),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "POST",
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
		body: JSON.stringify({
			notes,
			reviewer,
		}),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "POST",
	});
	if (!res.ok) {
		throw new Error("Failed to submit for review");
	}
	const result = await res.json();
	return {
		id: result["id"],
		reviewedBy: result["reviewed_by"],
		status: result.status,
	};
}

async function approveTestCase(
	id: string,
	notes?: string,
): Promise<{ id: string; status: string; approvedBy: string }> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/approve`, {
		body: JSON.stringify({
			reviewer: "", // Will be filled by backend from claims
			notes,
			approved: true,
		}),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "POST",
	});
	if (!res.ok) {
		throw new Error("Failed to approve test case");
	}
	const result = await res.json();
	return {
		approvedBy: result["approved_by"],
		id: result["id"],
		status: result.status,
	};
}

async function deprecateTestCase(
	id: string,
	reason: string,
	replacementTestCaseId?: string,
): Promise<{ id: string; status: string }> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}/deprecate`, {
		body: JSON.stringify({
			reason,
			replacement_test_case_id: replacementTestCaseId,
		}),
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		method: "POST",
	});
	if (!res.ok) {
		throw new Error("Failed to deprecate test case");
	}
	return res.json();
}

async function deleteTestCase(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/test-cases/${id}`, {
		headers: getAuthHeaders(),
		method: "DELETE",
	});
	if (!res.ok) {
		throw new Error("Failed to delete test case");
	}
}

async function fetchTestCaseActivities(
	testCaseId: string,
	limit = 50,
): Promise<{ testCaseId: string; activities: TestCaseActivity[] }> {
	const res = await fetch(
		`${API_URL}/api/v1/test-cases/${testCaseId}/activities?limit=${limit}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		throw new Error("Failed to fetch activities");
	}
	const data = await res.json();
	return {
		activities: (data["activities"] || []).map(
			(a: Record<string, unknown>) => ({
				activityType: a.activity_type,
				createdAt: a.created_at,
				description: a.description,
				fromValue: a.from_value,
				id: a.id,
				metadata: a.metadata,
				performedBy: a.performed_by,
				testCaseId: a.test_case_id,
				toValue: a.to_value,
			}),
		),
		testCaseId: data["test_case_id"],
	};
}

async function fetchTestCaseStats(projectId: string): Promise<TestCaseStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/test-cases/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) {
		throw new Error("Failed to fetch test case stats");
	}
	const data = await res.json();
	return {
		byAutomationStatus: data["by_automation_status"] || {},
		byPriority: data["by_priority"] || {},
		byStatus: data["by_status"] || {},
		byType: data["by_type"] || {},
		executionSummary: {
			totalFailed: data["execution_summary"]?.total_failed || 0,
			totalPassed: data["execution_summary"]?.total_passed || 0,
			totalRuns: data["execution_summary"]?.total_runs || 0,
		},
		projectId: data["project_id"],
		total: data["total"] || 0,
	};
}

// React Query hooks

export function useTestCases(filters: TestCaseFilters) {
	return useQuery({
		enabled: !!filters.projectId,
		queryFn: () => fetchTestCases(filters),
		queryKey: ["testCases", filters],
	});
}

export function useTestCase(id: string) {
	return useQuery({
		enabled: !!id,
		queryFn: () => fetchTestCase(id),
		queryKey: ["testCases", id],
	});
}

export function useCreateTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createTestCase,
		onSuccess: () => {
			undefined;
			undefined;
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
			undefined;
			undefined;
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
			undefined;
			undefined;
			undefined;
			undefined;
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
			undefined;
			undefined;
			undefined;
		},
	});
}

export function useApproveTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
			approveTestCase(id, notes),
		onSuccess: (_, { id }) => {
			undefined;
			undefined;
			undefined;
			undefined;
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
			undefined;
			undefined;
			undefined;
		},
	});
}

export function useDeleteTestCase() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteTestCase,
		onSuccess: () => {
			undefined;
			undefined;
		},
	});
}

export function useTestCaseActivities(testCaseId: string, limit = 50) {
	return useQuery({
		enabled: !!testCaseId,
		queryFn: () => fetchTestCaseActivities(testCaseId, limit),
		queryKey: ["testCaseActivities", testCaseId, limit],
	});
}

export function useTestCaseStats(projectId: string) {
	return useQuery({
		enabled: !!projectId,
		queryFn: () => fetchTestCaseStats(projectId),
		queryKey: ["testCaseStats", projectId],
	});
}
