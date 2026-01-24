import { createFileRoute } from "@tanstack/react-router";
import { ReportsView } from "@/views/ReportsView";

export const Route = createFileRoute("/reports/")({
	component: ReportsComponent,
	loader: async () => {
		// ReportsView fetches its own data
		return {};
	},
});

function ReportsComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Project Reports</h1>
					<p className="text-muted-foreground">
						Comprehensive analytics and reporting across all project metrics
					</p>
				</div>
			</div>

			<ReportsView />
		</div>
	);
}
