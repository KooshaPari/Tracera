import { createFileRoute } from "@tanstack/react-router";
import { ImpactAnalysisView } from "@/views/ImpactAnalysisView";

export const Route = createFileRoute("/impact/")({
	component: ImpactComponent,
	loader: async () => {
		// ImpactAnalysisView fetches its own data
		return {};
	},
});

function ImpactComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Impact Analysis</h1>
					<p className="text-muted-foreground">
						Analyze dependencies and cascading effects across your project
					</p>
				</div>
			</div>

			<ImpactAnalysisView />
		</div>
	);
}
