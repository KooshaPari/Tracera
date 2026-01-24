import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function WireframeView() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Wireframes & UI</h1>
					<p className="text-muted-foreground">UI/UX designs and wireframes</p>
				</div>
			</div>

			<ItemsTableView />
		</div>
	);
}

export const WIREFRAME_VIEW = WireframeView;

export const Route = createFileRoute("/projects/$projectId/views/wireframe")({
	component: WireframeView,
	loader: async () => {
		// ItemsTableView fetches its own data
		return {};
	},
});
