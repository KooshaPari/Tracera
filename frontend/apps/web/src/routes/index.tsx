import { createFileRoute, Navigate } from "@tanstack/react-router";
import { useIsAuthenticated } from "@/hooks/useAuth";
import { LandingPage } from "@/views";

function IndexComponent() {
	const isAuthenticated = useIsAuthenticated();
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

	if (isAuthenticated || hasStoredToken || isE2E) {
		return <Navigate to="/home" />;
	}

	return <LandingPage />;
}

export const Route = createFileRoute("/")({
	component: IndexComponent,
});
