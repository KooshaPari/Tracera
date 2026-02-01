import { createFileRoute } from "@tanstack/react-router";
import { ScenarioDetailView } from "@/views/ScenarioDetailView";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute(
	"/projects/$projectId/features/$featureId/scenarios/$scenarioId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: ScenarioDetailPage,
});

function ScenarioDetailPage() {
	return <ScenarioDetailView />;
}
