import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { ScenarioActivityView } from '@/views/ScenarioActivityView';

export const Route = createFileRoute('/projects/$projectId/scenario-activity')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: ScenarioActivityView,
});
