import type { Meta, StoryObj } from '@storybook/react';

import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { useAutoRecovery } from '@/hooks/useAutoRecovery';
import { logger } from '@/lib/logger';

import { EnhancedErrorState } from '../EnhancedErrorState';
import { GraphErrorBoundary } from '../GraphErrorBoundary';
import { NetworkErrorState } from '../NetworkErrorState';
import { RecoveryProgress } from '../RecoveryProgress';
import { TimeoutErrorState } from '../TimeoutErrorState';

const meta = {
  parameters: {
    layout: 'centered',
  },
  title: 'Graph/Error Recovery',
} satisfies Meta;

export default meta;

// EnhancedErrorState Stories
export const ErrorStateCard: StoryObj = {
  render: () => {
    const [retryCount, setRetryCount] = useState(0);

    return (
      <div className='w-96'>
        <EnhancedErrorState
          error='Failed to load graph data. The server returned a 500 error.'
          onRetry={() => {
            setRetryCount((c) => c + 1);
            logger.info('Retry clicked', retryCount + 1);
          }}
          onReportBug={(error) => {
            logger.info('Bug report:', error);
          }}
          variant='card'
        />
      </div>
    );
  },
};

export const ErrorStateInline: StoryObj = {
  render: () => (
    <div className='w-96'>
      <EnhancedErrorState
        error='Failed to load graph data'
        onRetry={() => logger.info('Retry clicked')}
        variant='inline'
      />
    </div>
  ),
};

export const ErrorStateWithStack: StoryObj = {
  render: () => {
    const error = new Error('Failed to fetch graph data');
    error.stack = `Error: Failed to fetch graph data
    at fetchGraphData (api.ts:42:15)
    at useGraphQuery (useGraphs.ts:28:20)
    at GraphView (GraphView.tsx:15:25)`;

    return (
      <div className='w-96'>
        <EnhancedErrorState
          error={error}
          onRetry={() => logger.info('Retry clicked')}
          showDetails
        />
      </div>
    );
  },
};

export const ErrorStateNoRetry: StoryObj = {
  render: () => (
    <div className='w-96'>
      <EnhancedErrorState error='This error cannot be retried' variant='card' />
    </div>
  ),
};

// NetworkErrorState Stories
export const NetworkError: StoryObj = {
  render: () => (
    <div className='w-96'>
      <NetworkErrorState isOffline={false} onRetry={() => logger.info('Retry clicked')} />
    </div>
  ),
};

export const OfflineError: StoryObj = {
  render: () => (
    <div className='w-96'>
      <NetworkErrorState isOffline onRetry={() => logger.info('Retry clicked')} />
    </div>
  ),
};

// TimeoutErrorState Stories
export const TimeoutError: StoryObj = {
  render: () => (
    <div className='w-96'>
      <TimeoutErrorState timeout={30_000} onRetry={() => logger.info('Retry clicked')} />
    </div>
  ),
};

export const TimeoutError60s: StoryObj = {
  render: () => (
    <div className='w-96'>
      <TimeoutErrorState timeout={60_000} onRetry={() => logger.info('Retry clicked')} />
    </div>
  ),
};

// RecoveryProgress Stories
export const RecoveryProgressInitial: StoryObj = {
  render: () => (
    <div className='w-96'>
      <RecoveryProgress retryCount={0} maxRetries={3} nextRetryIn={5000} />
    </div>
  ),
};

export const RecoveryProgressSecondAttempt: StoryObj = {
  render: () => (
    <div className='w-96'>
      <RecoveryProgress retryCount={1} maxRetries={3} nextRetryIn={10_000} />
    </div>
  ),
};

export const RecoveryProgressFinalAttempt: StoryObj = {
  render: () => (
    <div className='w-96'>
      <RecoveryProgress retryCount={2} maxRetries={3} nextRetryIn={20_000} />
    </div>
  ),
};

// GraphErrorBoundary Stories
const ErrorThrowingComponent = () => {
  throw new Error('Something went wrong in the graph component!');
};

export const ErrorBoundaryDemo: StoryObj = {
  tags: ['skip-tests'],
  parameters: {
    test: { disable: true },
  },
  render: () => (
    <div className='h-64 w-96'>
      <GraphErrorBoundary>
        <ErrorThrowingComponent />
      </GraphErrorBoundary>
    </div>
  ),
};

export const ErrorBoundaryWithCustomFallback: StoryObj = {
  tags: ['skip-tests'],
  parameters: {
    test: { disable: true },
  },
  render: () => (
    <div className='h-64 w-96'>
      <GraphErrorBoundary
        fallback={(error, reset) => (
          <div className='border-destructive rounded border p-4'>
            <h3 className='text-destructive font-semibold'>Custom Error UI</h3>
            <p className='mt-2 text-sm'>{error.message}</p>
            <Button onClick={reset} className='mt-4'>
              Reset
            </Button>
          </div>
        )}
      >
        <ErrorThrowingComponent />
      </GraphErrorBoundary>
    </div>
  ),
};

// Auto-Recovery Demo
const AutoRecoveryDemo = () => {
  const [hasError, setHasError] = useState(true);
  const [attemptCount, setAttemptCount] = useState(0);

  const retry = () => {
    setAttemptCount((c) => c + 1);
    // Simulate success after 2 retries
    if (attemptCount >= 2) {
      setHasError(false);
    }
  };

  const recovery = useAutoRecovery(hasError ? new Error('Network error') : null, retry, {
    exponentialBackoff: true,
    maxRetries: 3,
    onMaxRetriesReached: () => {
      logger.info('Max retries reached');
    },
    onRetry: (attempt) => {
      logger.info(`Retry attempt ${attempt}`);
    },
    retryDelay: 2000,
  });

  if (!hasError) {
    return (
      <div className='rounded border border-green-500 p-4'>
        <p className='text-green-700'>Success! Graph loaded.</p>
        <Button
          onClick={() => {
            setHasError(true);
            setAttemptCount(0);
          }}
          className='mt-4'
        >
          Simulate Error Again
        </Button>
      </div>
    );
  }

  if (recovery.isRetrying && recovery.nextRetryIn) {
    return (
      <RecoveryProgress
        retryCount={recovery.retryCount}
        maxRetries={3}
        nextRetryIn={recovery.nextRetryIn}
      />
    );
  }

  if (recovery.retryCount >= 3) {
    return (
      <EnhancedErrorState
        error='Failed to load after multiple attempts'
        onRetry={() => {
          setHasError(true);
          setAttemptCount(0);
        }}
      />
    );
  }

  return null;
};

export const AutoRecoveryExample: StoryObj = {
  tags: ['skip-tests'],
  parameters: {
    test: { disable: true },
  },
  render: () => (
    <div className='w-96'>
      <AutoRecoveryDemo />
    </div>
  ),
};

// Complete Integration Example
const CompleteErrorHandlingDemo = () => {
  const [errorType, setErrorType] = useState<'none' | 'network' | 'timeout' | 'generic'>('none');
  const [isRecovering, setIsRecovering] = useState(false);

  const handleRetry = () => {
    setIsRecovering(true);
    setTimeout(() => {
      setIsRecovering(false);
      setErrorType('none');
    }, 2000);
  };

  if (errorType === 'none') {
    return (
      <div className='space-y-4 p-4'>
        <div className='rounded border p-4'>
          <p className='text-muted-foreground text-sm'>Graph loaded successfully!</p>
        </div>

        <div className='space-y-2'>
          <p className='text-sm font-medium'>Simulate Errors:</p>
          <div className='flex flex-wrap gap-2'>
            <Button
              size='sm'
              variant='outline'
              onClick={() => {
                setErrorType('network');
              }}
            >
              Network Error
            </Button>
            <Button
              size='sm'
              variant='outline'
              onClick={() => {
                setErrorType('timeout');
              }}
            >
              Timeout Error
            </Button>
            <Button
              size='sm'
              variant='outline'
              onClick={() => {
                setErrorType('generic');
              }}
            >
              Generic Error
            </Button>
          </div>
        </div>
      </div>
    );
  }

  if (isRecovering) {
    return <RecoveryProgress retryCount={0} maxRetries={3} nextRetryIn={2000} />;
  }

  if (errorType === 'network') {
    return <NetworkErrorState onRetry={handleRetry} />;
  }

  if (errorType === 'timeout') {
    return <TimeoutErrorState timeout={30_000} onRetry={handleRetry} />;
  }

  return (
    <EnhancedErrorState
      error='An unexpected error occurred while loading the graph'
      onRetry={handleRetry}
      onReportBug={(error) => {
        logger.info('Bug report:', error);
        alert('Bug report submitted!');
      }}
    />
  );
};

export const CompleteIntegration: StoryObj = {
  render: () => (
    <div className='w-96'>
      <CompleteErrorHandlingDemo />
    </div>
  ),
};

// Error States Comparison
export const ErrorStatesComparison: StoryObj = {
  render: () => (
    <div className='w-[600px] space-y-4'>
      <div>
        <h3 className='mb-2 text-sm font-medium'>Network Error</h3>
        <NetworkErrorState onRetry={() => {}} />
      </div>

      <div>
        <h3 className='mb-2 text-sm font-medium'>Timeout Error</h3>
        <TimeoutErrorState timeout={30_000} onRetry={() => {}} />
      </div>

      <div>
        <h3 className='mb-2 text-sm font-medium'>Generic Error (Inline)</h3>
        <EnhancedErrorState error='Something went wrong' variant='inline' onRetry={() => {}} />
      </div>

      <div>
        <h3 className='mb-2 text-sm font-medium'>Generic Error (Card)</h3>
        <EnhancedErrorState error='Something went wrong' variant='card' onRetry={() => {}} />
      </div>

      <div>
        <h3 className='mb-2 text-sm font-medium'>Recovery Progress</h3>
        <RecoveryProgress retryCount={1} maxRetries={3} nextRetryIn={5000} />
      </div>
    </div>
  ),
};
