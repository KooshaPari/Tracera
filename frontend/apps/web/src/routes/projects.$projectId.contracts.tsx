import { createFileRoute, redirect } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';

export const Route = createFileRoute('/projects/$projectId/contracts')({
  beforeLoad: ({ params }) => {
    // Check auth first
    requireAuth();

    // Then redirect
    throw redirect({
      params,
      search: { tab: 'contracts' },
      to: '/projects/$projectId/specifications',
    });
  },
  component: ContractsPage,
});

function ContractsPage() {
  return null;
}
