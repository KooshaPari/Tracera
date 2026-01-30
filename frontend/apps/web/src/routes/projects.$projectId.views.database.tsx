import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function DatabaseView() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/database",
	});
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">
						Database Schemas
					</h1>
					<p className="text-muted-foreground">
						Database designs, schemas, and migrations
					</p>
				</div>
			</div>

			<ItemsTableView projectId={projectId} view="database" />
		</div>
	);
}

export const DATABASE_VIEW = DatabaseView;

export const Route = createFileRoute("/projects/$projectId/views/database")({
	component: DatabaseView,
	loader: async () => {
		// ItemsTableView fetches its own data
		return {};
	},
});
