import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export const InfrastructureView = () => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Infrastructure</h1>
          <p className='text-muted-foreground'>Infrastructure and deployment items</p>
        </div>
      </div>

      <ItemsTableView projectId={projectId} view='infrastructure' />
    </div>
  );
};

export const INFRASTRUCTURE_VIEW = InfrastructureView;

export const Route = createFileRoute('/projects/$projectId/views/infrastructure')({
  component: InfrastructureView,
  loader: async () => ({}),
});
