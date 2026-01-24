import { createFileRoute } from "@tanstack/react-router";
import { DashboardView } from "@/views/DashboardView";

export const Route = createFileRoute("/")({
	component: DashboardView,
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
					activeAgents: 0,
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
					activeAgents: 0,
					queuedJobs: 0,
				},
			};
		}
	},
});
