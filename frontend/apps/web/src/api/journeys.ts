import {
	type UseMutationOptions,
	type UseQueryOptions,
	useMutation,
	useQuery,
	useQueryClient,
} from "@tanstack/react-query";
import client from "./client";

const { apiClient, handleApiResponse } = client;

/**
 * Journey metadata for journey definitions
 */
export type JourneyMetadata = Record<
	string,
	string | number | boolean | object | null | undefined
>;

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
	const baseOptions = {
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
		enabled: Boolean(projectId),
	};

	return useQuery(Object.assign(baseOptions, options || {}));
}

// Get single journey
export function useJourney(
	journeyId: string,
	options?: UseQueryOptions<Journey>,
) {
	const baseOptions = {
		queryKey: journeyQueryKeys.detail(journeyId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/journeys/{journeyId}", {
					params: { path: { journeyId } },
				}),
			),
		enabled: Boolean(journeyId),
	};

	return useQuery(Object.assign(baseOptions, options || {}));
}

// Get journey steps
export function useJourneySteps(
	journeyId: string,
	options?: UseQueryOptions<JourneyStep[]>,
) {
	const baseOptions = {
		queryKey: journeyQueryKeys.steps(journeyId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/journeys/{journeyId}/steps", {
					params: { path: { journeyId } },
				}),
			),
		enabled: Boolean(journeyId),
	};

	return useQuery(Object.assign(baseOptions, options || {}));
}

// Trigger journey detection
export function useDetectJourneys(
	options?: UseMutationOptions<Journey[], Error, DetectJourneysInput>,
) {
	const queryClient = useQueryClient();
	const baseOptions = {
		mutationFn: (input: DetectJourneysInput) => {
			const { projectId, minLength, maxLength, types } = input;
			return handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/journeys/detect", {
					params: { path: { projectId } },
					body: { minLength, maxLength, types },
				}),
			);
		},
		onSuccess: async (
			unusedResult: Journey[],
			variables: DetectJourneysInput,
		) => {
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.list(variables.projectId),
			});
		},
	};

	return useMutation(Object.assign(baseOptions, options || {}));
}

// Create journey manually
export function useCreateJourney(
	options?: UseMutationOptions<Journey, Error, CreateJourneyInput>,
) {
	const queryClient = useQueryClient();
	const baseOptions = {
		mutationFn: (input: CreateJourneyInput) => {
			const { projectId, name, description, type, itemIds, metadata } = input;
			return handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/journeys", {
					params: { path: { projectId } },
					body: { name, description, type, itemIds, metadata },
				}),
			);
		},
		onSuccess: async (data: Journey) => {
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.list(data.projectId),
			});
		},
	};

	return useMutation(Object.assign(baseOptions, options || {}));
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
	const baseOptions = {
		mutationFn: (input: { journeyId: string; data: UpdateJourneyInput }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/journeys/{journeyId}", {
					params: { path: { journeyId: input.journeyId } },
					body: input.data,
				}),
			),
		onSuccess: async (data: Journey) => {
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.detail(data.id),
			});
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.list(data.projectId),
			});
		},
	};

	return useMutation(Object.assign(baseOptions, options || {}));
}

// Delete journey
export function useDeleteJourney(
	options?: UseMutationOptions<void, Error, string>,
) {
	const queryClient = useQueryClient();
	const baseOptions = {
		mutationFn: (journeyId: string) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/journeys/{journeyId}", {
					params: { path: { journeyId } },
				}),
			),
		onSuccess: async () => {
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.lists(),
			});
		},
	};

	return useMutation(Object.assign(baseOptions, options || {}));
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
	const baseOptions = {
		mutationFn: (input: {
			journeyId: string;
			itemId: string;
			order?: number;
		}) =>
			handleApiResponse(
				apiClient.POST("/api/v1/journeys/{journeyId}/steps", {
					params: { path: { journeyId: input.journeyId } },
					body: { itemId: input.itemId, order: input.order },
				}),
			),
		onSuccess: async (data: Journey) => {
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.detail(data.id),
			});
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.steps(data.id),
			});
		},
	};

	return useMutation(Object.assign(baseOptions, options || {}));
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
	const baseOptions = {
		mutationFn: (input: { journeyId: string; stepItemId: string }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/journeys/{journeyId}/steps/{itemId}", {
					params: {
						path: { journeyId: input.journeyId, itemId: input.stepItemId },
					},
				}),
			),
		onSuccess: async (
			unusedResult: void,
			variables: { journeyId: string; stepItemId: string },
		) => {
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.detail(variables.journeyId),
			});
			await queryClient.invalidateQueries({
				queryKey: journeyQueryKeys.steps(variables.journeyId),
			});
		},
	};

	return useMutation(Object.assign(baseOptions, options || {}));
}
