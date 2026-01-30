/**
 * Protected route wrapper component.
 * Redirects to login if user is not authenticated.
 */

import { useEffect } from "react";
import { useNavigate, useLocation } from "@tanstack/react-router";
import { useAuthStore } from "@/stores/authStore";

export interface ProtectedRouteProps {
	children: React.ReactNode;
	requireAccount?: boolean;
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
	const navigate = useNavigate();
	const location = useLocation();
	const { isAuthenticated, user } = useAuthStore();

	useEffect(() => {
		if (!isAuthenticated || !user) {
			// Store the attempted location for redirect after login
			const returnTo = location.pathname + location.search;
			navigate({
				to: "/auth/login",
				search: { returnTo },
			});
		}
	}, [isAuthenticated, user, navigate, location]);

	if (!isAuthenticated || !user) {
		return null; // Will redirect
	}

	return <>{children}</>;
}
