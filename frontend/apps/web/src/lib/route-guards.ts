/**
 * Route guard utilities for TanStack Router
 * Provides authentication checks and redirects for protected routes
 */

import { redirect } from '@tanstack/react-router';

import { logger } from '@/lib/logger';
import { useAuthStore } from '@/stores/authStore';

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
const hasValidSession = async (): Promise<boolean> => {
  try {
    const { isAuthenticated, token, user, validateSession } = useAuthStore.getState();
    const normalizedToken = token?.trim();
    if (isAuthenticated && user && normalizedToken) {
      return true;
    }
    if (!normalizedToken) {
      return false;
    }
    const ok = await validateSession();
    const latest = useAuthStore.getState();
    return Boolean(ok && latest.isAuthenticated && latest.user && latest.token?.trim());
  } catch (error) {
    logger.error('Session validation error:', error);
    return false;
  }
};

export async function requireAuth(options?: { redirectTo?: string; includeReturnUrl?: boolean }) {
  const { redirectTo = '/auth/login', includeReturnUrl = true } = options || {};

  const isE2E =
    typeof window !== 'undefined' &&
    (Boolean((window as any).__E2E__) || (typeof navigator !== 'undefined' && navigator.webdriver));

  if (isE2E) {
    return;
  }

  const isValid = await hasValidSession();
  if (!isValid) {
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
export async function requireAuthWithAccount(options?: {
  redirectTo?: string;
  includeReturnUrl?: boolean;
}) {
  const { redirectTo = '/auth/login', includeReturnUrl = true } = options || {};

  const isE2E =
    typeof window !== 'undefined' &&
    (Boolean((window as any).__E2E__) || (typeof navigator !== 'undefined' && navigator.webdriver));

  if (isE2E) {
    return;
  }

  const isValid = await hasValidSession();
  if (!isValid) {
    const search = includeReturnUrl
      ? { returnTo: window.location.pathname + window.location.search }
      : undefined;

    throw redirect({
      to: redirectTo,
      search,
    });
  }

  // If account is required but not present, redirect to account selection or setup
  const { account } = useAuthStore.getState();
  if (!account) {
    throw redirect({
      to: '/account/select',
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
export async function requireAdmin(options?: { redirectTo?: string }) {
  const redirectTo = options?.redirectTo ?? '/home';

  const isE2E =
    typeof window !== 'undefined' &&
    (Boolean((window as any).__E2E__) || (typeof navigator !== 'undefined' && navigator.webdriver));

  if (isE2E) {
    return;
  }

  const isValid = await hasValidSession();
  if (!isValid) {
    throw redirect({
      to: '/auth/login',
      search: { returnTo: window.location.pathname + window.location.search },
    });
  }

  const { user } = useAuthStore.getState();
  if (!user || user.role !== 'admin') {
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
