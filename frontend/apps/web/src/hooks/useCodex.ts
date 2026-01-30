// React hooks for Codex agent integration

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { codexApi, type CodexReviewRequest } from "../api/codex";

export function useCodexInteractions(
	projectId: string,
	options?: {
		limit?: number;
		offset?: number;
		status?: string;
		task_type?: string;
	},
) {
	return useQuery({
		queryKey: ["codex-interactions", projectId, options],
		queryFn: () => codexApi.listInteractions(projectId, options),
		enabled: !!projectId,
	});
}

export function useCodexAuthStatus(projectId: string) {
	return useQuery({
		queryKey: ["codex-auth-status", projectId],
		queryFn: () => codexApi.getAuthStatus(projectId),
		enabled: !!projectId,
		refetchInterval: 30000, // Refresh every 30s
	});
}

export function useCodexReviewImage(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: CodexReviewRequest) =>
			codexApi.reviewImage(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["codex-interactions", projectId],
			});
		},
	});
}

export function useCodexReviewVideo(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: CodexReviewRequest) =>
			codexApi.reviewVideo(projectId, data),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["codex-interactions", projectId],
			});
		},
	});
}
