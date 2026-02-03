import { useEffect } from "react";
import { createFileRoute, useParams, useNavigate } from "@tanstack/react-router";
import { useItem } from "@/hooks/useItems";
import { requireAuth } from "@/lib/route-guards";

/**
 * Redirect handler for old item URLs (/items/:itemId)
 * Maintains backward compatibility by redirecting to new format:
 * /projects/:projectId/views/:viewType/:itemId
 */
const ItemRedirectComponent = () => {
	const params = useParams();
	const navigate = useNavigate();
	const { data: item, error, isLoading } = useItem(params.itemId);

	useEffect(() => {
		if (item) {
			// Redirect to new URL format
			navigate(`/projects/${item.projectId}/views/items/${item.id}`);
		}
	}, [item, navigate]);

	if (isLoading) {
		return (
			<div className="flex flex-col items-center justify-center min-h-screen bg-background">
				<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
				<p className="mt-4 text-sm text-muted-foreground">Redirecting...</p>
			</div>
		);
	}

	if (error || !item) {
		return (
			<div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
				<h1 className="text-2xl font-bold text-destructive mb-4">
					Item Not Found
				</h1>
				<p className="text-muted-foreground mb-6">
					The item you're looking for doesn't exist or has been deleted.
				</p>
				<a
					href="/projects"
					className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
				>
					Back to Projects
				</a>
			</div>
		);
	}

	// Show nothing while redirecting
	return null;
};

export const Route = createFileRoute("/items/$itemId")({
	beforeLoad: () => requireAuth(),
	component: ItemRedirectComponent,
});
