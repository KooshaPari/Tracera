import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function SecurityView() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/security",
	});
	return <ItemsTableView projectId={projectId} view="security" />;
}

export const SECURITY_VIEW = SecurityView;

export const Route = createFileRoute("/projects/$projectId/views/security")({
	component: SecurityView,
});
