import { createFileRoute, redirect } from "@tanstack/react-router";
import { useEffect } from "react";
import { useAuth } from "@workos-inc/authkit-react";
import { useAuthStore } from "@/stores/authStore";

export const Route = createFileRoute("/auth/register" as any)({
	component: RegisterPage,
	beforeLoad: () => {
		const { isAuthenticated } = useAuthStore.getState();
		// If already authenticated, redirect to home
		if (isAuthenticated) {
			throw redirect({ to: "/" });
		}
	},
});

function RegisterPage() {
	const { signUp, user } = useAuth();
	const isSignedIn = !!user;

	useEffect(() => {
		// If already signed in, redirect to home
		if (isSignedIn) {
			window.location.href = "/";
			return;
		}

		// Immediately redirect to WorkOS AuthKit hosted UI
		// WorkOS handles everything: GitHub OAuth, user management, etc.
		// Configure GitHub and other providers in WorkOS dashboard
		// redirectUri is set on AuthKitProvider, so signUp() will use it automatically

		// Call signUp() without parameters - it will use redirectUri from AuthKitProvider
		// The redirectUri in AuthKitProvider must match EXACTLY an entry in WorkOS Dashboard
		signUp();
	}, [signUp, isSignedIn]);

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
