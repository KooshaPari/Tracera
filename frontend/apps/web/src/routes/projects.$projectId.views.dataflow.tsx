import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export function DataflowView() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return <ItemsTableView projectId={projectId} view='dataflow' />;
}

export const DATAFLOW_VIEW = DataflowView;

export const Route = createFileRoute('/projects/$projectId/views/dataflow')({
  component: DataflowView,
});
