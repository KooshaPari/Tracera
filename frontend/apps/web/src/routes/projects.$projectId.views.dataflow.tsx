import { createFileRoute } from "@tanstack/react-router";
import { ItemsTableView } from "@/views/ItemsTableView";

export function DataflowView() {
	return <ItemsTableView />;
}

export const DATAFLOW_VIEW = DataflowView;

export const Route = createFileRoute("/projects/$projectId/views/dataflow")({
	component: DataflowView,
});
