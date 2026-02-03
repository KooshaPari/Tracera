import { createFileRoute } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";
import { ContractDetailView } from "@/views/ContractDetailView";

export const Route = createFileRoute(
	"/projects/$projectId/contracts/$contractId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: ContractDetailPage,
});

const ContractDetailPage = () => {
	// ContractDetailView uses useParams internally
	return <ContractDetailView />;
};
