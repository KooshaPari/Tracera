import { createFileRoute } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";
import { ProjectSettingsView } from "@/views/ProjectSettingsView";

export const Route = createFileRoute("/projects/$projectId/settings")({
	beforeLoad: () => requireAuth(),
	component: ProjectSettingsPage,
});

const ProjectSettingsPage = () => {
	const { projectId } = Route.useParams();
	return <ProjectSettingsView projectId={projectId} />;
};
