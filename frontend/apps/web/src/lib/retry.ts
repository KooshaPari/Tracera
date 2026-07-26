/**
 * Retry Logic with Exponential Backoff
 *
 * Implements robust retry mechanism for transient API failures:
 * - Exponential backoff: 0ms, 1s, 2s
 * - Max 3 attempts total
 * - Only retries on transient errors (network, 5xx, 429)
 * - Skips retries on client errors (4xx), auth errors (401/403), validation failures
 */

import { ApiError } from '@/api/client-errors';

export interface RetryOptions {
  maxAttempts?: number | undefined;
  baseDelayMs?: number | undefined;
  onRetry?: ((attempt: number, error: Error) => void) | undefined;
}

export interface RetryResult<T> {
  success: boolean;
  data?: T | undefined;
  error?: Error | undefined;
  attempts: number;
  lastError?: Error | undefined;
}

/**
 * Determines if an error is retryable
 * Retryable: network errors, timeouts, 5xx, 429
 * Not retryable: 4xx (except 429), 401, 403, validation errors
 */
export function isRetryableError(error: unknown): boolean {
  // Network errors are retryable
  if (error instanceof TypeError) {
    const message = error.message.toLowerCase();
    return (
      message.includes('fetch') ||
      message.includes('network') ||
      message.includes('failed to fetch') ||
      message.includes('connection refused') ||
      message.includes('timeout')
    );
  }

  // Check ApiError status codes
  if (error instanceof ApiError) {
    const { status } = error;
    // 5xx server errors are retryable
    if (status >= 500) {
      return true;
    }
    // 429 Too Many Requests is retryable
    if (status === 429) {
      return true;
    }
    // Other 4xx errors (400, 422, etc.) are not retryable
    if (status >= 400 && status < 500) {
      return false;
    }
    // Unknown status - don't retry to be safe
    return false;
  }

  // Generic Error - treat as non-retryable
  return false;
}

/**
 * Calculate delay with exponential backoff
 * Attempt 1: 0ms (immediate first retry)
 * Attempt 2: 1000ms (1 second)
 * Attempt 3: 2000ms (2 seconds)
 */
function getBackoffDelay(attempt: number, baseDelayMs: number): number {
  if (attempt === 1) {
    return 0; // First retry is immediate
  }
  return baseDelayMs * (attempt - 1);
}

/**
 * Retry a function with exponential backoff
 *
 * @param fn - Async function to retry
 * @param options - Retry options (maxAttempts, baseDelayMs, onRetry)
 * @returns RetryResult with success status, data, error, and attempt count
 *
 * @example
 * const result = await withRetry(
 *   () => createItem(data),
 *   { maxAttempts: 3, baseDelayMs: 1000 }
 * );
 * if (result.success) {
 *   console.log('Item created:', result.data);
 * } else {
 *   console.error('Failed after', result.attempts, 'attempts:', result.error);
 * }
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {},
): Promise<RetryResult<T>> {
  const { maxAttempts = 3, baseDelayMs = 1000, onRetry } = options;

  let lastError: Error | undefined;

  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
    try {
      const data = await fn();
      return {
        attempts: attempt + 1,
        data,
        success: true,
      };
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      // Check if we should retry
      if (!isRetryableError(error) || attempt === maxAttempts - 1) {
        return {
          attempts: attempt + 1,
          error: lastError,
          lastError,
          success: false,
        };
      }

      // Calculate delay and notify
      const delay = getBackoffDelay(attempt + 1, baseDelayMs);
      onRetry?.(attempt + 2, lastError); // Notify about next attempt (attempt + 2)

      // Wait before retrying
      if (delay > 0) {
        await new Promise((resolve) => setTimeout(resolve, delay));
      }
    }
  }

  // Should not reach here, but handle it anyway
  return {
    attempts: maxAttempts,
    error: lastError,
    lastError,
    success: false,
  };
}

/**
 * Decorator for retry - wraps async function with retry logic
 * @example
 * const retryableCreate = withRetryDecorator(createItem, { maxAttempts: 3 });
 * const result = await retryableCreate(data);
 */
export function withRetryDecorator<T, Args extends unknown[]>(
  fn: (...args: Args) => Promise<T>,
  options: RetryOptions = {},
): (...args: Args) => Promise<RetryResult<T>> {
  return (...args: Args) => withRetry(() => fn(...args), options);
}

/**
 * Check if an error is a network error (no server connectivity)
 */
export function isNetworkError(error: unknown): boolean {
  if (error instanceof TypeError) {
    const message = error.message.toLowerCase();
    return (
      message.includes('fetch') ||
      message.includes('network') ||
      message.includes('failed to fetch') ||
      message.includes('connection')
    );
  }
  return false;
}

/**
 * Check if an error is a timeout
 */
export function isTimeoutError(error: unknown): boolean {
  if (error instanceof Error) {
    return error.message.toLowerCase().includes('timeout');
  }
  return false;
}

/**
 * Check if an error is a validation error (4xx but not 429)
 */
export function isValidationError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.status >= 400 && error.status < 500 && error.status !== 429;
  }
  return false;
}

/**
 * Check if an error is an auth error (401 or 403)
 */
export function isAuthError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.status === 401 || error.status === 403;
  }
  return false;
}

/**
 * Check if an error is a server error (5xx)
 */
export function isServerError(error: unknown): boolean {
  if (error instanceof ApiError) {
    return error.status >= 500;
  }
  return false;
}

// Re-export from api-error-handler for convenience
export {
  getErrorType,
  getUserFriendlyMessage,
  buildErrorMetadata,
  extractValidationErrors,
  formatValidationErrorMessage,
} from '@/lib/api-error-handler';
