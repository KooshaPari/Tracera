import { createFileRoute, redirect } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";

const FeaturesPage = () => null;

export const Route = createFileRoute("/projects/$projectId/features" as any)({
	beforeLoad: ({ params }) => {
		requireAuth();
		throw redirect({
			params,
			search: { tab: "features" },
			to: "/projects/$projectId/specifications",
		});
	},
	component: FeaturesPage,
});
