import { createFileRoute } from "@tanstack/react-router";
import { FeatureDetailView } from "@/views/FeatureDetailView";

export const Route = createFileRoute(
	"/projects/$projectId/features/$featureId" as any,
)({
	component: FeatureDetailPage,
});

function FeatureDetailPage() {
	// FeatureDetailView uses useParams internally
	return <FeatureDetailView />;
}
