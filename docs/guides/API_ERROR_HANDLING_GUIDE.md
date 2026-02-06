# API Error Handling Guide

## Overview

This guide documents the comprehensive error handling system implemented for the TraceRTM frontend. The system handles network failures, validation errors, authentication issues, and provides user-friendly feedback with automatic retry capabilities.

## Architecture

The error handling system consists of four main components:

### 1. Retry Logic (`lib/retry.ts`)

Implements exponential backoff retry mechanism with intelligent error discrimination.

**Features:**
- Automatic retry on transient errors (network, 5xx, 429)
- Exponential backoff: immediate, 1s, 2s delays
- Max 3 attempts by default
- Error classification (retryable vs non-retryable)
- Callback support for retry notifications

**Example:**
```typescript
import { withRetry } from '@/lib/retry';

const result = await withRetry(
  () => createItem(data),
  {
    maxAttempts: 3,
    baseDelayMs: 1000,
    onRetry: (attempt, error) => {
      console.log(`Retrying attempt ${attempt} after:`, error);
    },
  }
);

if (result.success) {
  console.log('Item created:', result.data);
} else {
  console.error('Failed after', result.attempts, 'attempts');
}
```

### 2. Error Handler (`lib/api-error-handler.ts`)

Provides error type discrimination and user-friendly message generation.

**Error Types:**
- `'network'` - No server connectivity
- `'timeout'` - Request timeout
- `'validation'` - Client input errors (4xx)
- `'auth'` - Authorization errors (401/403)
- `'server'` - Server errors (5xx)
- `'unknown'` - Unexpected errors

**Example:**
```typescript
import { buildErrorMetadata, extractValidationErrors } from '@/lib/api-error-handler';

try {
  const item = await createItem(data);
} catch (error) {
  const metadata = buildErrorMetadata(error);
  console.log(`Error type: ${metadata.type}`);
  console.log(`User message: ${metadata.userMessage}`);
  console.log(`Retryable: ${metadata.retryable}`);

  // Extract validation errors if present
  const validationErrors = extractValidationErrors(error);
  if (validationErrors) {
    // Display field-specific errors
  }
}
```

### 3. Mutation Queue (`lib/mutation-queue.ts`)

Stores failed operations in localStorage for retry when network reconnects.

**Features:**
- Persist failed mutations locally
- Track attempt count and errors
- Automatic cleanup on success
- Query pending mutations

**Example:**
```typescript
import { queueMutation, getQueuedMutations } from '@/lib/mutation-queue';

// Queue a failed mutation
const mutationId = queueMutation({
  type: 'create_item',
  data: itemData,
  createdAt: new Date().toISOString(),
  failedAttempts: 3,
});

// Later, when reconnected:
const pending = getQueuedMutations();
for (const mutation of pending) {
  // Retry each mutation
}
```

### 4. CreateItemDialog Integration

The dialog component implements complete error handling with user feedback.

**Features:**
- Real API calls with retry logic
- Toast notifications for all error types
- Validation error display with field details
- Mutation queuing for offline support
- Auth error detection and redirect
- User-friendly error messages

## Error Handling Patterns

### Pattern 1: Simple API Call with Retry

```typescript
import { withRetry } from '@/lib/retry';
import { toast } from '@/components/ui/toaster';
import { buildErrorMetadata } from '@/lib/api-error-handler';

async function handleCreateItem(data: CreateItemInput) {
  try {
    const result = await withRetry(
      () => createItem(data),
      { maxAttempts: 3, baseDelayMs: 1000 }
    );

    if (!result.success) {
      const metadata = buildErrorMetadata(result.error);
      toast.error(metadata.userMessage);
      return;
    }

    toast.success('Item created successfully');
    return result.data;
  } catch (error) {
    toast.error('Unexpected error. Please try again.');
  }
}
```

### Pattern 2: Validation Error Handling

```typescript
import { extractValidationErrors, formatValidationErrorMessage } from '@/lib/api-error-handler';

const result = await withRetry(() => createItem(data));

if (!result.success) {
  const validationErrors = extractValidationErrors(result.error);
  if (validationErrors) {
    const message = formatValidationErrorMessage(validationErrors);
    toast.error(message);
    // Display field-specific errors to user
    return;
  }

  const metadata = buildErrorMetadata(result.error);
  toast.error(metadata.userMessage);
}
```

### Pattern 3: Network Resilience with Queuing

```typescript
import { queueMutation, removeMutationFromQueue } from '@/lib/mutation-queue';

const result = await withRetry(() => createItem(data));

if (!result.success) {
  const metadata = buildErrorMetadata(result.error);

  if (metadata.retryable) {
    // Queue for later retry
    const mutationId = queueMutation({
      type: 'create_item',
      data,
      createdAt: new Date().toISOString(),
      failedAttempts: result.attempts,
      lastError: result.error?.message,
    });

    toast.error(metadata.userMessage, {
      action: {
        label: 'Undo',
        onClick: () => {
          removeMutationFromQueue(mutationId);
          toast.success('Queued operation cancelled');
        },
      },
      description: 'Operation queued for retry when online.',
    });
  }
}
```

## Error Type Decision Tree

```
Error occurs
  ├─ Network error (TypeError with 'fetch')?
  │  └─ RETRYABLE (network issue)
  │
  ├─ Timeout error?
  │  └─ RETRYABLE (transient)
  │
  ├─ ApiError status 401 or 403?
  │  └─ NOT RETRYABLE (redirect to login)
  │
  ├─ ApiError status 4xx (except 429)?
  │  └─ NOT RETRYABLE (validation error, show field errors)
  │
  ├─ ApiError status 429?
  │  └─ RETRYABLE (rate limit)
  │
  ├─ ApiError status 5xx?
  │  └─ RETRYABLE (server error)
  │
  └─ Other error?
     └─ NOT RETRYABLE (unknown)
```

## Testing Error Handling

### Unit Tests

Test individual error handling utilities:

```bash
cd frontend/apps/web
bun run test -- src/__tests__/lib/retry.test.ts
bun run test -- src/__tests__/lib/api-error-handler.test.ts
bun run test -- src/__tests__/lib/mutation-queue.test.ts
```

### Integration Tests

Test error handling in components:

```bash
bun run test -- src/__tests__/components/CreateItemDialog.error-handling.test.tsx
```

### Manual Testing

1. **Network Error:**
   - Disable network in DevTools
   - Try to create an item
   - Verify error toast with retry option

2. **Validation Error:**
   - Submit form with missing required fields
   - Verify field-specific errors displayed

3. **Server Error:**
   - Mock API error response
   - Verify automatic retry with backoff
   - After 3 attempts, show error toast

4. **Offline Operations:**
   - Disable network during form submission
   - Verify operation queued in localStorage
   - Re-enable network
   - Verify automatic retry of queued operations

## Configuration

### Retry Settings

Customize retry behavior:

```typescript
const result = await withRetry(fn, {
  maxAttempts: 5,        // Max 5 retries instead of 3
  baseDelayMs: 2000,     // 2 second base delay
  onRetry: (attempt, error) => {
    console.log(`Attempt ${attempt}:`, error.message);
  },
});
```

### Toast Notifications

Customize toast behavior:

```typescript
import { toast } from '@/components/ui/toaster';

toast.error('Error message', {
  description: 'Additional details',
  action: {
    label: 'Retry',
    onClick: () => retryOperation(),
  },
});
```

## Best Practices

1. **Always use `withRetry` for API calls** - Don't skip retry logic
2. **Distinguish error types** - Use error metadata for appropriate handling
3. **Queue failed mutations** - Enable offline support
4. **Show user-friendly messages** - Use `getUserFriendlyMessage()`
5. **Log errors properly** - Include error metadata for debugging
6. **Handle special cases** - Redirect on auth errors, display field errors for validation
7. **Test error paths** - Include error scenario tests

## Common Scenarios

### Scenario 1: User Goes Offline During Item Creation

1. User fills form and submits
2. API call fails (network error)
3. System retries 3 times with backoff
4. After 3rd attempt fails, operation is queued
5. Toast shows: "Operation queued, will retry when online"
6. User reconnects
7. System automatically retries queued operation
8. Success: item created, toast shows "Item created"

### Scenario 2: Validation Error

1. User submits form with invalid data
2. API returns 422 with validation errors
3. System detects validation error (non-retryable)
4. Field-specific errors extracted and shown
5. User fixes errors and resubmits

### Scenario 3: Server Error (5xx)

1. User submits form
2. API returns 500
3. System retries 3 times with exponential backoff
4. After 3rd attempt, shows: "Server error. Please try again later."
5. User can manually retry

## API Error Response Format

Expected validation error format from API:

```json
{
  "status": 422,
  "message": "Validation failed",
  "errors": {
    "name": ["Name is required", "Name must be unique"],
    "email": ["Invalid email format"]
  }
}
```

Or flat format:

```json
{
  "name": ["Name is required"],
  "email": ["Invalid email format"]
}
```

## Files

- **Core Libraries:**
  - `/src/lib/retry.ts` - Retry logic with exponential backoff
  - `/src/lib/api-error-handler.ts` - Error type discrimination and messages
  - `/src/lib/mutation-queue.ts` - Offline mutation storage

- **Components:**
  - `/src/components/forms/CreateItemDialog.tsx` - Example implementation

- **Tests:**
  - `/src/__tests__/lib/retry.test.ts`
  - `/src/__tests__/lib/api-error-handler.test.ts`
  - `/src/__tests__/lib/mutation-queue.test.ts`
  - `/src/__tests__/components/CreateItemDialog.error-handling.test.tsx`

## Troubleshooting

### Retries not happening

Check that:
- Error is actually retryable (network, 5xx, 429)
- Not mistaking validation error (422) for retryable
- Max attempts not reached

### Toast not showing

Check that:
- `@/components/ui/toaster` is properly imported
- Toast library (Sonner) is installed
- Component has `<Toaster />` in DOM

### Mutations not queuing

Check that:
- localStorage is enabled in browser
- localStorage quota not exceeded
- Mutation queue format matches spec

## Performance Considerations

- **Retry backoff:** 1s + 2s = 3s max delay per failed operation
- **localStorage:** Each queued mutation ~500 bytes
- **Max queued items:** ~100 mutations in 50MB localStorage
- **Retry callbacks:** Avoid expensive operations in `onRetry`

## Future Improvements

1. **Exponential backoff with jitter** - Reduce thundering herd
2. **Network status detection** - Use navigator.onLine API
3. **Request deduplication** - Avoid duplicate in-flight requests
4. **Circuit breaker pattern** - Stop retrying failing endpoints
5. **Error analytics** - Track error rates and types
6. **Custom error handlers** - Per-endpoint error handling
