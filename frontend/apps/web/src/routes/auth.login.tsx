import { createFileRoute, redirect } from "@tanstack/react-router";
import { useEffect } from "react";
import { useAuth } from "@workos-inc/authkit-react";
import { useAuthStore } from "@/stores/authStore";
import { getReturnTo } from "@/lib/auth-utils";

export const Route = createFileRoute("/auth/login" as any)({
	component: LoginPage,
	beforeLoad: ({ search }: { search: Record<string, unknown> }) => {
		const { isAuthenticated } = useAuthStore.getState();
		// If already authenticated, redirect to home or returnTo
		if (isAuthenticated) {
			// Ensure returnTo is a string, not an object
			const returnToValue =
				typeof search === "object" && search !== null
					? (search["returnTo"] as string | undefined) || "/"
					: "/";
			const toPath = typeof returnToValue === "string" ? returnToValue : "/";
			throw redirect({ to: toPath });
		}
	},
});

function LoginPage() {
	const { signIn, user } = useAuth();
	const isSignedIn = !!user;

	useEffect(() => {
		// If already signed in, redirect to returnTo or home
		if (isSignedIn) {
			const returnToPath = getReturnTo(
				new URLSearchParams(window.location.search),
			);
			window.location.href = returnToPath;
			return;
		}

		// Immediately redirect to WorkOS AuthKit hosted UI
		// WorkOS handles everything: GitHub OAuth, user management, etc.
		// Configure GitHub and other providers in WorkOS dashboard
		// redirectUri is set on AuthKitProvider, so signIn() will use it automatically
		// getReturnTo is used elsewhere to determine where to go after auth

		// Call signIn() without parameters - it will use redirectUri from AuthKitProvider
		// The redirectUri in AuthKitProvider must match EXACTLY an entry in WorkOS Dashboard
		signIn();
	}, [signIn, isSignedIn]);

	// Minimal loading state - redirect happens immediately
	return (
		<div className="min-h-screen bg-gradient-to-br from-background to-background/50 flex items-center justify-center p-4">
			<div className="w-full max-w-md text-center space-y-4">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
				<p className="text-muted-foreground">
					Redirecting to authentication...
				</p>
			</div>
		</div>
	);
}
