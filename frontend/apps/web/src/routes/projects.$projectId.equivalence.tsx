import { createFileRoute, useParams } from '@tanstack/react-router';

import { EquivalenceManager } from '@/components/EquivalenceManager';
import { requireAuth } from '@/lib/route-guards';

/**
 * Equivalence Management View
 * Allows users to view, export, and import equivalence mappings
 */
export const EquivalenceView = () => {
  const { projectId } = useParams({ from: '/projects/$projectId/equivalence' });

  return (
    <div className='flex-1 space-y-6 p-6'>
      <EquivalenceManager projectId={projectId} />
    </div>
  );
};

export const EQUIVALENCE_VIEW = EquivalenceView;

export const Route = createFileRoute('/projects/$projectId/equivalence')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: EquivalenceView,
  loader: async () => ({}),
});
