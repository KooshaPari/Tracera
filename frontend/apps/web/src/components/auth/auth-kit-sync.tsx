/* eslint-disable import/no-default-export, import/no-named-export, oxc/no-async-await, unicorn/no-null, eslint/no-duplicate-imports, eslint/no-magic-numbers, eslint/max-lines-per-function, eslint/max-statements, eslint/sort-imports */
import { useAuth } from '@workos-inc/authkit-react';
import { useEffect, useMemo, useRef } from 'react';

import { logger } from '@/lib/logger';

import type { User, UserMetadata } from '../../stores/authStore';

import config from '../../config/constants';
import { getReturnTo, isPublicRoute } from '../../lib/auth-utils';
import { useAuthStore } from '../../stores/authStore';

const MIN_LENGTH = 0;

const isRecordObject = (value: unknown): value is Record<string, unknown> =>
  Object.prototype.toString.call(value) === '[object Object]';

const readStringField = (obj: Record<string, unknown>, key: string): string | undefined => {
  const value = obj[key];
  if (typeof value === 'string') {
    return value;
  }
  return undefined;
};

const readMetadataField = (obj: Record<string, unknown>, key: string): UserMetadata | undefined => {
  const value = obj[key];
  if (value && typeof value === 'object') {
    return value as UserMetadata;
  }
  return undefined;
};

const toUser = (workosUser: unknown): User | null => {
  if (!isRecordObject(workosUser)) {
    return null;
  }
  const firstName = readStringField(workosUser, 'firstName');
  const lastName = readStringField(workosUser, 'lastName');
  const email = readStringField(workosUser, 'email');
  const id = readStringField(workosUser, 'id');
  if (!email || !id) {
    return null;
  }
  const nameParts = [firstName, lastName].filter(Boolean);
  let name = '';
  if (nameParts.length > MIN_LENGTH) {
    name = nameParts.join(' ');
  } else {
    name = email;
  }
  return {
    avatar: readStringField(workosUser, 'profilePictureUrl'),
    email,
    id,
    metadata: readMetadataField(workosUser, 'metadata'),
    name,
    role: readStringField(workosUser, 'role'),
  };
};

export default function AuthKitSync(): null {
  const { user, isLoading, getAccessToken } = useAuth();
  const setAuthFromWorkOS = useAuthStore((state) => state.setAuthFromWorkOS);
  const logout = useAuthStore((state) => state.logout);
  const hasRedirectedRef = useRef(false);

  // Stable refs for functions that change identity every render
  const getAccessTokenRef = useRef(getAccessToken);
  const logoutRef = useRef(logout);
  const setAuthFromWorkOSRef = useRef(setAuthFromWorkOS);

  // Keep refs current without triggering effect re-runs
  useEffect(() => {
    getAccessTokenRef.current = getAccessToken;
    logoutRef.current = logout;
    setAuthFromWorkOSRef.current = setAuthFromWorkOS;
  });

  const mappedUser = useMemo(() => toUser(user ?? null), [user]);
  const isSignedIn = Boolean(user);

  useEffect(() => {
    let active = true;

    const syncToken = async (): Promise<void> => {
      if (!isSignedIn) {
        // Delay logout slightly to allow CSRF to initialize first
        await new Promise((resolve) => setTimeout(resolve, 50));
        if (active) {
          logoutRef.current().catch(() => {
            // Silently ignore logout errors (CSRF token may not be ready yet)
          });
        }
        return;
      }

      try {
        const token = await getAccessTokenRef.current();
        if (!active) {
          return;
        }
        setAuthFromWorkOSRef.current(mappedUser, token ?? null);
        // Hydrate user from /auth/me only when we have a token (avoids 401)
        if (token && token.trim()) {
          await useAuthStore.getState().validateSession();
        }

        // Handle redirect after successful authentication
        // IMPORTANT: Don't redirect on /auth/callback - WorkOS handles that flow
        // Only redirect when user is authenticated on other auth pages (login/register)
        const currentPath = globalThis.location.pathname;

        if (
          !hasRedirectedRef.current &&
          isPublicRoute(currentPath) &&
          currentPath !== config.AUTH_ROUTES.CALLBACK
        ) {
          hasRedirectedRef.current = true;
          const searchParams = new globalThis.URLSearchParams(globalThis.location.search);
          const returnTo = getReturnTo(searchParams);

          // GetReturnTo already filters out auth routes and returns "/home" as default
          // If returnTo is "/home", user will be sent to dashboard
          // Otherwise, they'll be sent to their intended destination
          globalThis.location.href = returnTo;
        }
      } catch (error) {
        logger.error('Failed to sync AuthKit token:', error);
        logoutRef.current();
      }
    };

    if (!isLoading) {
      syncToken();
    }

    // No periodic interval here — auth-store's initializeAutoRefresh handles token refresh
    return (): void => {
      active = false;
    };
  }, [isLoading, isSignedIn, mappedUser]);

  return null;
}
/* eslint-enable import/no-default-export, import/no-named-export, oxc/no-async-await, unicorn/no-null, eslint/no-duplicate-imports, eslint/no-magic-numbers, eslint/max-lines-per-function, eslint/max-statements, eslint/sort-imports */
