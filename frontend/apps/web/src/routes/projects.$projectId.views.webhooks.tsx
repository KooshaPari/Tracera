import { createFileRoute, useParams } from "@tanstack/react-router";
import { WebhookIntegrationsView } from "@/pages/projects/views/WebhookIntegrationsView";

export function WebhooksViewRoute() {
	const { projectId } = useParams({ from: "/projects/$projectId" });
	return <WebhookIntegrationsView projectId={projectId} />;
}

export const Route = createFileRoute(
	"/projects/$projectId/views/webhooks" as any,
)({
	component: WebhooksViewRoute,
	loader: async () => ({}),
});
