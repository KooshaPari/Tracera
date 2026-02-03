import { authApi } from "./auth-api";
import authConstants from "./auth-constants";
import { AuthError, type AuthErrorDetails, type AuthResponse, type ChangePasswordRequest, type LoginRequest, type RefreshTokenRequest, type ResetPasswordConfirm, type ResetPasswordRequest, type UpdateUserProfileRequest, type User, type UserMetadata } from "./auth-types";
import {
	getAuthErrorMessage,
	getStoredToken,
	handleAuthResponse,
	hasWindow,
	isAuthError,
	normalizeToken,
	parseErrorData,
} from "./auth-utils";
import {
	getLoginErrorMessage,
	loginWithToast,
	loginWithToastStore,
	shouldLogoutOnError,
} from "./auth-toast";

export {
	authApi,
	authConstants,
	AuthError,
	getAuthErrorMessage,
	getLoginErrorMessage,
	getStoredToken,
	handleAuthResponse,
	hasWindow,
	isAuthError,
	loginWithToast,
	loginWithToastStore,
	normalizeToken,
	parseErrorData,
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
};
