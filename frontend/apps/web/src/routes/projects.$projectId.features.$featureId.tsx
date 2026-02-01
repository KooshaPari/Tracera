import { createFileRoute } from "@tanstack/react-router";
import { FeatureDetailView } from "@/views/FeatureDetailView";
import { requireAuth } from "@/lib/route-guards";

export const Route = createFileRoute(
	"/projects/$projectId/features/$featureId" as any,
)({
	beforeLoad: () => requireAuth(),
	component: FeatureDetailPage,
});

function FeatureDetailPage() {
	// FeatureDetailView uses useParams internally
	return <FeatureDetailView />;
}
