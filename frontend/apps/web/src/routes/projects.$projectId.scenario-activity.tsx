import { createFileRoute } from "@tanstack/react-router";
import { ScenarioActivityView } from "@/views/ScenarioActivityView";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/scenario-activity")({
	beforeLoad: () => requireAuth(),
	component: ScenarioActivityView,
});
