/**
 * Protected route wrapper component.
 * Redirects to login if user is not authenticated.
 * Uses WorkOS AuthKit for authentication state.
 */

/* eslint-disable import/no-default-export, import/no-named-export, eslint/no-duplicate-imports, eslint/sort-imports, react/jsx-filename-extension */
import { useAuth } from "@workos-inc/authkit-react";
import type { ReactNode } from "react";
import { useEffect } from "react";

interface ProtectedRouteProps {
	children: ReactNode;
	requireAccount?: boolean;
}

export default function ProtectedRoute({
	children,
}: ProtectedRouteProps): ReactNode {
	const { user, isLoading } = useAuth();

	useEffect(() => {
		// Wait for auth check to complete before redirecting
		if (!isLoading && !user) {
			// Not authenticated, redirect to login
			globalThis.location.href = "/auth/login";
		}
	}, [user, isLoading]);

	// Show loading state while checking authentication
	if (isLoading) {
		return (
			<div className="flex min-h-screen items-center justify-center">
				<div className="text-center">
					<p className="text-lg">Loading...</p>
				</div>
			</div>
		);
	}

	// If not authenticated, return nothing (will redirect via useEffect)
	if (!user) {
		return;
	}

	return children;
}
/* eslint-enable import/no-default-export, import/no-named-export, eslint/no-duplicate-imports, eslint/sort-imports, react/jsx-filename-extension */
