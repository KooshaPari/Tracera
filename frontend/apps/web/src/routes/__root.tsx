import { createRootRoute, Outlet, useRouter } from "@tanstack/react-router";
import { CommandPalette } from "@/components/CommandPalette";

// Not found component for 404 pages
function NotFoundComponent() {
	return (
		<div className="flex min-h-screen items-center justify-center bg-background p-4">
			<div className="max-w-md text-center space-y-4">
				<h1 className="text-6xl font-bold text-muted-foreground">404</h1>
				<h2 className="text-2xl font-semibold">Page Not Found</h2>
				<p className="text-muted-foreground">
					The page you're looking for doesn't exist or has been moved.
				</p>
				<a
					href="/"
					className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
				>
					Go Home
				</a>
			</div>
		</div>
	);
}

// Root error component to handle uncaught errors
function RootErrorComponent({ error }: { error: Error }) {
	const router = useRouter();

	return (
		<div className="flex min-h-screen items-center justify-center bg-background p-4">
			<div className="max-w-md text-center space-y-4">
				<h1 className="text-2xl font-bold text-destructive">
					Something went wrong
				</h1>
				<p className="text-muted-foreground">
					{error.message === "fetch failed"
						? "Unable to connect to the API server. Please ensure the backend is running."
						: error.message}
				</p>
				<div className="flex justify-center gap-4">
					<button
						type="button"
						onClick={() => router.invalidate()}
						className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
					>
						Retry
					</button>
					<button
						type="button"
						onClick={() => (window.location.href = "/")}
						className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/90"
					>
						Go Home
					</button>
				</div>
			</div>
		</div>
	);
}

const RootComponent = () => {
	return (
		<div className="relative flex min-h-screen bg-background">
			<div className="flex-1">
				<CommandPalette />
				<Outlet />
			</div>
		</div>
	);
};

export const Route = createRootRoute({
	component: RootComponent,
	errorComponent: RootErrorComponent,
	notFoundComponent: NotFoundComponent,
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
