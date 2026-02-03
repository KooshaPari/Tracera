import { logger } from "@/lib/logger";

const API_BASE_URL = import.meta.env?.VITE_API_URL || "http://localhost:4000";
const CSRF_COOKIE_NAME = "csrf_token";
const CSRF_HEADER = "X-CSRF-Token";
const HTTP_STATUS_FORBIDDEN = 403;

// In-memory token storage (never use localStorage for CSRF tokens)
let csrfToken: string | null = null;
let tokenFetchPromise: Promise<string> | null = null;

/**
 * Fetch CSRF token from server
 * Uses a promise to avoid race conditions if called multiple times
 */
export const fetchCSRFToken = async (): Promise<string> => {
	// If a fetch is already in progress, return that promise
	if (tokenFetchPromise) {
		return tokenFetchPromise;
	}

	// If token already exists and is valid, return it
	if (csrfToken) {
		return csrfToken;
	}

	// Create new fetch promise
	tokenFetchPromise = (async () => {
		try {
			const response = await fetch(`${API_BASE_URL}/api/v1/csrf-token`, {
				credentials: "include", // Include cookies for double-submit pattern
				headers: {
					"Content-Type": "application/json",
				},
				method: "GET",
			});

			if (!response.ok) {
				throw new Error(`Failed to fetch CSRF token: ${response.status}`);
			}

			const data = (await response.json()) as { token: string; valid: boolean };

			if (!data.token) {
				throw new Error("No CSRF token in response");
			}

			csrfToken = data.token;
			logger.debug("[CSRF] Token fetched successfully");

			return csrfToken;
		} catch (error) {
			logger.error("[CSRF] Failed to fetch token:", error);
			throw error;
		} finally {
			// Reset promise so next call will attempt fresh fetch
			tokenFetchPromise = null;
		}
	})();

	return tokenFetchPromise;
};

/**
 * Get current CSRF token without fetching
 * Returns null if token not loaded yet
 */
export const getCSRFToken = (): string | null => {
	return csrfToken;
};

/**
 * Set CSRF token (used after receiving new token in response)
 */
export const setCSRFToken = (token: string): void => {
	csrfToken = token;
	logger.debug("[CSRF] Token updated");
};

/**
 * Refresh CSRF token by fetching a new one
 */
export const refreshCSRFToken = async (): Promise<string> => {
	csrfToken = null; // Clear current token
	tokenFetchPromise = null; // Clear any pending promise
	return fetchCSRFToken();
};

/**
 * Initialize CSRF protection on app startup
 * This should be called once when the app initializes
 */
export const initializeCSRF = async (): Promise<void> => {
	try {
		await fetchCSRFToken();
		logger.info("[CSRF] Initialized successfully");
	} catch (error) {
		logger.error("[CSRF] Failed to initialize:", error);
		// Don't throw - CSRF is optional in dev mode
		// In production, requests will fail if token is missing
	}
};

/**
 * Check if a request method requires CSRF protection
 */
const isStateChangingRequest = (method: string): boolean => {
	return ["DELETE", "PATCH", "POST", "PUT"].includes(method.toUpperCase());
};

/**
 * Get CSRF headers to include in requests
 * Returns headers object with CSRF token if request requires it
 */
export const getCSRFHeaders = (method: string): Record<string, string> => {
	if (!isStateChangingRequest(method)) {
		return {};
	}

	if (!csrfToken) {
		logger.warn("[CSRF] Token not available for state-changing request");
		return {};
	}

	return {
		[CSRF_HEADER]: csrfToken,
	};
};

/**
 * Extract CSRF token from response (if server sends new token)
 * Some servers may send token in response header or body
 */
export const extractCSRFTokenFromResponse = (
	response: Response,
): string | null => {
	// Check for token in response header
	const headerToken = response.headers.get(CSRF_HEADER);
	if (headerToken) {
		setCSRFToken(headerToken);
		return headerToken;
	}

	// Try to extract from Set-Cookie header (cookie pattern)
	const setCookie = response.headers.get("set-cookie");
	if (setCookie?.includes(CSRF_COOKIE_NAME)) {
		// Cookie is automatically set by browser, no action needed
		logger.debug("[CSRF] New token cookie received");
		return null; // Token will be in cookie, fetch it when needed
	}

	return null;
};

/**
 * Middleware for API client to automatically include CSRF tokens
 * This should be used with the API client to inject tokens into all requests
 */
export const createCSRFRequestInterceptor = () => {
	return async (request: Request): Promise<Request> => {
		// Clone the request to modify it
		const newRequest = request.clone();

		// Only add CSRF token for state-changing requests
		if (isStateChangingRequest(newRequest.method)) {
			// Ensure we have a token
			if (!csrfToken) {
				try {
					await fetchCSRFToken();
				} catch (error) {
					logger.warn("[CSRF] Failed to fetch token before request:", error);
				}
			}

			// Add CSRF header if token is available
			if (csrfToken) {
				newRequest.headers.set(CSRF_HEADER, csrfToken);
			}
		}

		return newRequest;
	};
};

/**
 * Middleware for API client to handle CSRF errors
 * Returns true if error was a CSRF error and was handled
 */
export const handleCSRFError = async (
	response: Response,
): Promise<boolean> => {
	// Check for CSRF-related 403 errors
	if (response.status === HTTP_STATUS_FORBIDDEN) {
		const contentType = response.headers.get("content-type");
		if (contentType?.includes("application/json")) {
			try {
				const data = (await response.json()) as { error?: string };
				const isCsrfError =
					data.error?.toLowerCase().includes("csrf") ||
					data.error?.toLowerCase().includes("token");

				if (isCsrfError) {
					logger.warn("[CSRF] Token validation failed, refreshing...");

					try {
						// Refresh token
						await refreshCSRFToken();
						// Return true to indicate error was handled
						// Caller should retry the request
						return true;
					} catch (error) {
						logger.error("[CSRF] Failed to refresh token:", error);
						return false;
					}
				}
			} catch {
				// Response body not JSON, not a CSRF error
			}
		}
	}

	return false;
};

/**
 * Get all CSRF-related cookies
 * Useful for debugging
 */
export const getCSRFCookies = (): Record<string, string> => {
	const cookies: Record<string, string> = {};

	if (typeof document === "undefined") {
		return cookies;
	}

	// Parse document.cookie
	document.cookie.split(";").forEach((cookie) => {
		const [name, value] = cookie.trim().split("=");
		if (name && value) {
			cookies[name] = decodeURIComponent(value);
		}
	});

	return cookies;
};

/**
 * Clear CSRF token (useful for logout)
 */
export const clearCSRFToken = (): void => {
	csrfToken = null;
	tokenFetchPromise = null;
	logger.debug("[CSRF] Token cleared");
};

/**
 * Debug helper to log CSRF state
 */
export const logCSRFState = (): void => {
	logger.group("[CSRF] Current State");
	logger.info("Token in memory:", csrfToken ? "Yes" : "No");
	logger.info("Token value:", `${csrfToken?.substring(0, 20)}...` || "None");
	logger.info("Cookies:", getCSRFCookies());
	logger.groupEnd();
};
