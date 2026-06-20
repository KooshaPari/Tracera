import { RouterProvider } from '@tanstack/react-router';
import { createRoot } from 'react-dom/client';

import { ErrorBoundary } from '@/components/ErrorBoundary';
import { TooltipProvider } from '@/components/ui/tooltip';
import { createRetryFetch } from '@/lib/fetch-retry';
import { renderPreflightFailure, runFrontendPreflight } from '@/lib/preflight';
import { initSentry } from '@/lib/sentry';
import { AppProviders } from '@/providers/app-providers';
import { ThemeProvider } from '@/providers/theme-provider';

import { createRouter } from './router';
// This entrypoint intentionally imports global styles for side effects.
// eslint-disable-next-line import/no-unassigned-import
import './index.css';

// Initialize Sentry error tracking before anything else
// eslint-disable-next-line jest/require-hook
initSentry();

// Patch global fetch with wait+retry so all API and preflight calls use robust retry
if (typeof globalThis.fetch !== 'undefined') {
  (globalThis as unknown as Window & { fetch: typeof fetch }).fetch = createRetryFetch(
    globalThis.fetch,
    { maxRetries: 3, timeoutMs: 15_000 },
  );
}

// Initialize MSW in development mode - DISABLED to use real backend
const enableMocking = false; // Set to false to use real backend API
const handleReload = (): void => {
  globalThis.location.reload();
};

async function prepare(): Promise<boolean> {
  const preflight = await runFrontendPreflight();
  if (!preflight.ok) {
    renderPreflightFailure(preflight);
    return false;
  }

  if (!enableMocking) {
    return true;
  }

  const { startMockServiceWorker } = await import('./mocks/browser');
  await startMockServiceWorker();
  return true;
}

// Create router
const router = createRouter();
// eslint-disable-next-line jest/require-hook
router.update({
  defaultErrorComponent: ({ error }) => (
    <div className='bg-background text-foreground flex min-h-screen flex-col items-center justify-center'>
      <h1 className='text-destructive mb-4 text-2xl font-bold'>Something went wrong</h1>
      <p className='text-muted-foreground mb-4'>{error.message}</p>
      <button
        onClick={handleReload}
        className='bg-primary text-primary-foreground hover:bg-primary/90 rounded-md px-4 py-2'
        type='button'
      >
        Try again
      </button>
    </div>
  ),
});

// eslint-disable-next-line jest/require-hook
async function bootstrap(): Promise<void> {
  const ready = await prepare();
  if (!ready) {
    return;
  }

  const rootElement = document.querySelector('#root');
  if (!rootElement) {
    throw new Error('Root element not found');
  }

  const root = createRoot(rootElement);
  root.render(
    <ErrorBoundary name='AppRoot' showDetails={false}>
      <ThemeProvider>
        <AppProviders>
          <TooltipProvider>
            <RouterProvider router={router} />
          </TooltipProvider>
        </AppProviders>
      </ThemeProvider>
    </ErrorBoundary>,
  );
}

// eslint-disable-next-line jest/require-hook
bootstrap().catch(() => {
    // Preflight or render failed; preflight UI or error boundary handles it
});
