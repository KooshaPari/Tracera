import { createFileRoute, Navigate } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';

const DashboardRedirect = () => <Navigate to='/home' replace />;

export const Route = createFileRoute('/dashboard')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: DashboardRedirect,
});
