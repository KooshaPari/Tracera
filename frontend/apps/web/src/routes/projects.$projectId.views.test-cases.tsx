import { createFileRoute, useParams } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';

const TestCaseView = lazy(async () =>
  import('@/pages/projects/views/TestCaseView').then((m) => ({
    default: m.TestCaseView ?? m.default,
  })),
);

export function TestCaseViewRoute() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <Suspense fallback={<ChunkLoadingSkeleton message='Loading test cases...' />}>
      <TestCaseView projectId={projectId} />
    </Suspense>
  );
}

export const Route = createFileRoute('/projects/$projectId/views/test-cases' as any)({
  component: TestCaseViewRoute,
  loader: async () => ({}),
});
