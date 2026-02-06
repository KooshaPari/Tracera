import { createFileRoute } from '@tanstack/react-router';

import { ItemsTreeView } from '@/views/ItemsTreeView';

export const Route = createFileRoute('/items/tree')({
  component: ItemsTreeView,
});
