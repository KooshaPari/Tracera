import { createFileRoute, useParams } from "@tanstack/react-router";
import { TestCaseView } from "@/pages/projects/views/TestCaseView";

export function TestCaseViewRoute() {
	const { projectId } = useParams({ from: "/projects/$projectId" });
	return <TestCaseView projectId={projectId} />;
}

export const Route = createFileRoute(
	"/projects/$projectId/views/test-cases" as any,
)({
	component: TestCaseViewRoute,
	loader: async () => {
		return {};
	},
});
