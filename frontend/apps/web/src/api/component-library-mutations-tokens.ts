/* eslint-disable eslint/no-duplicate-imports, eslint/prefer-object-spread, eslint/sort-imports */
import type { UseMutationOptions, UseMutationResult } from "@tanstack/react-query";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { DesignToken } from "@tracertm/types";
import client from "./client";
import componentLibraryQueries from "./component-library.queries";

const { apiClient, handleApiResponse } = client;

interface CreateDesignTokenInput {
	libraryId: string;
	name: string;
	type: string;
	value: unknown;
	category: string;
	description?: string;
}

interface UpdateDesignTokenInput {
	name?: string;
	type?: string;
	value?: unknown;
	category?: string;
	description?: string;
}

const { componentLibraryQueryKeys } = componentLibraryQueries;
const apiDelete = apiClient.DELETE;
const apiPost = apiClient.POST;
const apiPut = apiClient.PUT;

const useCreateDesignToken = (
	options?: UseMutationOptions<DesignToken, Error, CreateDesignTokenInput>,
): UseMutationResult<DesignToken, Error, CreateDesignTokenInput> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: CreateDesignTokenInput) =>
				handleApiResponse(
					apiPost("/api/v1/libraries/{libraryId}/tokens", {
						body: {
							category: input.category,
							description: input.description,
							name: input.name,
							type: input.type,
							value: input.value,
						},
						params: { path: { libraryId: input.libraryId } },
					}),
				),
			onSuccess: (data: DesignToken) =>
				void queryClient.invalidateQueries({
					queryKey: componentLibraryQueryKeys.tokens(data.libraryId),
				}),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const useUpdateDesignToken = (
	options?: UseMutationOptions<
		DesignToken,
		Error,
		{ tokenId: string; data: UpdateDesignTokenInput }
	>,
): UseMutationResult<
	DesignToken,
	Error,
	{ tokenId: string; data: UpdateDesignTokenInput }
> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: { tokenId: string; data: UpdateDesignTokenInput }) =>
				handleApiResponse(
					apiPut("/api/v1/tokens/{tokenId}", {
						body: input.data,
						params: { path: { tokenId: input.tokenId } },
					}),
				),
			onSuccess: (data: DesignToken) =>
				void queryClient.invalidateQueries({
					queryKey: componentLibraryQueryKeys.tokens(data.libraryId),
				}),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const useDeleteDesignToken = (
	options?: UseMutationOptions<
		void,
		Error,
		{ tokenId: string; libraryId: string }
	>,
): UseMutationResult<void, Error, { tokenId: string; libraryId: string }> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: { tokenId: string; libraryId: string }) =>
				handleApiResponse(
					apiDelete("/api/v1/tokens/{tokenId}", {
						params: { path: { tokenId: input.tokenId } },
					}),
				),
			onSuccess: (
				_data: void,
				variables: { tokenId: string; libraryId: string },
			) =>
				void queryClient.invalidateQueries({
					queryKey: componentLibraryQueryKeys.tokens(variables.libraryId),
				}),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const componentLibraryMutationsTokens = {
	useCreateDesignToken,
	useDeleteDesignToken,
	useUpdateDesignToken,
};

// eslint-disable-next-line import/no-default-export
export default componentLibraryMutationsTokens;
