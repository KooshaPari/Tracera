import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export function DependencyView() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <ItemsTableView projectId={projectId} view='dependency' />;
}

export const DEPENDENCY_VIEW = DependencyView;

export const Route = createFileRoute('/projects/$projectId/views/dependency')({
  component: DependencyView,
});
