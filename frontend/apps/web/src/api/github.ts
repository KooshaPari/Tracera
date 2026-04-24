/**
 * GitHub API client functions.
 * Sends Bearer token via getAuthHeaders() for backend auth.
 */

import { client } from '@/api/client';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

/**
 * Default fetch config for authenticated requests
 */
const authHeaders = (): HeadersInit => ({
  'Content-Type': 'application/json',
  ...client.getAuthHeaders(),
});

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === '[object Object]';

const readStringField = (obj: Record<string, unknown>, key: string): string | undefined => {
  const value = obj[key];
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
};

const readNumberField = (obj: Record<string, unknown>, key: string): number | undefined => {
  const value = obj[key];
  if (typeof value === 'number') {
    return value;
  }
  return undefined;
};

const isGitHubRepo = (value: unknown): value is GitHubRepo => {
  if (!isRecordObject(value)) {
    return false;
  }

  const { owner } = value;
  if (!isRecordObject(owner)) {
    return false;
  }

  return (
    typeof value['id'] === 'number' &&
    typeof value['name'] === 'string' &&
    typeof value['full_name'] === 'string' &&
    typeof value['html_url'] === 'string' &&
    typeof value['private'] === 'boolean' &&
    typeof value['default_branch'] === 'string' &&
    typeof owner['login'] === 'string' &&
    typeof owner['avatar_url'] === 'string'
  );
};

const parseRepoListResponse = (data: unknown): GitHubRepoListResponse => {
  if (!isRecordObject(data)) {
    throw new Error('Invalid GitHub repo list response');
  }

  const reposValue = data['repos'];
  if (!Array.isArray(reposValue)) {
    throw new TypeError('Invalid GitHub repo list response');
  }
  const repos = reposValue.filter(isGitHubRepo);
  if (repos.length !== reposValue.length) {
    throw new Error('Invalid GitHub repo list response');
  }

  const page = readNumberField(data, 'page');
  const perPage = readNumberField(data, 'per_page');
  if (page === undefined || perPage === undefined) {
    throw new Error('Invalid GitHub repo list response');
  }

  return {
    page,
    per_page: perPage,
    repos,
  };
};

const parseInstallUrlResponse = (data: unknown): { install_url: string; state: string } => {
  if (!isRecordObject(data)) {
    throw new Error('Invalid GitHub install URL response');
  }

  const installUrl = readStringField(data, 'install_url');
  const state = readStringField(data, 'state');
  if (!installUrl || !state) {
    throw new Error('Invalid GitHub install URL response');
  }

  return {
    install_url: installUrl,
    state,
  };
};

const parseInstallationsResponse = (data: unknown): GitHubAppInstallationListResponse => {
  if (!isRecordObject(data)) {
    throw new Error('Invalid GitHub installations response');
  }

  const { installations } = data;
  const total = readNumberField(data, 'total');

  if (!Array.isArray(installations) || total === undefined) {
    throw new Error('Invalid GitHub installations response');
  }

  const filteredInstallations = installations.filter(
    (installation): installation is GitHubAppInstallation =>
      isRecordObject(installation) &&
      typeof installation['id'] === 'string' &&
      typeof installation['installation_id'] === 'number' &&
      typeof installation['account_login'] === 'string' &&
      typeof installation['target_type'] === 'string' &&
      isRecordObject(installation['permissions']) &&
      typeof installation['repository_selection'] === 'string' &&
      typeof installation['created_at'] === 'string',
  );

  if (filteredInstallations.length !== installations.length) {
    throw new Error('Invalid GitHub installations response');
  }

  return {
    installations: filteredInstallations,
    total,
  };
};

const parseLinkResponse = (
  data: unknown,
): { account_id: string; installation_id: string; status: string } => {
  if (!isRecordObject(data)) {
    throw new Error('Invalid GitHub installation link response');
  }

  const accountId = readStringField(data, 'account_id');
  const installationId = readStringField(data, 'installation_id');
  const status = readStringField(data, 'status');

  if (!accountId || !installationId || !status) {
    throw new Error('Invalid GitHub installation link response');
  }

  return {
    account_id: accountId,
    installation_id: installationId,
    status,
  };
};

const parseStatusResponse = (data: unknown): { status: string } => {
  if (!isRecordObject(data)) {
    throw new Error('Invalid GitHub installation response');
  }

  const status = readStringField(data, 'status');
  if (!status) {
    throw new Error('Invalid GitHub installation response');
  }

  return { status };
};

const parseRepoResponse = (data: unknown): GitHubRepo => {
  if (!isGitHubRepo(data)) {
    throw new Error('Invalid GitHub repo response');
  }
  return data;
};

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

interface GitHubRepoListResponse {
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

interface GitHubAppInstallationListResponse {
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

export const getGitHubAppInstallUrl = async (
  accountId: string,
): Promise<{ install_url: string; state: string }> => {
  const headers = authHeaders();
  const res = await fetch(
    `${API_URL}/api/v1/integrations/github/app/install-url?account_id=${accountId}`,
    {
      headers,
      method: 'GET',
    },
  );
  if (!res.ok) {
    throw new Error('Failed to get installation URL');
  }
  return parseInstallUrlResponse(await res.json());
};

export const listGitHubAppInstallations = async (
  accountId: string,
): Promise<GitHubAppInstallationListResponse> => {
  const headers = authHeaders();
  const res = await fetch(
    `${API_URL}/api/v1/integrations/github/app/installations?account_id=${accountId}`,
    {
      headers,
      method: 'GET',
    },
  );
  if (!res.ok) {
    throw new Error('Failed to list installations');
  }
  return parseInstallationsResponse(await res.json());
};

export const linkGitHubAppInstallation = async (
  installationId: string,
  accountId: string,
): Promise<{ account_id: string; installation_id: string; status: string }> => {
  const headers = authHeaders();
  const res = await fetch(
    `${API_URL}/api/v1/integrations/github/app/installations/${installationId}/link`,
    {
      body: JSON.stringify({ account_id: accountId }),
      headers,
      method: 'POST',
    },
  );
  if (!res.ok) {
    throw new Error('Failed to link installation');
  }
  return parseLinkResponse(await res.json());
};

export const deleteGitHubAppInstallation = async (
  installationId: string,
): Promise<{ status: string }> => {
  const headers = authHeaders();
  const res = await fetch(
    `${API_URL}/api/v1/integrations/github/app/installations/${installationId}`,
    {
      headers,
      method: 'DELETE',
    },
  );
  if (!res.ok) {
    throw new Error('Failed to delete installation');
  }
  return parseStatusResponse(await res.json());
};

export const listGitHubRepos = async (params: {
  accountId?: string;
  installationId?: string;
  credentialId?: string;
  search?: string;
  perPage?: number;
  page?: number;
}): Promise<GitHubRepoListResponse> => {
  const searchParams = new URLSearchParams();
  const entries: [string, string | number | undefined][] = [
    ['account_id', params.accountId],
    ['credential_id', params.credentialId],
    ['installation_id', params.installationId],
    ['page', params.page],
    ['per_page', params.perPage],
    ['search', params.search],
  ];

  for (const [key, value] of entries) {
    if (typeof value === 'string') {
      if (value !== '') {
        searchParams.set(key, value);
      }
    } else if (typeof value !== 'undefined' && Number.isFinite(value)) {
      searchParams.set(key, String(value));
    }
  }

  const headers = authHeaders();
  const res = await fetch(
    `${API_URL}/api/v1/integrations/github/repos?${searchParams.toString()}`,
    {
      headers,
      method: 'GET',
    },
  );
  if (!res.ok) {
    throw new Error('Failed to list repos');
  }
  return parseRepoListResponse(await res.json());
};

export const createGitHubRepo = async (data: CreateRepoRequest): Promise<GitHubRepo> => {
  const headers = authHeaders();
  const res = await fetch(`${API_URL}/api/v1/integrations/github/repos`, {
    body: JSON.stringify(data),
    headers,
    method: 'POST',
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Failed to create repo' }));
    if (isRecordObject(error)) {
      const detail = readStringField(error, 'detail');
      if (detail) {
        throw new Error(detail);
      }
    }
    throw new Error('Failed to create repo');
  }
  return parseRepoResponse(await res.json());
};

const githubApi = {
  createGitHubRepo,
  deleteGitHubAppInstallation,
  getGitHubAppInstallUrl,
  linkGitHubAppInstallation,
  listGitHubAppInstallations,
  listGitHubRepos,
};

export default githubApi;
