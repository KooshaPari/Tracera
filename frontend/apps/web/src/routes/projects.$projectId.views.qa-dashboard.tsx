import { createFileRoute, useParams } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';

const QADashboardView = lazy(async () =>
  import('@/pages/projects/views/QADashboardView').then((m) => ({
    default: m.QADashboardView,
  })),
);

export const QADashboardViewRoute = () => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <Suspense fallback={<ChunkLoadingSkeleton message='Loading QA dashboard...' />}>
      <QADashboardView projectId={projectId} />
    </Suspense>
  );
};

export const Route = createFileRoute('/projects/$projectId/views/qa-dashboard' as any)({
  component: QADashboardViewRoute,
  loader: async () => ({}),
});
