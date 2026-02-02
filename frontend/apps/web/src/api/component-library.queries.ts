/* eslint-disable eslint/no-duplicate-imports, eslint/prefer-object-spread, eslint/sort-imports */
import type { UseQueryOptions, UseQueryResult } from "@tanstack/react-query";
import { useQuery } from "@tanstack/react-query";
import type {
	ComponentLibrary,
	ComponentUsage,
	DesignToken,
	LibraryComponent,
} from "@tracertm/types";
import { apiClient, handleApiResponse } from "./client";

const apiGet = apiClient["GET"];

const componentLibraryQueryKeys = {
	all: ["componentLibrary"] as const,
	component: (componentId: string) =>
		["componentLibrary", "component", componentId] as const,
	components: (libraryId: string) =>
		["componentLibrary", "components", libraryId] as const,
	detail: (id: string) =>
		[...componentLibraryQueryKeys.details(), id] as const,
	details: () => [...componentLibraryQueryKeys.all, "detail"] as const,
	list: (projectId: string) =>
		[...componentLibraryQueryKeys.lists(), projectId] as const,
	lists: () => [...componentLibraryQueryKeys.all, "list"] as const,
	tokens: (libraryId: string) =>
		["componentLibrary", "tokens", libraryId] as const,
	usage: (componentId: string) =>
		["componentLibrary", "usage", componentId] as const,
};

const useComponentLibraries = (
	projectId: string,
	options?: UseQueryOptions<ComponentLibrary[]>,
): UseQueryResult<ComponentLibrary[]> => {
	const queryOptions = Object.assign(
		{
			enabled: Boolean(projectId),
			queryFn: () =>
				handleApiResponse(
					apiGet("/api/v1/projects/{projectId}/libraries", {
						params: { path: { projectId } },
					}),
				),
			queryKey: componentLibraryQueryKeys.list(projectId),
		},
		options,
	);

	return useQuery(queryOptions);
};

const useComponentLibrary = (
	libraryId: string,
	options?: UseQueryOptions<ComponentLibrary>,
): UseQueryResult<ComponentLibrary> => {
	const queryOptions = Object.assign(
		{
			enabled: Boolean(libraryId),
			queryFn: () =>
				handleApiResponse(
					apiGet("/api/v1/libraries/{libraryId}", {
						params: { path: { libraryId } },
					}),
				),
			queryKey: componentLibraryQueryKeys.detail(libraryId),
		},
		options,
	);

	return useQuery(queryOptions);
};

const useLibraryComponents = (
	libraryId: string,
	options?: UseQueryOptions<LibraryComponent[]>,
): UseQueryResult<LibraryComponent[]> => {
	const queryOptions = Object.assign(
		{
			enabled: Boolean(libraryId),
			queryFn: () =>
				handleApiResponse(
					apiGet("/api/v1/libraries/{libraryId}/components", {
						params: { path: { libraryId } },
					}),
				),
			queryKey: componentLibraryQueryKeys.components(libraryId),
		},
		options,
	);

	return useQuery(queryOptions);
};

const useLibraryComponent = (
	componentId: string,
	options?: UseQueryOptions<LibraryComponent>,
): UseQueryResult<LibraryComponent> => {
	const queryOptions = Object.assign(
		{
			enabled: Boolean(componentId),
			queryFn: () =>
				handleApiResponse(
					apiGet("/api/v1/components/{componentId}", {
						params: { path: { componentId } },
					}),
				),
			queryKey: componentLibraryQueryKeys.component(componentId),
		},
		options,
	);

	return useQuery(queryOptions);
};

const useComponentUsage = (
	componentId: string,
	options?: UseQueryOptions<ComponentUsage[]>,
): UseQueryResult<ComponentUsage[]> => {
	const queryOptions = Object.assign(
		{
			enabled: Boolean(componentId),
			queryFn: () =>
				handleApiResponse(
					apiGet("/api/v1/components/{componentId}/usage", {
						params: { path: { componentId } },
					}),
				),
			queryKey: componentLibraryQueryKeys.usage(componentId),
		},
		options,
	);

	return useQuery(queryOptions);
};

const useDesignTokens = (
	libraryId: string,
	options?: UseQueryOptions<DesignToken[]>,
): UseQueryResult<DesignToken[]> => {
	const queryOptions = Object.assign(
		{
			enabled: Boolean(libraryId),
			queryFn: () =>
				handleApiResponse(
					apiGet("/api/v1/libraries/{libraryId}/tokens", {
						params: { path: { libraryId } },
					}),
				),
			queryKey: componentLibraryQueryKeys.tokens(libraryId),
		},
		options,
	);

	return useQuery(queryOptions);
};

const componentLibraryQueries = {
	componentLibraryQueryKeys,
	useComponentLibraries,
	useComponentLibrary,
	useComponentUsage,
	useDesignTokens,
	useLibraryComponent,
	useLibraryComponents,
};

// eslint-disable-next-line import/no-default-export
export default componentLibraryQueries;
