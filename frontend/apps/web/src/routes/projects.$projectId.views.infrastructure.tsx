import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function InfrastructureView() {
	return <ItemsTableView />;
}

export const INFRASTRUCTURE_VIEW = InfrastructureView;

export const Route = createFileRoute(
	"/projects/$projectId/views/infrastructure",
)({
	component: InfrastructureView,
});
