import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export const CodeView = () => {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Code Implementation</h1>
          <p className='text-muted-foreground'>Source code implementations</p>
        </div>
      </div>

      <ItemsTableView projectId={projectId} view='code' />
    </div>
  );
};

export const CODE_VIEW = CodeView;

export const Route = createFileRoute('/projects/$projectId/views/code')({
  component: CodeView,
  loader: async () => ({}),
});
