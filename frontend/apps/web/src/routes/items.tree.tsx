import { createFileRoute } from "@tanstack/react-router";
import { ItemsTreeView } from "@/views/ItemsTreeView";

export const Route = createFileRoute("/items/tree")({
	component: TreeComponent,
	loader: async () => {
		// ItemsTreeView fetches its own data
		return {};
	},
});

function TreeComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Item Hierarchy</h1>
					<p className="text-muted-foreground">
						Hierarchical view of project relationships and dependencies
					</p>
				</div>
			</div>

			<ItemsTreeView />
		</div>
	);
}
