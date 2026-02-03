import { createFileRoute, useParams } from "@tanstack/react-router";
import { TestSuiteView } from "@/pages/projects/views/TestSuiteView";

const TestSuiteViewRoute = () => {
	const { projectId } = useParams({ from: "/projects/$projectId" });
	return <TestSuiteView projectId={projectId} />;
};

export { TestSuiteViewRoute };

export const Route = createFileRoute(
	"/projects/$projectId/views/test-suites" as any,
)({
	component: TestSuiteViewRoute,
	loader: async () => ({}),
});
