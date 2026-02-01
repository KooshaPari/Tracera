import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	TestSuite,
	TestSuiteActivity,
	TestSuiteStats,
	TestSuiteStatus,
	TestSuiteTestCase,
} from "@tracertm/types";
import { getAuthHeaders } from "@/api/client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformTestSuite(data: any): TestSuite {
	return {
		id: data.id,
		suiteNumber: data.suite_number,
		projectId: data.project_id,
		name: data.name,
		description: data.description,
		objective: data.objective,
		status: data.status,
		parentId: data.parent_id,
		orderIndex: data.order_index,
		category: data.category,
		tags: data.tags,
		isParallelExecution: data.is_parallel_execution,
		estimatedDurationMinutes: data.estimated_duration_minutes,
		requiredEnvironment: data.required_environment,
		environmentVariables: data.environment_variables,
		setupInstructions: data.setup_instructions,
		teardownInstructions: data.teardown_instructions,
		owner: data.owner,
		responsibleTeam: data.responsible_team,
		totalTestCases: data.total_test_cases,
		automatedCount: data.automated_count,
		manualCount: data.manual_count,
		passRate: data.pass_rate,
		lastRunAt: data.last_run_at,
		lastRunStatus: data.last_run_status,
		metadata: data.suite_metadata,
		version: data.version,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

function transformTestSuiteTestCase(data: any): TestSuiteTestCase {
	return {
		id: data.id,
		suiteId: data.suite_id,
		testCaseId: data.test_case_id,
		orderIndex: data.order_index,
		isMandatory: data.is_mandatory,
		skipReason: data.skip_reason,
		customParameters: data.custom_parameters,
		createdAt: data.created_at,
	};
}

interface TestSuiteFilters {
	projectId: string;
	status?: TestSuiteStatus;
	category?: string;
	parentId?: string;
	owner?: string;
	search?: string;
	skip?: number;
	limit?: number;
}

async function fetchTestSuites(
	filters: TestSuiteFilters,
): Promise<{ testSuites: TestSuite[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.status) params.set("status", filters.status);
	if (filters.category) params.set("category", filters.category);
	if (filters.parentId !== undefined) params.set("parent_id", filters.parentId);
	if (filters.owner) params.set("owner", filters.owner);
	if (filters.search) params.set("search", filters.search);
	if (filters.skip !== undefined) params.set("skip", String(filters.skip));
	if (filters.limit !== undefined) params.set("limit", String(filters.limit));

	const res = await fetch(`${API_URL}/api/v1/test-suites?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...getAuthHeaders(),
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch test suites: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		testSuites: (data.test_suites || []).map(transformTestSuite),
		total: data.total || 0,
	};
}

async function fetchTestSuite(id: string): Promise<TestSuite> {
	const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch test suite");
	const data = await res.json();
	return transformTestSuite(data);
}

interface CreateTestSuiteData {
	projectId: string;
	name: string;
	description?: string;
	objective?: string;
	parentId?: string;
	orderIndex?: number;
	category?: string;
	tags?: string[];
	isParallelExecution?: boolean;
	estimatedDurationMinutes?: number;
	requiredEnvironment?: string;
	environmentVariables?: Record<string, string>;
	setupInstructions?: string;
	teardownInstructions?: string;
	owner?: string;
	responsibleTeam?: string;
	metadata?: Record<string, unknown>;
}

async function createTestSuite(
	data: CreateTestSuiteData,
): Promise<{ id: string; suiteNumber: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/test-suites?project_id=${data.projectId}`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify({
				name: data.name,
				description: data.description,
				objective: data.objective,
				parent_id: data.parentId,
				order_index: data.orderIndex || 0,
				category: data.category,
				tags: data.tags,
				is_parallel_execution: data.isParallelExecution || false,
				estimated_duration_minutes: data.estimatedDurationMinutes,
				required_environment: data.requiredEnvironment,
				environment_variables: data.environmentVariables,
				setup_instructions: data.setupInstructions,
				teardown_instructions: data.teardownInstructions,
				owner: data.owner,
				responsible_team: data.responsibleTeam,
				metadata: data.metadata || {},
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to create test suite");
	const result = await res.json();
	return { id: result.id, suiteNumber: result.suite_number };
}

async function updateTestSuite(
	id: string,
	data: Partial<CreateTestSuiteData>,
): Promise<{ id: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
		method: "PUT",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			name: data.name,
			description: data.description,
			objective: data.objective,
			parent_id: data.parentId,
			order_index: data.orderIndex,
			category: data.category,
			tags: data.tags,
			is_parallel_execution: data.isParallelExecution,
			estimated_duration_minutes: data.estimatedDurationMinutes,
			required_environment: data.requiredEnvironment,
			environment_variables: data.environmentVariables,
			setup_instructions: data.setupInstructions,
			teardown_instructions: data.teardownInstructions,
			owner: data.owner,
			responsible_team: data.responsibleTeam,
			metadata: data.metadata,
		}),
	});
	if (!res.ok) throw new Error("Failed to update test suite");
	return res.json();
}

async function transitionTestSuiteStatus(
	id: string,
	newStatus: TestSuiteStatus,
	reason?: string,
): Promise<{ id: string; status: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/test-suites/${id}/status`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
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

async function deleteTestSuite(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/test-suites/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete test suite");
}

// Test case management within suites
async function addTestCaseToSuite(
	suiteId: string,
	testCaseId: string,
	orderIndex?: number,
	isMandatory?: boolean,
	skipReason?: string,
	customParameters?: Record<string, unknown>,
): Promise<TestSuiteTestCase> {
	const res = await fetch(
		`${API_URL}/api/v1/test-suites/${suiteId}/test-cases`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify({
				test_case_id: testCaseId,
				order_index: orderIndex || 0,
				is_mandatory: isMandatory !== false,
				skip_reason: skipReason,
				custom_parameters: customParameters,
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to add test case to suite");
	const data = await res.json();
	return transformTestSuiteTestCase(data);
}

async function removeTestCaseFromSuite(
	suiteId: string,
	testCaseId: string,
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/test-suites/${suiteId}/test-cases/${testCaseId}`,
		{
			method: "DELETE",
			headers: getAuthHeaders(),
		},
	);
	if (!res.ok) throw new Error("Failed to remove test case from suite");
}

async function fetchSuiteTestCases(
	suiteId: string,
): Promise<TestSuiteTestCase[]> {
	const res = await fetch(
		`${API_URL}/api/v1/test-suites/${suiteId}/test-cases`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch suite test cases");
	const data = await res.json();
	return (data.test_cases || []).map(transformTestSuiteTestCase);
}

async function reorderSuiteTestCases(
	suiteId: string,
	testCaseIds: string[],
): Promise<void> {
	const res = await fetch(
		`${API_URL}/api/v1/test-suites/${suiteId}/test-cases/reorder`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify({
				ordered_test_case_ids: testCaseIds,
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to reorder test cases");
}

async function fetchTestSuiteActivities(
	suiteId: string,
	limit = 50,
): Promise<{ suiteId: string; activities: TestSuiteActivity[] }> {
	const res = await fetch(
		`${API_URL}/api/v1/test-suites/${suiteId}/activities?limit=${limit}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch activities");
	const data = await res.json();
	return {
		suiteId: data.suite_id,
		activities: (data.activities || []).map((a: any) => ({
			id: a.id,
			suiteId: a.suite_id,
			activityType: a.activity_type,
			fromValue: a.from_value,
			toValue: a.to_value,
			description: a.description,
			performedBy: a.performed_by,
			metadata: a.activity_metadata,
			createdAt: a.created_at,
		})),
	};
}

async function fetchTestSuiteStats(projectId: string): Promise<TestSuiteStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/test-suites/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch test suite stats");
	const data = await res.json();
	return {
		projectId: data.project_id,
		total: data.total || 0,
		byStatus: data.by_status || {},
		byCategory: data.by_category || {},
		totalTestCases: data.total_test_cases || 0,
		automatedTestCases: data.automated_test_cases || 0,
	};
}

// React Query hooks

export function useTestSuites(filters: TestSuiteFilters) {
	return useQuery({
		queryKey: ["testSuites", filters],
		queryFn: () => fetchTestSuites(filters),
		enabled: !!filters.projectId,
	});
}

export function useTestSuite(id: string) {
	return useQuery({
		queryKey: ["testSuites", id],
		queryFn: () => fetchTestSuite(id),
		enabled: !!id,
	});
}

export function useCreateTestSuite() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createTestSuite,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["testSuites"] });
		},
	});
}

export function useUpdateTestSuite() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			data,
		}: {
			id: string;
			data: Partial<CreateTestSuiteData>;
		}) => updateTestSuite(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testSuites"] });
			queryClient.invalidateQueries({ queryKey: ["testSuites", id] });
		},
	});
}

export function useTransitionTestSuiteStatus() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			newStatus,
			reason,
		}: {
			id: string;
			newStatus: TestSuiteStatus;
			reason?: string;
		}) => transitionTestSuiteStatus(id, newStatus, reason),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["testSuites"] });
			queryClient.invalidateQueries({ queryKey: ["testSuites", id] });
			queryClient.invalidateQueries({ queryKey: ["testSuiteActivities", id] });
		},
	});
}

export function useDeleteTestSuite() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteTestSuite,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["testSuites"] });
		},
	});
}

export function useAddTestCaseToSuite() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			suiteId,
			testCaseId,
			orderIndex,
			isMandatory,
			skipReason,
			customParameters,
		}: {
			suiteId: string;
			testCaseId: string;
			orderIndex?: number;
			isMandatory?: boolean;
			skipReason?: string;
			customParameters?: Record<string, unknown>;
		}) =>
			addTestCaseToSuite(
				suiteId,
				testCaseId,
				orderIndex,
				isMandatory,
				skipReason,
				customParameters,
			),
		onSuccess: (_, { suiteId }) => {
			queryClient.invalidateQueries({ queryKey: ["suiteTestCases", suiteId] });
			queryClient.invalidateQueries({ queryKey: ["testSuites", suiteId] });
		},
	});
}

export function useRemoveTestCaseFromSuite() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			suiteId,
			testCaseId,
		}: {
			suiteId: string;
			testCaseId: string;
		}) => removeTestCaseFromSuite(suiteId, testCaseId),
		onSuccess: (_, { suiteId }) => {
			queryClient.invalidateQueries({ queryKey: ["suiteTestCases", suiteId] });
			queryClient.invalidateQueries({ queryKey: ["testSuites", suiteId] });
		},
	});
}

export function useSuiteTestCases(suiteId: string) {
	return useQuery({
		queryKey: ["suiteTestCases", suiteId],
		queryFn: () => fetchSuiteTestCases(suiteId),
		enabled: !!suiteId,
	});
}

export function useReorderSuiteTestCases() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			suiteId,
			testCaseIds,
		}: {
			suiteId: string;
			testCaseIds: string[];
		}) => reorderSuiteTestCases(suiteId, testCaseIds),
		onSuccess: (_, { suiteId }) => {
			queryClient.invalidateQueries({ queryKey: ["suiteTestCases", suiteId] });
		},
	});
}

export function useTestSuiteActivities(suiteId: string, limit = 50) {
	return useQuery({
		queryKey: ["testSuiteActivities", suiteId, limit],
		queryFn: () => fetchTestSuiteActivities(suiteId, limit),
		enabled: !!suiteId,
	});
}

export function useTestSuiteStats(projectId: string) {
	return useQuery({
		queryKey: ["testSuiteStats", projectId],
		queryFn: () => fetchTestSuiteStats(projectId),
		enabled: !!projectId,
	});
}
