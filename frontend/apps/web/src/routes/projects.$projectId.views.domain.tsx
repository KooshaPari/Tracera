import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export function DomainView() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <ItemsTableView projectId={projectId} view='domain' />;
}

export const DOMAIN_VIEW = DomainView;

export const Route = createFileRoute('/projects/$projectId/views/domain')({
  component: DomainView,
});
