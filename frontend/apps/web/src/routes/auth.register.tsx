import { createFileRoute } from "@tanstack/react-router";
import { useAuth } from "@workos-inc/authkit-react";
import { useEffect } from "react";

/**
 * Register redirect handler
 * Automatically redirects to WorkOS hosted UI for registration.
 * No custom UI - delegates fully to WorkOS AuthKit.
 */
function Register() {
	const { user, signUp } = useAuth();

	useEffect(() => {
		if (user) {
			// Already logged in, redirect to home
			globalThis.location.href = "/home";
		} else {
			// Not logged in, immediately redirect to WorkOS signup
			undefined;
		}
	}, [user, signUp]);

	// Minimal loading UI (shown briefly during redirect)
	return (
		<div className="flex min-h-screen items-center justify-center">
			<div className="text-center">
				<p className="text-lg">Redirecting to sign up...</p>
			</div>
		</div>
	);
}

export const Route = createFileRoute("/auth/register")({
	component: Register,
});
