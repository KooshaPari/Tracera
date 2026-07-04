import { createFileRoute } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export const Route = createFileRoute('/items/table')({
  component: ItemsTableView,
});
