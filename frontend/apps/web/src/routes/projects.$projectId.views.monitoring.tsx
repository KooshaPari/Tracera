import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function MonitoringView() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/monitoring",
	});
	return <ItemsTableView projectId={projectId} view="monitoring" />;
}

export const MONITORING_VIEW = MonitoringView;

export const Route = createFileRoute("/projects/$projectId/views/monitoring")({
	component: MonitoringView,
});
