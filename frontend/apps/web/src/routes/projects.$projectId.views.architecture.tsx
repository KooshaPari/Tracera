import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function ArchitectureView() {
	return <ItemsTableView />;
}

export const ARCHITECTURE_VIEW = ArchitectureView;

export const Route = createFileRoute("/projects/$projectId/views/architecture")(
	{
		component: ArchitectureView,
	},
);
