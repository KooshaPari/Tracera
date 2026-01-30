import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function InfrastructureView() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/infrastructure",
	});
	return <ItemsTableView projectId={projectId} view="infrastructure" />;
}

export const INFRASTRUCTURE_VIEW = InfrastructureView;

export const Route = createFileRoute(
	"/projects/$projectId/views/infrastructure" as any,
)({
	component: InfrastructureView,
});
