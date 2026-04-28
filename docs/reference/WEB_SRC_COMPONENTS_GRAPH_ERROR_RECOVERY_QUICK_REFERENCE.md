# Error Recovery - Quick Reference

## Components

### EnhancedErrorState

Rich error display with retry and bug reporting.

```typescript
<EnhancedErrorState
  error={error}
  onRetry={() => refetch()}
  onReportBug={(details) => logError(details)}
  variant="card" // or "inline"
  showDetails={true}
/>
```

### GraphErrorBoundary

React error boundary for graph components.

```typescript
<GraphErrorBoundary onError={(err, info) => log(err)}>
  <GraphComponent />
</GraphErrorBoundary>
```

### NetworkErrorState

Specialized network/offline error display.

```typescript
<NetworkErrorState
  isOffline={!navigator.onLine}
  onRetry={() => refetch()}
/>
```

### TimeoutErrorState

Timeout error display with duration.

```typescript
<TimeoutErrorState
  timeout={30000}
  onRetry={() => refetch()}
/>
```

### RecoveryProgress

Auto-recovery progress indicator.

```typescript
<RecoveryProgress
  retryCount={recovery.retryCount}
  maxRetries={3}
  nextRetryIn={recovery.nextRetryIn}
/>
```

## Hooks

### useAutoRecovery

Automatic error recovery with exponential backoff.

```typescript
const recovery = useAutoRecovery(error, refetch, {
  maxRetries: 3,
  retryDelay: 1000,
  exponentialBackoff: true,
  onRetry: (attempt) => console.log(`Retry ${attempt}`),
  onMaxRetriesReached: () => console.log('Failed'),
});

// Returns:
// - isRetrying: boolean
// - retryCount: number
// - nextRetryIn: number | null
```

## Complete Integration Pattern

```typescript
function GraphView() {
  const { data, error, refetch } = useQuery(...);

  const recovery = useAutoRecovery(error, refetch, {
    maxRetries: 3,
    exponentialBackoff: true,
  });

  // Show recovery progress
  if (recovery.isRetrying && recovery.nextRetryIn) {
    return <RecoveryProgress {...recovery} maxRetries={3} />;
  }

  // Show error after max retries
  if (error && recovery.retryCount >= 3) {
    if (!navigator.onLine) {
      return <NetworkErrorState isOffline onRetry={refetch} />;
    }

    if (error.message.includes('timeout')) {
      return <TimeoutErrorState onRetry={refetch} />;
    }

    return <EnhancedErrorState error={error} onRetry={refetch} />;
  }

  // Wrap in error boundary
  return (
    <GraphErrorBoundary>
      {data ? <Graph data={data} /> : <Loading />}
    </GraphErrorBoundary>
  );
}
```

## Error Types

```typescript
interface ErrorDetails {
  message: string;
  stack?: string;
  code?: string;
  timestamp?: Date;
}
```

## Props Summary

| Component          | Key Props                           | Optional Props                             |
| ------------------ | ----------------------------------- | ------------------------------------------ |
| EnhancedErrorState | error                               | onRetry, onReportBug, showDetails, variant |
| GraphErrorBoundary | children                            | fallback, onError                          |
| NetworkErrorState  | -                                   | isOffline, onRetry                         |
| TimeoutErrorState  | -                                   | timeout, onRetry                           |
| RecoveryProgress   | retryCount, maxRetries, nextRetryIn | -                                          |

## Auto-Recovery Options

| Option              | Type              | Default | Description                 |
| ------------------- | ----------------- | ------- | --------------------------- |
| maxRetries          | number            | 3       | Maximum retry attempts      |
| retryDelay          | number            | 1000    | Initial delay in ms         |
| exponentialBackoff  | boolean           | true    | Use exponential backoff     |
| onRetry             | (attempt) => void | -       | Called on each retry        |
| onMaxRetriesReached | () => void        | -       | Called when max retries hit |

## Backoff Schedule (exponential)

| Attempt | Delay |
| ------- | ----- |
| 1       | 1s    |
| 2       | 2s    |
| 3       | 4s    |
| 4       | 8s    |

## Common Patterns

### Detect Error Type

```typescript
const isOffline = !navigator.onLine;
const isNetwork = error?.message?.includes('network');
const isTimeout = error?.message?.includes('timeout');
```

### Copy Error to Clipboard

```typescript
// Built into EnhancedErrorState
// User clicks "Copy error" button
```

### Custom Error Fallback

```typescript
<GraphErrorBoundary
  fallback={(error, reset) => (
    <CustomErrorUI error={error} onReset={reset} />
  )}
>
  <Component />
</GraphErrorBoundary>
```

### Disable Auto-Recovery

```typescript
// Don't pass error to useAutoRecovery
// Or set maxRetries to 0
const recovery = useAutoRecovery(null, refetch);
```

## Files

- Components: `/components/graph/EnhancedErrorState.tsx` etc.
- Hook: `/hooks/useAutoRecovery.ts`
- Tests: `/__tests__/components/graph/ErrorRecovery.test.tsx`
- Stories: `/components/graph/__stories__/ErrorRecovery.stories.tsx`
- Example: `/components/graph/GraphViewWithErrorRecovery.example.tsx`
- Guide: `/components/graph/ERROR_RECOVERY_EXAMPLE.md`

## Exports

```typescript
// From @/components/graph
import {
  EnhancedErrorState,
  GraphErrorBoundary,
  NetworkErrorState,
  TimeoutErrorState,
  RecoveryProgress,
} from '@/components/graph';

// From @/hooks
import { useAutoRecovery } from '@/hooks';
```

## Best Practices

1. ✅ Use GraphErrorBoundary at top level
2. ✅ Enable auto-recovery for transient errors
3. ✅ Show appropriate error type (network/timeout/generic)
4. ✅ Always provide retry option
5. ✅ Log errors for debugging
6. ✅ Use exponential backoff
7. ✅ Set reasonable retry limits
8. ✅ Show progress during recovery

## See Also

- Full examples: `ERROR_RECOVERY_EXAMPLE.md`
- Real integration: `GraphViewWithErrorRecovery.example.tsx`
- Storybook: Run `bun run storybook` and navigate to Graph/Error Recovery
