import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

const DatabaseView = (): JSX.Element => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Database Schemas</h1>
          <p className='text-muted-foreground'>Database designs, schemas, and migrations</p>
        </div>
      </div>

      <ItemsTableView projectId={projectId} view='database' />
    </div>
  );
};

const DATABASE_VIEW = DatabaseView;

const Route = createFileRoute('/projects/$projectId/views/database')({
  component: DatabaseView,
  loader: () => ({}),
});

export { DATABASE_VIEW, DatabaseView, Route };
