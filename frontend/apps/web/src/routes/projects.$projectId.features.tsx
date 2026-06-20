import { createFileRoute, redirect } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';

function FeaturesPage() {
  return null;
}

export const Route = createFileRoute('/projects/$projectId/features' as any)({
  component: FeaturesPage,
  beforeLoad: ({ params }) => {
    requireAuth();
    throw redirect({
      params,
      search: { tab: 'features' },
      to: '/projects/$projectId/specifications',
    });
  },
});
