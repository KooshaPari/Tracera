import { createFileRoute } from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import { ChunkLoadingSkeleton } from "@/lib/lazy-loading";

const GraphView = lazy(() =>
	import("@/views/GraphView").then((m) => ({ default: m.GraphView })),
);

export const Route = createFileRoute("/graph/")({
	component: GraphComponent,
	loader: async () => {
		// GraphView fetches its own data
		return {};
	},
});

function GraphComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">
						Graph Visualization
					</h1>
					<p className="text-muted-foreground">
						Interactive graph of project relationships and dependencies
					</p>
				</div>
			</div>

			<Suspense
				fallback={
					<ChunkLoadingSkeleton message="Loading graph visualization..." />
				}
			>
				<GraphView />
			</Suspense>
		</div>
	);
}
