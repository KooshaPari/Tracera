import { createFileRoute } from "@tanstack/react-router";
import { AgentsView } from "@/views/AgentsView";

export const Route = createFileRoute("/agents/")({
	component: AgentsComponent,
	loader: async () => {
		// Load agents and projects for the view
		return {};
	},
});

function AgentsComponent() {
	return (
		<div className="flex-1 p-6 space-y-6">
			<AgentsView />
		</div>
	);
}
