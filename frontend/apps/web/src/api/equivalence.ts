import {
	type UseMutationOptions,
	type UseQueryOptions,
	useMutation,
	useQuery,
	useQueryClient,
} from "@tanstack/react-query";
import client from "./client";

const { apiClient, handleApiResponse } = client;

// Types for equivalence API
export interface EquivalenceLink {
	id: string;
	itemId1: string;
	itemId2: string;
	similarity: number;
	confidence: number;
	status: "pending" | "confirmed" | "rejected";
	createdAt: string;
	confirmedAt?: string;
}

export interface DetectEquivalencesInput {
	projectId: string;
	threshold?: number;
}

export interface ConfirmEquivalenceInput {
	equivalenceId: string;
	comment?: string;
}

export interface RejectEquivalenceInput {
	equivalenceId: string;
	reason?: string;
}

// Query Keys
export const equivalenceQueryKeys = {
	all: ["equivalences"] as const,
	lists: () => [...equivalenceQueryKeys.all, "list"] as const,
	list: (projectId: string, status?: string) =>
		[...equivalenceQueryKeys.lists(), projectId, status] as const,
	details: () => [...equivalenceQueryKeys.all, "detail"] as const,
	detail: (id: string) => [...equivalenceQueryKeys.details(), id] as const,
};

// List equivalence links for a project
export function useEquivalenceLinks(
	projectId: string,
	status?: string,
	options?: UseQueryOptions<EquivalenceLink[]>,
) {
	return useQuery({
		queryKey: equivalenceQueryKeys.list(projectId, status),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/equivalences", {
					params: {
						path: { projectId },
						query: status ? { status } : {},
					},
				}),
			),
		enabled: !!projectId,
		...options,
	});
}

// Get single equivalence link
export function useEquivalenceLink(
	equivalenceId: string,
	options?: UseQueryOptions<EquivalenceLink>,
) {
	return useQuery({
		queryKey: equivalenceQueryKeys.detail(equivalenceId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/equivalences/{equivalenceId}", {
					params: { path: { equivalenceId } },
				}),
			),
		enabled: !!equivalenceId,
		...options,
	});
}

// Trigger equivalence detection
export function useDetectEquivalences(
	options?: UseMutationOptions<
		EquivalenceLink[],
		Error,
		DetectEquivalencesInput
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, threshold }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/equivalences/detect", {
					params: { path: { projectId } },
					body: { threshold },
				}),
			),
		onSuccess: (_, { projectId }) => {
			void queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.list(projectId),
			});
		},
		...options,
	});
}

// Confirm equivalence
export function useConfirmEquivalence(
	options?: UseMutationOptions<EquivalenceLink, Error, ConfirmEquivalenceInput>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ equivalenceId, comment }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/equivalences/{equivalenceId}/confirm", {
					params: { path: { equivalenceId } },
					body: { comment },
				}),
			),
		onSuccess: (data) => {
			void queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.detail(data.id),
			});
			void queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
		},
		...options,
	});
}

// Reject equivalence
export function useRejectEquivalence(
	options?: UseMutationOptions<void, Error, RejectEquivalenceInput>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ equivalenceId, reason }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/equivalences/{equivalenceId}/reject", {
					params: { path: { equivalenceId } },
					body: { reason },
				}),
			),
		onSuccess: (_, { equivalenceId }) => {
			void queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.detail(equivalenceId),
			});
			void queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
		},
		...options,
	});
}

// Batch confirm equivalences
export function useBatchConfirmEquivalences(
	options?: UseMutationOptions<EquivalenceLink[], Error, string[]>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (equivalenceIds) =>
			handleApiResponse(
				apiClient.POST("/api/v1/equivalences/batch-confirm", {
					body: { equivalenceIds },
				}),
			),
		onSuccess: () => {
			void queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
		},
		...options,
	});
}

// Batch reject equivalences
export function useBatchRejectEquivalences(
	options?: UseMutationOptions<void, Error, string[]>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (equivalenceIds) =>
			handleApiResponse(
				apiClient.POST("/api/v1/equivalences/batch-reject", {
					body: { equivalenceIds },
				}),
			),
		onSuccess: () => {
			void queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
		},
		...options,
	});
}
