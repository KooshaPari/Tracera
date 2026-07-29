import { createFileRoute } from '@tanstack/react-router';

import { requireAuth } from '@/lib/route-guards';
import { ContractDetailView } from '@/views/ContractDetailView';

const ContractDetailPage = () => <ContractDetailView />;

export const Route = createFileRoute('/projects/$projectId/contracts/$contractId')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: ContractDetailPage,
});
