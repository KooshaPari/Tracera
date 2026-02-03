import { createFileRoute, useParams } from "@tanstack/react-router";
import { FullScreenPage } from "@/components/layout/FullScreenPage";
import { useItem } from "@/hooks/useItems";
import { requireAuth } from "@/lib/route-guards";
import { ItemDetailRouter } from "@/views/details";

function ItemDetailComponent() {
	const { projectId, itemId } = useParams({ strict: false });
	const projectIdValue = projectId ?? "";
	const itemIdValue = itemId ?? "";
	const { data: item, isLoading, error } = useItem(itemIdValue);

	if (isLoading) {
		return (
			<div className="flex items-center justify-center min-h-screen bg-background">
				<div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
			</div>
		);
	}

	if (error || !item) {
		return (
			<FullScreenPage>
				<div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
					<h1 className="text-2xl font-bold text-destructive mb-4">
						Item Not Found
					</h1>
					<p className="text-muted-foreground">
						The item you're looking for doesn't exist.
					</p>
				</div>
			</FullScreenPage>
		);
	}

	return <ItemDetailRouter item={item} projectId={projectIdValue} />;
}

export const Route = createFileRoute(
	"/projects/$projectId/views/$viewType/$itemId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: ItemDetailComponent,
	errorComponent: () => (
		<FullScreenPage>
			<div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
				<h1 className="text-2xl font-bold text-destructive mb-4">
					Item Not Found
				</h1>
				<p className="text-muted-foreground">
					The item you're looking for doesn't exist.
				</p>
			</div>
		</FullScreenPage>
	),
	loader: async () => {
		// ItemDetailView fetches its own data
		return {};
	},
});
