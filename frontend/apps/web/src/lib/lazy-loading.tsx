import { type ComponentType, lazy, type ReactNode, Suspense } from 'react';

import { cn } from '@/lib/utils';

/**
 * Loading skeleton component for lazy-loaded components
 * Shows a minimal loading state while chunks are downloading
 */
export function ChunkLoadingSkeleton({ message = 'Loading...' }: { message?: string }) {
  return (
    <div className='bg-muted/50 flex min-h-96 items-center justify-center'>
      <div className='flex flex-col items-center gap-4'>
        <div className='border-primary h-8 w-8 animate-spin rounded-full border-2 border-t-transparent' />
        <p className='text-muted-foreground text-sm'>{message}</p>
      </div>
    </div>
  );
}

/**
 * Standardized loading skeleton for list/table views.
 * Use in place of ad-hoc Skeleton grids for consistent UX.
 */
export function ListLoadingSkeleton({
  message = 'Loading...',
  rowCount = 6,
  className,
  dataTestId,
}: {
  message?: string;
  rowCount?: number;
  className?: string;
  dataTestId?: string;
}) {
  return (
    <div
      className={className ?? 'animate-pulse space-y-8 p-6'}
      role='status'
      aria-live='polite'
      aria-atomic='true'
      data-testid={dataTestId}
    >
      <p className='text-muted-foreground text-xs'>{message}</p>
      <div className='flex items-center gap-2'>
        <div className='border-primary h-4 w-4 animate-spin rounded-full border-2 border-t-transparent' />
        <div className='bg-muted h-10 w-48 rounded-md' />
      </div>
      <div className='space-y-4'>
        {Array.from({ length: rowCount }, (_, i) => (
          <div key={i} className='bg-muted h-16 w-full rounded-xl' aria-hidden />
        ))}
      </div>
    </div>
  );
}

/**
 * Modal-style overlay for in-place loading feedback.
 */
export function ModalLoadingOverlay({
  message = 'Loading...',
  detail,
  className,
  isVisible = true,
}: {
  message?: string;
  detail?: string;
  className?: string;
  isVisible?: boolean;
}) {
  if (!isVisible) {
    return null;
  }

  return (
    <div
      className='bg-background/70 fixed inset-0 z-50 flex items-center justify-center backdrop-blur-sm'
      role='presentation'
    >
      <div
        className={cn(
          'border-border/60 bg-card/95 text-foreground flex min-w-[280px] max-w-sm flex-col items-center gap-3 rounded-2xl border px-6 py-5 text-center shadow-xl',
          className,
        )}
        role='status'
        aria-live='polite'
        aria-atomic='true'
      >
        <div className='border-primary h-10 w-10 animate-spin rounded-full border-4 border-t-transparent' />
        <div className='text-sm font-semibold'>{message}</div>
        {detail ? <p className='text-muted-foreground text-xs'>{detail}</p> : null}
      </div>
    </div>
  );
}

/**
 * Error fallback component for failed lazy loads
 */
export function ChunkErrorFallback({ error, retry }: { error: Error; retry: () => void }) {
  return (
    <div className='bg-destructive/5 border-destructive/20 flex min-h-96 items-center justify-center rounded-lg border p-4'>
      <div className='flex flex-col items-center gap-4 text-center'>
        <div className='text-destructive text-sm font-semibold'>Failed to load this component</div>
        <p className='text-muted-foreground max-w-sm text-xs'>
          {error.message || 'An unexpected error occurred while loading this feature.'}
        </p>
        <button
          onClick={retry}
          className='bg-primary text-primary-foreground hover:bg-primary/90 rounded px-3 py-1 text-xs'
        >
          Try again
        </button>
      </div>
    </div>
  );
}

/**
 * Unified error fallback for list rows (e.g. table row, list item).
 * Use when a single row/item fails to load or fails an action.
 */
export function ListItemErrorFallback({
  message = 'Failed to load',
  detail,
  retry,
  className,
}: {
  message?: string;
  detail?: string;
  retry?: () => void;
  className?: string;
}) {
  return (
    <div
      className={
        className ??
        'border-destructive/20 bg-destructive/5 text-destructive flex items-center gap-3 rounded-lg border p-3'
      }
      role='alert'
    >
      <span className='shrink-0 text-sm font-medium'>{message}</span>
      {detail && (
        <span className='text-muted-foreground min-w-0 flex-1 truncate text-xs'>{detail}</span>
      )}
      {retry && (
        <button
          type='button'
          onClick={retry}
          className='bg-primary text-primary-foreground hover:bg-primary/90 shrink-0 rounded px-2 py-1 text-xs'
        >
          Retry
        </button>
      )}
    </div>
  );
}

/**
 * Unified error fallback for cards (e.g. search result card, detail card, view-level error).
 * Use when a card or view fails to load or shows an error state.
 */
export function CardErrorFallback({
  title = 'Something went wrong',
  message,
  error,
  retry,
  className,
}: {
  title?: string;
  message?: string;
  error?: Error | null;
  retry?: () => void;
  className?: string;
}) {
  const displayMessage =
    message ?? (error?.message || 'An unexpected error occurred. Please try again.');
  return (
    <div
      className={
        className ??
        'border-destructive/20 bg-destructive/5 flex flex-col items-center justify-center rounded-lg border p-6 text-center'
      }
      role='alert'
    >
      <p className='text-destructive text-sm font-semibold'>{title}</p>
      <p className='text-muted-foreground mt-1 max-w-sm text-xs'>{displayMessage}</p>
      {retry && (
        <button
          type='button'
          onClick={retry}
          className='bg-primary text-primary-foreground hover:bg-primary/90 mt-4 rounded px-3 py-1.5 text-xs'
        >
          Try again
        </button>
      )}
    </div>
  );
}

/**
 * Wraps a lazy component with Suspense boundary and error handling
 * Usage: useLazyComponent(() => import('./HeavyComponent'))
 */
export function useLazyComponent<P extends Record<string, any>>(
  importFn: () => Promise<{ default: ComponentType<P> }>,
  fallback?: ReactNode,
) {
  const Component = lazy(importFn);

  return (props: P) => (
    <Suspense fallback={fallback || <ChunkLoadingSkeleton />}>
      <Component {...props} />
    </Suspense>
  );
}

/**
 * Suspense boundary wrapper for lazy components with consistent styling
 */
export function LazyComponentBoundary({
  children,
  fallback,
}: {
  children: ReactNode;
  fallback?: ReactNode;
  errorFallback?: (error: Error) => ReactNode;
}) {
  return (
    <Suspense fallback={fallback || <ChunkLoadingSkeleton message='Loading view...' />}>
      {children}
    </Suspense>
  );
}
