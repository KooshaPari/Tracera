import { createFileRoute } from "@tanstack/react-router";
import { ADRDetailView } from "@/views/ADRDetailView";

export const Route = createFileRoute("/projects/$projectId/adrs/$adrId" as any)(
	{
		component: ADRDetailPage,
	},
);

function ADRDetailPage() {
	// ADRDetailView uses useParams internally
	return <ADRDetailView />;
}
