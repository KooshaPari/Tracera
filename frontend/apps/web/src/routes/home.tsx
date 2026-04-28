import { createFileRoute } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { logger } from '@/lib/logger';
import { requireAuth } from '@/lib/route-guards';

const DashboardView = lazy(async () =>
  import('@/views/DashboardView').then((m) => {
    const Comp = m.DashboardView;
    if (Comp === null || Comp === undefined) {
      logger.error('DashboardView module did not export a component', m);
      return {
        default: () => (
          <div className='text-destructive p-6' role='alert'>
            Failed to load dashboard.
          </div>
        ),
      };
    }
    return { default: Comp };
  }),
);

function DashboardComponent() {
  const { systemStatus } = Route.useLoaderData();
  return (
    <Suspense
      fallback={
        <div className='flex h-64 items-center justify-center'>
          <LoadingSpinner text='Loading dashboard...' />
        </div>
      }
    >
      <DashboardView systemStatus={systemStatus} />
    </Suspense>
  );
}

export const Route = createFileRoute('/home')({
  // Unauthenticated users should be sent back to the public landing page.
  beforeLoad: async () => {
    await requireAuth({ includeReturnUrl: false, redirectTo: '/' });
  },
  component: DashboardComponent,
  loader: async () => {
    // Only fetch systemStatus here; projects are fetched by DashboardView's
    // UseProjects() hook (with staleTime caching) to avoid a double-fetch.
    try {
      const { fetchSystemStatus } = await import('@/api/system');
      const systemStatus = await fetchSystemStatus().catch(() => ({
        queuedJobs: 0,
        status: 'healthy' as const,
        uptime: 99.9,
      }));

      return { systemStatus };
    } catch {
      return {
        systemStatus: {
          queuedJobs: 0,
          status: 'healthy' as const,
          uptime: 99.9,
        },
      };
    }
  },
});
