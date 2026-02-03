/* eslint-disable promise/prefer-await-to-then */
import { apiConstants } from "./client-constants";

class ApiError extends Error {
	public data?: unknown;
	public status: number;
	public statusText: string;

	public constructor(status: number, statusText: string, data?: unknown) {
		super(`API Error ${status}: ${statusText}`);
		this.data = data;
		this.name = "ApiError";
		this.status = status;
		this.statusText = statusText;
	}
}

const safeApiCall = <TData>(
	apiCall:
		| Promise<{ data?: TData; error?: unknown; response: Response }>
		| null
		| undefined,
): Promise<{ data?: TData; error?: unknown; response: Response }> => {
	if (apiCall) {
		return apiCall;
	}

	return Promise.reject(
		new ApiError(
			apiConstants.statusServerError,
			"API request failed: promise is null",
		),
	);
};

const handleApiResponse = <TData>(
	promise:
		| Promise<{ data?: TData; error?: unknown; response: Response }>
		| null
		| undefined,
): Promise<TData> => {
	if (promise) {
		return promise.then((result) => {
			const { data, error, response } = result;
			const status = response
				? response.status
				: apiConstants.statusServerError;
			const statusText = response ? response.statusText : "";

			if (error) {
				const errorText = statusText === "" ? "Unknown error" : statusText;
				throw new ApiError(status, errorText, error);
			}

			if (data) {
				return data;
			}

			throw new ApiError(status, "No data returned");
		});
	}

	return Promise.reject(
		new ApiError(
			apiConstants.statusServerError,
			"API request failed: promise is null",
		),
	);
};

const clientErrors = {
	ApiError,
	handleApiResponse,
	safeApiCall,
};

export { ApiError, clientErrors, handleApiResponse, safeApiCall };
