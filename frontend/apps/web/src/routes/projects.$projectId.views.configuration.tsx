import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function ConfigurationView() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/configuration",
	});
	return <ItemsTableView projectId={projectId} view="configuration" />;
}

export const CONFIGURATION_VIEW = ConfigurationView;

export const Route = createFileRoute(
	"/projects/$projectId/views/configuration" as any,
)({
	component: ConfigurationView,
});
