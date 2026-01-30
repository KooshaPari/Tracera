/**
 * React Query hooks for GitHub API.
 */

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
	getGitHubAppInstallUrl,
	listGitHubAppInstallations,
	linkGitHubAppInstallation,
	deleteGitHubAppInstallation,
	listGitHubRepos,
	createGitHubRepo,
	type CreateRepoRequest,
} from "../api/github";

/**
 * Get GitHub App installation URL.
 */
export function useGitHubAppInstallUrl(accountId: string | undefined) {
	return useQuery({
		queryKey: ["github", "app", "install-url", accountId],
		queryFn: () => getGitHubAppInstallUrl(accountId!),
		enabled: !!accountId,
	});
}

/**
 * List GitHub App installations for an account.
 */
export function useGitHubAppInstallations(accountId: string | undefined) {
	return useQuery({
		queryKey: ["github", "app", "installations", accountId],
		queryFn: () => listGitHubAppInstallations(accountId!),
		enabled: !!accountId,
	});
}

/**
 * Link GitHub App installation.
 */
export function useLinkGitHubAppInstallation() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({
			installationId,
			accountId,
		}: {
			installationId: string;
			accountId: string;
		}) => linkGitHubAppInstallation(installationId, accountId),
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: ["github", "app", "installations", variables.accountId],
			});
		},
	});
}

/**
 * Delete GitHub App installation.
 */
export function useDeleteGitHubAppInstallation() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteGitHubAppInstallation,
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: ["github", "app", "installations"],
			});
		},
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
		queryKey: ["github", "repos", params],
		queryFn: () => listGitHubRepos(params),
		enabled: !!(params.installationId || params.credentialId),
	});
}

/**
 * Create GitHub repository.
 */
export function useCreateGitHubRepo() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: (data: CreateRepoRequest) => createGitHubRepo(data),
		onSuccess: (_, variables) => {
			queryClient.invalidateQueries({
				queryKey: [
					"github",
					"repos",
					{ installationId: variables.installation_id },
				],
			});
		},
	});
}
