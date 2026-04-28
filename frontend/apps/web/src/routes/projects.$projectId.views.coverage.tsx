import { createFileRoute, useParams } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { ChunkLoadingSkeleton } from '@/lib/lazy-loading';

const CoverageMatrixView = lazy(async () =>
  import('@/pages/projects/views/CoverageMatrixView').then((m) => ({
    default: m.CoverageMatrixView ?? m.default,
  })),
);

export function CoverageViewRoute() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <Suspense fallback={<ChunkLoadingSkeleton message='Loading coverage...' />}>
      <CoverageMatrixView projectId={projectId} />
    </Suspense>
  );
}

export const Route = createFileRoute('/projects/$projectId/views/coverage' as any)({
  component: CoverageViewRoute,
  loader: async () => ({}),
});
