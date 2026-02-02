import clientCore from "./client-core";
import clientErrors from "./client-errors";

const client = {
	API_BASE_URL: clientCore.API_BASE_URL,
	ApiError: clientErrors.ApiError,
	apiClient: clientCore.apiClient,
	getAuthHeaders: clientCore.getAuthHeaders,
	getBackendURL: clientCore.getBackendURL,
	handleApiResponse: clientErrors.handleApiResponse,
	safeApiCall: clientErrors.safeApiCall,
	validateSession: clientCore.validateSession,
};

export default client;
