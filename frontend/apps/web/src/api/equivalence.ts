import {
	useMutation,
	useQuery,
	useQueryClient,
	type UseMutationOptions,
	type UseMutationResult,
	type UseQueryOptions,
	type UseQueryResult,
} from "@tanstack/react-query";
import client from "./client";

const apiClient = client.apiClient;
const handleApiResponse = client.handleApiResponse;
const get = apiClient.GET.bind(apiClient);
const post = apiClient.POST.bind(apiClient);

// Types for equivalence API
interface EquivalenceLink {
	confidence: number;
	confirmedAt?: string;
	createdAt: string;
	id: string;
	itemId1: string;
	itemId2: string;
	similarity: number;
	status: "pending" | "confirmed" | "rejected";
}

interface DetectEquivalencesInput {
	projectId: string;
	threshold?: number;
}

interface ConfirmEquivalenceInput {
	comment?: string;
	equivalenceId: string;
}

interface RejectEquivalenceInput {
	reason?: string;
	equivalenceId: string;
}

// Query Keys
const equivalenceQueryKeys = {
	all: ["equivalences"] as const,
	detail: (id: string) => [...equivalenceQueryKeys.details(), id] as const,
	details: () => [...equivalenceQueryKeys.all, "detail"] as const,
	list: (projectId: string, status?: string) =>
		[...equivalenceQueryKeys.lists(), projectId, status] as const,
	lists: () => [...equivalenceQueryKeys.all, "list"] as const,
};

const useEquivalenceLinks = (
	projectId: string,
	status?: string,
	options?: UseQueryOptions<EquivalenceLink[]>,
): UseQueryResult<EquivalenceLink[]> => {
	const query: Record<string, string> = {};
	if (typeof status === "string" && status !== "") {
		query["status"] = status;
	}

	const baseOptions: UseQueryOptions<EquivalenceLink[]> = {
		enabled: Boolean(projectId),
		queryFn: () =>
			handleApiResponse(
				get("/api/v1/projects/{projectId}/equivalences", {
					params: {
						path: { projectId },
						query,
					},
				}),
			),
		queryKey: equivalenceQueryKeys.list(projectId, status),
	};

	return useQuery({ ...baseOptions, ...(options ?? {}) });
};

const useEquivalenceLink = (
	equivalenceId: string,
	options?: UseQueryOptions<EquivalenceLink>,
): UseQueryResult<EquivalenceLink> => {
	const baseOptions: UseQueryOptions<EquivalenceLink> = {
		enabled: Boolean(equivalenceId),
		queryFn: () =>
			handleApiResponse(
				get("/api/v1/equivalences/{equivalenceId}", {
					params: { path: { equivalenceId } },
				}),
			),
		queryKey: equivalenceQueryKeys.detail(equivalenceId),
	};

	return useQuery({ ...baseOptions, ...(options ?? {}) });
};

const useDetectEquivalences = (
	options?: UseMutationOptions<
		EquivalenceLink[],
		Error,
		DetectEquivalencesInput
	>,
): UseMutationResult<EquivalenceLink[], Error, DetectEquivalencesInput> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<
		EquivalenceLink[],
		Error,
		DetectEquivalencesInput
	> = {
		mutationFn: (input: DetectEquivalencesInput) => {
			const { projectId, threshold } = input;
			return handleApiResponse(
				post("/api/v1/projects/{projectId}/equivalences/detect", {
					body: { threshold },
					params: { path: { projectId } },
				}),
			);
		},
		onSuccess: async (data: EquivalenceLink[], variables: DetectEquivalencesInput) => {
			await queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.list(variables.projectId),
			});
			return data;
		},
	};

	return useMutation({ ...baseOptions, ...(options ?? {}) });
};

const useConfirmEquivalence = (
	options?: UseMutationOptions<EquivalenceLink, Error, ConfirmEquivalenceInput>,
): UseMutationResult<EquivalenceLink, Error, ConfirmEquivalenceInput> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<EquivalenceLink, Error, ConfirmEquivalenceInput> = {
		mutationFn: (input: ConfirmEquivalenceInput) =>
			handleApiResponse(
				post("/api/v1/equivalences/{equivalenceId}/confirm", {
					body: { comment: input.comment },
					params: { path: { equivalenceId: input.equivalenceId } },
				}),
			),
		onSuccess: async (data: EquivalenceLink) => {
			await queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.detail(data.id),
			});
			await queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
			return data;
		},
	};

	return useMutation({ ...baseOptions, ...(options ?? {}) });
};

const useRejectEquivalence = (
	options?: UseMutationOptions<void, Error, RejectEquivalenceInput>,
): UseMutationResult<void, Error, RejectEquivalenceInput> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<void, Error, RejectEquivalenceInput> = {
		mutationFn: (input: RejectEquivalenceInput) =>
			handleApiResponse(
				post("/api/v1/equivalences/{equivalenceId}/reject", {
					body: { reason: input.reason },
					params: { path: { equivalenceId: input.equivalenceId } },
				}),
			),
		onSuccess: async (_data: void, variables: RejectEquivalenceInput) => {
			await queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.detail(variables.equivalenceId),
			});
			await queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
		},
	};

	return useMutation({ ...baseOptions, ...(options ?? {}) });
};

const useBatchConfirmEquivalences = (
	options?: UseMutationOptions<EquivalenceLink[], Error, string[]>,
): UseMutationResult<EquivalenceLink[], Error, string[]> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<EquivalenceLink[], Error, string[]> = {
		mutationFn: (equivalenceIds: string[]) =>
			handleApiResponse(
				post("/api/v1/equivalences/batch-confirm", {
					body: { equivalenceIds },
				}),
			),
		onSuccess: async () => {
			await queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
		},
	};

	return useMutation({ ...baseOptions, ...(options ?? {}) });
};

const useBatchRejectEquivalences = (
	options?: UseMutationOptions<void, Error, string[]>,
): UseMutationResult<void, Error, string[]> => {
	const queryClient = useQueryClient();
	const baseOptions: UseMutationOptions<void, Error, string[]> = {
		mutationFn: (equivalenceIds: string[]) =>
			handleApiResponse(
				post("/api/v1/equivalences/batch-reject", {
					body: { equivalenceIds },
				}),
			),
		onSuccess: async () => {
			await queryClient.invalidateQueries({
				queryKey: equivalenceQueryKeys.lists(),
			});
		},
	};

	return useMutation({ ...baseOptions, ...(options ?? {}) });
};

export {
	equivalenceQueryKeys,
	useBatchConfirmEquivalences,
	useBatchRejectEquivalences,
	useConfirmEquivalence,
	useDetectEquivalences,
	useEquivalenceLink,
	useEquivalenceLinks,
	useRejectEquivalence,
	type ConfirmEquivalenceInput,
	type DetectEquivalencesInput,
	type EquivalenceLink,
	type RejectEquivalenceInput,
};
