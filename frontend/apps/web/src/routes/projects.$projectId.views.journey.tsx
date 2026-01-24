import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function JourneyView() {
	return <ItemsTableView />;
}

export const JOURNEY_VIEW = JourneyView;

export const Route = createFileRoute("/projects/$projectId/views/journey")({
	component: JourneyView,
});
