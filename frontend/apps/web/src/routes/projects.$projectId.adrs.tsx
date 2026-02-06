import { createFileRoute, redirect } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';

function ADRsPage() {
  return null;
}

export const Route = createFileRoute('/projects/$projectId/adrs')({
  beforeLoad: ({ params }) => {
    // Check auth first
    requireAuth();

    // Then redirect
    throw redirect({
      params,
      search: { tab: 'adrs' },
      to: '/projects/$projectId/specifications',
    });
  },
  component: ADRsPage,
});
