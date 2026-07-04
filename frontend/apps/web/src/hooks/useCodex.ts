// React hooks for Codex agent integration

import { useMutation, useQuery } from '@tanstack/react-query';

import type { CodexReviewRequest } from '../api/codex';

import { codexApi } from '../api/codex';

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
    enabled: Boolean(projectId),
    queryFn: async () => codexApi.listInteractions(projectId, options),
    queryKey: ['codex-interactions', projectId, options],
  });
}

export function useCodexAuthStatus(projectId: string) {
  return useQuery({
    enabled: Boolean(projectId),
    queryFn: async () => codexApi.getAuthStatus(projectId),
    queryKey: ['codex-auth-status', projectId],
    refetchInterval: 30_000, // Refresh every 30s
  });
}

export function useCodexReviewImage(projectId: string) {
  return useMutation({
    mutationFn: async (data: CodexReviewRequest) => codexApi.reviewImage(projectId, data),
  });
}

export function useCodexReviewVideo(projectId: string) {
  return useMutation({
    mutationFn: async (data: CodexReviewRequest) => codexApi.reviewVideo(projectId, data),
  });
}
