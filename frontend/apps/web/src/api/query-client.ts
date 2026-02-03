import client from "./client";

type ApiResult<TData> = Promise<{
	data?: TData;
	error?: unknown;
	response: Response;
}>;

interface ApiClient {
	del: <TData>(path: string, init: unknown) => ApiResult<TData>;
	get: <TData>(path: string, init: unknown) => ApiResult<TData>;
	post: <TData>(path: string, init: unknown) => ApiResult<TData>;
	put: <TData>(path: string, init: unknown) => ApiResult<TData>;
}

const { apiClient, handleApiResponse } = client;
const api: ApiClient = {
	del: apiClient.DELETE.bind(apiClient),
	get: apiClient.GET.bind(apiClient),
	post: apiClient.POST.bind(apiClient),
	put: apiClient.PUT.bind(apiClient),
};

export { api, handleApiResponse, type ApiClient, type ApiResult };
