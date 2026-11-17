import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { Project } from "@tracertm/types";

import { useAuthStore } from "@/stores/authStore";

import { ApiError } from "@/api/client-errors";

import { API_ORIGIN } from "@/config/api-origin";

const API_URL = API_ORIGIN;

function authHeaders(token: string | null): Record<string, string> {
  const headers: Record<string, string> = {};
  if (token?.trim()) {
    headers["Authorization"] = `Bearer ${token.trim()}`;
  }
  return headers;
}

export async function fetchProjects(token: string | null): Promise<Project[]> {
  const res = await fetch(`${API_URL}/api/v1/projects`, {
    credentials: "include",
    headers: { ...authHeaders(token) },
  });
  if (!res.ok) {
    throw new ApiError(res.status, "Failed to fetch projects", await res.text());
  }
  const data = await res.json();
  // The gateway publishes its project summaries as { count, items } while
  // established adapters use either an array or { projects }.
  const projectsArray = Array.isArray(data) ? data : (data["projects"] ?? data["items"]);
  if (
    !Array.isArray(projectsArray) ||
    !projectsArray.every((project) => project && typeof project.id === "string")
  )
    throw new ApiError(502, "Invalid project list response");
  // Transform snake_case to camelCase for frontend compatibility
  return projectsArray.map((project: any) =>
    Object.assign(project, {
      createdAt: project.created_at ?? project.createdAt,
      updatedAt: project.updated_at ?? project.updatedAt,
    }),
  );
}

export async function fetchProject(id: string, token: string | null): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects/${encodeURIComponent(id)}`, {
    credentials: "include",
    headers: {
      "X-Bulk-Operation": "true",
      ...authHeaders(token),
    },
  });
  if (!res.ok) {
    // A listed project still exists when the detail capability is unavailable.
    // Render the real summary with a visible warning, never a false 404 screen.
    if (res.status === 501 || res.status === 404) {
      const projects = await fetchProjects(token);
      const summary = projects.find((project) => project.id === id);
      if (summary) return { ...summary, detailUnavailable: res.status } as Project;
    }
    throw new ApiError(res.status, "Failed to fetch project", await res.text());
  }
  const data = await res.json();
  if (!data || data.id !== id) throw new ApiError(502, "Invalid project detail response");
  return {
    ...data,
    createdAt: data["created_at"] ?? data["createdAt"],
    updatedAt: data["updated_at"] ?? data["updatedAt"],
  } as Project;
}

async function createProject(
  data: { name: string; description?: string | undefined },
  token: string | null,
): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects`, {
    body: JSON.stringify(data),
    credentials: "include",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    method: "POST",
  });
  if (!res.ok) {
    throw new Error("Failed to create project");
  }
  return res.json() as Promise<Project>;
}

async function updateProject(
  id: string,
  data: Partial<Project>,
  token: string | null,
): Promise<Project> {
  const res = await fetch(`${API_URL}/api/v1/projects/${encodeURIComponent(id)}`, {
    body: JSON.stringify(data),
    credentials: "include",
    headers: { "Content-Type": "application/json", ...authHeaders(token) },
    method: "PATCH",
  });
  if (!res.ok) {
    throw new Error("Failed to update project");
  }
  return res.json() as Promise<Project>;
}

async function deleteProject(id: string, token: string | null): Promise<void> {
  const res = await fetch(`${API_URL}/api/v1/projects/${encodeURIComponent(id)}`, {
    credentials: "include",
    headers: authHeaders(token),
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error("Failed to delete project");
  }
}

export function useProjects() {
  const token = useAuthStore((s) => s.token);
  return useQuery({
    enabled: Boolean(token),
    queryFn: async () => fetchProjects(token),
    queryKey: ["projects", token ?? ""],
    refetchOnWindowFocus: false,
    staleTime: 5 * 60 * 1000,
  });
}

export function useProject(id: string) {
  const token = useAuthStore((s) => s.token);
  return useQuery({
    enabled: Boolean(id) && Boolean(token),
    queryFn: async () => fetchProject(id, token),
    queryKey: ["projects", id, token ?? ""],
    retry: 1,
  });
}

export function useCreateProject() {
  const _queryClient = useQueryClient();
  const token = useAuthStore((s) => s.token);
  return useMutation({
    mutationFn: async (data: { name: string; description?: string }) => createProject(data, token),
    onSuccess: () => {
      _queryClient.invalidateQueries({ queryKey: ["projects"] });
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
      _queryClient.invalidateQueries({ queryKey: ["projects"] });
      _queryClient.invalidateQueries({ queryKey: ["project", _id] });
    },
  });
}

export function useDeleteProject() {
  const _queryClient = useQueryClient();
  const token = useAuthStore((s) => s.token);
  return useMutation({
    mutationFn: async (id: string) => deleteProject(id, token),
    onSuccess: () => {
      _queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
  });
}
