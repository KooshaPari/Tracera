import { createFileRoute, useParams } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';

const TestRunView = lazy(async () =>
  import('@/pages/projects/views/TestRunView').then((m) => ({
    default: m.TestRunView ?? m.default,
  })),
);

export function TestRunViewRoute() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <Suspense fallback={<ChunkLoadingSkeleton message='Loading test runs...' />}>
      <TestRunView projectId={projectId} />
    </Suspense>
  );
}

export const Route = createFileRoute('/projects/$projectId/views/test-runs' as any)({
  component: TestRunViewRoute,
  loader: async () => ({}),
});
