import {
	type UseMutationOptions,
	type UseQueryOptions,
	useMutation,
	useQuery,
	useQueryClient,
} from "@tanstack/react-query";
import { apiClient, handleApiResponse } from "./client";

/**
 * Properties for canonical concept definitions
 */
export interface ConceptProperties {
	[key: string]: string | number | boolean | object | null | undefined;
}

/**
 * Mapped properties for projections between items and concepts
 */
export interface ProjectionProperties {
	[key: string]: string | number | boolean | object | null | undefined;
}

// Types for canonical concept API
export interface CanonicalConcept {
	id: string;
	projectId: string;
	name: string;
	description?: string;
	category?: string;
	properties: ConceptProperties;
	itemCount: number;
	createdAt: string;
	updatedAt: string;
}

export interface CanonicalProjection {
	id: string;
	conceptId: string;
	itemId: string;
	confidence: number;
	mappedProperties: ProjectionProperties;
	createdAt: string;
}

export interface PivotTarget {
	itemId: string;
	conceptId: string;
	confidence: number;
	distance: number;
}

export interface CreateCanonicalConceptInput {
	projectId: string;
	name: string;
	description?: string;
	category?: string;
	properties?: ConceptProperties;
}

export interface UpdateCanonicalConceptInput {
	name?: string;
	description?: string;
	category?: string;
	properties?: ConceptProperties;
}

// Query Keys
export const canonicalQueryKeys = {
	all: ["canonical"] as const,
	lists: () => [...canonicalQueryKeys.all, "list"] as const,
	list: (projectId: string) =>
		[...canonicalQueryKeys.lists(), projectId] as const,
	details: () => [...canonicalQueryKeys.all, "detail"] as const,
	detail: (id: string) => [...canonicalQueryKeys.details(), id] as const,
	projections: (conceptId: string) =>
		["canonical", "projections", conceptId] as const,
	pivots: (itemId: string) => ["canonical", "pivots", itemId] as const,
};

// List canonical concepts for a project
export function useCanonicalConcepts(
	projectId: string,
	options?: UseQueryOptions<CanonicalConcept[]>,
) {
	return useQuery({
		queryKey: canonicalQueryKeys.list(projectId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/concepts", {
					params: { path: { projectId } },
				}),
			),
		enabled: !!projectId,
		...options,
	});
}

// Get single canonical concept
export function useCanonicalConcept(
	conceptId: string,
	options?: UseQueryOptions<CanonicalConcept>,
) {
	return useQuery({
		queryKey: canonicalQueryKeys.detail(conceptId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/concepts/{conceptId}", {
					params: { path: { conceptId } },
				}),
			),
		enabled: !!conceptId,
		...options,
	});
}

// Create canonical concept
export function useCreateCanonicalConcept(
	options?: UseMutationOptions<
		CanonicalConcept,
		Error,
		CreateCanonicalConceptInput
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, ...data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/concepts", {
					params: { path: { projectId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: canonicalQueryKeys.list(data.projectId),
			});
		},
		...options,
	});
}

// Update canonical concept
export function useUpdateCanonicalConcept(
	options?: UseMutationOptions<
		CanonicalConcept,
		Error,
		{ conceptId: string; data: UpdateCanonicalConceptInput }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ conceptId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/concepts/{conceptId}", {
					params: { path: { conceptId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: canonicalQueryKeys.detail(data.id),
			});
			queryClient.invalidateQueries({
				queryKey: canonicalQueryKeys.lists(),
			});
		},
		...options,
	});
}

// Delete canonical concept
export function useDeleteCanonicalConcept(
	options?: UseMutationOptions<void, Error, string>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (conceptId) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/concepts/{conceptId}", {
					params: { path: { conceptId } },
				}),
			),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: canonicalQueryKeys.lists(),
			});
		},
		...options,
	});
}

// Get projections for a canonical concept
export function useCanonicalProjections(
	conceptId: string,
	options?: UseQueryOptions<CanonicalProjection[]>,
) {
	return useQuery({
		queryKey: canonicalQueryKeys.projections(conceptId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/concepts/{conceptId}/projections", {
					params: { path: { conceptId } },
				}),
			),
		enabled: !!conceptId,
		...options,
	});
}

// Create projection for canonical concept
export function useCreateCanonicalProjection(
	options?: UseMutationOptions<
		CanonicalProjection,
		Error,
		{ conceptId: string; itemId: string; confidence?: number }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ conceptId, itemId, confidence }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/concepts/{conceptId}/projections", {
					params: { path: { conceptId } },
					body: { itemId, confidence },
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: canonicalQueryKeys.projections(data.conceptId),
			});
		},
		...options,
	});
}

// Delete projection
export function useDeleteCanonicalProjection(
	options?: UseMutationOptions<
		void,
		Error,
		{ conceptId: string; projectionId: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ conceptId, projectionId }) =>
			handleApiResponse(
				apiClient.DELETE(
					"/api/v1/concepts/{conceptId}/projections/{projectionId}",
					{
						params: { path: { conceptId, projectionId } },
					},
				),
			),
		onSuccess: (_, { conceptId }) => {
			queryClient.invalidateQueries({
				queryKey: canonicalQueryKeys.projections(conceptId),
			});
		},
		...options,
	});
}

// Get pivot targets for an item
export function usePivotTargets(
	itemId: string,
	options?: UseQueryOptions<PivotTarget[]>,
) {
	return useQuery({
		queryKey: canonicalQueryKeys.pivots(itemId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/items/{itemId}/pivot-targets", {
					params: { path: { itemId } },
				}),
			),
		enabled: !!itemId,
		...options,
	});
}

// Pivot item to canonical concept
export function usePivotItem(
	options?: UseMutationOptions<
		void,
		Error,
		{ itemId: string; conceptId: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ itemId, conceptId }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/items/{itemId}/pivot", {
					params: { path: { itemId } },
					body: { conceptId },
				}),
			),
		onSuccess: (_, { itemId }) => {
			queryClient.invalidateQueries({
				queryKey: canonicalQueryKeys.pivots(itemId),
			});
		},
		...options,
	});
}
