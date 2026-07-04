import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export const SecurityView = () => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Security & Compliance</h1>
          <p className='text-muted-foreground'>Security requirements and compliance items</p>
        </div>
      </div>

      <ItemsTableView projectId={projectId} view='security' />
    </div>
  );
};

export const SECURITY_VIEW = SecurityView;

export const Route = createFileRoute('/projects/$projectId/views/security')({
  component: SecurityView,
  loader: async () => ({}),
});
