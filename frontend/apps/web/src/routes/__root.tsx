import {
	Link as RouterLink,
	createRootRoute,
	Outlet,
	useRouter,
	useLocation,
	redirect,
} from "@tanstack/react-router";
import { useEffect } from "react";
import { CommandPalette } from "@/components/CommandPalette";
import { Layout } from "@/components/layout/Layout";
import { Toaster } from "sonner";
import { AlertCircle, FileQuestion, Home, RefreshCcw } from "lucide-react";
import { Button } from "@tracertm/ui";
import { useAuthStore } from "@/stores/authStore";
import { isPublicRoute } from "@/lib/auth-utils";

// Not found component for 404 pages
function NotFoundComponent() {
	return (
		<div className="flex min-h-[80vh] items-center justify-center bg-background p-4 animate-in fade-in duration-500">
			<div className="max-w-md w-full text-center space-y-8">
				<div className="relative mx-auto w-24 h-24">
					<div className="absolute inset-0 bg-primary/10 rounded-full animate-pulse" />
					<div className="relative flex items-center justify-center w-full h-full">
						<FileQuestion className="w-12 h-12 text-primary" />
					</div>
				</div>

				<div className="space-y-2">
					<h1 className="text-4xl font-bold tracking-tight">
						Lost in the Matrix?
					</h1>
					<p className="text-muted-foreground">
						The node you're looking for doesn't exist in our current graph. It
						might have been pruned or moved.
					</p>
				</div>

				<div className="flex flex-col sm:flex-row gap-3 justify-center">
					<Button asChild className="gap-2">
						<RouterLink to="/">
							<Home className="w-4 h-4" />
							Back to Dashboard
						</RouterLink>
					</Button>
				</div>
			</div>
		</div>
	);
}

// Root error component to handle uncaught errors
function RootErrorComponent({ error }: { error: Error }) {
	const router = useRouter();

	return (
		<div className="flex min-h-[80vh] items-center justify-center bg-background p-4 animate-in zoom-in-95 duration-300">
			<div className="max-w-lg w-full bg-card border rounded-2xl p-8 shadow-xl space-y-8">
				<div className="flex items-center gap-4">
					<div className="flex-shrink-0 w-12 h-12 bg-destructive/10 rounded-xl flex items-center justify-center text-destructive">
						<AlertCircle className="w-6 h-6" />
					</div>
					<div>
						<h1 className="text-xl font-bold">System Anomaly Detected</h1>
						<p className="text-sm text-muted-foreground font-mono">
							CODE: {error.name || "UNHANDLED_EXCEPTION"}
						</p>
					</div>
				</div>

				<div className="bg-muted/50 rounded-xl p-4 font-mono text-sm border overflow-x-auto">
					<p className="text-destructive font-bold mb-2">Error Detail:</p>
					<p className="text-muted-foreground">
						{error.message === "fetch failed"
							? "Critical API Link Failure: Unable to establish connection to the backend cluster."
							: error.message}
					</p>
				</div>

				<div className="flex flex-col sm:flex-row gap-3">
					<Button onClick={() => router.invalidate()} className="flex-1 gap-2">
						<RefreshCcw className="w-4 h-4" />
						Sync & Retry
					</Button>
					<Button
						variant="outline"
						onClick={() => (window.location.href = "/")}
						className="flex-1 gap-2"
					>
						<Home className="w-4 h-4" />
						Terminal Return
					</Button>
				</div>
			</div>
		</div>
	);
}

const RootComponent = () => {
	const router = useRouter();
	const location = useLocation();
	const isAuthRoute = location.pathname.startsWith("/auth");
	const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

	// Prefetch likely navigation targets for faster perceived performance
	useEffect(() => {
		if (!isAuthenticated || isAuthRoute) return;

		// Prefetch common routes after initial render
		const prefetchRoutes = async () => {
			try {
				// Preload routes user is likely to navigate to
				await Promise.all(
					[
						router.preloadRoute({ to: "/projects" }),
						// Only preload graph if user is on a project-related page
						location.pathname.includes("/projects/") &&
							router.preloadRoute({
								to: "/projects/$projectId/views/$viewType",
								params: {
									projectId: location.pathname.split("/")[2] || "",
									viewType: "graph",
								},
							}),
					].filter(Boolean),
				);
			} catch {
				// Silently ignore prefetch errors
			}
		};

		// Delay prefetch to not block initial render
		const timeoutId = setTimeout(prefetchRoutes, 1000);
		return () => clearTimeout(timeoutId);
	}, [router, isAuthenticated, isAuthRoute, location.pathname]);

	return (
		<>
			<CommandPalette />
			{isAuthRoute ? <Outlet /> : <Layout />}
			<Toaster position="top-right" richColors />
		</>
	);
};

export const Route = createRootRoute({
	component: RootComponent,
	errorComponent: RootErrorComponent,
	notFoundComponent: NotFoundComponent,
	beforeLoad: ({ location }) => {
		const pathname = location.pathname;

		// CRITICAL: Always allow /auth/callback - don't redirect it EVER
		// WorkOS handles authentication and the callback page manages the flow
		// This must be checked FIRST before any auth state checks
		if (pathname === "/auth/callback") {
			console.log("[__root] Allowing /auth/callback to load");
			return; // Allow callback page to load unconditionally
		}

		// Get auth state - but be aware it might be stale during callback processing
		const { isAuthenticated, user } = useAuthStore.getState();

		console.log("[__root] Auth check:", {
			pathname,
			isAuthenticated,
			hasUser: !!user,
		});

		// If user is authenticated and trying to access auth routes, redirect to home
		if (isAuthenticated && user && isPublicRoute(pathname)) {
			console.log(
				"[__root] Authenticated user accessing auth route, redirecting to home",
			);
			throw redirect({ to: "/" });
		}

		// If user is not authenticated and trying to access protected routes, redirect to login
		if (!isAuthenticated && !isPublicRoute(pathname)) {
			console.log(
				"[__root] Unauthenticated user accessing protected route, redirecting to login",
			);
			// Build returnTo URL properly - location.search is an object in TanStack Router
			// Serialize it to a string for the returnTo parameter
			// IMPORTANT: Only include pathname, not query params (to avoid including auth codes)
			const returnTo = pathname;

			// Don't include search params in returnTo to avoid including auth codes
			// The original search params will be preserved by the redirect if needed

			throw redirect({
				to: "/auth/login",
				search: { returnTo },
			});
		}
	},
	head: () => ({
		meta: [
			{
				charSet: "utf-8",
			},
			{
				name: "viewport",
				content: "width=device-width, initial-scale=1",
			},
			{
				title: "TraceRTM - Multi-View Requirements Traceability System",
			},
			{
				name: "description",
				content:
					"Enterprise-grade requirements traceability and project management system with 16 professional views and intelligent CRUD operations.",
			},
		],
		links: [
			{
				rel: "icon",
				href: "/favicon.svg",
				type: "image/svg+xml",
			},
		],
	}),
});
