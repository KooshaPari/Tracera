import {
  Link as RouterLink,
  createRootRoute,
  useLocation,
  useRouter,
} from '@tanstack/react-router';
import { AlertCircle, FileQuestion, Home, RefreshCcw } from 'lucide-react';
import { useEffect } from 'react';
import { Toaster } from 'sonner';

import { CommandPalette } from '@/components/CommandPalette';
import Layout from '@/components/layout/Layout';
import { LostConnectionBanner } from '@/components/LostConnectionBanner';
import { useConnectionHealth } from '@/hooks/useConnectionHealth';
import { Button } from '@tracertm/ui';

// Not found component for 404 pages
function NotFoundComponent() {
  const router = useRouter();
  const location = useLocation();

  useEffect(() => {
    if (location.pathname === '/') {
      router.navigate({ replace: true, to: '/landing' });
    }
  }, [location.pathname, router]);

  return (
    <div className='bg-background animate-in fade-in flex min-h-[80vh] items-center justify-center p-4 duration-500'>
      <div className='w-full max-w-md space-y-8 text-center'>
        <div className='relative mx-auto h-24 w-24'>
          <div className='bg-primary/10 absolute inset-0 animate-pulse rounded-full' />
          <div className='relative flex h-full w-full items-center justify-center'>
            <FileQuestion className='text-primary h-12 w-12' />
          </div>
        </div>

        <div className='space-y-2'>
          <h1 className='text-4xl font-bold tracking-tight'>Lost in the Matrix?</h1>
          <p className='text-muted-foreground'>
            The node you're looking for doesn't exist in our current graph. It might have been
            pruned or moved.
          </p>
        </div>

        <div className='flex flex-col justify-center gap-3 sm:flex-row'>
          <Button asChild className='gap-2'>
            <RouterLink to='/home'>
              <Home className='h-4 w-4' />
              Back to Dashboard
            </RouterLink>
          </Button>
        </div>
      </div>
    </div>
  );
}

// Root error component to handle uncaught errors
function RootErrorComponent({ error }: { error: Error }) {
  const router = useRouter();

  return (
    <div className='bg-background animate-in zoom-in-95 flex min-h-[80vh] items-center justify-center p-4 duration-300'>
      <div className='bg-card w-full max-w-lg space-y-8 rounded-2xl border p-8 shadow-xl'>
        <div className='flex items-center gap-4'>
          <div className='bg-destructive/10 text-destructive flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-xl'>
            <AlertCircle className='h-6 w-6' />
          </div>
          <div>
            <h1 className='text-xl font-bold'>System Anomaly Detected</h1>
            <p className='text-muted-foreground font-mono text-sm'>
              CODE: {error.name || 'UNHANDLED_EXCEPTION'}
            </p>
          </div>
        </div>

        <div className='bg-muted/50 overflow-x-auto rounded-xl border p-4 font-mono text-sm'>
          <p className='text-destructive mb-2 font-bold'>Error Detail:</p>
          <p className='text-muted-foreground'>
            {error.message === 'fetch failed'
              ? 'Critical API Link Failure: Unable to establish connection to the backend cluster.'
              : error.message}
          </p>
        </div>

        <div className='flex flex-col gap-3 sm:flex-row'>
          <Button onClick={async () => router.invalidate()} className='flex-1 gap-2'>
            <RefreshCcw className='h-4 w-4' />
            Sync & Retry
          </Button>
          <Button
            variant='outline'
            onClick={() => (globalThis.location.href = '/')}
            className='flex-1 gap-2'
          >
            <Home className='h-4 w-4' />
            Terminal Return
          </Button>
        </div>
      </div>
    </div>
  );
}

const RootComponent = () => {
  const router = useRouter();
  const location = useLocation();

  // Background health polling; updates connection status store on loss/recovery
  useConnectionHealth();

  // Prefetch likely navigation targets for faster perceived performance
  useEffect(() => {
    // Prefetch common routes after initial render
    const prefetchRoutes = async () => {
      try {
        const routes = [router.preloadRoute({ to: '/projects' })];

        // Only preload graph if user is on a project-related page
        if (location.pathname.includes('/projects/')) {
          const projectId = location.pathname.split('/')[2];
          if (projectId) {
            routes.push(
              router.preloadRoute({
                params: {
                  projectId,
                  viewType: 'graph',
                },
                to: '/projects/$projectId/views/$viewType',
              }),
            );
          }
        }

        // Preload routes user is likely to navigate to
        await Promise.all(routes);
      } catch {
        // Silently ignore prefetch errors
      }
    };

    // Delay prefetch to not block initial render
    const timeoutId = setTimeout(prefetchRoutes, 1000);
    return () => {
      clearTimeout(timeoutId);
    };
  }, [router, location.pathname]);

  return (
    <>
      <LostConnectionBanner />
      <CommandPalette />
      <Layout />
      <Toaster position='top-right' richColors />
    </>
  );
};

export const Route = createRootRoute({
  beforeLoad: () => {},
  component: RootComponent,
  errorComponent: RootErrorComponent,
  head: () => ({
    links: [
      {
        href: '/favicon.svg',
        rel: 'icon',
        type: 'image/svg+xml',
      },
    ],
    meta: [
      {
        charSet: 'utf8',
      },
      {
        content: 'width=device-width, initial-scale=1',
        name: 'viewport',
      },
      {
        title: 'TraceRTM - Multi-View Requirements Traceability System',
      },
      {
        content:
          'Enterprise-grade requirements traceability and project management system with 16 professional views and intelligent CRUD operations.',
        name: 'description',
      },
    ],
  }),
  notFoundComponent: NotFoundComponent,
});
