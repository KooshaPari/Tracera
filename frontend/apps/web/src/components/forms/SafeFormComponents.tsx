/**
 * Safe Form Components - Form components wrapped with error boundaries
 *
 * This file provides error-boundary-wrapped versions of critical form components
 * to prevent form errors from crashing the entire application.
 */

import { AlertCircle } from 'lucide-react';
import { Suspense, lazy } from 'react';

import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Button } from '@tracertm/ui/components/Button';
import { Skeleton } from '@tracertm/ui/components/Skeleton';

// Lazy load form components for better code splitting
const CreateItemForm = lazy(async () =>
  import('./CreateItemForm').then((m) => ({ default: m.CreateItemForm })),
);
const CreateProblemForm = lazy(async () =>
  import('./CreateProblemForm').then((m) => ({ default: m.CreateProblemForm })),
);
const CreateProcessForm = lazy(async () =>
  import('./CreateProcessForm').then((m) => ({ default: m.CreateProcessForm })),
);
const CreateTestCaseForm = lazy(async () =>
  import('./CreateTestCaseForm').then((m) => ({
    default: m.CreateTestCaseForm,
  })),
);
const CreateProjectForm = lazy(async () =>
  import('./CreateProjectForm').then((m) => ({ default: m.CreateProjectForm })),
);
const CreateLinkForm = lazy(async () =>
  import('./CreateLinkForm').then((m) => ({ default: m.CreateLinkForm })),
);

// Loading fallback for form components
function FormLoadingFallback() {
  return (
    <div className='space-y-4 p-4'>
      <Skeleton className='h-10 w-full' />
      <Skeleton className='h-32 w-full' />
      <Skeleton className='h-10 w-full' />
      <div className='flex justify-end gap-2'>
        <Skeleton className='h-10 w-24' />
        <Skeleton className='h-10 w-24' />
      </div>
    </div>
  );
}

// Error fallback for form components
function FormErrorFallback(error: Error, reset: () => void) {
  return (
    <div className='border-destructive/50 bg-destructive/5 flex min-h-[300px] items-center justify-center rounded-lg border p-6'>
      <div className='max-w-md space-y-4 text-center'>
        <div className='flex justify-center'>
          <AlertCircle className='text-destructive h-12 w-12' />
        </div>
        <h3 className='text-destructive text-lg font-semibold'>Form Error</h3>
        <p className='text-muted-foreground text-sm'>{error.message || 'Unable to load form'}</p>
        <div className='flex justify-center gap-2'>
          <Button variant='outline' onClick={reset}>
            Try Again
          </Button>
          <Button
            variant='ghost'
            onClick={() => {
              globalThis.location.reload();
            }}
          >
            Reload Page
          </Button>
        </div>
      </div>
    </div>
  );
}

/**
 * Safe wrapper for CreateItemForm with error boundary and lazy loading
 */
export function SafeCreateItemForm(props: React.ComponentProps<typeof CreateItemForm>) {
  return (
    <ErrorBoundary name='CreateItemForm' fallback={FormErrorFallback}>
      <Suspense fallback={<FormLoadingFallback />}>
        <CreateItemForm {...props} />
      </Suspense>
    </ErrorBoundary>
  );
}

/**
 * Safe wrapper for CreateProblemForm with error boundary and lazy loading
 */
export function SafeCreateProblemForm(props: React.ComponentProps<typeof CreateProblemForm>) {
  return (
    <ErrorBoundary name='CreateProblemForm' fallback={FormErrorFallback}>
      <Suspense fallback={<FormLoadingFallback />}>
        <CreateProblemForm {...props} />
      </Suspense>
    </ErrorBoundary>
  );
}

/**
 * Safe wrapper for CreateProcessForm with error boundary and lazy loading
 */
export function SafeCreateProcessForm(props: React.ComponentProps<typeof CreateProcessForm>) {
  return (
    <ErrorBoundary name='CreateProcessForm' fallback={FormErrorFallback}>
      <Suspense fallback={<FormLoadingFallback />}>
        <CreateProcessForm {...props} />
      </Suspense>
    </ErrorBoundary>
  );
}

/**
 * Safe wrapper for CreateTestCaseForm with error boundary and lazy loading
 */
export function SafeCreateTestCaseForm(props: React.ComponentProps<typeof CreateTestCaseForm>) {
  return (
    <ErrorBoundary name='CreateTestCaseForm' fallback={FormErrorFallback}>
      <Suspense fallback={<FormLoadingFallback />}>
        <CreateTestCaseForm {...props} />
      </Suspense>
    </ErrorBoundary>
  );
}

/**
 * Safe wrapper for CreateProjectForm with error boundary and lazy loading
 */
export function SafeCreateProjectForm(props: React.ComponentProps<typeof CreateProjectForm>) {
  return (
    <ErrorBoundary name='CreateProjectForm' fallback={FormErrorFallback}>
      <Suspense fallback={<FormLoadingFallback />}>
        <CreateProjectForm {...props} />
      </Suspense>
    </ErrorBoundary>
  );
}

/**
 * Safe wrapper for CreateLinkForm with error boundary and lazy loading
 */
export function SafeCreateLinkForm(props: React.ComponentProps<typeof CreateLinkForm>) {
  return (
    <ErrorBoundary name='CreateLinkForm' fallback={FormErrorFallback}>
      <Suspense fallback={<FormLoadingFallback />}>
        <CreateLinkForm {...props} />
      </Suspense>
    </ErrorBoundary>
  );
}
