import { createFileRoute, redirect } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';

const CompliancePage = () => null;

export const Route = createFileRoute('/projects/$projectId/compliance')({
  beforeLoad: ({ params }) => {
    // Check auth first
    requireAuth();

    // Then redirect
    throw redirect({
      params,
      search: { tab: 'compliance' },
      to: '/projects/$projectId/specifications',
    });
  },
  component: CompliancePage,
});
