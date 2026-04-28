import type { ReactElement } from 'react';

import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { ScenarioDetailView } from '@/views/ScenarioDetailView';

const ScenarioDetailPage = (): ReactElement => <ScenarioDetailView />;

export const Route = createFileRoute(
  '/projects/$projectId/features/$featureId/scenarios/$scenarioId',
)({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: ScenarioDetailPage,
});
