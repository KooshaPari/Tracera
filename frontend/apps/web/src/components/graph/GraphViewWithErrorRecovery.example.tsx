/**
 * Complete Error Recovery Integration Example
 *
 * This file demonstrates how to integrate all error recovery components
 * in a real-world graph view component with React Query.
 */

import { useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';

import { useAutoRecovery } from '@/hooks/useAutoRecovery';
import { logger } from '@/lib/logger';

import { EnhancedErrorState } from './EnhancedErrorState';
import { FlowGraphView } from './FlowGraphView';
import { GraphErrorBoundary } from './GraphErrorBoundary';
import { GraphSkeleton } from './GraphSkeleton';
import { NetworkErrorState } from './NetworkErrorState';
import { RecoveryProgress } from './RecoveryProgress';
import { TimeoutErrorState } from './TimeoutErrorState';

// Example API function
async function fetchGraphData(projectId: string) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => {
    controller.abort();
  }, 30_000);

  try {
    const response = await fetch(`/api/projects/${projectId}/graph`, {
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } finally {
    clearTimeout(timeoutId);
  }
}

interface GraphViewWithErrorRecoveryProps {
  projectId: string;
}

export function GraphViewWithErrorRecovery({ projectId }: GraphViewWithErrorRecoveryProps) {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  // Track online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
    };
    const handleOffline = () => {
      setIsOffline(true);
    };

    globalThis.addEventListener('online', handleOnline);
    globalThis.addEventListener('offline', handleOffline);

    return () => {
      globalThis.removeEventListener('online', handleOnline);
      globalThis.removeEventListener('offline', handleOffline);
    };
  }, []);

  // Fetch graph data with React Query
  const { data, error, isLoading, refetch } = useQuery({
    queryKey: ['graph', projectId],
    queryFn: async () => fetchGraphData(projectId),
    retry: false, // We handle retries ourselves
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  // Auto-recovery with exponential backoff
  const recovery = useAutoRecovery(error, refetch, {
    exponentialBackoff: true,
    maxRetries: 3,
    onMaxRetriesReached: () => {
      logger.error('[GraphView] Max retries reached, showing error state');
    },
    onRetry: (attempt) => {
      logger.info(`[GraphView] Auto-retry attempt ${attempt}/${3}`);
    },
    retryDelay: 1000,
  });

  // Determine error type
  const isNetworkError =
    error?.message?.includes('network') ?? error?.message?.includes('Failed to fetch');
  const isTimeoutError = error?.message?.includes('timeout') ?? error?.message?.includes('aborted');

  // Show loading skeleton
  if (isLoading && !data) {
    return <GraphSkeleton />;
  }

  // Show recovery progress during auto-retry
  if (recovery.isRetrying && recovery.nextRetryIn) {
    return (
      <div className='flex h-full items-center justify-center p-4'>
        <RecoveryProgress
          retryCount={recovery.retryCount}
          maxRetries={3}
          nextRetryIn={recovery.nextRetryIn}
        />
      </div>
    );
  }

  // Show error states after max retries
  if (error && recovery.retryCount >= 3) {
    // Offline error
    if (isOffline) {
      return (
        <div className='flex h-full items-center justify-center p-4'>
          <NetworkErrorState isOffline onRetry={async () => refetch()} />
        </div>
      );
    }

    // Network error
    if (isNetworkError) {
      return (
        <div className='flex h-full items-center justify-center p-4'>
          <NetworkErrorState isOffline={false} onRetry={async () => refetch()} />
        </div>
      );
    }

    // Timeout error
    if (isTimeoutError) {
      return (
        <div className='flex h-full items-center justify-center p-4'>
          <TimeoutErrorState timeout={30_000} onRetry={async () => refetch()} />
        </div>
      );
    }

    // Generic error
    return (
      <div className='flex h-full items-center justify-center p-4'>
        <EnhancedErrorState
          error={error}
          onRetry={async () => refetch()}
          onReportBug={(errorDetails) => {
            // Send to error tracking service
            logger.error('[Bug Report]', {
              component: 'GraphView',
              error: errorDetails,
              projectId,
              timestamp: new Date().toISOString(),
              userAgent: navigator.userAgent,
            });

            // You could also send to Sentry, LogRocket, etc.
            // Sentry.captureException(error, { extra: errorDetails });
          }}
          showDetails
          variant='card'
        />
      </div>
    );
  }

  // Render graph with error boundary
  return (
    <GraphErrorBoundary
      onError={(error, errorInfo) => {
        // Log to error tracking service
        logger.error('[GraphView] Caught error:', error, errorInfo);

        // Send to Sentry/LogRocket
        // Sentry.captureException(error, {
        //   Contexts: {
        //     React: {
        //       ComponentStack: errorInfo.componentStack,
        //     },
        //   },
        // });
      }}
    >
      {data ? (
        <FlowGraphView items={data.nodes} links={data.edges} projectId={projectId} />
      ) : (
        <GraphSkeleton />
      )}
    </GraphErrorBoundary>
  );
}

// Export for use in routes/pages
export default GraphViewWithErrorRecovery;

/**
 * Usage Example:
 *
 * import GraphViewWithErrorRecovery from '@/components/graph/GraphViewWithErrorRecovery.example';
 *
 * function ProjectPage({ projectId }) {
 *   return (
 *     <div className="h-screen">
 *       <GraphViewWithErrorRecovery projectId={projectId} />
 *     </div>
 *   );
 * }
 */

/**
 * Features Demonstrated:
 *
 * 1. ✅ Online/Offline Detection
 * 2. ✅ Auto-Recovery with Exponential Backoff
 * 3. ✅ Error Type Detection (Network, Timeout, Generic)
 * 4. ✅ Loading States (Skeleton)
 * 5. ✅ Recovery Progress Indicator
 * 6. ✅ Specialized Error States
 * 7. ✅ Error Boundary for Unexpected Errors
 * 8. ✅ Bug Reporting Integration
 * 9. ✅ Manual Retry Option
 * 10. ✅ Error Logging/Tracking
 *
 * Error Flow:
 *
 * 1. Component mounts
 * 2. React Query fetches data
 * 3. If error occurs:
 *    a. useAutoRecovery triggers
 *    b. Shows RecoveryProgress
 *    c. Auto-retries with backoff (1s, 2s, 4s)
 * 4. If retries fail:
 *    a. Determines error type
 *    b. Shows appropriate error component
 *    c. User can manually retry
 * 5. If unexpected error during render:
 *    a. GraphErrorBoundary catches it
 *    b. Shows error state
 *    c. Logs to tracking service
 */
