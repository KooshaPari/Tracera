/**
 * React Query hooks for GitHub API.
 */

import { useMutation, useQuery } from '@tanstack/react-query';

import type { CreateRepoRequest, GitHubRepo } from '../api/github';

import {
  createGitHubRepo,
  deleteGitHubAppInstallation,
  getGitHubAppInstallUrl,
  linkGitHubAppInstallation,
  listGitHubAppInstallations,
  listGitHubRepos,
} from '../api/github';

/**
 * Get GitHub App installation URL.
 */
export function useGitHubAppInstallUrl(accountId: string | undefined) {
  return useQuery({
    enabled: Boolean(accountId),
    queryFn: async () => getGitHubAppInstallUrl(accountId!),
    queryKey: ['github', 'app', 'install-url', accountId],
  });
}

/**
 * List GitHub App installations for an account.
 */
export function useGitHubAppInstallations(accountId: string | undefined) {
  return useQuery({
    enabled: Boolean(accountId),
    queryFn: async () => listGitHubAppInstallations(accountId!),
    queryKey: ['github', 'app', 'installations', accountId],
  });
}

/**
 * Link GitHub App installation.
 */
export function useLinkGitHubAppInstallation() {
  return useMutation({
    mutationFn: async ({
      installationId,
      accountId,
    }: {
      installationId: string;
      accountId: string;
    }) => linkGitHubAppInstallation(installationId, accountId),
  });
}

/**
 * Delete GitHub App installation.
 */
export function useDeleteGitHubAppInstallation() {
  return useMutation({
    mutationFn: async (installationId: string) => deleteGitHubAppInstallation(installationId),
  });
}

/**
 * List GitHub repositories.
 */
export function useGitHubRepos(params: {
  accountId?: string;
  installationId?: string;
  credentialId?: string;
  search?: string;
  perPage?: number;
  page?: number;
}) {
  return useQuery({
    enabled: Boolean(params.installationId ?? params.credentialId),
    queryFn: async () => listGitHubRepos(params),
    queryKey: ['github', 'repos', params],
  });
}

/**
 * Create GitHub repository.
 */
export function useCreateGitHubRepo() {
  return useMutation<GitHubRepo, Error, CreateRepoRequest>({
    mutationFn: async (data: CreateRepoRequest) => createGitHubRepo(data),
  });
}
