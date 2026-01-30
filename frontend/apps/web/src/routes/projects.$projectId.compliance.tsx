import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/projects/$projectId/compliance")({
	beforeLoad: ({ params }) => {
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
