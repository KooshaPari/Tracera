/**
 * GitHub API client functions.
 * Sends Bearer token via getAuthHeaders() for backend auth.
 */

import client from "@/api/client";

const { getAuthHeaders } = client;

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:4000";

/**
 * Default fetch config for authenticated requests
 */
function authHeaders(): RequestInit["headers"] {
	return {
		"Content-Type": "application/json",
		...getAuthHeaders(),
	};
}

export interface GitHubRepo {
	id: number;
	name: string;
	full_name: string;
	description?: string;
	html_url: string;
	private: boolean;
	owner: {
		login: string;
		avatar_url: string;
	};
	default_branch: string;
	updated_at?: string;
}

export interface GitHubRepoListResponse {
	repos: GitHubRepo[];
	page: number;
	per_page: number;
}

export interface GitHubAppInstallation {
	id: string;
	installation_id: number;
	account_login: string;
	target_type: string;
	permissions: Record<string, string>;
	repository_selection: string;
	suspended_at?: string;
	created_at: string;
}

export interface GitHubAppInstallationListResponse {
	installations: GitHubAppInstallation[];
	total: number;
}

export interface CreateRepoRequest {
	installation_id: string;
	account_id: string;
	name: string;
	description?: string;
	private?: boolean;
	org?: string;
}

/**
 * Get GitHub App installation URL for an account.
 */
export async function getGitHubAppInstallUrl(
	accountId: string,
): Promise<{ install_url: string; state: string }> {
	const headers = authHeaders();
	const res = await fetch(
		`${API_URL}/api/v1/integrations/github/app/install-url?account_id=${accountId}`,
		{
			method: "GET",
			...(headers && { headers }),
		},
	);
	if (!res.ok) throw new Error("Failed to get installation URL");
	return res.json();
}

/**
 * List GitHub App installations for an account.
 */
export async function listGitHubAppInstallations(
	accountId: string,
): Promise<GitHubAppInstallationListResponse> {
	const headers = authHeaders();
	const res = await fetch(
		`${API_URL}/api/v1/integrations/github/app/installations?account_id=${accountId}`,
		{
			method: "GET",
			...(headers && { headers }),
		},
	);
	if (!res.ok) throw new Error("Failed to list installations");
	return res.json();
}

/**
 * Link a GitHub App installation to an account.
 */
export async function linkGitHubAppInstallation(
	installationId: string,
	accountId: string,
): Promise<{ status: string; installation_id: string; account_id: string }> {
	const headers = authHeaders();
	const res = await fetch(
		`${API_URL}/api/v1/integrations/github/app/installations/${installationId}/link`,
		{
			method: "POST",
			...(headers && { headers }),
			body: JSON.stringify({ account_id: accountId }),
		},
	);
	if (!res.ok) throw new Error("Failed to link installation");
	return res.json();
}

/**
 * Delete a GitHub App installation.
 */
export async function deleteGitHubAppInstallation(
	installationId: string,
): Promise<{ status: string }> {
	const headers = authHeaders();
	const res = await fetch(
		`${API_URL}/api/v1/integrations/github/app/installations/${installationId}`,
		{
			method: "DELETE",
			...(headers && { headers }),
		},
	);
	if (!res.ok) throw new Error("Failed to delete installation");
	return res.json();
}

/**
 * List GitHub repositories.
 */
export async function listGitHubRepos(params: {
	accountId?: string;
	installationId?: string;
	credentialId?: string;
	search?: string;
	perPage?: number;
	page?: number;
}): Promise<GitHubRepoListResponse> {
	const searchParams = new URLSearchParams();
	if (params.accountId) searchParams.set("account_id", params.accountId);
	if (params.installationId)
		searchParams.set("installation_id", params.installationId);
	if (params.credentialId)
		searchParams.set("credential_id", params.credentialId);
	if (params.search) searchParams.set("search", params.search);
	if (params.perPage) searchParams.set("per_page", String(params.perPage));
	if (params.page) searchParams.set("page", String(params.page));

	const headers = authHeaders();
	const res = await fetch(
		`${API_URL}/api/v1/integrations/github/repos?${searchParams.toString()}`,
		{
			method: "GET",
			...(headers && { headers }),
		},
	);
	if (!res.ok) throw new Error("Failed to list repos");
	return res.json();
}

/**
 * Create a GitHub repository.
 */
export async function createGitHubRepo(
	data: CreateRepoRequest,
): Promise<GitHubRepo> {
	const headers = authHeaders();
	const res = await fetch(`${API_URL}/api/v1/integrations/github/repos`, {
		method: "POST",
		...(headers && { headers }),
		body: JSON.stringify(data),
	});
	if (!res.ok) {
		const error = await res
			.json()
			.catch(() => ({ detail: "Failed to create repo" }));
		throw new Error(error.detail || "Failed to create repo");
	}
	return res.json();
}
