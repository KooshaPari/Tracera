import { createFileRoute } from '@tanstack/react-router';

import { ItemsKanbanView } from '@/views/ItemsKanbanView';

export const Route = createFileRoute('/items/kanban')({
  component: ItemsKanbanView,
});
