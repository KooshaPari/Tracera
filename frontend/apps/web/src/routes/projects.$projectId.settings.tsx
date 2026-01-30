import { createFileRoute } from "@tanstack/react-router";
import { ProjectSettingsView } from "@/views/ProjectSettingsView";

export const Route = createFileRoute("/projects/$projectId/settings")({
	component: ProjectSettingsPage,
});

function ProjectSettingsPage() {
	const { projectId } = Route.useParams();
	return <ProjectSettingsView projectId={projectId} />;
}
