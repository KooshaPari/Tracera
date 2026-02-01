import { createFileRoute, redirect } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/compliance")({
	beforeLoad: ({ params }) => {
		// Check auth first
		requireAuth();

		// Then redirect
		throw redirect({
			to: "/projects/$projectId/specifications",
			params,
			search: { tab: "compliance" },
		});
	},
	component: CompliancePage,
});

function CompliancePage() {
	return null;
}
