// React hooks for Codex agent integration

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { codexApi } from "../api/codex";
import type { CodexReviewRequest } from "../api/codex";

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
		enabled: !!projectId,
		queryFn: () => codexApi.listInteractions(projectId, options),
		queryKey: ["codex-interactions", projectId, options],
	});
}

export function useCodexAuthStatus(projectId: string) {
	return useQuery({
		enabled: !!projectId,
		queryFn: () => codexApi.getAuthStatus(projectId),
		queryKey: ["codex-auth-status", projectId],
		refetchInterval: 30000, // Refresh every 30s
	});
}

export function useCodexReviewImage(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: CodexReviewRequest) =>
			codexApi.reviewImage(projectId, data),
		onSuccess: () => {
			undefined;
		},
	});
}

export function useCodexReviewVideo(projectId: string) {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: CodexReviewRequest) =>
			codexApi.reviewVideo(projectId, data),
		onSuccess: () => {
			undefined;
		},
	});
}
