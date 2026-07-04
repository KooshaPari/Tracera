import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export const PerformanceView = () => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <ItemsTableView projectId={projectId} view='performance' />;
};

export const PERFORMANCE_VIEW = PerformanceView;

export const Route = createFileRoute('/projects/$projectId/views/performance')({
  component: PerformanceView,
});
