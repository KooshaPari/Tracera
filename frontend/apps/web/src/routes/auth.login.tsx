import { createFileRoute } from "@tanstack/react-router";
import { useAuth } from "@workos-inc/authkit-react";
import { useEffect } from "react";

/**
 * Login redirect handler
 * Automatically redirects to WorkOS hosted UI for authentication.
 * No custom UI - delegates fully to WorkOS AuthKit.
 */
function Login() {
	const { user, isLoading, signIn } = useAuth();

	useEffect(() => {
		if (user && !isLoading) {
			// Already logged in, redirect to dashboard
			globalThis.location.href = "/home";
		} else if (!isLoading && !user) {
			// Not logged in, immediately redirect to WorkOS
			undefined;
		}
	}, [user, isLoading, signIn]);

	// Minimal loading UI (shown briefly during redirect)
	return (
		<div className="flex min-h-screen items-center justify-center">
			<div className="text-center">
				<p className="text-lg">Redirecting to sign in...</p>
			</div>
		</div>
	);
}

export const Route = createFileRoute("/auth/login")({
	component: Login,
});
