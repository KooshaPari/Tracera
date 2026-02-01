# Error Recovery Integration Example

## Basic Usage

### 1. Using Enhanced Error State

```typescript
import { EnhancedErrorState } from '@/components/graph/EnhancedErrorState';

function MyComponent() {
  const [error, setError] = useState<Error | null>(null);

  const handleRetry = () => {
    setError(null);
    // Retry logic
  };

  if (error) {
    return (
      <EnhancedErrorState
        error={error}
        onRetry={handleRetry}
        variant="card"
      />
    );
  }

  return <div>Content</div>;
}
```

### 2. Using Error Boundary

```typescript
import { GraphErrorBoundary } from '@/components/graph/GraphErrorBoundary';

function App() {
  return (
    <GraphErrorBoundary
      onError={(error, errorInfo) => {
        console.error('Caught error:', error, errorInfo);
        // Send to error tracking service
      }}
    >
      <MyGraphComponent />
    </GraphErrorBoundary>
  );
}
```

### 3. Using Auto-Recovery

```typescript
import { useAutoRecovery } from '@/hooks/useAutoRecovery';
import { RecoveryProgress } from '@/components/graph/RecoveryProgress';
import { EnhancedErrorState } from '@/components/graph/EnhancedErrorState';

function MyComponent() {
  const [error, setError] = useState<Error | null>(null);
  const { data, refetch } = useQuery(...);

  const recovery = useAutoRecovery(error, refetch, {
    maxRetries: 3,
    retryDelay: 1000,
    exponentialBackoff: true,
    onRetry: (attempt) => {
      console.log(`Retry attempt ${attempt}`);
    },
    onMaxRetriesReached: () => {
      console.log('Max retries reached');
    },
  });

  if (recovery.isRetrying && recovery.nextRetryIn) {
    return (
      <RecoveryProgress
        retryCount={recovery.retryCount}
        maxRetries={3}
        nextRetryIn={recovery.nextRetryIn}
      />
    );
  }

  if (error && recovery.retryCount >= 3) {
    return (
      <EnhancedErrorState
        error={error}
        onRetry={() => {
          setError(null);
          refetch();
        }}
      />
    );
  }

  return <div>Content</div>;
}
```

### 4. Network Error Handling

```typescript
import { NetworkErrorState } from '@/components/graph/NetworkErrorState';

function MyComponent() {
  const [isOffline, setIsOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOffline(false);
    const handleOffline = () => setIsOffline(true);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  if (isOffline) {
    return <NetworkErrorState isOffline onRetry={refetch} />;
  }

  return <div>Content</div>;
}
```

### 5. Timeout Error Handling

```typescript
import { TimeoutErrorState } from '@/components/graph/TimeoutErrorState';

function MyComponent() {
  const [timedOut, setTimedOut] = useState(false);

  useEffect(() => {
    const timeout = setTimeout(() => {
      setTimedOut(true);
    }, 30000);

    return () => clearTimeout(timeout);
  }, []);

  if (timedOut) {
    return (
      <TimeoutErrorState
        timeout={30000}
        onRetry={() => {
          setTimedOut(false);
          refetch();
        }}
      />
    );
  }

  return <div>Content</div>;
}
```

## Complete Integration Example

```typescript
import { useState } from 'react';
import { GraphErrorBoundary } from '@/components/graph/GraphErrorBoundary';
import { EnhancedErrorState } from '@/components/graph/EnhancedErrorState';
import { NetworkErrorState } from '@/components/graph/NetworkErrorState';
import { TimeoutErrorState } from '@/components/graph/TimeoutErrorState';
import { RecoveryProgress } from '@/components/graph/RecoveryProgress';
import { useAutoRecovery } from '@/hooks/useAutoRecovery';
import { useQuery } from '@tanstack/react-query';

function GraphViewWithErrorRecovery() {
  const { data, error, refetch, isLoading } = useQuery({
    queryKey: ['graph'],
    queryFn: fetchGraphData,
    retry: false, // We handle retries ourselves
  });

  const recovery = useAutoRecovery(error as Error | null, refetch, {
    maxRetries: 3,
    retryDelay: 1000,
    exponentialBackoff: true,
  });

  // Determine error type
  const isNetworkError = error?.message?.includes('network');
  const isTimeoutError = error?.message?.includes('timeout');
  const isOffline = !navigator.onLine;

  // Show recovery progress
  if (recovery.isRetrying && recovery.nextRetryIn) {
    return (
      <RecoveryProgress
        retryCount={recovery.retryCount}
        maxRetries={3}
        nextRetryIn={recovery.nextRetryIn}
      />
    );
  }

  // Show error states
  if (error && recovery.retryCount >= 3) {
    if (isOffline) {
      return <NetworkErrorState isOffline onRetry={refetch} />;
    }

    if (isNetworkError) {
      return <NetworkErrorState onRetry={refetch} />;
    }

    if (isTimeoutError) {
      return <TimeoutErrorState timeout={30000} onRetry={refetch} />;
    }

    return (
      <EnhancedErrorState
        error={error as Error}
        onRetry={refetch}
        onReportBug={(errorDetails) => {
          // Send to bug tracking
          console.error('Bug report:', errorDetails);
        }}
      />
    );
  }

  return (
    <GraphErrorBoundary>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <GraphView data={data} />
      )}
    </GraphErrorBoundary>
  );
}
```

## Error Types

### Error Details Structure

```typescript
interface ErrorDetails {
  message: string;
  stack?: string;
  code?: string;
  timestamp?: Date;
}
```

### Error Variants

- **inline**: Compact alert-style error
- **card**: Full card with details and actions

### Auto-Recovery Options

```typescript
interface AutoRecoveryOptions {
  maxRetries?: number;           // Default: 3
  retryDelay?: number;           // Default: 1000ms
  exponentialBackoff?: boolean;  // Default: true
  onRetry?: (attempt: number) => void;
  onMaxRetriesReached?: () => void;
}
```

## Best Practices

1. **Use Error Boundary at the top level** - Catch unexpected React errors
2. **Implement auto-recovery for transient failures** - Network issues, timeouts
3. **Show appropriate error messages** - Network vs timeout vs general errors
4. **Provide retry mechanisms** - Always give users a way to recover
5. **Log errors for debugging** - Use onError callbacks to track issues
6. **Use exponential backoff** - Prevents overwhelming servers during issues
7. **Set reasonable retry limits** - Don't retry indefinitely
8. **Show progress during recovery** - Keep users informed

## Error Flow

```
Error Occurs
    ↓
Auto-Recovery Triggered (if enabled)
    ↓
Show Recovery Progress (with countdown)
    ↓
Retry Automatically
    ↓
Success? → Resume Normal Operation
    ↓ (No)
Max Retries Reached?
    ↓ (Yes)
Show Appropriate Error State
    ↓
User Can Manually Retry
```
