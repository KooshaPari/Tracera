import { createFileRoute } from "@tanstack/react-router";
import { requireAuth } from "@/lib/route-guards";
import { ContractDetailView } from "@/views/ContractDetailView";

const ContractDetailPage = () => {
	// ContractDetailView uses useParams internally
	return <ContractDetailView />;
};

export const Route = createFileRoute(
	"/projects/$projectId/contracts/$contractId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: ContractDetailPage,
});
