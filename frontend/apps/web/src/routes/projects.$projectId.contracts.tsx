import { createFileRoute, redirect } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/contracts")({
	beforeLoad: ({ params }) => {
		// Check auth first
		requireAuth();

		// Then redirect
		throw redirect({
			to: "/projects/$projectId/specifications",
			params,
			search: { tab: "contracts" },
		});
	},
	component: ContractsPage,
});

function ContractsPage() {
	return null;
}
