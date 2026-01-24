import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function DependencyView() {
	return <ItemsTableView />;
}

export const DEPENDENCY_VIEW = DependencyView;

export const Route = createFileRoute("/projects/$projectId/views/dependency")({
	component: DependencyView,
});
