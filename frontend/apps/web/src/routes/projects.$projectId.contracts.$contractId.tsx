import { createFileRoute } from "@tanstack/react-router";
import { ContractDetailView } from "@/views/ContractDetailView";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute(
	"/projects/$projectId/contracts/$contractId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: ContractDetailPage,
});

function ContractDetailPage() {
	// ContractDetailView uses useParams internally
	return <ContractDetailView />;
}
