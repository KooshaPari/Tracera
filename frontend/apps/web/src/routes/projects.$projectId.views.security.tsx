import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function SecurityView() {
	return <ItemsTableView />;
}

export const SECURITY_VIEW = SecurityView;

export const Route = createFileRoute("/projects/$projectId/views/security")({
	component: SecurityView,
});
