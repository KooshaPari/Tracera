import { createFileRoute, redirect } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/adrs")({
	beforeLoad: ({ params }) => {
		// Check auth first
		requireAuth();

		// Then redirect
		throw redirect({
			to: "/projects/$projectId/specifications",
			params,
			search: { tab: "adrs" },
		});
	},
	component: ADRsPage,
});

function ADRsPage() {
	return null;
}
