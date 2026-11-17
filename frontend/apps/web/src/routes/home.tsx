import { createFileRoute } from "@tanstack/react-router";
import { Suspense, lazy } from "react";

import { Unavailable } from "@/components/Availability";
import { LoadingSpinner } from "@/components/layout/LoadingSpinner";
import { logger } from "@/lib/logger";
import { requireAuth } from "@/lib/route-guards";

const DashboardView = lazy(async () =>
  import("@/views/DashboardView").then((m) => {
    const Comp = m.DashboardView;
    if (Comp === null || Comp === undefined) {
      logger.error("DashboardView module did not export a component", m);
      return {
        default: () => (
          <div className="text-destructive p-6" role="alert">
            Failed to load dashboard.
          </div>
        ),
      };
    }
    return { default: Comp };
  }),
);

const dashboardFallback = (
  <div className="flex h-64 items-center justify-center">
    <LoadingSpinner text="Loading dashboard..." />
  </div>
);

function DashboardComponent() {
  const { systemStatus } = Route.useLoaderData();
  return (
    <Suspense fallback={dashboardFallback}>
      <DashboardView systemStatus={systemStatus} />
    </Suspense>
  );
}

export const Route = createFileRoute("/home")({
  // Unauthenticated users should be sent back to the public landing page.
  beforeLoad: async () => {
    await requireAuth({ includeReturnUrl: false, redirectTo: "/" });
  },
  component: DashboardComponent,
  loader: async () => {
    // Only fetch systemStatus here; projects are fetched by DashboardView's
    // UseProjects() hook (with staleTime caching) to avoid a double-fetch.
    const { fetchSystemStatus } = await import("@/api/system");
    return { systemStatus: await fetchSystemStatus() };
  },
  errorComponent: ({ error }) => <Unavailable error={error} />,
});
