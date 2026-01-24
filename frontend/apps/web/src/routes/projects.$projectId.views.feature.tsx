import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function FeatureView() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Features</h1>
					<p className="text-muted-foreground">
						Manage feature requirements and user stories
					</p>
				</div>
			</div>

			<ItemsTableView />
		</div>
	);
}

export const FEATURE_VIEW = FeatureView;

export const Route = createFileRoute("/projects/$projectId/views/feature")({
	component: FeatureView,
	loader: async () => {
		// ItemsTableView fetches its own data
		return {};
	},
});
