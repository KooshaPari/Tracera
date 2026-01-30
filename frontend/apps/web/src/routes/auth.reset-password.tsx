import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

export const Route = createFileRoute("/auth/reset-password" as any)({
	component: ResetPasswordPage,
	beforeLoad: () => {
		// Reset password is handled by WorkOS hosted UI
		// Just redirect to login where WorkOS handles password reset
	},
});

function ResetPasswordPage() {
	const navigate = useNavigate();

	useEffect(() => {
		// WorkOS handles password resets through their hosted UI
		// Redirect to login - WorkOS hosted UI has "Forgot password" functionality
		navigate({ to: "/auth/login" });
	}, [navigate]);

	// Minimal loading state - redirect happens immediately
	return (
		<div className="min-h-screen bg-gradient-to-br from-background to-background/50 flex items-center justify-center p-4">
			<div className="w-full max-w-md text-center space-y-4">
				<div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto" />
				<p className="text-muted-foreground">Redirecting to sign in...</p>
			</div>
		</div>
	);
}
