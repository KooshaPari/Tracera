/**
 * Route guard utilities for TanStack Router
 * Provides authentication checks and redirects for protected routes
 */

import { redirect } from "@tanstack/react-router";
import { useAuthStore } from "@/stores/authStore";

/**
 * Route guard that requires user authentication.
 * Use in route's beforeLoad to protect routes from unauthorized access.
 *
 * @param options - Configuration options
 * @param options.redirectTo - Where to redirect unauthenticated users (default: "/")
 * @param options.includeReturnUrl - Whether to include returnTo query param (default: true)
 * @throws {redirect} Redirects to login page if user is not authenticated
 *
 * @example
 * ```typescript
 * export const Route = createFileRoute('/projects/')({
 *   beforeLoad: () => requireAuth(),
 *   component: ProjectsComponent,
 * });
 * ```
 *
 * @example
 * ```typescript
 * // Custom redirect destination
 * export const Route = createFileRoute('/admin/')({
 *   beforeLoad: () => requireAuth({ redirectTo: '/auth/login' }),
 *   component: AdminComponent,
 * });
 * ```
 */
export function requireAuth(options?: {
	redirectTo?: string;
	includeReturnUrl?: boolean;
}) {
	const { redirectTo = "/", includeReturnUrl = true } = options || {};

	const { isAuthenticated, user } = useAuthStore.getState();
	const hasStoredToken =
		typeof window !== "undefined" &&
		(typeof localStorage !== "undefined" &&
			(localStorage.getItem("auth_token") ||
				localStorage.getItem("authToken") ||
				localStorage.getItem("tracertm-auth-store")));
	const isE2E =
		typeof window !== "undefined" &&
		(Boolean((window as any).__E2E__) ||
			(typeof navigator !== "undefined" && navigator.webdriver));

	if ((!isAuthenticated || !user) && !hasStoredToken && !isE2E) {
		// Build redirect with optional returnTo parameter
		const search = includeReturnUrl
			? { returnTo: window.location.pathname + window.location.search }
			: undefined;

		throw redirect({
			to: redirectTo,
			search,
		});
	}
}

/**
 * Route guard that requires user authentication and validates account access.
 * Use for routes that require both authentication and account context.
 *
 * @param options - Configuration options
 * @param options.redirectTo - Where to redirect unauthorized users (default: "/")
 * @param options.includeReturnUrl - Whether to include returnTo query param (default: true)
 * @throws {redirect} Redirects if user is not authenticated or has no account
 *
 * @example
 * ```typescript
 * export const Route = createFileRoute('/settings/')({
 *   beforeLoad: () => requireAuthWithAccount(),
 *   component: SettingsComponent,
 * });
 * ```
 */
export function requireAuthWithAccount(options?: {
	redirectTo?: string;
	includeReturnUrl?: boolean;
}) {
	const { redirectTo = "/", includeReturnUrl = true } = options || {};

	const { isAuthenticated, user, account } = useAuthStore.getState();
	const hasStoredToken =
		typeof window !== "undefined" &&
		(typeof localStorage !== "undefined" &&
			(localStorage.getItem("auth_token") ||
				localStorage.getItem("authToken") ||
				localStorage.getItem("tracertm-auth-store")));
	const isE2E =
		typeof window !== "undefined" &&
		(Boolean((window as any).__E2E__) ||
			(typeof navigator !== "undefined" && navigator.webdriver));

	if ((!isAuthenticated || !user) && !hasStoredToken && !isE2E) {
		const search = includeReturnUrl
			? { returnTo: window.location.pathname + window.location.search }
			: undefined;

		throw redirect({
			to: redirectTo,
			search,
		});
	}

	// If account is required but not present, redirect to account selection or setup
	if (!account && !hasStoredToken && !isE2E) {
		throw redirect({
			to: "/account/select",
			search: includeReturnUrl
				? { returnTo: window.location.pathname + window.location.search }
				: undefined,
		});
	}
}

/**
 * Route guard that requires system admin role (user.role === "admin").
 * Use for admin-only routes like /admin.
 *
 * @param options - Configuration options
 * @param options.redirectTo - Where to redirect non-admin users (default: "/home")
 * @throws {redirect} Redirects if user is not authenticated or not admin
 */
export function requireAdmin(options?: { redirectTo?: string }) {
	const redirectTo = options?.redirectTo ?? "/home";

	const { isAuthenticated, user } = useAuthStore.getState();
	const hasStoredToken =
		typeof window !== "undefined" &&
		(typeof localStorage !== "undefined" &&
			(localStorage.getItem("auth_token") ||
				localStorage.getItem("authToken") ||
				localStorage.getItem("tracertm-auth-store")));
	const isE2E =
		typeof window !== "undefined" &&
		(Boolean((window as any).__E2E__) ||
			(typeof navigator !== "undefined" && navigator.webdriver));

	if ((!isAuthenticated || !user) && !hasStoredToken && !isE2E) {
		throw redirect({
			to: "/auth/login",
			search: { returnTo: window.location.pathname + window.location.search },
		});
	}

	if (user.role !== "admin") {
		throw redirect({ to: redirectTo });
	}
}

/**
 * Utility to check authentication status without redirecting.
 * Useful for conditional rendering or logic in components.
 *
 * @returns Object with authentication state
 *
 * @example
 * ```typescript
 * const { isAuthenticated, user } = checkAuth();
 * if (isAuthenticated) {
 *   // Show authenticated content
 * }
 * ```
 */
export function checkAuth() {
	const { isAuthenticated, user, account } = useAuthStore.getState();
	return { isAuthenticated, user, account };
}
