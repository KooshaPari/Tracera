import { createFileRoute } from "@tanstack/react-router";
import { ProjectSettingsView } from "@/views/ProjectSettingsView";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/settings")({
	beforeLoad: () => requireAuth(),
	component: ProjectSettingsPage,
});

function ProjectSettingsPage() {
	const { projectId } = Route.useParams();
	return <ProjectSettingsView projectId={projectId} />;
}
