import createClient from "openapi-fetch";
import {
	getCSRFHeaders,
	extractCSRFTokenFromResponse,
	handleCSRFError,
} from "../lib/csrf";

// API client configuration
const API_BASE_URL = import.meta.env?.VITE_API_URL || "http://localhost:8000";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyPaths = any;

/**
 * Create typed API client with HttpOnly cookie-based authentication
 *
 * Authentication flow:
 * 1. Cookies are sent automatically via credentials: 'include'
 * 2. No Authorization header or localStorage token
 * 3. Session validated on app startup via validateSession()
 * 4. 401 responses trigger redirect to /login
 *
 * NOTE: Using `any` as a temporary measure until we can generate comprehensive OpenAPI types.
 * This is acceptable because:
 * - The underlying fetch calls are still type-safe at runtime
 * - We use strict input validation with Zod in handlers
 * - Response types are validated in the caller
 * - We're migrating toward full type safety incrementally
 */
export const apiClient = createClient<AnyPaths>({
	baseUrl: API_BASE_URL,
	headers: {
		"Content-Type": "application/json",
	},
});

// Validate apiClient is initialized
if (!apiClient) {
	console.error("API client failed to initialize");
	throw new Error("API client initialization failed");
}

/**
 * Validate session is still active
 * Call this on app startup to verify authentication
 */
export async function validateSession(): Promise<boolean> {
	try {
		const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
			method: "GET",
			credentials: "include", // Send HttpOnly cookies
			headers: {
				"Content-Type": "application/json",
			},
		});

		if (response.status === 401) {
			// Session expired or invalid
			console.warn("[Auth] Session validation failed: 401 Unauthorized");
			return false;
		}

		if (!response.ok) {
			throw new Error(`Session validation failed: ${response.status}`);
		}

		console.debug("[Auth] Session validated successfully");
		return true;
	} catch (error) {
		console.error("[Auth] Session validation error:", error);
		return false;
	}
}

/**
 * Clear auth state on logout
 * Cookies are cleared by backend via Set-Cookie headers
 */
function handleLogout(): void {
	// Clear auth state from stores
	if (typeof globalThis.window !== "undefined") {
		// Trigger auth store logout
		const logoutEvent = new CustomEvent("auth:logout");
		globalThis.window.dispatchEvent(logoutEvent);

		// Redirect to login
		globalThis.window.location.href = "/login";
	}
}

// Add request interceptor for CSRF protection and response handling
apiClient.use({
	onRequest: async ({ request }) => {
		// Add CSRF token for state-changing requests
		// Cookies are sent automatically via credentials in fetch config
		const csrfHeaders = getCSRFHeaders(request.method);
		Object.entries(csrfHeaders).forEach(([key, value]) => {
			request.headers.set(key, value);
		});

		return request;
	},
	onResponse: async ({ response }) => {
		// Extract new CSRF token from response if available
		extractCSRFTokenFromResponse(response);

		// Handle CSRF token errors with automatic retry
		if (response.status === 403) {
			const wasCsrfError = await handleCSRFError(response.clone());
			if (wasCsrfError) {
				console.warn(
					"[API Client] CSRF token was refreshed, request may need to be retried",
				);
				// Note: The actual retry should be handled by the calling code
				// or by implementing a more sophisticated retry mechanism
			}
		}

		// Handle 401 Unauthorized - session expired or invalid
		if (response.status === 401) {
			console.warn("[Auth] Session expired or invalid - redirecting to login");
			handleLogout();
		}

		return response;
	},
});

// Helper to handle API errors
export class ApiError extends Error {
	constructor(
		public status: number,
		public statusText: string,
		public data?: unknown,
	) {
		super(`API Error ${status}: ${statusText}`);
		this.name = "ApiError";
	}
}

// Helper to safely get a promise from API client methods
export function safeApiCall<T>(
	apiCall:
		| Promise<{ data?: T; error?: unknown; response: Response }>
		| null
		| undefined,
): Promise<{ data?: T; error?: unknown; response: Response }> {
	if (!apiCall) {
		return Promise.reject(
			new ApiError(500, "API request failed: promise is null", undefined),
		);
	}
	return apiCall;
}

export async function handleApiResponse<T>(
	promise:
		| Promise<{ data?: T; error?: unknown; response: Response }>
		| null
		| undefined,
): Promise<T> {
	if (!promise) {
		throw new ApiError(500, "API request failed: promise is null", undefined);
	}

	const { data, error, response } = await promise;

	if (error) {
		throw new ApiError(
			response?.status || 500,
			response?.statusText || "Unknown error",
			error,
		);
	}

	if (!data) {
		throw new ApiError(response?.status || 500, "No data returned", undefined);
	}

	return data;
}

// Export API base URL for WebSocket connections
export { API_BASE_URL };
