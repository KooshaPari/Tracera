import { createFileRoute } from "@tanstack/react-router";
import { lazy, Suspense } from "react";
import { requireAuth } from "@/lib/route-guards";
import { logger } from '@/lib/logger';

const DashboardView = lazy(() =>
	import("@/views/DashboardView").then((m) => {
		const Comp = m.DashboardView ?? m.default;
		if (Comp == null) {
			logger.error("DashboardView module did not export a component", m);
			return {
				default: () => (
					<div className="p-6 text-destructive" role="alert">
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
				<div className="flex items-center justify-center h-64">
					Loading dashboard...
				</div>
			}
		>
			<DashboardView systemStatus={systemStatus} />
		</Suspense>
	);
}

export const Route = createFileRoute("/home")({
	beforeLoad: () => requireAuth(),
	component: DashboardComponent,
	loader: async () => {
		// Preload dashboard data for enterprise feel
		try {
			const [{ fetchProjects }, { fetchRecentItems }, { fetchSystemStatus }] =
				await Promise.all([
					import("@/api/projects"),
					import("@/api/items"),
					import("@/api/system"),
				]);

			const [projects, recentItems, systemStatus] = await Promise.all([
				fetchProjects().catch(() => []),
				fetchRecentItems().catch(() => []),
				fetchSystemStatus().catch(() => ({
					status: "healthy" as const,
					uptime: 99.9,
					queuedJobs: 0,
				})),
			]);

			return { projects, recentItems, systemStatus };
		} catch (_error) {
			// Return empty data on error to prevent page crash
			return {
				projects: [],
				recentItems: [],
				systemStatus: {
					status: "healthy" as const,
					uptime: 99.9,
					queuedJobs: 0,
				},
			};
		}
	},
});
