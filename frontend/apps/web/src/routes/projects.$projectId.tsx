import { Outlet, createFileRoute, useLocation, useParams } from '@tanstack/react-router';
import { useCallback, Suspense, lazy } from 'react';

import { ErrorBoundary } from '@/components/layout/ErrorBoundary';
import { FullScreenPage } from '@/components/layout/FullScreenPage';
import { LoadingSpinner } from '@/components/layout/LoadingSpinner';
import { logger } from '@/lib/logger';
import { requireAuth } from '@/lib/route-guards';

const ProjectDetailView = lazy(async () =>
  import('@/views/ProjectDetailView').then((m) => {
    const Comp = m.ProjectDetailView;
    if (Comp === null || Comp === undefined) {
      logger.error('ProjectDetailView module did not export a component', m);
      return {
        default: () => (
          <div className='text-destructive p-6' role='alert'>
            Failed to load project.
          </div>
        ),
      };
    }
    return { default: Comp };
  }),
);

const ProjectDetailComponent = () => {
  const params = Route.useParams();
  const location = useLocation();

  // Check if we are deeper than the project root (i.e. showing a child route)
  const currentPath = location.pathname.replace(/\/$/, '');
  const rootPath = `/projects/${params.projectId}`;
  const isChildRoute = currentPath !== rootPath;

  return (
    <ErrorBoundary>
      {isChildRoute ? (
        <Outlet />
      ) : (
        <Suspense
          fallback={
            <div className='flex h-64 items-center justify-center'>
              <LoadingSpinner text='Loading project...' />
            </div>
          }
        >
          <ProjectDetailView />
        </Suspense>
      )}
    </ErrorBoundary>
  );
};

const ErrorComponent = ({ error }: { error?: Error }) => {
  const { projectId } = useParams({ strict: false });
  const handleGoBack = useCallback(() => {
    globalThis.history.back();
  }, []);

  return (
    <FullScreenPage>
      <div className='bg-background text-foreground flex min-h-screen flex-col items-center justify-center'>
        <h1 className='text-destructive mb-4 text-2xl font-bold'>Project Not Found</h1>
        <p className='text-muted-foreground mb-6'>
          The project you're looking for doesn't exist or you don't have access.
        </p>
        {error && <p className='text-muted-foreground mb-4 text-sm'>Error: {error.message}</p>}
        {projectId && <p className='text-muted-foreground mb-4 text-xs'>Project ID: {projectId}</p>}
        <button
          onClick={handleGoBack}
          className='bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2'
        >
          Go Back
        </button>
      </div>
    </FullScreenPage>
  );
};

export const Route = createFileRoute('/projects/$projectId')({
  beforeLoad: async () => {
    await requireAuth();
  },
  component: ProjectDetailComponent,
  errorComponent: ErrorComponent,
  loader: async ({ params }: { params: { projectId: string } }) => ({
    projectId: params.projectId,
  }),
});
