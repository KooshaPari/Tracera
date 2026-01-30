import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function ApiView() {
	const { projectId } = useParams({ from: "/projects/$projectId/views/api" });
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">API Endpoints</h1>
					<p className="text-muted-foreground">
						REST API contracts and specifications
					</p>
				</div>
			</div>

			<ItemsTableView projectId={projectId} view="api" />
		</div>
	);
}

export const API_VIEW = ApiView;

export const Route = createFileRoute("/projects/$projectId/views/api")({
	component: ApiView,
	loader: async () => {
		// ItemsTableView fetches its own data
		return {};
	},
});
