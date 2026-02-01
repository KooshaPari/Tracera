import { createFileRoute } from "@tanstack/react-router";
import { useMemo } from "react";
import { ItemsTableView } from "@/views/ItemsTableView";
import { useProjects } from "@/hooks/useProjects";

function ItemsListView() {
	const { data: projects } = useProjects();
	const projectId = useMemo(() => {
		if (!projects || !Array.isArray(projects)) return undefined;
		return projects[0]?.id;
	}, [projects]);

	return <ItemsTableView projectId={projectId} />;
}

export const Route = createFileRoute("/items/")({
	component: ItemsListView,
});
