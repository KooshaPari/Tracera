/* eslint-disable eslint/no-duplicate-imports, eslint/prefer-object-spread, eslint/sort-imports, promise/prefer-await-to-then */
import type { UseMutationOptions, UseMutationResult } from "@tanstack/react-query";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import type { ComponentLibrary, LibraryComponent } from "@tracertm/types";
import { apiClient, handleApiResponse } from "./client";
import componentLibraryQueries from "./component-library.queries";

interface CreateComponentLibraryInput {
	projectId: string;
	name: string;
	description?: string;
	version?: string;
}

interface UpdateComponentLibraryInput {
	name?: string;
	description?: string;
	version?: string;
}

interface CreateLibraryComponentInput {
	libraryId: string;
	name: string;
	description?: string;
	category: string;
	properties?: Record<string, unknown>;
	variant?: string;
}

interface UpdateLibraryComponentInput {
	name?: string;
	description?: string;
	category?: string;
	properties?: Record<string, unknown>;
	variant?: string;
}

const { componentLibraryQueryKeys } = componentLibraryQueries;
const apiDelete = apiClient["DELETE"];
const apiPost = apiClient["POST"];
const apiPut = apiClient["PUT"];

const useCreateComponentLibrary = (
	options?: UseMutationOptions<
		ComponentLibrary,
		Error,
		CreateComponentLibraryInput
	>,
): UseMutationResult<ComponentLibrary, Error, CreateComponentLibraryInput> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: CreateComponentLibraryInput) =>
				handleApiResponse(
					apiPost("/api/v1/projects/{projectId}/libraries", {
						body: {
							description: input.description,
							name: input.name,
							version: input.version,
						},
						params: { path: { projectId: input.projectId } },
					}),
				),
			onSuccess: (data: ComponentLibrary) =>
				queryClient.invalidateQueries({
					queryKey: componentLibraryQueryKeys.list(data.projectId),
				}),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const useUpdateComponentLibrary = (
	options?: UseMutationOptions<
		ComponentLibrary,
		Error,
		{ libraryId: string; data: UpdateComponentLibraryInput }
	>,
): UseMutationResult<
	ComponentLibrary,
	Error,
	{ libraryId: string; data: UpdateComponentLibraryInput }
> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: {
				libraryId: string;
				data: UpdateComponentLibraryInput;
			}) =>
				handleApiResponse(
					apiPut("/api/v1/libraries/{libraryId}", {
						body: input.data,
						params: { path: { libraryId: input.libraryId } },
					}),
				),
			onSuccess: (data: ComponentLibrary) =>
				Promise.all([
					queryClient.invalidateQueries({
						queryKey: componentLibraryQueryKeys.detail(data.id),
					}),
					queryClient.invalidateQueries({
						queryKey: componentLibraryQueryKeys.lists(),
					}),
				]),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const useDeleteComponentLibrary = (
	options?: UseMutationOptions<void, Error, string>,
): UseMutationResult<void, Error, string> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (libraryId: string) =>
				handleApiResponse(
					apiDelete("/api/v1/libraries/{libraryId}", {
						params: { path: { libraryId } },
					}),
				),
			onSuccess: () =>
				queryClient.invalidateQueries({
					queryKey: componentLibraryQueryKeys.lists(),
				}),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const useCreateLibraryComponent = (
	options?: UseMutationOptions<
		LibraryComponent,
		Error,
		CreateLibraryComponentInput
	>,
): UseMutationResult<LibraryComponent, Error, CreateLibraryComponentInput> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: CreateLibraryComponentInput) =>
				handleApiResponse(
					apiPost("/api/v1/libraries/{libraryId}/components", {
						body: {
							category: input.category,
							description: input.description,
							name: input.name,
							properties: input.properties,
							variant: input.variant,
						},
						params: { path: { libraryId: input.libraryId } },
					}),
				),
			onSuccess: (data: LibraryComponent) =>
				queryClient.invalidateQueries({
					queryKey: componentLibraryQueryKeys.components(data.libraryId),
				}),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const useUpdateLibraryComponent = (
	options?: UseMutationOptions<
		LibraryComponent,
		Error,
		{ componentId: string; data: UpdateLibraryComponentInput }
	>,
): UseMutationResult<
	LibraryComponent,
	Error,
	{ componentId: string; data: UpdateLibraryComponentInput }
> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: {
				componentId: string;
				data: UpdateLibraryComponentInput;
			}) =>
				handleApiResponse(
					apiPut("/api/v1/components/{componentId}", {
						body: input.data,
						params: { path: { componentId: input.componentId } },
					}),
				),
			onSuccess: (data: LibraryComponent) =>
				Promise.all([
					queryClient.invalidateQueries({
						queryKey: componentLibraryQueryKeys.component(data.id),
					}),
					queryClient.invalidateQueries({
						queryKey: componentLibraryQueryKeys.components(data.libraryId),
					}),
				]),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const useDeleteLibraryComponent = (
	options?: UseMutationOptions<
		void,
		Error,
		{ componentId: string; libraryId: string }
	>,
): UseMutationResult<void, Error, { componentId: string; libraryId: string }> => {
	const queryClient = useQueryClient();

	const mutationOptions = Object.assign(
		{
			mutationFn: (input: { componentId: string; libraryId: string }) =>
				handleApiResponse(
					apiDelete("/api/v1/components/{componentId}", {
						params: { path: { componentId: input.componentId } },
					}),
				),
			onSuccess: (
				unusedResult: void,
				variables: { componentId: string; libraryId: string },
			) =>
				queryClient.invalidateQueries({
					queryKey: componentLibraryQueryKeys.components(variables.libraryId),
				}),
		},
		options,
	);

	return useMutation(mutationOptions);
};

const componentLibraryMutationsLibrary = {
	useCreateComponentLibrary,
	useCreateLibraryComponent,
	useDeleteComponentLibrary,
	useDeleteLibraryComponent,
	useUpdateComponentLibrary,
	useUpdateLibraryComponent,
};

// eslint-disable-next-line import/no-default-export
export default componentLibraryMutationsLibrary;
