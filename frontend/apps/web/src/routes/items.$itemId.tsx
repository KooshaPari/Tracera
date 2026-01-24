import { createFileRoute } from "@tanstack/react-router";
import { ItemDetailView } from "@/views/ItemDetailView";

function ItemDetailComponent() {
	return <ItemDetailView />;
}

export const Route = createFileRoute("/items/$itemId")({
	component: ItemDetailComponent,
	loader: async () => {
		// ItemDetailView fetches its own data
		return {};
	},
	errorComponent: () => (
		<div className="flex flex-col items-center justify-center min-h-screen bg-background text-foreground">
			<h1 className="text-2xl font-bold text-destructive mb-4">
				Item Not Found
			</h1>
			<p className="text-muted-foreground">
				The item you're looking for doesn't exist or has been moved.
			</p>
		</div>
	),
});
