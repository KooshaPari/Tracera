import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { ADRDetailView } from '@/views/ADRDetailView';

export const Route = createFileRoute('/projects/$projectId/adrs/$adrId' as any)({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: ADRDetailPage,
});

function ADRDetailPage() {
  // ADRDetailView uses useParams internally
  return <ADRDetailView />;
}
