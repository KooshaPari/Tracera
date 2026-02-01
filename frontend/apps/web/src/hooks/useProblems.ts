import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	ImpactLevel,
	Problem,
	ProblemActivity,
	ProblemStatus,
	RCAMethod,
	ResolutionType,
	RootCauseCategory,
} from "@tracertm/types";
import { getAuthHeaders } from "@/api/client";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

// Transform API response (snake_case) to frontend format (camelCase)
function transformProblem(data: any): Problem {
	return {
		id: data.id,
		problemNumber: data.problem_number,
		projectId: data.project_id,
		title: data.title,
		description: data.description,
		status: data.status,
		resolutionType: data.resolution_type,
		category: data.category,
		subCategory: data.sub_category,
		tags: data.tags,
		impactLevel: data.impact_level,
		urgency: data.urgency,
		priority: data.priority,
		affectedSystems: data.affected_systems,
		affectedUsersEstimated: data.affected_users_estimated,
		businessImpactDescription: data.business_impact_description,
		rcaPerformed: data.rca_performed,
		rcaMethod: data.rca_method,
		rcaNotes: data.rca_notes,
		rcaData: data.rca_data,
		rootCauseIdentified: data.root_cause_identified,
		rootCauseDescription: data.root_cause_description,
		rootCauseCategory: data.root_cause_category,
		rootCauseConfidence: data.root_cause_confidence,
		rcaCompletedAt: data.rca_completed_at,
		rcaCompletedBy: data.rca_completed_by,
		workaroundAvailable: data.workaround_available,
		workaroundDescription: data.workaround_description,
		workaroundEffectiveness: data.workaround_effectiveness,
		permanentFixAvailable: data.permanent_fix_available,
		permanentFixDescription: data.permanent_fix_description,
		permanentFixImplementedAt: data.permanent_fix_implemented_at,
		permanentFixChangeId: data.permanent_fix_change_id,
		knownErrorId: data.known_error_id,
		knowledgeArticleId: data.knowledge_article_id,
		assignedTo: data.assigned_to,
		assignedTeam: data.assigned_team,
		owner: data.owner,
		closedBy: data.closed_by,
		closedAt: data.closed_at,
		closureNotes: data.closure_notes,
		targetResolutionDate: data.target_resolution_date,
		metadata: data.metadata,
		version: data.version,
		createdAt: data.created_at,
		updatedAt: data.updated_at,
	};
}

interface ProblemFilters {
	projectId: string;
	status?: ProblemStatus;
	priority?: ImpactLevel;
	impactLevel?: ImpactLevel;
	category?: string;
	assignedTo?: string;
}

async function fetchProblems(
	filters: ProblemFilters,
): Promise<{ problems: Problem[]; total: number }> {
	const params = new URLSearchParams();
	params.set("project_id", filters.projectId);
	if (filters.status) params.set("status", filters.status);
	if (filters.priority) params.set("priority", filters.priority);
	if (filters.impactLevel) params.set("impact_level", filters.impactLevel);
	if (filters.category) params.set("category", filters.category);
	if (filters.assignedTo) params.set("assigned_to", filters.assignedTo);

	const res = await fetch(`${API_URL}/api/v1/problems?${params}`, {
		headers: {
			"X-Bulk-Operation": "true",
			...getAuthHeaders(),
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch problems: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	return {
		problems: (data.problems || []).map(transformProblem),
		total: data.total || 0,
	};
}

async function fetchProblem(id: string): Promise<Problem> {
	const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to fetch problem");
	const data = await res.json();
	return transformProblem(data);
}

interface CreateProblemData {
	projectId: string;
	title: string;
	description?: string;
	category?: string;
	subCategory?: string;
	tags?: string[];
	impactLevel?: ImpactLevel;
	urgency?: ImpactLevel;
	priority?: ImpactLevel;
	affectedSystems?: string[];
	affectedUsersEstimated?: number;
	businessImpactDescription?: string;
	assignedTo?: string;
	assignedTeam?: string;
	owner?: string;
	targetResolutionDate?: string;
	metadata?: Record<string, unknown>;
}

async function createProblem(
	data: CreateProblemData,
): Promise<{ id: string; problemNumber: string }> {
	const res = await fetch(
		`${API_URL}/api/v1/problems?project_id=${data.projectId}`,
		{
			method: "POST",
			headers: { "Content-Type": "application/json", ...getAuthHeaders() },
			body: JSON.stringify({
				title: data.title,
				description: data.description,
				category: data.category,
				sub_category: data.subCategory,
				tags: data.tags,
				impact_level: data.impactLevel || "medium",
				urgency: data.urgency || "medium",
				priority: data.priority || "medium",
				affected_systems: data.affectedSystems,
				affected_users_estimated: data.affectedUsersEstimated,
				business_impact_description: data.businessImpactDescription,
				assigned_to: data.assignedTo,
				assigned_team: data.assignedTeam,
				owner: data.owner,
				target_resolution_date: data.targetResolutionDate,
				metadata: data.metadata || {},
			}),
		},
	);
	if (!res.ok) throw new Error("Failed to create problem");
	const result = await res.json();
	return { id: result.id, problemNumber: result.problem_number };
}

async function updateProblem(
	id: string,
	data: Partial<CreateProblemData>,
): Promise<{ id: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
		method: "PUT",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			title: data.title,
			description: data.description,
			category: data.category,
			sub_category: data.subCategory,
			tags: data.tags,
			impact_level: data.impactLevel,
			urgency: data.urgency,
			priority: data.priority,
			affected_systems: data.affectedSystems,
			affected_users_estimated: data.affectedUsersEstimated,
			business_impact_description: data.businessImpactDescription,
			assigned_to: data.assignedTo,
			assigned_team: data.assignedTeam,
			owner: data.owner,
			target_resolution_date: data.targetResolutionDate,
			metadata: data.metadata,
		}),
	});
	if (!res.ok) throw new Error("Failed to update problem");
	return res.json();
}

async function transitionProblemStatus(
	id: string,
	toStatus: ProblemStatus,
	reason?: string,
): Promise<{ id: string; status: string; version: number }> {
	const res = await fetch(`${API_URL}/api/v1/problems/${id}/status`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			to_status: toStatus,
			reason,
		}),
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to transition status: ${errorText}`);
	}
	return res.json();
}

interface RCAData {
	rcaMethod: RCAMethod;
	rcaNotes?: string;
	rcaData?: Record<string, unknown>;
	rootCauseIdentified?: boolean;
	rootCauseDescription?: string;
	rootCauseCategory?: RootCauseCategory;
	rootCauseConfidence?: "high" | "medium" | "low";
}

async function recordRCA(
	id: string,
	data: RCAData,
): Promise<{
	id: string;
	rcaPerformed: boolean;
	rootCauseIdentified: boolean;
}> {
	const res = await fetch(`${API_URL}/api/v1/problems/${id}/rca`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			rca_method: data.rcaMethod,
			rca_notes: data.rcaNotes,
			rca_data: data.rcaData,
			root_cause_identified: data.rootCauseIdentified || false,
			root_cause_description: data.rootCauseDescription,
			root_cause_category: data.rootCauseCategory,
			root_cause_confidence: data.rootCauseConfidence,
		}),
	});
	if (!res.ok) throw new Error("Failed to record RCA");
	const result = await res.json();
	return {
		id: result.id,
		rcaPerformed: result.rca_performed,
		rootCauseIdentified: result.root_cause_identified,
	};
}

async function closeProblem(
	id: string,
	resolutionType: ResolutionType,
	closureNotes?: string,
): Promise<{ id: string; status: string; resolutionType: string }> {
	const res = await fetch(`${API_URL}/api/v1/problems/${id}/close`, {
		method: "POST",
		headers: { "Content-Type": "application/json", ...getAuthHeaders() },
		body: JSON.stringify({
			resolution_type: resolutionType,
			closure_notes: closureNotes,
		}),
	});
	if (!res.ok) throw new Error("Failed to close problem");
	const result = await res.json();
	return {
		id: result.id,
		status: result.status,
		resolutionType: result.resolution_type,
	};
}

async function deleteProblem(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/problems/${id}`, {
		method: "DELETE",
		headers: getAuthHeaders(),
	});
	if (!res.ok) throw new Error("Failed to delete problem");
}

async function fetchProblemActivities(
	problemId: string,
	limit = 50,
): Promise<{ problemId: string; activities: ProblemActivity[] }> {
	const res = await fetch(
		`${API_URL}/api/v1/problems/${problemId}/activities?limit=${limit}`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch activities");
	const data = await res.json();
	return {
		problemId: data.problem_id,
		activities: (data.activities || []).map((a: any) => ({
			id: a.id,
			problemId: a.problem_id,
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

async function fetchProblemStats(projectId: string): Promise<{
	projectId: string;
	byStatus: Record<string, number>;
	byPriority: Record<string, number>;
	total: number;
}> {
	const res = await fetch(
		`${API_URL}/api/v1/projects/${projectId}/problems/stats`,
		{ headers: getAuthHeaders() },
	);
	if (!res.ok) throw new Error("Failed to fetch problem stats");
	const data = await res.json();
	return {
		projectId: data.project_id,
		byStatus: data.by_status || {},
		byPriority: data.by_priority || {},
		total: data.total || 0,
	};
}

// React Query hooks

export function useProblems(filters: ProblemFilters) {
	return useQuery({
		queryKey: ["problems", filters],
		queryFn: () => fetchProblems(filters),
		enabled: !!filters.projectId,
	});
}

export function useProblem(id: string) {
	return useQuery({
		queryKey: ["problems", id],
		queryFn: () => fetchProblem(id),
		enabled: !!id,
	});
}

export function useCreateProblem() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createProblem,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["problems"] });
		},
	});
}

export function useUpdateProblem() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			data,
		}: {
			id: string;
			data: Partial<CreateProblemData>;
		}) => updateProblem(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["problems"] });
			queryClient.invalidateQueries({ queryKey: ["problems", id] });
		},
	});
}

export function useTransitionProblemStatus() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			toStatus,
			reason,
		}: {
			id: string;
			toStatus: ProblemStatus;
			reason?: string;
		}) => transitionProblemStatus(id, toStatus, reason),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["problems"] });
			queryClient.invalidateQueries({ queryKey: ["problems", id] });
			queryClient.invalidateQueries({ queryKey: ["problemActivities", id] });
		},
	});
}

export function useRecordRCA() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: RCAData }) =>
			recordRCA(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["problems", id] });
			queryClient.invalidateQueries({ queryKey: ["problemActivities", id] });
		},
	});
}

export function useCloseProblem() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			id,
			resolutionType,
			closureNotes,
		}: {
			id: string;
			resolutionType: ResolutionType;
			closureNotes?: string;
		}) => closeProblem(id, resolutionType, closureNotes),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["problems"] });
			queryClient.invalidateQueries({ queryKey: ["problems", id] });
			queryClient.invalidateQueries({ queryKey: ["problemActivities", id] });
		},
	});
}

export function useDeleteProblem() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteProblem,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["problems"] });
		},
	});
}

export function useProblemActivities(problemId: string, limit = 50) {
	return useQuery({
		queryKey: ["problemActivities", problemId, limit],
		queryFn: () => fetchProblemActivities(problemId, limit),
		enabled: !!problemId,
	});
}

export function useProblemStats(projectId: string) {
	return useQuery({
		queryKey: ["problemStats", projectId],
		queryFn: () => fetchProblemStats(projectId),
		enabled: !!projectId,
	});
}
