import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export const ArchitectureView = () => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <ItemsTableView projectId={projectId} view='architecture' />;
};

export const ARCHITECTURE_VIEW = ArchitectureView;

export const Route = createFileRoute('/projects/$projectId/views/architecture')({
  component: ArchitectureView,
});
