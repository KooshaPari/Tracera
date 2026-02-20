import { createFileRoute, useParams } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';

const TestSuiteView = lazy(async () =>
  import('@/pages/projects/views/TestSuiteView').then((m) => ({
    default: m.TestSuiteView ?? m.default,
  })),
);

const TestSuiteViewRoute = () => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <Suspense fallback={<ChunkLoadingSkeleton message='Loading test suites...' />}>
      <TestSuiteView projectId={projectId} />
    </Suspense>
  );
};

export { TestSuiteViewRoute };

export const Route = createFileRoute('/projects/$projectId/views/test-suites' as any)({
  component: TestSuiteViewRoute,
  loader: async () => ({}),
});
