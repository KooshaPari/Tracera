import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { logger } from '@/lib/logger';
import { useAuth } from "@workos-inc/authkit-react";
import { Loader2, LogOut } from "lucide-react";
import { useEffect, useState } from "react";
import { AUTH_ROUTES } from "@/config/constants";
import { useAuthStore } from "@/stores/authStore";

/**
 * Logout page component
 * Handles clearing auth state and redirecting to login
 */
function LogoutPage() {
	const navigate = useNavigate();
	const { signOut } = useAuth();
	const logout = useAuthStore((state) => state.logout);
	const [isLoggingOut, setIsLoggingOut] = useState(true);

	useEffect(() => {
		const performLogout = async () => {
			try {
				// Clear local auth state first
				await logout();

				// Sign out from WorkOS
				// This will clear the WorkOS session and redirect to login
				await signOut();

				// Navigate to login page as fallback
				// (WorkOS signOut may handle redirect automatically)
				setTimeout(() => {
					navigate({ to: AUTH_ROUTES.LOGIN });
				}, 500);
			} catch (error) {
				logger.error("Logout error:", error);
				// Even if there's an error, navigate to login
				navigate({ to: AUTH_ROUTES.LOGIN });
			} finally {
				setIsLoggingOut(false);
			}
		};

		performLogout();
	}, [logout, signOut, navigate]);

	return (
		<div className="flex min-h-screen items-center justify-center bg-background">
			<div className="text-center space-y-6">
				<div className="relative mx-auto w-20 h-20">
					<div className="absolute inset-0 bg-primary/10 rounded-full animate-pulse" />
					<div className="relative flex items-center justify-center w-full h-full">
						{isLoggingOut ? (
							<Loader2 className="w-10 h-10 text-primary animate-spin" />
						) : (
							<LogOut className="w-10 h-10 text-primary" />
						)}
					</div>
				</div>

				<div className="space-y-2">
					<h2 className="text-2xl font-bold">
						{isLoggingOut ? "Signing out..." : "Signed out successfully"}
					</h2>
					<p className="text-muted-foreground">
						{isLoggingOut
							? "Clearing your session"
							: "Redirecting to login page"}
					</p>
				</div>
			</div>
		</div>
	);
}

export const Route = createFileRoute("/auth/logout")({
	component: LogoutPage,
});
