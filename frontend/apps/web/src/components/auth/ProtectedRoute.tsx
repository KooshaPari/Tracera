/**
 * Protected route wrapper component.
 * Redirects to login if user is not authenticated.
 * Uses WorkOS AuthKit for authentication state.
 */

import { useAuth } from "@workos-inc/authkit-react";
import { useEffect } from "react";

export interface ProtectedRouteProps {
	children: React.ReactNode;
	requireAccount?: boolean;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
	const { user, isLoading } = useAuth();

	useEffect(() => {
		// Wait for auth check to complete before redirecting
		if (!isLoading && !user) {
			// Not authenticated, redirect to login
			window.location.href = "/auth/login";
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

	// If not authenticated, return null (will redirect via useEffect)
	if (!user) {
		return null;
	}

	return <>{children}</>;
}
