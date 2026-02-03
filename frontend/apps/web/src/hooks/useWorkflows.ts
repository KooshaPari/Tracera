import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	WorkflowRun,
	WorkflowSchedule,
} from "../../../packages/types/src/index";
import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

function transformRun(data: Record<string, unknown>): WorkflowRun {
	return {
		completedAt: data["completed_at"],
		createdAt: data["created_at"],
		createdByUserId: data["created_by_user_id"],
		errorMessage: data["error_message"],
		externalRunId: data["external_run_id"],
		graphId: data["graph_id"],
		id: data["id"],
		payload: data["payload"],
		projectId: data["project_id"],
		result: data["result"],
		startedAt: data["started_at"],
		status: data.status,
		updatedAt: data["updated_at"],
		workflowName: data["workflow_name"],
	};
}

function transformSchedule(data: Record<string, unknown>): WorkflowSchedule {
	return {
		id: data["id"] || data["cron_id"],
		cronName: data["cron_name"] || data.name,
		expression: data["expression"] || data["cron_expression"],
		workflowName: data["workflow_name"],
		additionalMetadata: data["additional_metadata"],
		...data,
	};
}

export function useWorkflowRuns(
	projectId: string,
	status?: string,
	workflowName?: string,
	limit = 100,
) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: async () => {
			const params = new URLSearchParams({ limit: String(limit) });
			if (status) params.set("status", status);
			if (workflowName) params.set("workflow_name", workflowName);
			const res = await fetch(
				`${API_URL}/api/v1/projects/${projectId}/workflows/runs?${params}`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch workflow runs: ${res.status}`);
			}
			const data = await res.json();
			return {
				runs: (data["runs"] || []).map(transformRun),
				total: data["total"] || 0,
			};
		},
		queryKey: ["workflows", "runs", projectId, status, workflowName, limit],
		refetchInterval: 15000,
	});
}

export function useWorkflowSchedules(projectId: string) {
	return useQuery({
		enabled: Boolean(projectId),
		queryFn: async () => {
			const res = await fetch(
				`${API_URL}/api/v1/projects/${projectId}/workflows/schedules`,
				{ headers: { "X-Bulk-Operation": "true", ...getAuthHeaders() } },
			);
			if (!res.ok) {
				throw new Error(`Failed to fetch workflow schedules: ${res.status}`);
			}
			const data = await res.json();
			return {
				schedules: (data["schedules"] || []).map(transformSchedule),
				total: data["total"] || 0,
			};
		},
		queryKey: ["workflows", "schedules", projectId],
		refetchInterval: 30000,
	});
}

export function useBootstrapWorkflowSchedules() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async (projectId: string) => {
			const res = await fetch(
				`${API_URL}/api/v1/projects/${projectId}/workflows/schedules/bootstrap`,
				{
					headers: { "Content-Type": "application/json", ...getAuthHeaders() },
					method: "POST",
				},
			);
			if (!res.ok) {
				throw new Error(`Failed to bootstrap schedules: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: (_data, projectId) => {
			queryClient.invalidateQueries({
				queryKey: ["workflows", "schedules", projectId],
			});
		},
	});
}

export function useDeleteWorkflowSchedule() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: async ({
			projectId,
			cronId,
		}: {
			projectId: string;
			cronId: string;
		}) => {
			const res = await fetch(
				`${API_URL}/api/v1/projects/${projectId}/workflows/schedules/${cronId}`,
				{ headers: getAuthHeaders(), method: "DELETE" },
			);
			if (!res.ok) {
				throw new Error(`Failed to delete schedule: ${res.status}`);
			}
			return res.json();
		},
		onSuccess: (_data, variables) => {
			queryClient.invalidateQueries({
				queryKey: ["workflows", "schedules", variables.projectId],
			});
		},
	});
}
