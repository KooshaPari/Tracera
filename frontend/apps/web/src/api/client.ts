import createClient from "openapi-fetch";
import { logger } from '@/lib/logger';
import {
	extractCSRFTokenFromResponse,
	getCSRFHeaders,
	handleCSRFError,
} from "../lib/csrf";
import { useAuthStore } from "../stores/authStore";
import { useConnectionStatusStore } from "../stores/connectionStatusStore";

/**
 * Gateway-only API base URL.
 * All external clients (frontend, MCP, CLI) must use the gateway so routing, CORS, and
 * contracts are consistent and auditable. No direct backend URLs in dev or prod.
 */
export function getBackendURL(_path?: string): string {
	const url = import.meta.env?.VITE_API_URL || "";
	if (url) return url.replace(/\/$/, "");
	// Default when no env: gateway on port 4000 (process-compose / Caddy)
	return "http://localhost:4000";
}

// API client configuration
const API_BASE_URL = getBackendURL();

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyPaths = any;

/**
 * Create typed API client with HttpOnly cookie-based authentication.
 * All requests use the global fetch patched with wait+retry (see main.tsx and lib/fetch-retry.ts).
 *
 * Authentication flow:
 * 1. Cookies are sent automatically via credentials: 'include'
 * 2. No Authorization header or localStorage token
 * 3. Session validated on app startup via validateSession()
 * 4. 401 responses trigger redirect to /auth/login
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
	// CRITICAL: Send cookies with all requests for HttpOnly cookie authentication
	// In development (devMode), tokens are in localStorage but cookies still needed for CSRF
	// In production, tokens are in HttpOnly cookies and MUST be sent
	credentials: "include",
});

// Validate apiClient is initialized
if (!apiClient) {
	logger.error("API client failed to initialize");
	throw new Error("API client initialization failed");
}

/**
 * Validate session is still active
 * Call this on app startup to verify authentication
 */
export async function validateSession(): Promise<boolean> {
	try {
		const fromStorage =
			typeof globalThis.window !== "undefined"
				? globalThis.window.localStorage?.getItem("auth_token")
				: null;
		const fromStore = useAuthStore.getState().token;
		const token = (fromStorage ?? fromStore)?.trim();
		// Don't call /auth/me without a token — backend returns 401 and we'd just get false
		if (!token) {
			return false;
		}
		const headers: Record<string, string> = {
			"Content-Type": "application/json",
			Authorization: `Bearer ${token}`,
		};
		const response = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
			method: "GET",
			credentials: "include", // Send HttpOnly cookies
			headers,
		});

		if (response.status === 401) {
			// Session expired or invalid
			logger.warn("[Auth] Session validation failed: 401 Unauthorized");
			return false;
		}

		if (!response.ok) {
			throw new Error(`Session validation failed: ${response.status}`);
		}

		logger.debug("[Auth] Session validated successfully");
		return true;
	} catch (error) {
		logger.error("[Auth] Session validation error:", error);
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
		globalThis.window.location.href = "/auth/login";
	}
}

// Add request interceptor for CSRF protection, auth, and response handling
apiClient.use({
	onRequest: async ({ request }) => {
		// Route requests to the correct backend in development.
		// openapi-fetch builds the URL up-front, so we rewrite the origin here.
		if (!import.meta.env.PROD) {
			try {
				const url = new URL(request.url);
				const targetBase = getBackendURL(url.pathname);
				if (targetBase) {
					const target = new URL(targetBase);
					if (url.origin !== target.origin) {
						logger.warn(
							`[API Routing] Redirecting ${url.pathname} from ${url.origin} -> ${target.origin}`,
						);
						const nextUrl = `${target.origin}${url.pathname}${url.search}`;
						request = new Request(nextUrl, request);
					}
				}
			} catch {
				// Ignore URL rewrite failures; fall back to the original request.
			}
		}

		// Add CSRF token for state-changing requests
		// Cookies are sent automatically via credentials in fetch config
		const csrfHeaders = getCSRFHeaders(request.method);
		Object.entries(csrfHeaders).forEach(([key, value]) => {
			request.headers.set(key, value);
		});

		// Send Bearer token for API requests when user is logged in (WorkOS token in auth store)
		// Backend auth_guard expects Authorization: Bearer <token>; without it requests return 401
		if (
			typeof globalThis.window !== "undefined" &&
			request.url.includes("/api/")
		) {
			const fromStorage = globalThis.window.localStorage?.getItem("auth_token");
			const fromStore = useAuthStore.getState().token;
			const token = (fromStorage ?? fromStore)?.trim();
			if (token) {
				request.headers.set("Authorization", `Bearer ${token}`);
			}
		}

		return request;
	},
	onResponse: async ({ response }) => {
		// Extract new CSRF token from response if available
		extractCSRFTokenFromResponse(response);

		// Handle CSRF token errors with automatic retry; track so we don't double-toast 403
		let wasCsrfError = false;
		if (response.status === 403) {
			wasCsrfError = await handleCSRFError(response.clone());
			if (wasCsrfError) {
				logger.warn(
					"[API Client] CSRF token was refreshed, request may need to be retried",
				);
			}
		}

		// Handle 401: integration auth vs session auth (graceful/loud, no silent)
		// Skip session handling for login endpoint so caller can show invalid-credentials toast
		if (response.status === 401) {
			if (response.url.includes("/auth/login")) {
				// Login attempt failed — caller (e.g. authApi.login) will throw and show toast
				return response;
			}
			let body: { code?: string; detail?: string } | undefined;
			try {
				body = await response.clone().json();
			} catch {
				body = undefined;
			}
			if (body?.code === "integration_auth_required") {
				if (typeof globalThis.window !== "undefined") {
					import("sonner").then(({ toast }) => {
						toast.error("Connection expired", {
							description:
								body?.detail ||
								"Reconnect this integration in Settings.",
							action: {
								label: "Settings",
								onClick: () => {
									globalThis.window.location.href = "/settings";
								},
							},
						});
					});
				}
			} else {
				logger.warn("[Auth] Session expired or invalid - redirecting to login");
				handleLogout();
			}
		}

		// Handle 429 rate limit: loud, with retry-after
		if (response.status === 429) {
			let retryAfter = response.headers.get("Retry-After");
			let body: { retry_after?: number; detail?: string } | undefined;
			try {
				body = await response.clone().json();
			} catch {
				body = undefined;
			}
			const seconds = retryAfter
				? parseInt(retryAfter, 10)
				: body?.retry_after ?? 60;
			const message =
				seconds >= 60
					? `Try again in ${Math.ceil(seconds / 60)} minute(s).`
					: `Try again in ${seconds} second(s).`;
			if (typeof globalThis.window !== "undefined") {
				import("sonner").then(({ toast }) => {
					toast.error("Rate limited", {
						description: body?.detail ?? message,
					});
				});
			}
		}

		// Handle 403 Forbidden - clear message for users (skip if already handled as CSRF)
		if (response.status === 403 && !wasCsrfError) {
			if (typeof globalThis.window !== "undefined") {
				import("sonner").then(({ toast }) => {
					toast.error("Access denied", {
						description: "You don't have permission for this action.",
					});
				});
			}
		}

		// Handle 404 from integration endpoints: loud so user knows resource missing
		if (response.status === 404) {
			let body: { code?: string; detail?: string } | undefined;
			try {
				body = await response.clone().json();
			} catch {
				body = undefined;
			}
			if (body?.code === "integration_not_found" && typeof globalThis.window !== "undefined") {
				import("sonner").then(({ toast }) => {
					toast.error("Resource not found", {
						description: body?.detail ?? "The requested item was not found.",
					});
				});
			}
		}

		// Connection loss: 5xx — loud: banner + toast
		if (response.status >= 500) {
			const message = `Backend error ${response.status}`;
			useConnectionStatusStore.getState().setLost(message);
			if (typeof globalThis.window !== "undefined") {
				import("sonner").then(({ toast }) => {
					toast.error("Server error", {
						description: "Connection issue. We'll retry; check back in a moment.",
					});
				});
			}
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

/**
 * Headers for direct fetch() calls that need auth (same token as apiClient).
 * Use when calling /api/v1/* with fetch() instead of apiClient.
 */
export function getAuthHeaders(): Record<string, string> {
	if (typeof globalThis.window === "undefined") return {};
	const fromStorage = globalThis.window.localStorage?.getItem("auth_token");
	const fromStore = useAuthStore.getState().token;
	const token = (fromStore ?? fromStorage)?.trim();
	if (!token) return {};
	return { Authorization: `Bearer ${token}` };
}
