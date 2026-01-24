import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function PerformanceView() {
	return <ItemsTableView />;
}

export const PERFORMANCE_VIEW = PerformanceView;

export const Route = createFileRoute("/projects/$projectId/views/performance")({
	component: PerformanceView,
});
