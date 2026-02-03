/* eslint-disable import/no-default-export */
import { clientCore } from "./client-core";
import { ApiError, handleApiResponse, safeApiCall } from "./client-errors";

const client = {
	API_BASE_URL: clientCore.API_BASE_URL,
	ApiError,
	apiClient: clientCore.apiClient,
	getAuthHeaders: clientCore.getAuthHeaders,
	getBackendURL: clientCore.getBackendURL,
	handleApiResponse,
	safeApiCall,
	validateSession: clientCore.validateSession,
};

export default client;
