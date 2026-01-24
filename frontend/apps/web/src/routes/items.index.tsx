import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export const Route = createFileRoute("/items/")({
	component: ItemsComponent,
	loader: async () => {
		// ItemsTableView fetches its own data
		return {};
	},
});

function ItemsComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">All Items</h1>
					<p className="text-muted-foreground">
						Browse and manage all project items across all views
					</p>
				</div>
			</div>

			<ItemsTableView />
		</div>
	);
}
