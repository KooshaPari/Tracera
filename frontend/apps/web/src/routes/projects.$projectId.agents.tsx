import { createFileRoute } from "@tanstack/react-router";
import { AgentWorkflowView } from "@/views/AgentWorkflowView";

export const Route = createFileRoute("/projects/$projectId/agents")({
	component: AgentWorkflowView,
});
