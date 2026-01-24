import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function TestView() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Test Coverage</h1>
					<p className="text-muted-foreground">
						Test cases and coverage metrics
					</p>
				</div>
			</div>

			<ItemsTableView />
		</div>
	);
}

export const TEST_VIEW = TestView;

export const Route = createFileRoute("/projects/$projectId/views/test")({
	component: TestView,
	loader: async () => {
		// ItemsTableView fetches its own data
		return {};
	},
});
