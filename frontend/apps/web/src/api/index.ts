// Export all API utilities

import client from "./client";

// Re-export commonly used types
export type {
	Agent,
	Item,
	ItemStatus,
	Link,
	LinkType,
	Mutation,
	PaginatedResponse,
	Priority,
	Project,
	ViewType,
} from "@tracertm/types";
export { createAgentSession } from "./agent";
export {
	AuthError,
	authApi,
	getAuthErrorMessage,
	isAuthError,
	loginWithToast,
	loginWithToastStore,
	shouldLogoutOnError,
	type AuthErrorDetails,
	type AuthResponse,
	type ChangePasswordRequest,
	type LoginRequest,
	type RefreshTokenRequest,
	type ResetPasswordConfirm,
	type ResetPasswordRequest,
	type UpdateUserProfileRequest,
	type User,
	type UserMetadata,
} from "./auth";

const {
	API_BASE_URL,
	ApiError,
	apiClient,
	getAuthHeaders,
	getBackendURL,
	handleApiResponse,
	safeApiCall,
	validateSession,
} = client;

export {
	API_BASE_URL,
	ApiError,
	apiClient,
	getAuthHeaders,
	getBackendURL,
	handleApiResponse,
	safeApiCall,
	validateSession,
};
export { default as componentLibraryApi } from "./component-library";
