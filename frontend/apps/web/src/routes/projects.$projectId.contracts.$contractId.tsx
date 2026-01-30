import { createFileRoute } from "@tanstack/react-router";
import { ContractDetailView } from "@/views/ContractDetailView";

export const Route = createFileRoute(
	"/projects/$projectId/contracts/$contractId" as any,
)({
	component: ContractDetailPage,
});

function ContractDetailPage() {
	// ContractDetailView uses useParams internally
	return <ContractDetailView />;
}
