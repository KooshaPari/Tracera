/**
 * Authentication API Client
 *
 * Handles all authentication-related API calls including login, logout, refresh,
 * and user profile management. Integrates with CSRF protection and cookie-based
 * authentication.
 *
 * Features:
 * - Type-safe requests and responses
 * - Automatic CSRF token injection
 * - Cookie-based credential handling
 * - Comprehensive error handling
 * - Token refresh logic
 */

import { fetchCSRFToken, getCSRFToken } from "../lib/csrf";
import { useAuthStore } from "../stores/authStore";
import { ApiError, apiClient, handleApiResponse, safeApiCall } from "./client";
import type { ErrorDetails } from "./types";

// ============================================================================
// TYPES
// ============================================================================

/**
 * User metadata that can contain arbitrary attributes
 */
export interface UserMetadata {
	[key: string]: string | number | boolean | object | null | undefined;
}

/**
 * User authentication representation
 */
export interface User {
	id: string;
	email: string;
	name?: string;
	avatar?: string;
	role?: string;
	metadata?: UserMetadata;
}

/**
 * Login request credentials
 */
export interface LoginRequest {
	email: string;
	password: string;
}

/**
 * Authentication response with user and token
 */
export interface AuthResponse {
	user: User;
	token: string;
	expiresIn?: number;
	refreshToken?: string;
}

/**
 * Refresh token request
 */
export interface RefreshTokenRequest {
	refreshToken: string;
}

/**
 * Password change request
 */
export interface ChangePasswordRequest {
	currentPassword: string;
	newPassword: string;
	confirmPassword: string;
}

/**
 * Password reset request
 */
export interface ResetPasswordRequest {
	email: string;
}

/**
 * Password reset confirmation
 */
export interface ResetPasswordConfirm {
	token: string;
	newPassword: string;
	confirmPassword: string;
}

/**
 * User profile update request
 */
export interface UpdateUserProfileRequest {
	name?: string;
	avatar?: string;
	metadata?: UserMetadata;
}

/**
 * Authentication error details structure
 */
export interface AuthErrorDetails {
	[key: string]: string | number | boolean | object | null | undefined;
}

/**
 * Authentication error with detailed information
 */
export class AuthError extends Error {
	constructor(
		message: string,
		public statusCode: number,
		public code?: string,
		public details?: AuthErrorDetails,
	) {
		super(message);
		this.name = "AuthError";
		Object.setPrototypeOf(this, AuthError.prototype);
	}
}

/**
 * Validates that CSRF token is available before making auth requests
 * Fetches token if needed
 */
async function ensureCSRFToken(): Promise<string> {
	let token = getCSRFToken();
	if (!token) {
		try {
			token = await fetchCSRFToken();
		} catch (error) {
			throw new AuthError(
				"Failed to fetch CSRF token",
				403,
				"CSRF_TOKEN_MISSING",
				{
					originalError: error instanceof Error ? error.message : String(error),
				},
			);
		}
	}
	if (!token) {
		throw new AuthError("CSRF token not available", 403, "CSRF_TOKEN_MISSING");
	}
	return token;
}

/**
 * Helper to handle auth API responses and convert errors
 */
async function handleAuthResponse<T>(
	promise:
		| Promise<{ data?: T; error?: unknown; response: Response }>
		| null
		| undefined,
): Promise<T> {
	try {
		return await handleApiResponse(promise);
	} catch (error) {
		if (error instanceof ApiError) {
			// Convert ApiError to AuthError
			const data = error.data as ErrorDetails | undefined;
			throw new AuthError(
				(data?.['message'] as string) || error.message,
				error.status,
				data?.['code'] as string | undefined,
				data?.['details'] as AuthErrorDetails | undefined,
			);
		}
		throw error;
	}
}

// ============================================================================
// AUTHENTICATION API
// ============================================================================

/**
 * Authentication API client
 *
 * All endpoints:
 * - Use credentials: 'include' for cookie-based auth
 * - Include CSRF tokens for state-changing requests (POST, PUT, DELETE)
 * - Return typed responses with proper error handling
 * - Automatically manage authentication state
 */
export const authApi = {
	/**
	 * Authenticate user with email and password
	 *
	 * POST /api/v1/auth/login
	 *
	 * @param credentials User email and password
	 * @returns Authentication response with user and token
	 * @throws AuthError on invalid credentials or server error
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   const { user, token } = await authApi.login({
	 *     email: 'user@example.com',
	 *     password: 'password123'
	 *   });
	 *   // Store token, update auth state
	 * } catch (error) {
	 *   if (error instanceof AuthError && error.statusCode === 401) {
	 *     // Invalid credentials
	 *   }
	 * }
	 * ```
	 */
	login: async (credentials: LoginRequest): Promise<AuthResponse> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		return handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/login", {
					body: credentials,
				}),
			),
		);
	},

	/**
	 * Refresh authentication token
	 *
	 * POST /api/v1/auth/refresh
	 *
	 * Obtains a new access token using the refresh token or existing session.
	 * Automatically called when token is near expiration.
	 *
	 * @returns New authentication response with fresh token
	 * @throws AuthError if session is invalid or expired
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   const { user, token } = await authApi.refresh();
	 *   // Update stored token
	 * } catch (error) {
	 *   if (error instanceof AuthError && error.statusCode === 401) {
	 *     // Session expired, need to login again
	 *   }
	 * }
	 * ```
	 */
	refresh: async (): Promise<AuthResponse> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		return handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/refresh", {
					body: {},
				}),
			),
		);
	},

	/**
	 * Logout current user
	 *
	 * POST /api/v1/auth/logout
	 *
	 * Invalidates the current session and clears authentication cookies.
	 * Should be called before removing local token storage.
	 *
	 * @throws AuthError on server error (non-fatal, token should still be cleared locally)
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   await authApi.logout();
	 * } finally {
	 *   // Clear local auth state regardless of server response
	 *   localStorage.removeItem('auth_token');
	 *   authStore.logout();
	 * }
	 * ```
	 */
	logout: async (): Promise<void> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		await handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/logout", {
					body: {},
				}),
			),
		);
	},

	/**
	 * Get current authenticated user
	 *
	 * GET /api/v1/auth/me
	 *
	 * Retrieves the profile of the currently authenticated user.
	 * Can be used to validate token and restore session on app startup.
	 *
	 * @returns Current user profile, or null if not authenticated
	 * @throws AuthError on server error (not thrown for 401, returns null instead)
	 *
	 * @example
	 * ```typescript
	 * const user = await authApi.getCurrentUser();
	 * if (user) {
	 *   authStore.setUser(user);
	 * } else {
	 *   // Not authenticated
	 *   authStore.logout();
	 * }
	 * ```
	 */
	getCurrentUser: async (): Promise<User | null> => {
		const token =
			typeof globalThis.window !== "undefined"
				? (globalThis.window.localStorage?.getItem("auth_token") ??
						useAuthStore.getState().token)?.trim()
				: useAuthStore.getState().token?.trim();
		if (!token) {
			return null;
		}
		try {
			return await handleAuthResponse(
				safeApiCall(
					apiClient.GET("/api/v1/auth/me", {
						params: { query: {} },
					}),
				),
			);
		} catch (error) {
			if (error instanceof AuthError && error.statusCode === 401) {
				// Not authenticated
				return null;
			}
			throw error;
		}
	},

	/**
	 * Update user profile
	 *
	 * PUT /api/v1/auth/profile
	 *
	 * Updates the current user's profile information including name, avatar, and metadata.
	 *
	 * @param updates Profile fields to update
	 * @returns Updated user profile
	 * @throws AuthError on validation error or server error
	 *
	 * @example
	 * ```typescript
	 * const updatedUser = await authApi.updateProfile({
	 *   name: 'John Doe',
	 *   avatar: 'https://example.com/avatar.jpg'
	 * });
	 * authStore.setUser(updatedUser);
	 * ```
	 */
	updateProfile: async (updates: UpdateUserProfileRequest): Promise<User> => {
		// Ensure CSRF token is available for PUT request
		await ensureCSRFToken();

		return handleAuthResponse(
			safeApiCall(
				apiClient.PUT("/api/v1/auth/profile", {
					body: updates,
				}),
			),
		);
	},

	/**
	 * Change user password
	 *
	 * POST /api/v1/auth/change-password
	 *
	 * Changes the password for the currently authenticated user.
	 * Requires the current password for verification.
	 *
	 * @param request Current and new password
	 * @throws AuthError if current password is invalid or new password doesn't meet requirements
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   await authApi.changePassword({
	 *     currentPassword: 'oldPassword123',
	 *     newPassword: 'newPassword123',
	 *     confirmPassword: 'newPassword123'
	 *   });
	 *   // Show success message
	 * } catch (error) {
	 *   if (error instanceof AuthError && error.code === 'INVALID_PASSWORD') {
	 *     // Current password incorrect
	 *   }
	 * }
	 * ```
	 */
	changePassword: async (request: ChangePasswordRequest): Promise<void> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		await handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/change-password", {
					body: request,
				}),
			),
		);
	},

	/**
	 * Request password reset
	 *
	 * POST /api/v1/auth/reset-password
	 *
	 * Sends a password reset link to the user's email address.
	 * The email contains a token valid for 24 hours.
	 *
	 * @param request User email address
	 * @throws AuthError on server error
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   await authApi.requestPasswordReset({
	 *     email: 'user@example.com'
	 *   });
	 *   // Show message: "Check your email for reset link"
	 * } catch (error) {
	 *   // Show error message
	 * }
	 * ```
	 */
	requestPasswordReset: async (
		request: ResetPasswordRequest,
	): Promise<void> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		await handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/reset-password", {
					body: request,
				}),
			),
		);
	},

	/**
	 * Confirm password reset with token
	 *
	 * POST /api/v1/auth/reset-password/confirm
	 *
	 * Completes the password reset process using the token from the reset email.
	 *
	 * @param request Reset token and new password
	 * @throws AuthError if token is invalid or expired
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   await authApi.confirmPasswordReset({
	 *     token: 'reset_token_from_email',
	 *     newPassword: 'newPassword123',
	 *     confirmPassword: 'newPassword123'
	 *   });
	 *   // Redirect to login
	 * } catch (error) {
	 *   if (error instanceof AuthError && error.code === 'INVALID_TOKEN') {
	 *     // Token expired or invalid
	 *   }
	 * }
	 * ```
	 */
	confirmPasswordReset: async (
		request: ResetPasswordConfirm,
	): Promise<void> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		await handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/reset-password/confirm", {
					body: request,
				}),
			),
		);
	},

	/**
	 * Verify email address
	 *
	 * POST /api/v1/auth/verify-email
	 *
	 * Confirms email verification using a token sent to the user's email.
	 *
	 * @param token Email verification token
	 * @throws AuthError if token is invalid or expired
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   await authApi.verifyEmail('verification_token');
	 *   // Update user status
	 * } catch (error) {
	 *   if (error instanceof AuthError && error.code === 'INVALID_TOKEN') {
	 *     // Token expired, request new one
	 *   }
	 * }
	 * ```
	 */
	verifyEmail: async (token: string): Promise<void> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		await handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/verify-email", {
					body: { token },
				}),
			),
		);
	},

	/**
	 * Request email verification
	 *
	 * POST /api/v1/auth/request-verification
	 *
	 * Sends a new email verification link to the user's email address.
	 *
	 * @throws AuthError on server error
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   await authApi.requestEmailVerification();
	 *   // Show message: "Verification email sent"
	 * } catch (error) {
	 *   // Show error message
	 * }
	 * ```
	 */
	requestEmailVerification: async (): Promise<void> => {
		// Ensure CSRF token is available for POST request
		await ensureCSRFToken();

		await handleAuthResponse(
			safeApiCall(
				apiClient.POST("/api/v1/auth/request-verification", {
					body: {},
				}),
			),
		);
	},

	/**
	 * Delete user account
	 *
	 * DELETE /api/v1/auth/account
	 *
	 * Permanently deletes the user account and all associated data.
	 * This action is irreversible.
	 *
	 * @throws AuthError on server error
	 *
	 * @example
	 * ```typescript
	 * try {
	 *   await authApi.deleteAccount();
	 *   // Logout user
	 *   authStore.logout();
	 *   // Redirect to home
	 * } catch (error) {
	 *   // Show error message
	 * }
	 * ```
	 */
	deleteAccount: async (): Promise<void> => {
		// Ensure CSRF token is available for DELETE request
		await ensureCSRFToken();

		await handleAuthResponse(
			safeApiCall(
				apiClient.DELETE("/api/v1/auth/account", {
					params: { query: {} },
				}),
			),
		);
	},
};

/**
 * Utility function to check if an error is an AuthError
 *
 * @param error Error to check
 * @returns True if error is an AuthError
 *
 * @example
 * ```typescript
 * try {
 *   await authApi.login(credentials);
 * } catch (error) {
 *   if (isAuthError(error) && error.statusCode === 401) {
 *     // Invalid credentials
 *   }
 * }
 * ```
 */
export function isAuthError(error: unknown): error is AuthError {
	return error instanceof AuthError;
}

/**
 * Extract error message from auth error
 *
 * @param error Auth error
 * @returns User-friendly error message
 */
export function getAuthErrorMessage(error: AuthError): string {
	if (error.code === "INVALID_CREDENTIALS") {
		return "Invalid email or password";
	}
	if (error.code === "USER_NOT_FOUND") {
		return "User not found";
	}
	if (error.code === "USER_DISABLED") {
		return "This account has been disabled";
	}
	if (error.code === "INVALID_PASSWORD") {
		return "Current password is incorrect";
	}
	if (error.code === "PASSWORD_MISMATCH") {
		return "Passwords do not match";
	}
	if (error.code === "INVALID_TOKEN") {
		return "Invalid or expired token";
	}
	if (error.code === "CSRF_TOKEN_MISSING") {
		return "Security token missing, please refresh the page";
	}
	if (error.statusCode === 429) {
		return "Too many login attempts, please try again later";
	}
	if (error.statusCode >= 500) {
		return "Server error, please try again later";
	}
	return error.message || "Authentication failed";
}

/**
 * User-initiated login with loud error handling: calls authApi.login and shows
 * a toast on failure using getAuthErrorMessage. Use this from login forms so
 * users always see feedback (invalid credentials, rate limit, etc.).
 *
 * @param credentials User email and password
 * @returns Authentication response with user and token
 * @throws Same error as authApi.login after showing toast
 *
 * @example
 * ```tsx
 * const handleSubmit = async () => {
 *   try {
 *     const res = await loginWithToast({ email, password });
 *     authStore.getState().setUser(res.user);
 *     authStore.getState().setToken(res.token);
 *     navigate({ to: "/home" });
 *   } catch {
 *     // Toast already shown; optionally focus form
 *   }
 * };
 * ```
 */
export async function loginWithToast(
	credentials: LoginRequest,
): Promise<AuthResponse> {
	try {
		return await authApi.login(credentials);
	} catch (error) {
		const message = isAuthError(error)
			? getAuthErrorMessage(error)
			: error instanceof ApiError
				? getAuthErrorMessage(
						new AuthError(
							((error.data as ErrorDetails)?.['message'] as string) ?? error.statusText,
							error.status,
							(error.data as ErrorDetails)?.['code'] as string | undefined,
							error.data as AuthErrorDetails,
						),
					)
				: error instanceof Error
					? error.message
					: "Login failed";
		if (typeof globalThis.window !== "undefined") {
			const { toast } = await import("sonner");
			toast.error("Login failed", { description: message });
		}
		throw error;
	}
}

/**
 * User-initiated login via authStore with loud error handling: calls
 * authStore.login(email, password) and shows a toast on failure. Use this
 * when the app uses authStore for login (e.g. custom email/password form).
 *
 * @param email User email
 * @param password User password
 * @throws Same error as authStore.login after showing toast
 *
 * @example
 * ```tsx
 * const handleSubmit = async () => {
 *   try {
 *     await loginWithToastStore(email, password);
 *     navigate({ to: "/home" });
 *   } catch {
 *     // Toast already shown
 *   }
 * };
 * ```
 */
export async function loginWithToastStore(
	email: string,
	password: string,
): Promise<void> {
	try {
		await useAuthStore.getState().login(email, password);
	} catch (error) {
		const message =
			error instanceof Error ? error.message : "Login failed";
		if (typeof globalThis.window !== "undefined") {
			const { toast } = await import("sonner");
			toast.error("Login failed", { description: message });
		}
		throw error;
	}
}

/**
 * Check if user is likely not authenticated based on error
 *
 * @param error Auth error
 * @returns True if user should be logged out
 */
export function shouldLogoutOnError(error: AuthError): boolean {
	// Logout on invalid credentials or session errors
	return (
		error.statusCode === 401 ||
		error.code === "SESSION_EXPIRED" ||
		error.code === "INVALID_TOKEN"
	);
}
