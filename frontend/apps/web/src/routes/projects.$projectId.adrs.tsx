import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/projects/$projectId/adrs")({
	beforeLoad: ({ params }) => {
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
