import { createFileRoute } from "@tanstack/react-router";
import { Suspense, lazy } from "react";
import { ChunkLoadingSkeleton } from "@/lib/lazy-loading";
import { logger } from "@/lib/logger";
import { requireAuth } from "@/lib/route-guards";

const ProjectsListView = lazy(() =>
	import("@/views/ProjectsListView").then((m) => {
		const Comp = m.ProjectsListView;
		if (Comp == null) {
			logger.error("ProjectsListView module did not export a component", m);
			return {
				default: () => (
					<div className="p-6 text-destructive" role="alert">
						Failed to load projects list.
					</div>
				),
			};
		}
		return { default: Comp };
	}),
);

export const Route = createFileRoute("/projects/")({
	beforeLoad: () => requireAuth(),
	component: ProjectsComponent,
	loader: async () => ({}),
});

function ProjectsComponent() {
	return (
		<Suspense fallback={<ChunkLoadingSkeleton message="Loading projects..." />}>
			<ProjectsListView />
		</Suspense>
	);
}
