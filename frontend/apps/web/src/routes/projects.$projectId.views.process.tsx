import { createFileRoute, useParams } from "@tanstack/react-router";
import { ProcessView } from "@/pages/projects/views/ProcessView";

export function ProcessViewRoute() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/process",
	});
	return <ProcessView projectId={projectId} />;
}

export const PROCESS_VIEW = ProcessViewRoute;

export const Route = createFileRoute(
	"/projects/$projectId/views/process" as any,
)({
	component: ProcessViewRoute,
	loader: async () => {
		return {};
	},
});
