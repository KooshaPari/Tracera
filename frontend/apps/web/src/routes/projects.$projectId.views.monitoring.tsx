import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function MonitoringView() {
	return <ItemsTableView />;
}

export const MONITORING_VIEW = MonitoringView;

export const Route = createFileRoute("/projects/$projectId/views/monitoring")({
	component: MonitoringView,
});
