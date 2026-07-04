import { createFileRoute, useParams } from '@tanstack/react-router';

import { ItemsTableView } from '@/views/ItemsTableView';

export function TestView() {
  const { projectId } = useParams({ from: '/projects/$projectId' });
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Test Coverage</h1>
          <p className='text-muted-foreground'>Test cases and coverage metrics</p>
        </div>
      </div>

      <ItemsTableView projectId={projectId} view='test' />
    </div>
  );
}

export const TEST_VIEW = TestView;

export const Route = createFileRoute('/projects/$projectId/views/test')({
  component: TestView,
  loader: async () => ({}),
});
