import { createFileRoute, redirect } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/features" as any)({
	beforeLoad: ({ params }) => {
		// Check auth first
		requireAuth();

		// Then redirect to specifications
		throw redirect({
			to: "/projects/$projectId/specifications",
			params,
			search: { tab: "features" },
		});
	},
	component: FeaturesPage,
});

function FeaturesPage() {
	return null;
}
