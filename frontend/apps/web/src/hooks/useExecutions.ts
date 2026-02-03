// React hooks for execution management

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { executionsApi } from "../api/executions";
import type {
	ExecutionComplete,
	ExecutionCreate,
	ExecutionEnvironmentConfigUpdate,
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
		enabled: !!projectId,
		queryFn: () => executionsApi.list(projectId, options),
		queryKey: ["executions", projectId, options],
	});
}

export function useExecution(projectId: string, executionId: string) {
	return useQuery({
		enabled: !!projectId && !!executionId,
		queryFn: () => executionsApi.get(projectId, executionId),
		queryKey: ["execution", projectId, executionId],
	});
}

export function useExecutionArtifacts(
	projectId: string,
	executionId: string,
	artifactType?: string,
) {
	return useQuery({
		enabled: !!projectId && !!executionId,
		queryFn: () =>
			executionsApi.listArtifacts(projectId, executionId, artifactType),
		queryKey: ["execution-artifacts", projectId, executionId, artifactType],
	});
}

export function useExecutionConfig(projectId: string) {
	return useQuery({
		enabled: !!projectId,
		queryFn: () => executionsApi.getConfig(projectId),
		queryKey: ["execution-config", projectId],
	});
}

export function useCreateExecution(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: ExecutionCreate) =>
			executionsApi.create(projectId, data),
		onSuccess: () => {
			undefined;
		},
	});
}

export function useStartExecution(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (executionId: string) =>
			executionsApi.start(projectId, executionId),
		onSuccess: (_, executionId) => {
			undefined;
			undefined;
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
			undefined;
			undefined;
		},
	});
}

export function useUpdateExecutionConfig(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: ExecutionEnvironmentConfigUpdate) =>
			executionsApi.updateConfig(projectId, data),
		onSuccess: () => {
			undefined;
		},
	});
}
