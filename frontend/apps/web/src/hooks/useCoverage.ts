import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	CoverageActivity,
	CoverageGapsResponse,
	CoverageStats,
	CoverageStatus,
	CoverageType,
	TestCoverage,
	TraceabilityMatrix,
} from "../../../../packages/types/src/index";
import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformCoverage(data: Record<string, unknown>): TestCoverage {
	return {
		id: data['id'] as string,
		projectId: data['project_id'] as string,
		testCaseId: data['test_case_id'] as string,
		requirementId: data['requirement_id'] as string,
		coverageType: data['coverage_type'] as CoverageType,
		status: data['status'] as CoverageStatus,
		coveragePercentage: data['coverage_percentage'] as number | undefined,
		rationale: data['rationale'] as string | undefined,
		notes: data['notes'] as string | undefined,
		lastVerifiedAt: data['last_verified_at'] as string | undefined,
		verifiedBy: data['verified_by'] as string | undefined,
		lastTestResult: data['last_test_result'] as string | undefined,
		lastTestedAt: data['last_tested_at'] as string | undefined,
		createdBy: data['created_by'] as string | undefined,
		metadata: data['coverage_metadata'] as Record<string, unknown> | undefined,
		version: data['version'] as number,
		createdAt: data['created_at'] as string,
		updatedAt: data['updated_at'] as string,
	};
}

interface CoverageFilters {
	projectId: string;
	coverageType?: CoverageType;
	status?: CoverageStatus;
	testCaseId?: string;
	requirementId?: string;
	skip?: number;
	limit?: number;
}

async function fetchCoverages(
	filters: CoverageFilters,
): Promise<{ coverages: TestCoverage[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.coverageType) params.set("coverage_type", filters.coverageType);
	if (filters.status) params.set("status", filters.status);
	if (filters.testCaseId) params.set("test_case_id", filters.testCaseId);
	if (filters.requirementId)
		params.set("requirement_id", filters.requirementId);
	if (filters.skip !== undefined) params.set("skip", String(filters.skip));
	if (filters.limit !== undefined) params.set("limit", String(filters.limit));

	const res = await fetch(`${API_URL}/api/v1/coverage?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...getAuthHeaders(),
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch coverages: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		coverages: (data['coverages'] || []).map(transformCoverage),
		total: data['total'] || 0,
	};
}

async function fetchCoverage(id: string): Promise<TestCoverage> {
	const res = await fetch(`${API_URL}/api/v1/coverage/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch coverage");
	const data = await res.json();
	return transformCoverage(data);
}

interface CreateCoverageData {
	projectId: string;
	testCaseId: string;
	requirementId: string;
	coverageType?: CoverageType;
	coveragePercentage?: number;
	rationale?: string;
	notes?: string;
	metadata?: Record<string, unknown>;
}

async function createCoverage(
	data: CreateCoverageData,
): Promise<{ id: string; coverageType: string; status: string }> {
	const params = new URLSearchParams();
	params.set("project_id", data['projectId']);
	params.set("test_case_id", data['testCaseId']);
	params.set("requirement_id", data['requirementId']);
	if (data['coverageType']) params.set("coverage_type", data['coverageType']);
	if (data['coveragePercentage'] !== undefined) {
		params.set("coverage_percentage", String(data['coveragePercentage']));
	}
	if (data['rationale']) params.set("rationale", data['rationale']);
	if (data['notes']) params.set("notes", data['notes']);

	const res = await fetch(`${API_URL}/api/v1/coverage?${params}`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
	});
	if (!res.ok) throw new Error("Failed to create coverage");
	const result = await res.json();
	return {
		id: result['id'],
		coverageType: result['coverage_type'],
		status: result.status,
	};
}

async function updateCoverage(
	id: string,
	data: Partial<{
		coverageType: CoverageType;
		status: CoverageStatus;
		coveragePercentage: number;
		rationale: string;
		notes: string;
	}>,
): Promise<{ id: string; version: number }> {
	const params = new URLSearchParams();
	if (data['coverageType']) params.set("coverage_type", data['coverageType']);
	if (data.status) params.set("status", data.status);
	if (data['coveragePercentage'] !== undefined) {
		params.set("coverage_percentage", String(data['coveragePercentage']));
	}
	if (data['rationale']) params.set("rationale", data['rationale']);
	if (data['notes']) params.set("notes", data['notes']);

	const res = await fetch(`${API_URL}/api/v1/coverage/${id}?${params}`, {
		method: "PUT",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
	});
	if (!res.ok) throw new Error("Failed to update coverage");
	return res.json();
}

async function deleteCoverage(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/coverage/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete coverage");
}

async function verifyCoverage(
	id: string,
	notes?: string,
): Promise<{ id: string; lastVerifiedAt: string; verifiedBy: string }> {
	const params = new URLSearchParams();
	if (notes) params.set("notes", notes);

	const res = await fetch(`${API_URL}/api/v1/coverage/${id}/verify?${params}`, {
		method: "POST",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to verify coverage");
	const result = await res.json();
	return {
		id: result['id'],
		lastVerifiedAt: result['last_verified_at'],
		verifiedBy: result['verified_by'],
	};
}

async function fetchTraceabilityMatrix(
	projectId: string,
	requirementView?: string,
): Promise<TraceabilityMatrix> {
	const params = new URLSearchParams();
	params.set("project_id", projectId);
	if (requirementView) params.set("requirement_view", requirementView);

	const res = await fetch(`${API_URL}/api/v1/coverage/matrix?${params}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch traceability matrix");
	const data = await res.json();

	return {
		projectId: data['project_id'],
		totalRequirements: data['total_requirements'],
		coveredRequirements: data['covered_requirements'],
		uncoveredRequirements: data['uncovered_requirements'],
		coveragePercentage: data['coverage_percentage'],
		matrix: (data['matrix'] as unknown[] || []).map((value: unknown) => {
			const item = (typeof value === "object" && value !== null ? value : {}) as Record<string, unknown>;
			return {
				requirementId: item['requirement_id'],
				requirementTitle: item['requirement_title'],
				requirementView: item['requirement_view'],
				requirementStatus: item['requirement_status'],
				isCovered: item['is_covered'],
				testCount: item['test_count'],
				testCases: (item['test_cases'] as unknown[] || []).map((tcValue: unknown) => {
					const tc = (typeof tcValue === "object" && tcValue !== null ? tcValue : {}) as Record<string, unknown>;
					return {
						testCaseId: tc['test_case_id'],
						coverageType: tc['coverage_type'],
						coveragePercentage: tc['coverage_percentage'],
						lastTestResult: tc['last_test_result'],
						lastTestedAt: tc['last_tested_at'],
					};
				}),
				overallStatus: item['overall_status'],
			};
		}),
	};
}

async function fetchCoverageGaps(
	projectId: string,
	requirementView?: string,
): Promise<CoverageGapsResponse> {
	const params = new URLSearchParams();
	params.set("project_id", projectId);
	if (requirementView) params.set("requirement_view", requirementView);

	const res = await fetch(`${API_URL}/api/v1/coverage/gaps?${params}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch coverage gaps");
	const data = await res.json();

	return {
		projectId: data['project_id'],
		totalRequirements: data['total_requirements'],
		uncoveredCount: data['uncovered_count'],
		coveragePercentage: data['coverage_percentage'],
		gaps: (data['gaps'] as unknown[] || []).map((value: unknown) => {
			const gap = (typeof value === "object" && value !== null ? value : {}) as Record<string, unknown>;
			return {
				requirementId: gap['requirement_id'],
				requirementTitle: gap['requirement_title'],
				requirementView: gap['requirement_view'],
				requirementStatus: gap['requirement_status'],
				priority: gap['priority'],
			};
		}),
	};
}

async function fetchCoverageStats(projectId: string): Promise<CoverageStats> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/coverage/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch coverage stats");
	const data = await res.json();

	return {
		projectId: data['project_id'],
		totalMappings: data['total_mappings'] || 0,
		byType: data['by_type'] || {},
		byStatus: data['by_status'] || {},
		uniqueTestCases: data['unique_test_cases'] || 0,
		uniqueRequirements: data['unique_requirements'] || 0,
	};
}

async function fetchCoverageActivities(
	coverageId: string,
	limit = 50,
): Promise<{ coverageId: string; activities: CoverageActivity[] }> {
	const res = await fetch(
		`${API_URL}/api/v1/coverage/${coverageId}/activities?limit=${limit}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch activities");
	const data = await res.json();

	return {
		coverageId: data['coverage_id'],
		activities: (data['activities'] as unknown[] || []).map((value: unknown) => {
			const a = (typeof value === "object" && value !== null ? value : {}) as Record<string, unknown>;
			return {
				id: a['id'],
				coverageId: a['coverage_id'],
				activityType: a['activity_type'],
				fromValue: a['from_value'],
				toValue: a['to_value'],
				description: a['description'],
				performedBy: a['performed_by'],
				metadata: a['activity_metadata'],
				createdAt: a['created_at'],
			};
		}),
	};
}

// React Query hooks

export function useCoverages(filters: CoverageFilters) {
	return useQuery({
		queryKey: ["coverages", filters],
		queryFn: () => fetchCoverages(filters),
		enabled: !!filters.projectId,
	});
}

export function useCoverage(id: string) {
	return useQuery({
		queryKey: ["coverages", id],
		queryFn: () => fetchCoverage(id),
		enabled: !!id,
	});
}

export function useCreateCoverage() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createCoverage,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["coverages"] });
			queryClient.invalidateQueries({ queryKey: ["traceabilityMatrix"] });
			queryClient.invalidateQueries({ queryKey: ["coverageGaps"] });
			queryClient.invalidateQueries({ queryKey: ["coverageStats"] });
		},
	});
}

export function useUpdateCoverage() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			data,
		}: {
			id: string;
			data: Partial<{
				coverageType: CoverageType;
				status: CoverageStatus;
				coveragePercentage: number;
				rationale: string;
				notes: string;
			}>;
		}) => updateCoverage(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["coverages"] });
			queryClient.invalidateQueries({ queryKey: ["coverages", id] });
			queryClient.invalidateQueries({ queryKey: ["traceabilityMatrix"] });
		},
	});
}

export function useDeleteCoverage() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteCoverage,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["coverages"] });
			queryClient.invalidateQueries({ queryKey: ["traceabilityMatrix"] });
			queryClient.invalidateQueries({ queryKey: ["coverageGaps"] });
			queryClient.invalidateQueries({ queryKey: ["coverageStats"] });
		},
	});
}

export function useVerifyCoverage() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, notes }: { id: string; notes?: string }) =>
			verifyCoverage(id, notes),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["coverages", id] });
			queryClient.invalidateQueries({ queryKey: ["coverageActivities", id] });
		},
	});
}

export function useTraceabilityMatrix(
	projectId: string,
	requirementView?: string,
) {
	return useQuery({
		queryKey: ["traceabilityMatrix", projectId, requirementView],
		queryFn: () => fetchTraceabilityMatrix(projectId, requirementView),
		enabled: !!projectId,
	});
}

export function useCoverageGaps(projectId: string, requirementView?: string) {
	return useQuery({
		queryKey: ["coverageGaps", projectId, requirementView],
		queryFn: () => fetchCoverageGaps(projectId, requirementView),
		enabled: !!projectId,
	});
}

export function useCoverageStats(projectId: string) {
	return useQuery({
		queryKey: ["coverageStats", projectId],
		queryFn: () => fetchCoverageStats(projectId),
		enabled: !!projectId,
	});
}

export function useCoverageActivities(coverageId: string, limit = 50) {
	return useQuery({
		queryKey: ["coverageActivities", coverageId, limit],
		queryFn: () => fetchCoverageActivities(coverageId, limit),
		enabled: !!coverageId,
	});
}
