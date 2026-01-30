/**
 * Authentication utility functions and helpers
 */

import { useAuthStore } from "@/stores/authStore";

/**
 * Check if a route path is a public auth route
 */
export function isPublicRoute(pathname: string): boolean {
	const publicRoutes = [
		"/auth/login",
		"/auth/register",
		"/auth/reset-password",
		"/auth/callback",
	];
	return publicRoutes.some((route) => pathname.startsWith(route));
}

/**
 * Check if a URL is an auth route (should not be used as returnTo)
 */
function isAuthRoute(url: string): boolean {
	try {
		const urlObj = new URL(url, window.location.origin);
		const pathname = urlObj.pathname;
		return pathname.startsWith("/auth/");
	} catch {
		// If URL parsing fails, check if it starts with /auth/
		return url.startsWith("/auth/");
	}
}

/**
 * Get the redirect URL after login
 * Filters out auth routes and invalid URLs to prevent redirect loops
 */
export function getReturnTo(
	searchParams: URLSearchParams | Record<string, string> | string | undefined,
): string {
	if (!searchParams) {
		return "/";
	}

	let returnTo: string | null = null;

	if (searchParams instanceof URLSearchParams) {
		returnTo = searchParams.get("returnTo");
	} else if (typeof searchParams === "string") {
		// If it's a string, try to parse it as URLSearchParams
		try {
			const params = new URLSearchParams(searchParams);
			returnTo = params.get("returnTo");
		} catch {
			return "/";
		}
	} else if (typeof searchParams === "object" && searchParams !== null) {
		const returnToValue = (searchParams as Record<string, unknown>)["returnTo"];
		if (typeof returnToValue === "string") {
			returnTo = returnToValue;
		}
	}

	// Validate returnTo
	if (!returnTo || typeof returnTo !== "string") {
		return "/";
	}

	// Filter out invalid values
	if (returnTo.includes("[object Object]")) {
		return "/";
	}

	// Filter out auth routes to prevent redirect loops
	if (isAuthRoute(returnTo)) {
		return "/";
	}

	// Extract pathname if it's a full URL (remove query params that might include auth codes)
	try {
		const urlObj = new URL(returnTo, window.location.origin);
		const pathname = urlObj.pathname;

		// If pathname is an auth route, ignore it
		if (isAuthRoute(pathname)) {
			return "/";
		}

		// Return just the pathname (ignore query params to avoid including auth codes)
		return pathname;
	} catch {
		// If URL parsing fails, check if it's an auth route
		if (isAuthRoute(returnTo)) {
			return "/";
		}
		// Return as-is if it's a valid path
		return returnTo.startsWith("/") ? returnTo : "/";
	}
}

/**
 * Hook to check authentication status
 */
export function useIsAuthenticated(): boolean {
	return useAuthStore((state) => state.isAuthenticated);
}

/**
 * Hook to get current user
 */
export function useCurrentUser() {
	return useAuthStore((state) => state.user);
}
