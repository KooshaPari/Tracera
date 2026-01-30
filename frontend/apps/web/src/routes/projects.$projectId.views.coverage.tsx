import { createFileRoute, useParams } from "@tanstack/react-router";
import { CoverageMatrixView } from "@/pages/projects/views/CoverageMatrixView";

export function CoverageViewRoute() {
	const { projectId } = useParams({
		from: "/projects/$projectId/views/coverage",
	});
	return <CoverageMatrixView projectId={projectId} />;
}

export const Route = createFileRoute(
	"/projects/$projectId/views/coverage" as any,
)({
	component: CoverageViewRoute,
	loader: async () => {
		return {};
	},
});
