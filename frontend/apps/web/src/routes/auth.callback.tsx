import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useAuthStore } from "@/stores/authStore";
import { getReturnTo } from "@/lib/auth-utils";
import { XCircle } from "lucide-react";
import { Button } from "@tracertm/ui";

export const Route = createFileRoute("/auth/callback" as any)({
	component: AuthCallbackPage,
	// Don't validate search params - accept all query parameters as-is
	// This ensures the code parameter from WorkOS is preserved
	validateSearch: () => ({}),
	// Don't throw on invalid search - just render the component
	errorComponent: ({ error }) => {
		console.error("[AuthCallback Route] Error:", error);
		return <AuthCallbackPage />;
	},
});

/**
 * Auth callback page - handles WorkOS AuthKit redirects after authentication
 *
 * WorkOS redirects users here after successful authentication with a code parameter.
 * This page processes the callback via the backend (B2B flow) to avoid CORS issues
 * and then redirects to the appropriate page.
 */
function AuthCallbackPage() {
	const navigate = useNavigate();
	const [error, setError] = useState<string | null>(null);
	const [status, setStatus] = useState<string>("Initializing...");

	// Parse search params
	const [searchParams] = useState(() => {
		if (typeof window === "undefined")
			return { code: undefined, returnTo: undefined };
		const urlParams = new URLSearchParams(window.location.search);
		return {
			code: urlParams.get("code") || undefined,
			returnTo: urlParams.get("returnTo") || undefined,
		};
	});

	const setAuthFromWorkOS = useAuthStore((state) => state.setAuthFromWorkOS);
	const logout = useAuthStore((state) => state.logout);

	useEffect(() => {
		const code = searchParams.code;

		if (!code) {
			console.error("[AuthCallback] No code found in URL");
			setError("No authorization code found. Please try signing in again.");
			return;
		}

		const processCallback = async () => {
			try {
				setStatus("Exchanging code for session...");
				console.log("[AuthCallback] Sending code to backend for exchange...");

				const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
				const response = await fetch(`${API_URL}/api/v1/auth/callback`, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify({ code }),
				});

				if (!response.ok) {
					const errorData = await response
						.json()
						.catch(() => ({ detail: "Unknown error" }));
					throw new Error(
						errorData.detail || `Backend error: ${response.status}`,
					);
				}

				const authData = await response.json();
				console.log("[AuthCallback] Code exchange successful");

				setStatus("Syncing user session...");

				// Map backend response to our store format
				// The WorkOS SDK returns user info and tokens
				const { user, access_token } = authData;

				if (!user || !access_token) {
					throw new Error("Invalid response from auth backend");
				}

				const nameParts = [user.firstName, user.lastName].filter(Boolean);
				const mappedUser = {
					id: user.id,
					email: user.email,
					name: nameParts.length ? nameParts.join(" ") : user.email,
					avatar: user.profilePictureUrl,
					role: user.role,
					metadata: user.metadata,
				};

				// Set auth in store (includes auto-refresh initialization)
				const { setAuthFromWorkOS } = useAuthStore.getState();
				setAuthFromWorkOS(mappedUser, access_token);

				// Verify persistence
				setStatus("Finalizing...");
				let attempts = 0;
				while (attempts < 20) {
					const state = useAuthStore.getState();
					if (state.isAuthenticated && state.user) {
						break;
					}
					await new Promise((resolve) => setTimeout(resolve, 50));
					attempts++;
				}

				// Redirect
				const returnTo = getReturnTo(
					new URLSearchParams(window.location.search),
				);
				const targetPath =
					returnTo &&
					!returnTo.startsWith("/auth/") &&
					returnTo !== "/auth/callback"
						? returnTo
						: "/";

				console.log("[AuthCallback] Success! Navigating to:", targetPath);
				navigate({ to: targetPath, replace: true });
			} catch (err) {
				console.error("[AuthCallback] Processing failed:", err);
				setError(err instanceof Error ? err.message : "Authentication failed");
				logout();
			}
		};

		processCallback();
	}, [searchParams.code, navigate, logout, setAuthFromWorkOS]);

	// Show loading or error state
	return (
		<div className="min-h-screen bg-gradient-to-br from-background to-background/50 flex items-center justify-center p-4">
			<div className="w-full max-w-md text-center space-y-6">
				{error ? (
					<div className="space-y-4 animate-in fade-in zoom-in duration-300">
						<div className="bg-destructive/10 text-destructive p-4 rounded-xl border border-destructive/20 flex flex-col items-center gap-3">
							<XCircle className="h-10 w-10" />
							<div className="space-y-1">
								<p className="font-bold uppercase tracking-wider text-xs">
									Authentication Failed
								</p>
								<p className="text-sm opacity-90">{error}</p>
							</div>
						</div>
						<Button
							variant="outline"
							className="w-full rounded-xl"
							onClick={() => (window.location.href = "/auth/login")}
						>
							Return to Login
						</Button>
					</div>
				) : (
					<div className="space-y-4">
						<div className="relative">
							<div className="animate-spin rounded-full h-16 w-16 border-b-2 border-primary mx-auto" />
							<div className="absolute inset-0 flex items-center justify-center">
								<div className="h-2 w-2 rounded-full bg-primary/40 animate-ping" />
							</div>
						</div>
						<div className="space-y-2">
							<p className="text-lg font-bold tracking-tight">Authenticating</p>
							<p className="text-sm text-muted-foreground animate-pulse">
								{status}
							</p>
						</div>
						<div className="pt-4 flex justify-center gap-1.5">
							{[0, 1, 2].map((i) => (
								<div
									key={i}
									className="h-1.5 w-1.5 rounded-full bg-primary/20 animate-bounce"
									style={{ animationDelay: `${i * 0.15}s` }}
								/>
							))}
						</div>
					</div>
				)}
			</div>
		</div>
	);
}
