import { createFileRoute } from "@tanstack/react-router";
import { Suspense, lazy } from "react";

const ProjectMappingGraphView = lazy(() =>
	import("@/views/ProjectMappingGraphView").then((m) => ({
		default: m.ProjectMappingGraphView,
	})),
);

export function WireframeView() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">Wireframes & UI</h1>
					<p className="text-muted-foreground">UI/UX designs and wireframes</p>
				</div>
			</div>

			<Suspense
				fallback={
					<div className="flex items-center justify-center h-64">
						Loading wireframes...
					</div>
				}
			>
				<ProjectMappingGraphView />
			</Suspense>
		</div>
	);
}

export const WIREFRAME_VIEW = WireframeView;

export const Route = createFileRoute("/projects/$projectId/views/wireframe")({
	component: WireframeView,
	loader: async () => ({}),
});
