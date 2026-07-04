import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import type { Project } from '@tracertm/types';

import { useAuthStore } from '@/stores/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:4000';

function authHeaders(token: string | null): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token?.trim()) {
    headers['Authorization'] = `Bearer ${token.trim()}`;
  }
  return headers;
}

async function fetchProjects(token: string | null): Promise<Project[]> {
  const res = await fetch(`${API_URL}/api/v1/projects`, {
    credentials: 'include',
    headers: { ...authHeaders(token) },
  });
  if (!res.ok) {
    throw new Error('Failed to fetch projects');
  }
  const data = await res.json();
  // API returns { total: number, projects: Project[] }, extract projects array
  const projectsArray = Array.isArray(data) ? data : (data['projects'] ?? []);
  // Transform snake_case to camelCase for frontend compatibility
  return projectsArray.map((project: any) =>
    Object.assign(project, {
      createdAt: project.created_at ?? project.createdAt,
      updatedAt: project.updated_at ?? project.updatedAt,
    }),
  );
}

async function fetchProject(id: string, token: string | null): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects/${id}`, {
    credentials: 'include',
    headers: {
      'X-Bulk-Operation': 'true',
      ...authHeaders(token),
    },
  });
  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(`Failed to fetch project: ${res.status} ${errorText}`);
  }
  const data = await res.json();
  return {
    ...data,
    createdAt: data['created_at'] ?? data['createdAt'],
    updatedAt: data['updated_at'] ?? data['updatedAt'],
  } as Project;
}

async function createProject(
  data: { name: string; description?: string | undefined },
  token: string | null,
): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects`, {
    body: JSON.stringify(data),
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    method: 'POST',
  });
  if (!res.ok) {
    throw new Error('Failed to create project');
  }
  return res.json() as Promise<Project>;
}

async function updateProject(
  id: string,
  data: Partial<Project>,
  token: string | null,
): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects/${id}`, {
    body: JSON.stringify(data),
    credentials: 'include',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    method: 'PATCH',
  });
  if (!res.ok) {
    throw new Error('Failed to update project');
  }
  return res.json() as Promise<Project>;
}

async function deleteProject(id: string, token: string | null): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/projects/${id}`, {
    credentials: 'include',
    headers: authHeaders(token),
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete project');
  }
}

export function useProjects() {
  const token = useAuthStore((s) => s.token);
  return useQuery({
    enabled: Boolean(token),
    queryFn: async () => fetchProjects(token),
    queryKey: ['projects', token ?? ''],
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,
  });
}

export function useProject(id: string) {
  const token = useAuthStore((s) => s.token);
  return useQuery({
    enabled: Boolean(id) && Boolean(token),
    queryFn: async () => fetchProject(id, token),
    queryKey: ['projects', id, token ?? ''],
    retry: 1,
  });
}

export function useCreateProject() {
  const _queryClient = useQueryClient();
  const token = useAuthStore((s) => s.token);
  return useMutation({
    mutationFn: async (data: { name: string; description?: string }) => createProject(data, token),
    onSuccess: () => {
      _queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}

export function useUpdateProject() {
  const _queryClient = useQueryClient();
  const token = useAuthStore((s) => s.token);
  return useMutation({
    mutationFn: async ({ data, id }: { id: string; data: Partial<Project> }) =>
      updateProject(id, data, token),
    onSuccess: (_, { id: _id }) => {
      _queryClient.invalidateQueries({ queryKey: ['projects'] });
      _queryClient.invalidateQueries({ queryKey: ['project', _id] });
    },
  });
}

export function useDeleteProject() {
  const _queryClient = useQueryClient();
  const token = useAuthStore((s) => s.token);
  return useMutation({
    mutationFn: async (id: string) => deleteProject(id, token),
    onSuccess: () => {
      _queryClient.invalidateQueries({ queryKey: ['projects'] });
    },
  });
}
