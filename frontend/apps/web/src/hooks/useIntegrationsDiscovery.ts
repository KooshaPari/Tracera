import * as reactQuery from '@tanstack/react-query';

import type * as TracerTypes from '@tracertm/types';

import { API_URL, getAuthHeaders } from '@/hooks/integrationsApi';

interface GitHubReposResponse {
  repos: TracerTypes.GitHubRepo[];
  page: number;
  perPage: number;
}

interface GitHubIssuesResponse {
  issues: TracerTypes.GitHubIssue[];
  page: number;
  perPage: number;
}

interface GitHubProjectsResponse {
  projects: TracerTypes.GitHubProject[];
}

interface LinearTeamsResponse {
  teams: TracerTypes.LinearTeam[];
}

interface LinearIssuesResponse {
  issues: TracerTypes.LinearIssue[];
}

interface LinearProjectsResponse {
  projects: TracerTypes.LinearProject[];
}

async function fetchGitHubRepos(
  credentialId: string,
  search?: string,
  page?: number,
): Promise<GitHubReposResponse> {
  const params = new URLSearchParams({ credential_id: credentialId });
  if (search !== undefined && search !== '') {
    params.set('search', search);
  }
  if (page !== undefined) {
    params.set('page', String(page));
  }

  const res = await fetch(`${API_URL}/api/v1/integrations/github/repos?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch GitHub repos: ${res.status}`);
  }
  const data = await res.json();
  const repos = (data['repos'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    page: data['page'],
    perPage: data['per_page'],
    repos: repos.map((repo) => ({
      defaultBranch: repo['default_branch'],
      description: repo['description'],
      fullName: repo['full_name'],
      htmlUrl: repo['html_url'],
      id: repo['id'],
      name: repo['name'],
      owner: {
        avatarUrl: (repo['owner'] as { avatar_url?: string } | undefined)?.avatar_url,
        login: (repo['owner'] as { login?: string } | undefined)?.login,
      },
      private: repo['private'],
      updatedAt: repo['updated_at'],
    })) as TracerTypes.GitHubRepo[],
  };
}

async function fetchGitHubIssues(
  credentialId: string,
  owner: string,
  repo: string,
  state?: string,
  page?: number,
): Promise<GitHubIssuesResponse> {
  const params = new URLSearchParams({ credential_id: credentialId });
  if (state !== undefined) {
    params.set('state', state);
  }
  if (page !== undefined) {
    params.set('page', String(page));
  }

  const res = await fetch(
    `${API_URL}/api/v1/integrations/github/repos/${owner}/${repo}/issues?${params}`,
    { headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() } },
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch GitHub issues: ${res.status}`);
  }
  const data = await res.json();
  const issues = (data['issues'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    issues: issues.map((issue) => ({
      assignees: (issue['assignees'] as string[] | undefined) ?? [],
      body: issue['body'],
      createdAt: issue['created_at'],
      htmlUrl: issue['html_url'],
      id: issue['id'],
      labels: (issue['labels'] as string[] | undefined) ?? [],
      number: issue['number'],
      state: issue['state'],
      title: issue['title'],
      updatedAt: issue['updated_at'],
      user: {
        avatarUrl: (issue['user'] as { avatar_url?: string } | undefined)?.avatar_url,
        login: (issue['user'] as { login?: string } | undefined)?.login,
      },
    })) as TracerTypes.GitHubIssue[],
    page: data['page'],
    perPage: data['per_page'],
  };
}

async function fetchGitHubProjects(
  credentialId: string,
  owner: string,
  isOrg?: boolean,
): Promise<GitHubProjectsResponse> {
  const params = new URLSearchParams({
    credential_id: credentialId,
    owner,
  });
  if (isOrg !== undefined) {
    params.set('is_org', String(isOrg));
  }

  const res = await fetch(`${API_URL}/api/v1/integrations/github/projects?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch GitHub projects: ${res.status}`);
  }
  const data = await res.json();
  const projects = (data['projects'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    projects: projects.map((project) => ({
      closed: project['closed'],
      createdAt: project['created_at'],
      description: project['description'],
      id: project['id'],
      public: project['public'],
      title: project['title'],
      updatedAt: project['updated_at'],
      url: project['url'],
    })) as TracerTypes.GitHubProject[],
  };
}

async function fetchLinearTeams(credentialId: string): Promise<LinearTeamsResponse> {
  const res = await fetch(
    `${API_URL}/api/v1/integrations/linear/teams?credential_id=${credentialId}`,
    { headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() } },
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch Linear teams: ${res.status}`);
  }
  const data = await res.json();
  const teams = (data['teams'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    teams: teams.map((team) => ({
      color: team['color'],
      description: team['description'],
      icon: team['icon'],
      id: team['id'],
      key: team['key'],
      name: team['name'],
    })) as TracerTypes.LinearTeam[],
  };
}

async function fetchLinearIssues(
  credentialId: string,
  teamId: string,
  first?: number,
): Promise<LinearIssuesResponse> {
  const params = new URLSearchParams({ credential_id: credentialId });
  if (first !== undefined) {
    params.set('first', String(first));
  }

  const res = await fetch(
    `${API_URL}/api/v1/integrations/linear/teams/${teamId}/issues?${params}`,
    { headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() } },
  );
  if (!res.ok) {
    throw new Error(`Failed to fetch Linear issues: ${res.status}`);
  }
  const data = await res.json();
  const issues = (data['issues'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    issues: issues.map((issue) => ({
      assignee: issue['assignee'],
      createdAt: issue['created_at'],
      description: issue['description'],
      id: issue['id'],
      identifier: issue['identifier'],
      labels: (issue['labels'] as string[] | undefined) ?? [],
      priority: issue['priority'],
      state: issue['state'],
      title: issue['title'],
      updatedAt: issue['updated_at'],
      url: issue['url'],
    })) as TracerTypes.LinearIssue[],
  };
}

async function fetchLinearProjects(
  credentialId: string,
  first?: number,
): Promise<LinearProjectsResponse> {
  const params = new URLSearchParams({ credential_id: credentialId });
  if (first !== undefined) {
    params.set('first', String(first));
  }

  const res = await fetch(`${API_URL}/api/v1/integrations/linear/projects?${params}`, {
    headers: { 'X-Bulk-Operation': 'true', ...getAuthHeaders() },
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch Linear projects: ${res.status}`);
  }
  const data = await res.json();
  const projects = (data['projects'] as Record<string, unknown>[] | undefined) ?? [];
  return {
    projects: projects.map((project) => ({
      description: project['description'],
      id: project['id'],
      name: project['name'],
      progress: project['progress'],
      startDate: project['start_date'],
      state: project['state'],
      targetDate: project['target_date'],
      url: project['url'],
    })) as TracerTypes.LinearProject[],
  };
}

const useGitHubRepos = (
  credentialId: string,
  search?: string,
  page?: number,
): reactQuery.UseQueryResult<GitHubReposResponse> =>
  reactQuery.useQuery({
    enabled: Boolean(credentialId),
    queryFn: async () => fetchGitHubRepos(credentialId, search, page),
    queryKey: ['integrations', 'github', 'repos', credentialId, search, page],
  });

const useGitHubIssues = (
  credentialId: string,
  owner: string,
  repo: string,
  state?: string,
  page?: number,
): reactQuery.UseQueryResult<GitHubIssuesResponse> =>
  reactQuery.useQuery({
    enabled: Boolean(credentialId) && Boolean(owner) && Boolean(repo),
    queryFn: async () => fetchGitHubIssues(credentialId, owner, repo, state, page),
    queryKey: ['integrations', 'github', 'issues', credentialId, owner, repo, state, page],
  });

const useGitHubProjects = (
  credentialId: string,
  owner: string,
  isOrg?: boolean,
): reactQuery.UseQueryResult<GitHubProjectsResponse> =>
  reactQuery.useQuery({
    enabled: Boolean(credentialId) && Boolean(owner),
    queryFn: async () => fetchGitHubProjects(credentialId, owner, isOrg),
    queryKey: ['integrations', 'github', 'projects', credentialId, owner, isOrg],
  });

const useLinearTeams = (credentialId: string): reactQuery.UseQueryResult<LinearTeamsResponse> =>
  reactQuery.useQuery({
    enabled: Boolean(credentialId),
    queryFn: async () => fetchLinearTeams(credentialId),
    queryKey: ['integrations', 'linear', 'teams', credentialId],
  });

const useLinearIssues = (
  credentialId: string,
  teamId: string,
  first?: number,
): reactQuery.UseQueryResult<LinearIssuesResponse> =>
  reactQuery.useQuery({
    enabled: Boolean(credentialId) && Boolean(teamId),
    queryFn: async () => fetchLinearIssues(credentialId, teamId, first),
    queryKey: ['integrations', 'linear', 'issues', credentialId, teamId, first],
  });

const useLinearProjects = (
  credentialId: string,
  first?: number,
): reactQuery.UseQueryResult<LinearProjectsResponse> =>
  reactQuery.useQuery({
    enabled: Boolean(credentialId),
    queryFn: async () => fetchLinearProjects(credentialId, first),
    queryKey: ['integrations', 'linear', 'projects', credentialId, first],
  });

export {
  useGitHubIssues,
  useGitHubProjects,
  useGitHubRepos,
  useLinearIssues,
  useLinearProjects,
  useLinearTeams,
};
