import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function CodeView() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">
						Code Implementation
					</h1>
					<p className="text-muted-foreground">Source code implementations</p>
				</div>
			</div>

			<ItemsTableView />
		</div>
	);
}

export const CODE_VIEW = CodeView;

export const Route = createFileRoute("/projects/$projectId/views/code")({
	component: CodeView,
	loader: async () => {
		// ItemsTableView fetches its own data
		return {};
	},
});
