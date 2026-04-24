import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { FeatureDetailView } from '@/views/FeatureDetailView';

export const Route = createFileRoute('/projects/$projectId/features/$featureId' as any)({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: FeatureDetailPage,
});

function FeatureDetailPage() {
  // FeatureDetailView uses useParams internally
  return <FeatureDetailView />;
}
