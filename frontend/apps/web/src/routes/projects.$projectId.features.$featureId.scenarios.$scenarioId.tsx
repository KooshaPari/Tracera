import { createFileRoute } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";
import { ScenarioDetailView } from "@/views/ScenarioDetailView";

const ScenarioDetailPage = () => <ScenarioDetailView />;

export const Route = createFileRoute(
	"/projects/$projectId/features/$featureId/scenarios/$scenarioId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: ScenarioDetailPage,
});
