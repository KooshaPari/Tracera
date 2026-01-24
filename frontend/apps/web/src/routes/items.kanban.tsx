import { createFileRoute } from "@tanstack/react-router";
import { ItemsKanbanView } from "@/views/ItemsKanbanView";

export const Route = createFileRoute("/items/kanban")({
	component: KanbanComponent,
	loader: async () => {
		// ItemsKanbanView fetches its own data
		return {};
	},
});

function KanbanComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Kanban Board</h1>
					<p className="text-muted-foreground">
						Visual workflow management for all project items
					</p>
				</div>
			</div>

			<ItemsKanbanView />
		</div>
	);
}
