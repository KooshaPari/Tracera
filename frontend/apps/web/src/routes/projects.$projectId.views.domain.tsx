import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function DomainView() {
	return <ItemsTableView />;
}

export const DOMAIN_VIEW = DomainView;

export const Route = createFileRoute("/projects/$projectId/views/domain")({
	component: DomainView,
});
