import {
	type UseMutationOptions,
	type UseQueryOptions,
	useMutation,
	useQuery,
	useQueryClient,
} from "@tanstack/react-query";
import type {
	Agent,
	Item,
	Link,
	Mutation,
	PaginatedResponse,
	Project,
} from "@tracertm/types";
import { apiClient, handleApiResponse } from "./client";

// Query Keys
export const queryKeys = {
	projects: ["projects"] as const,
	project: (id: string) => ["projects", id] as const,
	projectItems: (projectId: string, filters?: Record<string, unknown>) =>
		["projects", projectId, "items", filters] as const,
	item: (id: string) => ["items", id] as const,
	projectLinks: (projectId: string) =>
		["projects", projectId, "links"] as const,
	agents: ["agents"] as const,
	mutations: (filters?: Record<string, unknown>) =>
		["mutations", filters] as const,
};

// Projects
export function useProjects(
	options?: UseQueryOptions<PaginatedResponse<Project>>,
) {
	return useQuery({
		queryKey: queryKeys.projects,
		queryFn: () => handleApiResponse(apiClient.GET("/api/v1/projects", {})),
		...options,
	});
}

export function useProject(
	projectId: string,
	options?: UseQueryOptions<Project>,
) {
	return useQuery({
		queryKey: queryKeys.project(projectId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}", {
					params: { path: { projectId } },
				}),
			),
		enabled: !!projectId,
		...options,
	});
}

export function useCreateProject(
	options?: UseMutationOptions<
		Project,
		Error,
		{ name: string; description?: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data) =>
			handleApiResponse(apiClient.POST("/api/v1/projects", { body: data })),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
		...options,
	});
}

export function useUpdateProject(
	options?: UseMutationOptions<
		Project,
		Error,
		{ projectId: string; data: Partial<Project> }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/projects/{projectId}", {
					params: { path: { projectId } },
					body: data,
				}),
			),
		onSuccess: (_, { projectId }) => {
			queryClient.invalidateQueries({ queryKey: queryKeys.project(projectId) });
			queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
		...options,
	});
}

export function useDeleteProject(
	options?: UseMutationOptions<void, Error, string>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (projectId) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/projects/{projectId}", {
					params: { path: { projectId } },
				}),
			),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
		...options,
	});
}

// Items
export function useProjectItems(
	projectId: string,
	filters?: {
		view?: string;
		status?: string;
		priority?: string;
		page?: number;
		pageSize?: number;
	},
	options?: UseQueryOptions<PaginatedResponse<Item>>,
) {
	return useQuery({
		queryKey: queryKeys.projectItems(projectId, filters),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/items", {
					params: {
						path: { projectId },
						query: filters,
					},
				}),
			),
		enabled: !!projectId,
		...options,
	});
}

export function useItem(itemId: string, options?: UseQueryOptions<Item>) {
	return useQuery({
		queryKey: queryKeys.item(itemId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/items/{itemId}", {
					params: { path: { itemId } },
				}),
			),
		enabled: !!itemId,
		...options,
	});
}

export function useCreateItem(
	options?: UseMutationOptions<
		Item,
		Error,
		{ projectId: string; data: Partial<Item> }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/items", {
					params: { path: { projectId } },
					body: data as any,
				}),
			),
		onSuccess: (_, { projectId }) => {
			queryClient.invalidateQueries({
				queryKey: queryKeys.projectItems(projectId),
			});
		},
		...options,
	});
}

export function useUpdateItem(
	options?: UseMutationOptions<
		Item,
		Error,
		{ itemId: string; data: Partial<Item> }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ itemId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/items/{itemId}", {
					params: { path: { itemId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({ queryKey: queryKeys.item(data.id) });
			queryClient.invalidateQueries({
				queryKey: queryKeys.projectItems(data.projectId),
			});
		},
		...options,
	});
}

export function useDeleteItem(
	options?: UseMutationOptions<
		void,
		Error,
		{ itemId: string; projectId: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ itemId }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/items/{itemId}", {
					params: { path: { itemId } },
				}),
			),
		onSuccess: (_, { projectId }) => {
			queryClient.invalidateQueries({
				queryKey: queryKeys.projectItems(projectId),
			});
		},
		...options,
	});
}

// Links
export function useProjectLinks(
	projectId: string,
	options?: UseQueryOptions<Link[]>,
) {
	return useQuery({
		queryKey: queryKeys.projectLinks(projectId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/links", {
					params: { path: { projectId } },
				}),
			),
		enabled: !!projectId,
		...options,
	});
}

export function useCreateLink(
	options?: UseMutationOptions<
		Link,
		Error,
		{ projectId: string; data: Partial<Link> }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/links", {
					params: { path: { projectId } },
					body: data as any,
				}),
			),
		onSuccess: (_, { projectId }) => {
			queryClient.invalidateQueries({
				queryKey: queryKeys.projectLinks(projectId),
			});
		},
		...options,
	});
}

export function useDeleteLink(
	options?: UseMutationOptions<
		void,
		Error,
		{ linkId: string; projectId: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ linkId }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/links/{linkId}", {
					params: { path: { linkId } },
				}),
			),
		onSuccess: (_, { projectId }) => {
			queryClient.invalidateQueries({
				queryKey: queryKeys.projectLinks(projectId),
			});
		},
		...options,
	});
}

// Agents
export function useAgents(options?: UseQueryOptions<Agent[]>) {
	return useQuery({
		queryKey: queryKeys.agents,
		queryFn: () => handleApiResponse(apiClient.GET("/api/v1/agents", {})),
		refetchInterval: 5000, // Poll every 5 seconds
		...options,
	});
}

// Mutations (for sync)
export function useMutations(
	filters?: { agentId?: string; synced?: boolean; since?: string },
	options?: UseQueryOptions<Mutation[]>,
) {
	return useQuery({
		queryKey: queryKeys.mutations(filters),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/mutations", {
					params: { query: filters },
				}),
			),
		...options,
	});
}

export function useCreateMutation(
	options?: UseMutationOptions<Mutation, Error, Partial<Mutation>>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (data) =>
			handleApiResponse(
				apiClient.POST("/api/v1/mutations", { body: data as any }),
			),
		onSuccess: () => {
			queryClient.invalidateQueries({ queryKey: queryKeys.mutations() });
		},
		...options,
	});
}
