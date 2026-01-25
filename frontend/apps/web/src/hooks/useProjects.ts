import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type { Project } from "@tracertm/types";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function fetchProjects(): Promise<Project[]> {
	const res = await fetch(`${API_URL}/api/v1/projects`);
	if (!res.ok) throw new Error("Failed to fetch projects");
	const data = await res.json();
	// API returns { total: number, projects: Project[] }, extract projects array
	const projectsArray = Array.isArray(data) ? data : data.projects || [];
	// Transform snake_case to camelCase for frontend compatibility
	return projectsArray.map((project: any) => ({
		...project,
		createdAt: project.created_at || project.createdAt,
		updatedAt: project.updated_at || project.updatedAt,
	}));
}

async function fetchProject(id: string): Promise<Project> {
	const res = await fetch(`${API_URL}/api/v1/projects/${id}`, {
		headers: {
			"X-Bulk-Operation": "true", // Skip rate limiting for project fetches
		},
	});
	if (!res.ok) {
		const errorText = await res.text();
		throw new Error(`Failed to fetch project: ${res.status} ${errorText}`);
	}
	const data = await res.json();
	// Transform snake_case to camelCase for frontend compatibility
	return {
		...data,
		createdAt: data.created_at || data.createdAt,
		updatedAt: data.updated_at || data.updatedAt,
	} as Project;
}

async function createProject(data: {
	name: string;
	description?: string | undefined;
}): Promise<Project> {
	const res = await fetch(`${API_URL}/api/v1/projects`, {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(data),
	});
	if (!res.ok) throw new Error("Failed to create project");
	return res.json() as Promise<Project>;
}

async function updateProject(
	id: string,
	data: Partial<Project>,
): Promise<Project> {
	const res = await fetch(`${API_URL}/api/v1/projects/${id}`, {
		method: "PATCH",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify(data),
	});
	if (!res.ok) throw new Error("Failed to update project");
	return res.json() as Promise<Project>;
}

async function deleteProject(id: string): Promise<void> {
	const res = await fetch(`${API_URL}/api/v1/projects/${id}`, {
		method: "DELETE",
	});
	if (!res.ok) throw new Error("Failed to delete project");
}

export function useProjects() {
	return useQuery({
		queryKey: ["projects"],
		queryFn: fetchProjects,
	});
}

export function useProject(id: string) {
	return useQuery({
		queryKey: ["projects", id],
		queryFn: () => fetchProject(id),
		enabled: !!id,
		retry: 1, // Only retry once on failure
		// Don't use throwOnError - React Query v5 handles errors differently
		// Errors will be available in the error property
	});
}

export function useCreateProject() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: createProject,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["projects"] });
		},
	});
}

export function useUpdateProject() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: ({ id, data }: { id: string; data: Partial<Project> }) =>
			updateProject(id, data),
		onSuccess: (_, { id }) => {
			queryClient.invalidateQueries({ queryKey: ["projects"] });
			queryClient.invalidateQueries({ queryKey: ["projects", id] });
		},
	});
}

export function useDeleteProject() {
	const queryClient = useQueryClient();
	return useMutation({
		mutationFn: deleteProject,
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: ["projects"] });
		},
	});
}
