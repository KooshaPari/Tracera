import { createFileRoute, Navigate } from "@tanstack/react-router";
import { useIsAuthenticated } from "@/hooks/useAuth";
import { LandingPage } from "@/views";

export const Route = createFileRoute("/")({
	component: IndexComponent,
});

const hasStoredTokenOrIsE2E = (): boolean => {
	if (typeof globalThis.window === "undefined") {
		return false;
	}

	if (localStorage?.getItem("auth_token") ||
		localStorage?.getItem("authToken") ||
		localStorage?.getItem("tracertm-auth-store")) {
		return true;
	}

	if ((globalThis as { __E2E__?: boolean }).__E2E__ || navigator?.webdriver) {
		return true;
	}

	return false;
};

const IndexComponent = () => {
	const isAuthenticated = useIsAuthenticated();

	if (isAuthenticated || hasStoredTokenOrIsE2E()) {
		return <Navigate to="/home" />;
	}

	return <LandingPage />;
};
