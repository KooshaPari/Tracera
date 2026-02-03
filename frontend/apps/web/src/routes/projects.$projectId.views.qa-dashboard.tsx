import { createFileRoute, useParams } from "@tanstack/react-router";
import { QADashboardView } from "@/pages/projects/views/QADashboardView";

export const QADashboardViewRoute = () => {
	const { projectId } = useParams({ from: "/projects/$projectId" });
	return <QADashboardView projectId={projectId} />;
};

export const Route = createFileRoute(
	"/projects/$projectId/views/qa-dashboard" as any,
)({
	component: QADashboardViewRoute,
	loader: async () => ({}),
});
