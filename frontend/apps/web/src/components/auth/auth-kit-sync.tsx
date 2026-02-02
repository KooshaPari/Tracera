/* eslint-disable import/no-default-export, import/no-named-export, oxc/no-async-await, unicorn/no-null, eslint/no-duplicate-imports, eslint/no-magic-numbers, eslint/max-lines-per-function, eslint/max-statements, eslint/sort-imports */
import { useAuth } from "@workos-inc/authkit-react";
import { logger } from "@/lib/logger";
import { AUTH_ROUTES } from "../../config/constants";
import { getReturnTo, isPublicRoute } from "../../lib/auth-utils";
import { useAuthStore } from "../../stores/authStore";
import type { User } from "../../stores/authStore";
import { useEffect, useMemo, useRef } from "react";

const SECONDS_PER_MINUTE = 60;
const MILLIS_PER_SECOND = 1000;
const REFRESH_INTERVAL_MS = 5 * SECONDS_PER_MINUTE * MILLIS_PER_SECOND;
const MIN_LENGTH = 0;

const toUser = (workosUser: unknown): User | null => {
	if (!workosUser) {
		return null;
	}
	const nameParts = [workosUser.firstName, workosUser.lastName].filter(Boolean);
	let name = "";
	if (nameParts.length > MIN_LENGTH) {
		name = nameParts.join(" ");
	} else {
		name = workosUser.email;
	}
	return {
		avatar: workosUser.profilePictureUrl,
		email: workosUser.email,
		id: workosUser.id,
		metadata: workosUser.metadata,
		name,
		role: workosUser.role,
	};
};

export default function AuthKitSync(): null {
	const { user, isLoading, getAccessToken } = useAuth();
	const setAuthFromWorkOS = useAuthStore((state) => state.setAuthFromWorkOS);
	const logout = useAuthStore((state) => state.logout);
	const hasRedirectedRef = useRef(false);

	const mappedUser = useMemo(() => toUser(user ?? null), [user]);
	const isSignedIn = Boolean(user);

	useEffect(() => {
		let active = true;

		const syncToken = async (): Promise<void> => {
			if (!isSignedIn) {
				logout();
				return;
			}

			try {
				const token = await getAccessToken();
				if (!active) {
					return;
				}
				setAuthFromWorkOS(mappedUser, token ?? null);
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
					currentPath !== AUTH_ROUTES.CALLBACK
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
				logger.error("Failed to sync AuthKit token:", error);
				logout();
			}
		};

		if (!isLoading) {
			syncToken();
		}

		const interval = globalThis.setInterval(syncToken, REFRESH_INTERVAL_MS);
		return (): void => {
			active = false;
			globalThis.clearInterval(interval);
		};
	}, [
		getAccessToken,
		isLoading,
		isSignedIn,
		logout,
		mappedUser,
		setAuthFromWorkOS,
	]);

	return null;
}
/* eslint-enable import/no-default-export, import/no-named-export, oxc/no-async-await, unicorn/no-null, eslint/no-duplicate-imports, eslint/no-magic-numbers, eslint/max-lines-per-function, eslint/max-statements, eslint/sort-imports */
