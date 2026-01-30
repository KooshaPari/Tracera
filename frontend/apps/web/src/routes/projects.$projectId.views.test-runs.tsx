import { createFileRoute, useParams } from "@tanstack/react-router";
import { TestRunView } from "@/pages/projects/views/TestRunView";

export function TestRunViewRoute() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/test-runs",
	});
	return <TestRunView projectId={projectId} />;
}

export const Route = createFileRoute(
	"/projects/$projectId/views/test-runs" as any,
)({
	component: TestRunViewRoute,
	loader: async () => {
		return {};
	},
});
