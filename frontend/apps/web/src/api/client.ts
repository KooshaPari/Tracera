/* eslint-disable import/no-default-export */
import { clientCore, type ClientCore } from "./client-core";
import { ApiError, handleApiResponse, safeApiCall } from "./client-errors";

const core: ClientCore = clientCore;

const client = {
	API_BASE_URL: core.API_BASE_URL,
	ApiError,
	apiClient: core.apiClient,
	getAuthHeaders: core.getAuthHeaders,
	getBackendURL: core.getBackendURL,
	handleApiResponse,
	safeApiCall,
	validateSession: core.validateSession,
};

export default client;
