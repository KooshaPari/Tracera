import { createFileRoute } from '@tanstack/react-router';
import { Suspense, lazy } from 'react';

import { LoadingSpinner } from '@/components/layout/LoadingSpinner';

const ProjectMappingGraphView = lazy(async () =>
  import('@/views/ProjectMappingGraphView').then((m) => ({
    default: m.ProjectMappingGraphView,
  })),
);

export function WireframeView() {
  return (
    <div className='flex-1 space-y-6 p-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>Wireframes & UI</h1>
          <p className='text-muted-foreground'>UI/UX designs and wireframes</p>
        </div>
      </div>

      <Suspense
        fallback={
          <div className='flex h-64 items-center justify-center'>
            <LoadingSpinner text='Loading wireframes...' />
          </div>
        }
      >
        <ProjectMappingGraphView />
      </Suspense>
    </div>
  );
}

export const WIREFRAME_VIEW = WireframeView;

export const Route = createFileRoute('/projects/$projectId/views/wireframe')({
  component: WireframeView,
  loader: async () => ({}),
});
