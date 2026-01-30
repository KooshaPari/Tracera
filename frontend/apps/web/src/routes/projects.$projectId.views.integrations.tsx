import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";

export const Route = createFileRoute(
	"/projects/$projectId/views/integrations" as any,
)({
	component: ProjectIntegrationsPage,
});

function ProjectIntegrationsPage() {
	const { projectId } = Route.useParams();
	const navigate = useNavigate();

	useEffect(() => {
		navigate({
			to: `/projects/${projectId}/settings`,
			search: { tab: "integrations" } as any,
			replace: true,
		});
	}, [navigate, projectId]);

	return null;
}
