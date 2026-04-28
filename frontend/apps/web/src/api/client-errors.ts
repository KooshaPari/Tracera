import { apiConstants } from './client-constants';

class ApiError extends Error {
  public data?: unknown;
  public status: number;
  public statusText: string;

  public constructor(status: number, statusText: string, data?: unknown) {
    super(`API Error ${status}: ${statusText}`);
    this.data = data;
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
  }
}

const safeApiCall = async <TData>(
  apiCall: Promise<{ data?: TData; error?: unknown; response: Response }> | null | undefined,
): Promise<{ data?: TData; error?: unknown; response: Response }> => {
  if (apiCall !== null && typeof apiCall !== 'undefined') {
    return apiCall;
  }

  throw new ApiError(apiConstants.statusServerError, 'API request failed: promise is null');
};

const handleApiResponse = async <TData>(
  promise: Promise<{ data?: TData; error?: unknown; response: Response }> | null | undefined,
): Promise<TData> => {
  if (promise === null || typeof promise === 'undefined') {
    throw new ApiError(apiConstants.statusServerError, 'API request failed: promise is null');
  }

  const result = await promise;
  const { data, error, response } = result;
  let status = apiConstants.statusServerError;
  let statusText = '';
  if (response) {
    ({ status } = response);
    ({ statusText } = response);
  }

  if (typeof error !== 'undefined' && error !== null) {
    const errorText = statusText === '' ? 'Unknown error' : statusText;
    throw new ApiError(status, errorText, error);
  }

  if (typeof data !== 'undefined') {
    return data;
  }

  throw new ApiError(status, 'No data returned');
};

const clientErrors = {
  ApiError,
  handleApiResponse,
  safeApiCall,
};

export { ApiError, clientErrors, handleApiResponse, safeApiCall };
