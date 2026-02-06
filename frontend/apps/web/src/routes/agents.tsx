import { createFileRoute } from '@tanstack/react-router';

import { AgentsView } from '@/views/AgentsView';

export const Route = createFileRoute('/agents')({
  component: AgentsView,
});
