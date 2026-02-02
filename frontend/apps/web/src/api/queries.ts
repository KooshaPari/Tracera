/* eslint-disable import/max-dependencies -- API surface file */
/* eslint-disable max-lines -- cohesive query hooks module */
/* eslint-disable new-cap -- apiClient.GET/POST/PUT/DELETE are HTTP method names */
/* eslint-disable no-void -- void used to explicitly ignore promise in callbacks */
/* eslint-disable oxc/no-rest-spread-properties -- options spread is idiomatic for React Query */
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import type {
	UseMutationOptions,
	UseMutationResult,
	UseQueryOptions,
	UseQueryResult,
} from "@tanstack/react-query";
import type {
	Item,
	Link,
	Mutation,
	PaginatedResponse,
	Project,
} from "@tracertm/types";
import client from "./client";

const { apiClient, handleApiResponse } = client;

// Query Keys (keys sorted alphabetically)
const queryKeys = {
	item: (id: string) => ["items", id] as const,
	mutations: (filters?: Record<string, unknown>) =>
		["mutations", filters] as const,
	project: (id: string) => ["projects", id] as const,
	projectItems: (projectId: string, filters?: Record<string, unknown>) =>
		["projects", projectId, "items", filters] as const,
	projectLinks: (projectId: string) =>
		["projects", projectId, "links"] as const,
	projects: ["projects"] as const,
};

// Projects
const useProjects = (
	options?: UseQueryOptions<PaginatedResponse<Project>>,
): UseQueryResult<PaginatedResponse<Project>, Error> =>
	useQuery({
		...options,
		queryFn: () => handleApiResponse(apiClient.GET("/api/v1/projects", {})),
		queryKey: queryKeys.projects,
	});

const useProject = (
	projectId: string,
	options?: UseQueryOptions<Project>,
): UseQueryResult<Project, Error> =>
	useQuery({
		...options,
		enabled: Boolean(projectId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}", {
					params: { path: { projectId } },
				}),
			),
		queryKey: queryKeys.project(projectId),
	});

const useCreateProject = (
	options?: UseMutationOptions<
		Project,
		Error,
		{ name: string; description?: string }
	>,
): UseMutationResult<
	Project,
	Error,
	{ name: string; description?: string },
	unknown
> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: (data) =>
			handleApiResponse(apiClient.POST("/api/v1/projects", { body: data })),
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
	});
};

const useUpdateProject = (
	options?: UseMutationOptions<
		Project,
		Error,
		{ projectId: string; data: Partial<Project> }
	>,
): UseMutationResult<
	Project,
	Error,
	{ projectId: string; data: Partial<Project> },
	unknown
> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: ({ projectId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/projects/{projectId}", {
					body: data,
					params: { path: { projectId } },
				}),
			),
		onSuccess: (_res, { projectId }) => {
			void queryClient.invalidateQueries({
				queryKey: queryKeys.project(projectId),
			});
			void queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
	});
};

const useDeleteProject = (
	options?: UseMutationOptions<void, Error, string>,
): UseMutationResult<void, Error, string, unknown> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: (projectId) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/projects/{projectId}", {
					params: { path: { projectId } },
				}),
			),
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: queryKeys.projects });
		},
	});
};

// Items
const useProjectItems = (
	projectId: string,
	filters?: {
		page?: number;
		pageSize?: number;
		priority?: string;
		status?: string;
		view?: string;
	},
	options?: UseQueryOptions<PaginatedResponse<Item>>,
): UseQueryResult<PaginatedResponse<Item>, Error> =>
	useQuery({
		...options,
		enabled: Boolean(projectId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/items", {
					params: {
						path: { projectId },
						query: filters,
					},
				}),
			),
		queryKey: queryKeys.projectItems(projectId, filters),
	});

const useItem = (
	itemId: string,
	options?: UseQueryOptions<Item>,
): UseQueryResult<Item, Error> =>
	useQuery({
		...options,
		enabled: Boolean(itemId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/items/{itemId}", {
					params: { path: { itemId } },
				}),
			),
		queryKey: queryKeys.item(itemId),
	});

const useCreateItem = (
	options?: UseMutationOptions<
		Item,
		Error,
		{ projectId: string; data: Partial<Item> }
	>,
): UseMutationResult<
	Item,
	Error,
	{ projectId: string; data: Partial<Item> },
	unknown
> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: ({ projectId, data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/items", {
					body: data as Record<string, unknown>,
					params: { path: { projectId } },
				}),
			),
		onSuccess: (_res, { projectId }) => {
			void queryClient.invalidateQueries({
				queryKey: queryKeys.projectItems(projectId),
			});
		},
	});
};

const useUpdateItem = (
	options?: UseMutationOptions<
		Item,
		Error,
		{ itemId: string; data: Partial<Item> }
	>,
): UseMutationResult<
	Item,
	Error,
	{ itemId: string; data: Partial<Item> },
	unknown
> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: ({ itemId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/items/{itemId}", {
					body: data,
					params: { path: { itemId } },
				}),
			),
		onSuccess: (data) => {
			void queryClient.invalidateQueries({ queryKey: queryKeys.item(data.id) });
			void queryClient.invalidateQueries({
				queryKey: queryKeys.projectItems(data.projectId),
			});
		},
	});
};

const useDeleteItem = (
	options?: UseMutationOptions<
		void,
		Error,
		{ itemId: string; projectId: string }
	>,
): UseMutationResult<
	void,
	Error,
	{ itemId: string; projectId: string },
	unknown
> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: ({ itemId }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/items/{itemId}", {
					params: { path: { itemId } },
				}),
			),
		onSuccess: (_res, { projectId }) => {
			void queryClient.invalidateQueries({
				queryKey: queryKeys.projectItems(projectId),
			});
		},
	});
};

// Links
const useProjectLinks = (
	projectId: string,
	options?: UseQueryOptions<Link[]>,
): UseQueryResult<Link[], Error> =>
	useQuery({
		...options,
		enabled: Boolean(projectId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/links", {
					params: { path: { projectId } },
				}),
			),
		queryKey: queryKeys.projectLinks(projectId),
	});

const useCreateLink = (
	options?: UseMutationOptions<
		Link,
		Error,
		{ projectId: string; data: Partial<Link> }
	>,
): UseMutationResult<
	Link,
	Error,
	{ projectId: string; data: Partial<Link> },
	unknown
> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: ({ projectId, data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/links", {
					body: data as Record<string, unknown>,
					params: { path: { projectId } },
				}),
			),
		onSuccess: (_res, { projectId }) => {
			void queryClient.invalidateQueries({
				queryKey: queryKeys.projectLinks(projectId),
			});
		},
	});
};

const useDeleteLink = (
	options?: UseMutationOptions<
		void,
		Error,
		{ linkId: string; projectId: string }
	>,
): UseMutationResult<
	void,
	Error,
	{ linkId: string; projectId: string },
	unknown
> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: ({ linkId }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/links/{linkId}", {
					params: { path: { linkId } },
				}),
			),
		onSuccess: (_res, { projectId }) => {
			void queryClient.invalidateQueries({
				queryKey: queryKeys.projectLinks(projectId),
			});
		},
	});
};

// Mutations (for sync)
const useMutations = (
	filters?: { synced?: boolean; since?: string },
	options?: UseQueryOptions<Mutation[]>,
): UseQueryResult<Mutation[], Error> =>
	useQuery({
		...options,
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/mutations", {
					params: { query: filters },
				}),
			),
		queryKey: queryKeys.mutations(filters),
	});

const useCreateMutation = (
	options?: UseMutationOptions<Mutation, Error, Partial<Mutation>>,
): UseMutationResult<Mutation, Error, Partial<Mutation>, unknown> => {
	const queryClient = useQueryClient();
	return useMutation({
		...options,
		mutationFn: (data) =>
			handleApiResponse(
				apiClient.POST("/api/v1/mutations", {
					body: data as Record<string, unknown>,
				}),
			),
		onSuccess: () => {
			void queryClient.invalidateQueries({ queryKey: queryKeys.mutations() });
		},
	});
};

export {
	queryKeys,
	useCreateItem,
	useCreateLink,
	useCreateMutation,
	useCreateProject,
	useDeleteItem,
	useDeleteLink,
	useDeleteProject,
	useItem,
	useMutations,
	useProject,
	useProjectItems,
	useProjectLinks,
	useProjects,
	useUpdateItem,
	useUpdateProject,
};
