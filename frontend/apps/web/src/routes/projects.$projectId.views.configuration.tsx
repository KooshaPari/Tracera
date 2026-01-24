import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function ConfigurationView() {
	return <ItemsTableView />;
}

export const CONFIGURATION_VIEW = ConfigurationView;

export const Route = createFileRoute(
	"/projects/$projectId/views/configuration",
)({
	component: ConfigurationView,
});
