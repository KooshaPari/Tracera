import { createFileRoute, useParams } from "@tanstack/react-router";
import { ProcessView } from "@/pages/projects/views/ProcessView";

export const ProcessViewRoute = (): JSX.Element => {
	const { projectId } = useParams({ from: "/projects/$projectId" });
	return <ProcessView projectId={projectId} />;
};

export const PROCESS_VIEW = ProcessViewRoute;

export const Route = createFileRoute(
	"/projects/$projectId/views/process" as any,
)({
	component: ProcessViewRoute,
	loader: async () => ({}),
});
