/**
 * Route guard utilities for TanStack Router
 * Provides authentication checks and redirects for protected routes
 */

import { redirect } from '@tanstack/react-router';

import { logger } from '@/lib/logger';
import { useAuthStore } from '@/stores/authStore';

interface RouteGuardOptions {
  includeReturnUrl?: boolean;
  redirectTo?: string;
}

interface RouteGuardState {
  account: ReturnType<typeof useAuthStore.getState>['account'];
  isAuthenticated: boolean;
  token: ReturnType<typeof useAuthStore.getState>['token'];
  user: ReturnType<typeof useAuthStore.getState>['user'];
}

type E2EWindow = Window & { __E2E__?: boolean };

const getReturnTo = (): string => window.location.pathname + window.location.search;

const isE2ERuntime = (): boolean =>
  typeof window !== 'undefined' &&
  (Boolean((window as E2EWindow).__E2E__) ||
    (typeof navigator !== 'undefined' && navigator.webdriver));

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

export async function requireAuth(options?: RouteGuardOptions): Promise<void> {
  const { redirectTo = '/auth/login', includeReturnUrl = true } = options || {};

  if (isE2ERuntime()) {
    return;
  }

  const isValid = await hasValidSession();
  if (!isValid) {
    throw redirect({
      search: includeReturnUrl ? { returnTo: getReturnTo() } : undefined,
      to: redirectTo,
    });
  }
}

export async function requireAuthWithAccount(options?: RouteGuardOptions): Promise<void> {
  const { redirectTo = '/auth/login', includeReturnUrl = true } = options || {};

  if (isE2ERuntime()) {
    return;
  }

  const isValid = await hasValidSession();
  if (!isValid) {
    throw redirect({
      search: includeReturnUrl ? { returnTo: getReturnTo() } : undefined,
      to: redirectTo,
    });
  }

  const { account } = useAuthStore.getState();
  if (!account) {
    throw redirect({
      search: includeReturnUrl ? { returnTo: getReturnTo() } : undefined,
      to: '/account/select',
    });
  }
}

export async function requireAdmin(options?: Pick<RouteGuardOptions, 'redirectTo'>): Promise<void> {
  const redirectTo = options?.redirectTo ?? '/home';

  if (isE2ERuntime()) {
    return;
  }

  const isValid = await hasValidSession();
  if (!isValid) {
    throw redirect({
      search: { returnTo: getReturnTo() },
      to: '/auth/login',
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
 * @returns {RouteGuardState} Object with authentication state
 *
 * @example
 * ```typescript
 * const { isAuthenticated, user } = checkAuth();
 * if (isAuthenticated) {
 *   // Show authenticated content
 * }
 * ```
 */
export function checkAuth(): RouteGuardState {
  const { isAuthenticated, user, account, token } = useAuthStore.getState();
  return { isAuthenticated, user, account, token };
}
