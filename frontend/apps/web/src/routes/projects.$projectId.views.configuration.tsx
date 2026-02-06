import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export function ConfigurationView() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Configuration</h1>
          <p className='text-muted-foreground'>Project and environment configuration</p>
        </div>
      </div>

      <ItemsTableView projectId={projectId} view='configuration' />
    </div>
  );
}

export const CONFIGURATION_VIEW = ConfigurationView;

export const Route = createFileRoute('/projects/$projectId/views/configuration')({
  component: ConfigurationView,
  loader: async () => ({}),
});
