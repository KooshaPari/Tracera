import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/projects/$projectId/features" as any)({
	beforeLoad: ({ params }) => {
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
