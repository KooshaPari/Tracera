import { createFileRoute, redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/projects/$projectId/contracts")({
	beforeLoad: ({ params }) => {
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
