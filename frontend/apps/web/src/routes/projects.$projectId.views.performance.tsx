import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function PerformanceView() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/performance",
	});
	return <ItemsTableView projectId={projectId} view="performance" />;
}

export const PERFORMANCE_VIEW = PerformanceView;

export const Route = createFileRoute("/projects/$projectId/views/performance")({
	component: PerformanceView,
});
