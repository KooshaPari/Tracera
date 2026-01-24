import { createFileRoute } from "@tanstack/react-router";
import { TraceabilityMatrixView } from "@/views/TraceabilityMatrixView";

export const Route = createFileRoute("/matrix/traceability/")({
	component: MatrixComponent,
	loader: async () => {
		// TraceabilityMatrixView fetches its own data
		return {};
	},
});

function MatrixComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<div className="flex items-center justify-between">
				<div>
					<h1 className="text-3xl font-bold tracking-tight">
						Traceability Matrix
					</h1>
					<p className="text-muted-foreground">
						Comprehensive traceability relationships between items and views
					</p>
				</div>
			</div>

			<TraceabilityMatrixView />
		</div>
	);
}
