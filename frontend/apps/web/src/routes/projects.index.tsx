import { createFileRoute } from "@tanstack/react-router";
import { ProjectsListView } from "@/views/ProjectsListView";

export const Route = createFileRoute("/projects/")({
	component: ProjectsComponent,
	loader: async () => {
		// ProjectsListView fetches its own data
		return {};
	},
});

function ProjectsComponent() {
	return <ProjectsListView />;
}
