import { ItemsKanbanView } from "@/views/ItemsKanbanView";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/items/kanban")({
	component: ItemsKanbanView,
});
