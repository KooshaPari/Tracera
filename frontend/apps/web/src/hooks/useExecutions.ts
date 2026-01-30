// React hooks for execution management

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	executionsApi,
	type ExecutionCreate,
	type ExecutionComplete,
	type ExecutionEnvironmentConfigUpdate,
} from "../api/executions";

export function useExecutions(
	projectId: string,
	options?: {
		status?: string;
		execution_type?: string;
		limit?: number;
		offset?: number;
	},
) {
	return useQuery({
		queryKey: ["executions", projectId, options],
		queryFn: () => executionsApi.list(projectId, options),
		enabled: !!projectId,
	});
}

export function useExecution(projectId: string, executionId: string) {
	return useQuery({
		queryKey: ["execution", projectId, executionId],
		queryFn: () => executionsApi.get(projectId, executionId),
		enabled: !!projectId && !!executionId,
	});
}

export function useExecutionArtifacts(
	projectId: string,
	executionId: string,
	artifactType?: string,
) {
	return useQuery({
		queryKey: ["execution-artifacts", projectId, executionId, artifactType],
		queryFn: () =>
			executionsApi.listArtifacts(projectId, executionId, artifactType),
		enabled: !!projectId && !!executionId,
	});
}

export function useExecutionConfig(projectId: string) {
	return useQuery({
		queryKey: ["execution-config", projectId],
		queryFn: () => executionsApi.getConfig(projectId),
		enabled: !!projectId,
	});
}

export function useCreateExecution(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: ExecutionCreate) =>
			executionsApi.create(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["executions", projectId] });
		},
	});
}

export function useStartExecution(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (executionId: string) =>
			executionsApi.start(projectId, executionId),
		onSuccess: (_, executionId) => {
			queryClient.invalidateQueries({
				queryKey: ["execution", projectId, executionId],
			});
			queryClient.invalidateQueries({ queryKey: ["executions", projectId] });
		},
	});
}

export function useCompleteExecution(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			executionId,
			data,
		}: {
			executionId: string;
			data: ExecutionComplete;
		}) => executionsApi.complete(projectId, executionId, data),
		onSuccess: (_, { executionId }) => {
			queryClient.invalidateQueries({
				queryKey: ["execution", projectId, executionId],
			});
			queryClient.invalidateQueries({ queryKey: ["executions", projectId] });
		},
	});
}

export function useUpdateExecutionConfig(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: ExecutionEnvironmentConfigUpdate) =>
			executionsApi.updateConfig(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["execution-config", projectId],
			});
		},
	});
}
