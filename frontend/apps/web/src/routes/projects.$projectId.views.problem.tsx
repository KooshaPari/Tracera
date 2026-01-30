import { createFileRoute, useParams } from "@tanstack/react-router";
import { ProblemView } from "@/pages/projects/views/ProblemView";

export function ProblemViewRoute() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/problem",
	});
	return <ProblemView projectId={projectId} />;
}

export const PROBLEM_VIEW = ProblemViewRoute;

export const Route = createFileRoute(
	"/projects/$projectId/views/problem" as any,
)({
	component: ProblemViewRoute,
	loader: async () => {
		return {};
	},
});
