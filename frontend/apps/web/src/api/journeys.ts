import {
	type UseMutationOptions,
	type UseQueryOptions,
	useMutation,
	useQuery,
	useQueryClient,
} from "@tanstack/react-query";
import { apiClient, handleApiResponse } from "./client";

/**
 * Journey metadata for journey definitions
 */
export interface JourneyMetadata {
	[key: string]: string | number | boolean | object | null | undefined;
}

// Types for journey API
export interface Journey {
	id: string;
	projectId: string;
	name: string;
	description?: string;
	type: "user" | "system" | "business" | "technical";
	itemIds: string[];
	sequence: number[];
	metadata?: JourneyMetadata;
	detectedAt?: string;
	createdAt: string;
	updatedAt: string;
}

export interface JourneyStep {
	itemId: string;
	order: number;
	duration?: number;
	description?: string;
}

export interface CreateJourneyInput {
	projectId: string;
	name: string;
	description?: string;
	type: "user" | "system" | "business" | "technical";
	itemIds: string[];
	metadata?: JourneyMetadata;
}

export interface UpdateJourneyInput {
	name?: string;
	description?: string;
	type?: "user" | "system" | "business" | "technical";
	itemIds?: string[];
	metadata?: JourneyMetadata;
}

export interface DetectJourneysInput {
	projectId: string;
	minLength?: number;
	maxLength?: number;
	types?: ("user" | "system" | "business" | "technical")[];
}

// Query Keys
export const journeyQueryKeys = {
	all: ["journeys"] as const,
	lists: () => [...journeyQueryKeys.all, "list"] as const,
	list: (projectId: string, type?: string) =>
		[...journeyQueryKeys.lists(), projectId, type] as const,
	details: () => [...journeyQueryKeys.all, "detail"] as const,
	detail: (id: string) => [...journeyQueryKeys.details(), id] as const,
	steps: (journeyId: string) => ["journeys", "steps", journeyId] as const,
};

// List derived journeys for a project
export function useDerivedJourneys(
	projectId: string,
	type?: string,
	options?: UseQueryOptions<Journey[]>,
) {
	return useQuery({
		queryKey: journeyQueryKeys.list(projectId, type),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/journeys", {
					params: {
						path: { projectId },
						query: type ? { type } : {},
					},
				}),
			),
		enabled: !!projectId,
		...options,
	});
}

// Get single journey
export function useJourney(
	journeyId: string,
	options?: UseQueryOptions<Journey>,
) {
	return useQuery({
		queryKey: journeyQueryKeys.detail(journeyId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/journeys/{journeyId}", {
					params: { path: { journeyId } },
				}),
			),
		enabled: !!journeyId,
		...options,
	});
}

// Get journey steps
export function useJourneySteps(
	journeyId: string,
	options?: UseQueryOptions<JourneyStep[]>,
) {
	return useQuery({
		queryKey: journeyQueryKeys.steps(journeyId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/journeys/{journeyId}/steps", {
					params: { path: { journeyId } },
				}),
			),
		enabled: !!journeyId,
		...options,
	});
}

// Trigger journey detection
export function useDetectJourneys(
	options?: UseMutationOptions<Journey[], Error, DetectJourneysInput>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, minLength, maxLength, types }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/journeys/detect", {
					params: { path: { projectId } },
					body: { minLength, maxLength, types },
				}),
			),
		onSuccess: (_, { projectId }) => {
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.list(projectId),
			});
		},
		...options,
	});
}

// Create journey manually
export function useCreateJourney(
	options?: UseMutationOptions<Journey, Error, CreateJourneyInput>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, ...data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/journeys", {
					params: { path: { projectId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.list(data.projectId),
			});
		},
		...options,
	});
}

// Update journey
export function useUpdateJourney(
	options?: UseMutationOptions<
		Journey,
		Error,
		{ journeyId: string; data: UpdateJourneyInput }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ journeyId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/journeys/{journeyId}", {
					params: { path: { journeyId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.detail(data.id),
			});
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.list(data.projectId),
			});
		},
		...options,
	});
}

// Delete journey
export function useDeleteJourney(
	options?: UseMutationOptions<void, Error, string>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (journeyId) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/journeys/{journeyId}", {
					params: { path: { journeyId } },
				}),
			),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.lists(),
			});
		},
		...options,
	});
}

// Add item to journey
export function useAddJourneyStep(
	options?: UseMutationOptions<
		Journey,
		Error,
		{ journeyId: string; itemId: string; order?: number }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ journeyId, itemId, order }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/journeys/{journeyId}/steps", {
					params: { path: { journeyId } },
					body: { itemId, order },
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.detail(data.id),
			});
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.steps(data.id),
			});
		},
		...options,
	});
}

// Remove item from journey
export function useRemoveJourneyStep(
	options?: UseMutationOptions<
		void,
		Error,
		{ journeyId: string; stepItemId: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ journeyId, stepItemId }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/journeys/{journeyId}/steps/{itemId}", {
					params: { path: { journeyId, itemId: stepItemId } },
				}),
			),
		onSuccess: (_, { journeyId }) => {
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.detail(journeyId),
			});
			queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.steps(journeyId),
			});
		},
		...options,
	});
}
