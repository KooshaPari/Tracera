import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Button } from "@tracertm/ui";
import { useAuth } from "@workos-inc/authkit-react";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { AUTH_ROUTES } from "@/config/constants";
import { getReturnTo } from "@/lib/auth-utils";
import { useAuthStore } from "@/stores/authStore";

/**
 * OAuth Callback Route for WorkOS Authentication
 *
 * This route handles the redirect from WorkOS after authentication.
 * It processes the OAuth callback, exchanges the authorization code for tokens,
 * updates the auth store, and redirects the user to their intended destination.
 *
 * Flow:
 * 1. WorkOS redirects here with auth code/state in URL
 * 2. WorkOS AuthKit SDK automatically handles token exchange
 * 3. AuthKitSync component syncs user/token to our auth store
 * 4. This component shows loading state and handles final redirect
 * 5. Redirects to returnTo URL or dashboard
 */

interface CallbackState {
	status: "loading" | "success" | "error";
	message: string;
}

function AuthCallback() {
	const navigate = useNavigate();
	const { user, isLoading } = useAuth();
	const setAuthFromWorkOS = useAuthStore((state) => state.setAuthFromWorkOS);
	const [state, setState] = useState<CallbackState>({
		status: "loading",
		message: "Processing authentication...",
	});

	useEffect(() => {
		// Get the URL search params for returnTo
		const searchParams = new URLSearchParams(window.location.search);
		const error = searchParams.get("error");
		const errorDescription = searchParams.get("error_description");

		// Handle OAuth errors from WorkOS
		if (error) {
			setState({
				status: "error",
				message: errorDescription || "Authentication failed. Please try again.",
			});
			return;
		}

		// WorkOS SDK handles the OAuth callback automatically
		// Wait for the SDK to complete authentication
		if (isLoading) {
			setState({
				status: "loading",
				message: "Verifying credentials...",
			});
			return;
		}

		// Check if authentication was successful
		if (!user) {
			// If no user after loading completes, something went wrong
			setState({
				status: "error",
				message: "Authentication failed. No user information received.",
			});
			return;
		}

		// Success! User is authenticated
		setState({
			status: "success",
			message: "Authentication successful! Redirecting...",
		});

		// Redirect to intended destination
		// AuthKitSync will handle the actual token sync
		const returnTo = getReturnTo(searchParams);

		// Use a small delay to show success state
		const redirectTimeout = setTimeout(() => {
			// Use navigate for proper router integration
			navigate({ to: returnTo });
		}, 500);

		return () => clearTimeout(redirectTimeout);
	}, [user, isLoading, navigate]);

	// Handle manual retry for error state
	const handleRetry = () => {
		setState({
			status: "loading",
			message: "Retrying authentication...",
		});

		// Clear any stale state and redirect to login
		setTimeout(() => {
			window.location.href = AUTH_ROUTES.LOGIN;
		}, 500);
	};

	// Handle cancel - redirect to dashboard
	const handleCancel = () => {
		window.location.href = "/home";
	};

	return (
		<div className="flex min-h-screen items-center justify-center bg-background p-4">
			<div className="max-w-md w-full bg-card border rounded-2xl p-8 shadow-xl space-y-6 animate-in fade-in zoom-in-95 duration-300">
				{/* Status Icon */}
				<div className="flex items-center justify-center">
					{state.status === "loading" && (
						<div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
							<Loader2 className="w-8 h-8 text-primary animate-spin" />
						</div>
					)}
					{state.status === "success" && (
						<div className="w-16 h-16 bg-green-500/10 rounded-full flex items-center justify-center animate-in zoom-in duration-300">
							<CheckCircle className="w-8 h-8 text-green-500" />
						</div>
					)}
					{state.status === "error" && (
						<div className="w-16 h-16 bg-destructive/10 rounded-full flex items-center justify-center animate-in zoom-in duration-300">
							<AlertCircle className="w-8 h-8 text-destructive" />
						</div>
					)}
				</div>

				{/* Status Message */}
				<div className="text-center space-y-2">
					<h1 className="text-2xl font-bold">
						{state.status === "loading" && "Authenticating"}
						{state.status === "success" && "Welcome Back"}
						{state.status === "error" && "Authentication Error"}
					</h1>
					<p className="text-muted-foreground">{state.message}</p>
				</div>

				{/* Error State Actions */}
				{state.status === "error" && (
					<div className="flex flex-col gap-3">
						<Button onClick={handleRetry} className="w-full">
							Try Again
						</Button>
						<Button variant="outline" onClick={handleCancel} className="w-full">
							Cancel
						</Button>
					</div>
				)}

				{/* Loading Indicator */}
				{state.status === "loading" && (
					<div className="space-y-2">
						<div className="w-full bg-muted rounded-full h-1.5 overflow-hidden">
							<div className="h-full bg-primary rounded-full animate-pulse-slow" />
						</div>
						<p className="text-xs text-center text-muted-foreground">
							This may take a few moments...
						</p>
					</div>
				)}

				{/* Success State - auto-redirecting */}
				{state.status === "success" && (
					<div className="text-center text-sm text-muted-foreground">
						Redirecting you now...
					</div>
				)}
			</div>
		</div>
	);
}

// TanStack Router file-based route export
export const Route = createFileRoute("/auth/callback")({
	component: AuthCallback,
	// This is a public route - no auth required
	beforeLoad: () => {
		// No-op - allow access without authentication
	},
});
