import { createFileRoute, redirect } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/features" as any)({
	beforeLoad: ({ params }) => {
		// Check auth first
		requireAuth();

		// Then redirect to specifications
		throw redirect({
			params,
			search: { tab: "features" },
			to: "/projects/$projectId/specifications",
		});
	},
	component: FeaturesPage,
});

function FeaturesPage() {
	return null;
}
