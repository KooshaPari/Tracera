import { createFileRoute, redirect } from "@tanstack/react-router";
import { useAuthStore } from "@/stores/authStore";
import { useEffect } from "react";

export const Route = createFileRoute("/auth/logout" as any)({
	component: LogoutPage,
	beforeLoad: async () => {
		const logout = useAuthStore.getState().logout;
		const workosEnabled = Boolean(import.meta.env["VITE_WORKOS_CLIENT_ID"]);

		// Logout from auth store
		logout();

		// Clear localStorage
		if (typeof window !== "undefined") {
			localStorage.removeItem("authToken");
			localStorage.removeItem("user");
			localStorage.removeItem("rememberMe");
			localStorage.removeItem("tracertm-auth-store");
		}

		// If WorkOS is not enabled, redirect immediately
		if (!workosEnabled) {
			throw redirect({ to: "/auth/login" });
		}
	},
});

function LogoutPage() {
	const logout = useAuthStore.getState().logout;
	const workosEnabled = Boolean(import.meta.env["VITE_WORKOS_CLIENT_ID"]);

	useEffect(() => {
		const performLogout = async () => {
			try {
				// WorkOS logout is handled by AuthKitSync component
				// Just perform local logout here

				// Ensure local logout
				logout();

				// Clear localStorage
				localStorage.removeItem("authToken");
				localStorage.removeItem("user");
				localStorage.removeItem("rememberMe");
				localStorage.removeItem("tracertm-auth-store");

				// Redirect to login
				window.location.href = "/auth/login";
			} catch (error) {
				console.error("Logout error:", error);
				// Still redirect even if logout fails
				window.location.href = "/auth/login";
			}
		};

		performLogout();
	}, [workosEnabled, logout]);

	return (
		<div className="flex min-h-screen items-center justify-center">
			<div className="text-center">
				<p className="text-muted-foreground">Logging out...</p>
			</div>
		</div>
	);
}
