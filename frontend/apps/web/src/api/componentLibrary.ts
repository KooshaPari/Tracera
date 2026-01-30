import {
	type UseMutationOptions,
	type UseQueryOptions,
	useMutation,
	useQuery,
	useQueryClient,
} from "@tanstack/react-query";
import { apiClient, handleApiResponse } from "./client";

/**
 * Component properties for library components
 */
export interface ComponentProperties {
	[key: string]: string | number | boolean | object | null | undefined;
}

/**
 * Design token value type
 */
export type TokenValue = string | number | boolean | object | null | undefined;

// Types for component library API
export interface ComponentLibrary {
	id: string;
	projectId: string;
	name: string;
	description?: string;
	version: string;
	itemCount: number;
	createdAt: string;
	updatedAt: string;
}

export interface LibraryComponent {
	id: string;
	libraryId: string;
	name: string;
	description?: string;
	category: string;
	properties: ComponentProperties;
	variant?: string;
	usageCount: number;
	createdAt: string;
	updatedAt: string;
}

export interface ComponentUsage {
	itemId: string;
	componentId: string;
	usageCount: number;
	lastUsedAt: string;
}

export interface DesignToken {
	id: string;
	libraryId: string;
	name: string;
	type: string;
	value: TokenValue;
	category: string;
	description?: string;
	createdAt: string;
	updatedAt: string;
}

export interface CreateComponentLibraryInput {
	projectId: string;
	name: string;
	description?: string;
	version?: string;
}

export interface UpdateComponentLibraryInput {
	name?: string;
	description?: string;
	version?: string;
}

export interface CreateLibraryComponentInput {
	libraryId: string;
	name: string;
	description?: string;
	category: string;
	properties?: ComponentProperties;
	variant?: string;
}

export interface UpdateLibraryComponentInput {
	name?: string;
	description?: string;
	category?: string;
	properties?: ComponentProperties;
	variant?: string;
}

export interface CreateDesignTokenInput {
	libraryId: string;
	name: string;
	type: string;
	value: TokenValue;
	category: string;
	description?: string;
}

export interface UpdateDesignTokenInput {
	name?: string;
	type?: string;
	value?: TokenValue;
	category?: string;
	description?: string;
}

// Query Keys
export const componentLibraryQueryKeys = {
	all: ["componentLibrary"] as const,
	lists: () => [...componentLibraryQueryKeys.all, "list"] as const,
	list: (projectId: string) =>
		[...componentLibraryQueryKeys.lists(), projectId] as const,
	details: () => [...componentLibraryQueryKeys.all, "detail"] as const,
	detail: (id: string) => [...componentLibraryQueryKeys.details(), id] as const,
	components: (libraryId: string) =>
		["componentLibrary", "components", libraryId] as const,
	component: (componentId: string) =>
		["componentLibrary", "component", componentId] as const,
	usage: (componentId: string) =>
		["componentLibrary", "usage", componentId] as const,
	tokens: (libraryId: string) =>
		["componentLibrary", "tokens", libraryId] as const,
};

// List component libraries for a project
export function useComponentLibraries(
	projectId: string,
	options?: UseQueryOptions<ComponentLibrary[]>,
) {
	return useQuery({
		queryKey: componentLibraryQueryKeys.list(projectId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/projects/{projectId}/libraries", {
					params: { path: { projectId } },
				}),
			),
		enabled: !!projectId,
		...options,
	});
}

// Get single component library
export function useComponentLibrary(
	libraryId: string,
	options?: UseQueryOptions<ComponentLibrary>,
) {
	return useQuery({
		queryKey: componentLibraryQueryKeys.detail(libraryId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/libraries/{libraryId}", {
					params: { path: { libraryId } },
				}),
			),
		enabled: !!libraryId,
		...options,
	});
}

// Create component library
export function useCreateComponentLibrary(
	options?: UseMutationOptions<
		ComponentLibrary,
		Error,
		CreateComponentLibraryInput
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ projectId, ...data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/projects/{projectId}/libraries", {
					params: { path: { projectId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.list(data.projectId),
			});
		},
		...options,
	});
}

// Update component library
export function useUpdateComponentLibrary(
	options?: UseMutationOptions<
		ComponentLibrary,
		Error,
		{ libraryId: string; data: UpdateComponentLibraryInput }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ libraryId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/libraries/{libraryId}", {
					params: { path: { libraryId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.detail(data.id),
			});
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.lists(),
			});
		},
		...options,
	});
}

// Delete component library
export function useDeleteComponentLibrary(
	options?: UseMutationOptions<void, Error, string>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: (libraryId) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/libraries/{libraryId}", {
					params: { path: { libraryId } },
				}),
			),
		onSuccess: () => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.lists(),
			});
		},
		...options,
	});
}

// List components in a library
export function useLibraryComponents(
	libraryId: string,
	options?: UseQueryOptions<LibraryComponent[]>,
) {
	return useQuery({
		queryKey: componentLibraryQueryKeys.components(libraryId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/libraries/{libraryId}/components", {
					params: { path: { libraryId } },
				}),
			),
		enabled: !!libraryId,
		...options,
	});
}

// Get single library component
export function useLibraryComponent(
	componentId: string,
	options?: UseQueryOptions<LibraryComponent>,
) {
	return useQuery({
		queryKey: componentLibraryQueryKeys.component(componentId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/components/{componentId}", {
					params: { path: { componentId } },
				}),
			),
		enabled: !!componentId,
		...options,
	});
}

// Create library component
export function useCreateLibraryComponent(
	options?: UseMutationOptions<
		LibraryComponent,
		Error,
		CreateLibraryComponentInput
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ libraryId, ...data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/libraries/{libraryId}/components", {
					params: { path: { libraryId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.components(data.libraryId),
			});
		},
		...options,
	});
}

// Update library component
export function useUpdateLibraryComponent(
	options?: UseMutationOptions<
		LibraryComponent,
		Error,
		{ componentId: string; data: UpdateLibraryComponentInput }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ componentId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/components/{componentId}", {
					params: { path: { componentId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.component(data.id),
			});
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.components(data.libraryId),
			});
		},
		...options,
	});
}

// Delete library component
export function useDeleteLibraryComponent(
	options?: UseMutationOptions<
		void,
		Error,
		{ componentId: string; libraryId: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ componentId }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/components/{componentId}", {
					params: { path: { componentId } },
				}),
			),
		onSuccess: (_, { libraryId }) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.components(libraryId),
			});
		},
		...options,
	});
}

// Get component usage statistics
export function useComponentUsage(
	componentId: string,
	options?: UseQueryOptions<ComponentUsage[]>,
) {
	return useQuery({
		queryKey: componentLibraryQueryKeys.usage(componentId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/components/{componentId}/usage", {
					params: { path: { componentId } },
				}),
			),
		enabled: !!componentId,
		...options,
	});
}

// List design tokens for a library
export function useDesignTokens(
	libraryId: string,
	options?: UseQueryOptions<DesignToken[]>,
) {
	return useQuery({
		queryKey: componentLibraryQueryKeys.tokens(libraryId),
		queryFn: () =>
			handleApiResponse(
				apiClient.GET("/api/v1/libraries/{libraryId}/tokens", {
					params: { path: { libraryId } },
				}),
			),
		enabled: !!libraryId,
		...options,
	});
}

// Create design token
export function useCreateDesignToken(
	options?: UseMutationOptions<DesignToken, Error, CreateDesignTokenInput>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ libraryId, ...data }) =>
			handleApiResponse(
				apiClient.POST("/api/v1/libraries/{libraryId}/tokens", {
					params: { path: { libraryId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.tokens(data.libraryId),
			});
		},
		...options,
	});
}

// Update design token
export function useUpdateDesignToken(
	options?: UseMutationOptions<
		DesignToken,
		Error,
		{ tokenId: string; data: UpdateDesignTokenInput }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ tokenId, data }) =>
			handleApiResponse(
				apiClient.PUT("/api/v1/tokens/{tokenId}", {
					params: { path: { tokenId } },
					body: data,
				}),
			),
		onSuccess: (data) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.tokens(data.libraryId),
			});
		},
		...options,
	});
}

// Delete design token
export function useDeleteDesignToken(
	options?: UseMutationOptions<
		void,
		Error,
		{ tokenId: string; libraryId: string }
	>,
) {
	const queryClient = useQueryClient();

	return useMutation({
		mutationFn: ({ tokenId }) =>
			handleApiResponse(
				apiClient.DELETE("/api/v1/tokens/{tokenId}", {
					params: { path: { tokenId } },
				}),
			),
		onSuccess: (_, { libraryId }) => {
			queryClient.invalidateQueries({
				queryKey: componentLibraryQueryKeys.tokens(libraryId),
			});
		},
		...options,
	});
}
