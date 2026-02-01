import { createFileRoute } from "@tanstack/react-router";
import { ADRDetailView } from "@/views/ADRDetailView";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute("/projects/$projectId/adrs/$adrId" as any)(
	{
		beforeLoad: () => requireAuth(),
		component: ADRDetailPage,
	},
);

function ADRDetailPage() {
	// ADRDetailView uses useParams internally
	return <ADRDetailView />;
}
