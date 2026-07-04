import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { AgentWorkflowView } from '@/views/AgentWorkflowView';

export const Route = createFileRoute('/projects/$projectId/agents')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: AgentWorkflowView,
});
