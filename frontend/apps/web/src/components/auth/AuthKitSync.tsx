import { useAuth } from "@workos-inc/authkit-react";
import { logger } from '@/lib/logger';
import { useEffect, useMemo, useRef } from "react";
import { AUTH_ROUTES } from "../../config/constants";
import { getReturnTo, isPublicRoute } from "../../lib/auth-utils";
import { type User, useAuthStore } from "../../stores/authStore";

const REFRESH_INTERVAL_MS = 5 * 60 * 1000;

const toUser = (workosUser: any | null): User | null => {
	if (!workosUser) return null;
	const nameParts = [workosUser.firstName, workosUser.lastName].filter(Boolean);
	return {
		id: workosUser.id,
		email: workosUser.email,
		name: nameParts.length ? nameParts.join(" ") : workosUser.email,
		avatar: workosUser.profilePictureUrl,
		role: workosUser.role,
		metadata: workosUser.metadata,
	};
};

export function AuthKitSync() {
	const { user, isLoading, getAccessToken } = useAuth();
	const setAuthFromWorkOS = useAuthStore((state) => state.setAuthFromWorkOS);
	const logout = useAuthStore((state) => state.logout);
	const hasRedirectedRef = useRef(false);

	const mappedUser = useMemo(() => toUser(user ?? null), [user]);
	const isSignedIn = !!user;

	useEffect(() => {
		let active = true;

		const syncToken = async () => {
			if (!isSignedIn) {
				logout();
				return;
			}

			try {
				const token = await getAccessToken();
				if (!active) return;
				setAuthFromWorkOS(mappedUser, token ?? null);
				// Hydrate user from /auth/me only when we have a token (avoids 401)
				if (token?.trim()) {
					await useAuthStore.getState().validateSession();
				}

				// Handle redirect after successful authentication
				// IMPORTANT: Don't redirect on /auth/callback - WorkOS handles that flow
				// Only redirect when user is authenticated on other auth pages (login/register)
				const currentPath = window.location.pathname;

				if (
					!hasRedirectedRef.current &&
					isPublicRoute(currentPath) &&
					currentPath !== AUTH_ROUTES.CALLBACK
				) {
					hasRedirectedRef.current = true;
					const searchParams = new URLSearchParams(window.location.search);
					const returnTo = getReturnTo(searchParams);

					// getReturnTo already filters out auth routes and returns "/home" as default
					// If returnTo is "/home", user will be sent to dashboard
					// Otherwise, they'll be sent to their intended destination
					window.location.href = returnTo;
				}
			} catch (error) {
				logger.error("Failed to sync AuthKit token:", error);
				logout();
			}
		};

		if (!isLoading) {
			syncToken();
		}

		const interval = window.setInterval(syncToken, REFRESH_INTERVAL_MS);
		return () => {
			active = false;
			window.clearInterval(interval);
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
