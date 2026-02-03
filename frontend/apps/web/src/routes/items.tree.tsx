import { ItemsTreeView } from "@/views/ItemsTreeView";
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/items/tree")({
	component: ItemsTreeView,
});
