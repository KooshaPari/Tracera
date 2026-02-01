import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

/**
 * Redirect handler for old graph URL (/graph)
 * Redirects to projects page where users can select a project to view its graph
 */
function GraphRedirectComponent() {
	const navigate = useNavigate();

	useEffect(() => {
		// Redirect to projects list with a hint to select a project
		navigate({
			to: "/projects",
			replace: true, // Replace history entry to prevent back button issues
		});
	}, [navigate]);

	return (
		<div className="flex flex-col items-center justify-center min-h-screen bg-background">
			<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
			<p className="mt-4 text-sm text-muted-foreground">
				Redirecting to projects...
			</p>
			<p className="mt-2 text-xs text-muted-foreground">
				Please select a project to view its graph
			</p>
		</div>
	);
}

export const Route = createFileRoute("/graph/")({
	component: GraphRedirectComponent,
});
