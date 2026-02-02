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
import client from "./client";

const { ApiError, apiClient, handleApiResponse, safeApiCall } = client;

/** HTTP 401 Unauthorized */
const HTTP_UNAUTHORIZED = 401;
/** HTTP 403 Forbidden */
const HTTP_FORBIDDEN = 403;
/** HTTP 429 Too Many Requests */
const HTTP_TOO_MANY_REQUESTS = 429;
/** Minimum status for server errors (5xx) */
const HTTP_SERVER_ERROR_MIN = 500;

// ============================================================================
// TYPES
// ============================================================================

/**
 * User metadata that can contain arbitrary attributes
 */
export type UserMetadata = Record<string, unknown>;

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
export type AuthErrorDetails = Record<string, unknown>;

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
			const originalError =
				error instanceof Error ? error.message : String(error);
			throw new AuthError(
				"Failed to fetch CSRF token",
				HTTP_FORBIDDEN,
				"CSRF_TOKEN_MISSING",
				{ originalError },
			);
		}
	}
	if (!token) {
		throw new AuthError(
			"CSRF token not available",
			HTTP_FORBIDDEN,
			"CSRF_TOKEN_MISSING",
		);
	}
	return token;
}

/**
 * Parse API error data into message, code, and details using runtime checks.
 */
const isRecordObject = (value: unknown): value is Record<string, unknown> =>
	value !== null && typeof value === "object";

const readStringField = (
	obj: Record<string, unknown>,
	key: string,
): string | null => {
	const value = obj[key];
	if (typeof value === "string") {
		return value;
	}
	return null;
};

const readDetailsField = (
	obj: Record<string, unknown>,
): AuthErrorDetails | null => {
	const value = obj["details"];
	if (value !== null && typeof value === "object") {
		return value as AuthErrorDetails;
	}
	return null;
};

const buildErrorResult = (
	data: Record<string, unknown>,
): { message: string; code?: string; details?: AuthErrorDetails } => {
	const message = readStringField(data, "message") ?? "";
	const code = readStringField(data, "code");
	const details = readDetailsField(data);
	const result: {
		message: string;
		code?: string;
		details?: AuthErrorDetails;
	} = { message };
	if (code) {
		result.code = code;
	}
	if (details) {
		result.details = details;
	}
	return result;
};

function parseErrorData(data: unknown): {
	message: string;
	code?: string;
	details?: AuthErrorDetails;
} {
	if (!isRecordObject(data)) {
		return { message: "" };
	}
	return buildErrorResult(data);
}

/**
 * Helper to handle auth API responses and convert errors
 */
async function handleAuthResponse<TResponse>(
	promise:
		| Promise<{ data?: TResponse; error?: unknown; response: Response }>
		| null
		| undefined,
): Promise<TResponse> {
	try {
		return await handleApiResponse(promise);
	} catch (error) {
		if (error instanceof ApiError) {
			const { message, code, details } = parseErrorData(error.data);
			throw new AuthError(
				message || error.message,
				error.status,
				code,
				details,
			);
		}
		throw error;
	}
}

const AUTH_ERROR_MESSAGES: Record<string, string> = {
	INVALID_CREDENTIALS: "Invalid email or password",
	USER_NOT_FOUND: "User not found",
	USER_DISABLED: "This account has been disabled",
	INVALID_PASSWORD: "Current password is incorrect",
	PASSWORD_MISMATCH: "Passwords do not match",
	INVALID_TOKEN: "Invalid or expired token",
	CSRF_TOKEN_MISSING: "Security token missing, please refresh the page",
};

const EMPTY_LENGTH = 0;

const hasWindow = (): boolean => "window" in globalThis;

const normalizeToken = (value: unknown): string | null => {
	if (value === null || value === globalThis.undefined) {
		return null;
	}
	const trimmed = String(value).trim();
	if (trimmed.length === EMPTY_LENGTH) {
		return null;
	}
	return trimmed;
};

const getStoredToken = (): string | null => {
	if (hasWindow()) {
		const storage = globalThis.window.localStorage;
		const fromStorage = storage ? storage.getItem("auth_token") : null;
		const fromStore = useAuthStore.getState().token;
		const raw = fromStorage ?? fromStore;
		return normalizeToken(raw);
	}
	const storedToken = useAuthStore.getState().token;
	return normalizeToken(storedToken);
};

const fetchCurrentUser = (): Promise<User> =>
	handleAuthResponse(
		safeApiCall(
			apiClient.GET("/api/v1/auth/me", {
				params: { query: {} },
			}),
		),
	);

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
		const token = getStoredToken();
		if (token === null) {
			return null;
		}
		try {
			return await fetchCurrentUser();
		} catch (error) {
			if (
				error instanceof AuthError &&
				error.statusCode === HTTP_UNAUTHORIZED
			) {
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
	const codeMessage = error.code ? AUTH_ERROR_MESSAGES[error.code] : null;
	if (codeMessage) {
		return codeMessage;
	}
	if (error.statusCode === HTTP_TOO_MANY_REQUESTS) {
		return "Too many login attempts, please try again later";
	}
	if (error.statusCode >= HTTP_SERVER_ERROR_MIN) {
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
 *   } catch (error) {
 *     // Toast already shown; optionally focus form
 *   }
 * };
 * ```
 */
function getLoginErrorMessage(error: unknown): string {
	if (isAuthError(error)) {
		return getAuthErrorMessage(error);
	}
	if (error instanceof ApiError) {
		const { message, code, details } = parseErrorData(error.data);
		return getAuthErrorMessage(
			new AuthError(
				message || error.statusText,
				error.status,
				code,
				details,
			),
		);
	}
	if (error instanceof Error) {
		return error.message;
	}
	return "Login failed";
}

export async function loginWithToast(
	credentials: LoginRequest,
): Promise<AuthResponse> {
	try {
		return await authApi.login(credentials);
	} catch (error) {
		const message = getLoginErrorMessage(error);
		if (hasWindow()) {
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
 *   } catch (error) {
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
		let message = "Login failed";
		if (error instanceof Error) {
			const { message: errorMessage } = error;
			message = errorMessage;
		}
		if (hasWindow()) {
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
		error.statusCode === HTTP_UNAUTHORIZED ||
		error.code === "SESSION_EXPIRED" ||
		error.code === "INVALID_TOKEN"
	);
}
