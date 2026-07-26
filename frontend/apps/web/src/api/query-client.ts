import { client } from './client';

type ApiResult<TData> = Promise<{
  data?: TData;
  error?: unknown;
  response: Response;
}>;

type ApiMethod = <TData>(path: string, init: Record<string, unknown>) => ApiResult<TData>;

interface ApiClient {
  del: ApiMethod;
  get: ApiMethod;
  post: ApiMethod;
  put: ApiMethod;
}

const { apiClient, handleApiResponse } = client;
const api: ApiClient = {
  del: apiClient.DELETE as unknown as ApiMethod,
  get: apiClient.GET as unknown as ApiMethod,
  post: apiClient.POST as unknown as ApiMethod,
  put: apiClient.PUT as unknown as ApiMethod,
};

export { api, handleApiResponse, type ApiClient, type ApiResult };
