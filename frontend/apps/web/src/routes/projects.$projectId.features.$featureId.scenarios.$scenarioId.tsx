import { createFileRoute } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";
import { ScenarioDetailView } from "@/views/ScenarioDetailView";

export const Route = createFileRoute(
	"/projects/$projectId/features/$featureId/scenarios/$scenarioId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: ScenarioDetailPage,
});

const ScenarioDetailPage = () => <ScenarioDetailView />;
