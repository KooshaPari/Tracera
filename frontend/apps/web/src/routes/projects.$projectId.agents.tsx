import { createFileRoute } from "@tanstack/react-router";
import { AgentWorkflowView } from "@/views/AgentWorkflowView";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/agents")({
	beforeLoad: () => requireAuth(),
	component: AgentWorkflowView,
});
