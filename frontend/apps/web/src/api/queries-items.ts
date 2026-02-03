import type * as ReactQuery from "@tanstack/react-query";
import type * as TracerTypes from "@tracertm/types";
import * as QueryClient from "./query-client";
import * as QueryKeys from "./queries-keys";
import * as ReactQueryHooks from "./react-query-hooks";

type Item = TracerTypes.Item;
type ItemListResponse = TracerTypes.PaginatedResponse<Item>;

type ItemFilters = {
	page?: number;
	pageSize?: number;
	priority?: string;
	status?: string;
	view?: string;
};

type CreateItemInput = {
	data: Partial<Item>;
	projectId: string;
};

type UpdateItemInput = {
	data: Partial<Item>;
	itemId: string;
};

type DeleteItemInput = {
	itemId: string;
	projectId: string;
};

const useProjectItems = (
	projectId: string,
	filters?: ItemFilters,
	options?: ReactQuery.UseQueryOptions<ItemListResponse>,
): ReactQuery.UseQueryResult<ItemListResponse> => {
	const baseOptions: ReactQuery.UseQueryOptions<ItemListResponse> = {
		enabled: Boolean(projectId),
		queryFn: async (): Promise<ItemListResponse> =>
			await QueryClient.handleApiResponse(
				QueryClient.api.get<ItemListResponse>(
					"/api/v1/projects/{projectId}/items",
					{
						params: {
							path: { projectId },
							query: filters,
						},
					},
				),
			),
		queryKey: QueryKeys.queryKeys.projectItems(projectId, filters),
	};

	if (options) {
		return ReactQueryHooks.useQuery(Object.assign(baseOptions, options));
	}

	return ReactQueryHooks.useQuery(baseOptions);
};

const useItem = (
	itemId: string,
	options?: ReactQuery.UseQueryOptions<Item>,
): ReactQuery.UseQueryResult<Item> => {
	const baseOptions: ReactQuery.UseQueryOptions<Item> = {
		enabled: Boolean(itemId),
		queryFn: async (): Promise<Item> =>
			await QueryClient.handleApiResponse(
				QueryClient.api.get<Item>("/api/v1/items/{itemId}", {
					params: { path: { itemId } },
				}),
			),
		queryKey: QueryKeys.queryKeys.item(itemId),
	};

	if (options) {
		return ReactQueryHooks.useQuery(Object.assign(baseOptions, options));
	}

	return ReactQueryHooks.useQuery(baseOptions);
};

const useCreateItem = (
	options?: ReactQuery.UseMutationOptions<Item, Error, CreateItemInput>,
): ReactQuery.UseMutationResult<Item, Error, CreateItemInput> => {
	const queryClient = ReactQueryHooks.useQueryClient();
	const baseOptions: ReactQuery.UseMutationOptions<Item, Error, CreateItemInput> =
		{
			mutationFn: async (input: CreateItemInput): Promise<Item> =>
				await QueryClient.handleApiResponse(
					QueryClient.api.post<Item>(
						"/api/v1/projects/{projectId}/items",
						{
							body: input.data as Record<string, unknown>,
							params: { path: { projectId: input.projectId } },
						},
					),
				),
			onSuccess: async (
				_data: Item,
				variables: CreateItemInput,
			): Promise<void> => {
				await queryClient.invalidateQueries({
					queryKey: QueryKeys.queryKeys.projectItems(variables.projectId),
				});
			},
		};

	let mergedOptions = baseOptions;
	if (options) {
		mergedOptions = Object.assign(baseOptions, options);
	}

	return ReactQueryHooks.useMutation<Item, Error, CreateItemInput>(
		mergedOptions,
	);
};

const useUpdateItem = (
	options?: ReactQuery.UseMutationOptions<Item, Error, UpdateItemInput>,
): ReactQuery.UseMutationResult<Item, Error, UpdateItemInput> => {
	const queryClient = ReactQueryHooks.useQueryClient();
	const baseOptions: ReactQuery.UseMutationOptions<Item, Error, UpdateItemInput> =
		{
			mutationFn: async (input: UpdateItemInput): Promise<Item> =>
				await QueryClient.handleApiResponse(
					QueryClient.api.put<Item>("/api/v1/items/{itemId}", {
						body: input.data,
						params: { path: { itemId: input.itemId } },
					}),
				),
			onSuccess: async (data: Item): Promise<void> => {
				await queryClient.invalidateQueries({
					queryKey: QueryKeys.queryKeys.item(data.id),
				});
				await queryClient.invalidateQueries({
					queryKey: QueryKeys.queryKeys.projectItems(data.projectId),
				});
			},
		};

	let mergedOptions = baseOptions;
	if (options) {
		mergedOptions = Object.assign(baseOptions, options);
	}

	return ReactQueryHooks.useMutation<Item, Error, UpdateItemInput>(
		mergedOptions,
	);
};

const useDeleteItem = (
	options?: ReactQuery.UseMutationOptions<void, Error, DeleteItemInput>,
): ReactQuery.UseMutationResult<void, Error, DeleteItemInput> => {
	const queryClient = ReactQueryHooks.useQueryClient();
	const baseOptions: ReactQuery.UseMutationOptions<void, Error, DeleteItemInput> =
		{
			mutationFn: async (input: DeleteItemInput): Promise<void> =>
				await QueryClient.handleApiResponse(
					QueryClient.api.del<void>("/api/v1/items/{itemId}", {
						params: { path: { itemId: input.itemId } },
					}),
				),
			onSuccess: async (
				_data: void,
				variables: DeleteItemInput,
			): Promise<void> => {
				await queryClient.invalidateQueries({
					queryKey: QueryKeys.queryKeys.projectItems(variables.projectId),
				});
			},
		};

	let mergedOptions = baseOptions;
	if (options) {
		mergedOptions = Object.assign(baseOptions, options);
	}

	return ReactQueryHooks.useMutation<void, Error, DeleteItemInput>(
		mergedOptions,
	);
};

export {
	useCreateItem,
	useDeleteItem,
	useItem,
	useProjectItems,
	useUpdateItem,
};
