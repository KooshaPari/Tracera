import { createFileRoute, useParams } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function JourneyView() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/journey",
	});
	return <ItemsTableView projectId={projectId} view="journey" />;
}

export const JOURNEY_VIEW = JourneyView;

export const Route = createFileRoute("/projects/$projectId/views/journey")({
	component: JourneyView,
});
