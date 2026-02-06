import { createFileRoute, useParams } from '@tanstack/react-router';

import { MonitoringView as MonitoringViewPage } from '@/pages/projects/views/MonitoringView';

export function MonitoringView() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <MonitoringViewPage projectId={projectId} />;
}

export const MONITORING_VIEW = MonitoringView;

export const Route = createFileRoute('/projects/$projectId/views/monitoring')({
  component: MonitoringView,
});
