import { createFileRoute, useParams } from "@tanstack/react-router";
import { TestSuiteView } from "@/pages/projects/views/TestSuiteView";

export function TestSuiteViewRoute() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/test-suites",
	});
	return <TestSuiteView projectId={projectId} />;
}

export const Route = createFileRoute(
	"/projects/$projectId/views/test-suites" as any,
)({
	component: TestSuiteViewRoute,
	loader: async () => {
		return {};
	},
});
