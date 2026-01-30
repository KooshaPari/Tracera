import { useAuth } from "@workos-inc/authkit-react";
import { useEffect, useMemo, useRef } from "react";
import { useAuthStore, type User } from "../../stores/authStore";
import { getReturnTo } from "../../lib/auth-utils";

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

				// Handle redirect after successful authentication
				// BUT: Don't handle redirects on /auth/callback - let the callback page handle it
				// This prevents double redirects and race conditions
				if (
					!hasRedirectedRef.current &&
					window.location.pathname.startsWith("/auth") &&
					window.location.pathname !== "/auth/callback"
				) {
					hasRedirectedRef.current = true;
					const searchParams = new URLSearchParams(window.location.search);
					const returnTo = getReturnTo(searchParams);
					if (
						returnTo !== "/auth/login" &&
						returnTo !== "/auth/register" &&
						returnTo !== "/auth/callback"
					) {
						window.location.href = returnTo;
					} else {
						window.location.href = "/";
					}
				}
			} catch (error) {
				console.error("Failed to sync AuthKit token:", error);
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
