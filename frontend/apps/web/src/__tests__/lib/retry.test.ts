import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

import { ApiError } from '@/api/client-errors';
import {
  isAuthError,
  isNetworkError,
  isRetryableError,
  isServerError,
  isTimeoutError,
  isValidationError,
  withRetry,
} from '@/lib/retry';

// Note: These error type checks are re-exported from api-error-handler
// but imported directly from retry.ts for testing
function createNetworkError(message: string): TypeError {
  return new TypeError(`Failed to fetch: ${message}`);
}

describe('Retry Logic', () => {
  describe('isRetryableError', () => {
    it('should retry network errors', () => {
      const error = createNetworkError('network error');
      expect(isRetryableError(error)).toBe(true);
    });

    it('should retry 5xx server errors', () => {
      const error = new ApiError(500, 'Internal Server Error');
      expect(isRetryableError(error)).toBe(true);
    });

    it('should retry 429 rate limit errors', () => {
      const error = new ApiError(429, 'Too Many Requests');
      expect(isRetryableError(error)).toBe(true);
    });

    it('should not retry 4xx client errors (except 429)', () => {
      const error400 = new ApiError(400, 'Bad Request');
      const error422 = new ApiError(422, 'Validation Error');
      expect(isRetryableError(error400)).toBe(false);
      expect(isRetryableError(error422)).toBe(false);
    });

    it('should not retry 401 auth errors', () => {
      const error = new ApiError(401, 'Unauthorized');
      expect(isRetryableError(error)).toBe(false);
    });

    it('should not retry 403 forbidden errors', () => {
      const error = new ApiError(403, 'Forbidden');
      expect(isRetryableError(error)).toBe(false);
    });
  });

  describe('error type checks', () => {
    it('isNetworkError should detect network errors', () => {
      expect(isNetworkError(createNetworkError('test'))).toBe(true);
      expect(isNetworkError(new ApiError(500, 'Server Error'))).toBe(false);
    });

    it('isTimeoutError should detect timeout errors', () => {
      expect(isTimeoutError(new Error('Request timeout'))).toBe(true);
      expect(isTimeoutError(new Error('Other error'))).toBe(false);
    });

    it('isValidationError should detect 4xx errors', () => {
      expect(isValidationError(new ApiError(400, 'Bad Request'))).toBe(true);
      expect(isValidationError(new ApiError(422, 'Validation Error'))).toBe(true);
      expect(isValidationError(new ApiError(500, 'Server Error'))).toBe(false);
    });

    it('isAuthError should detect 401/403 errors', () => {
      expect(isAuthError(new ApiError(401, 'Unauthorized'))).toBe(true);
      expect(isAuthError(new ApiError(403, 'Forbidden'))).toBe(true);
      expect(isAuthError(new ApiError(400, 'Bad Request'))).toBe(false);
    });

    it('isServerError should detect 5xx errors', () => {
      expect(isServerError(new ApiError(500, 'Internal Server Error'))).toBe(true);
      expect(isServerError(new ApiError(503, 'Service Unavailable'))).toBe(true);
      expect(isServerError(new ApiError(400, 'Bad Request'))).toBe(false);
    });
  });

  describe('withRetry', () => {
    beforeEach(() => {
      vi.clearAllMocks();
      vi.useFakeTimers();
    });

    afterEach(() => {
      vi.useRealTimers();
    });

    it('should succeed on first try', async () => {
      const fn = vi.fn().mockResolvedValue('success');
      const result = await withRetry(fn);

      expect(result.success).toBe(true);
      expect(result.data).toBe('success');
      expect(result.attempts).toBe(1);
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should retry on network error and eventually succeed', async () => {
      const fn = vi
        .fn()
        .mockRejectedValueOnce(createNetworkError('offline'))
        .mockResolvedValueOnce('success');

      const result = await withRetry(fn, { maxAttempts: 3 });

      expect(result.success).toBe(true);
      expect(result.data).toBe('success');
      expect(result.attempts).toBe(2);
      expect(fn).toHaveBeenCalledTimes(2);
    });

    it('should not retry on validation error', async () => {
      const fn = vi.fn().mockRejectedValue(new ApiError(422, 'Validation Error'));

      const result = await withRetry(fn, { maxAttempts: 3 });

      expect(result.success).toBe(false);
      expect(result.attempts).toBe(1);
      expect(fn).toHaveBeenCalledTimes(1);
    });

    it('should stop after maxAttempts', { timeout: 10000 }, async () => {
      vi.useFakeTimers();

      const fn = vi.fn().mockRejectedValue(new ApiError(500, 'Server Error'));

      const promise = withRetry(fn, { maxAttempts: 3, baseDelayMs: 100 });

      // Advance through all retries
      await vi.advanceTimersByTimeAsync(0);
      await vi.advanceTimersByTimeAsync(100);
      await vi.advanceTimersByTimeAsync(200);

      const result = await promise;

      expect(result.success).toBe(false);
      expect(result.attempts).toBe(3);
      expect(fn).toHaveBeenCalledTimes(3);

      vi.useRealTimers();
    });

    it('should call onRetry callback', async () => {
      const onRetry = vi.fn();
      const fn = vi
        .fn()
        .mockRejectedValueOnce(new ApiError(500, 'Server Error'))
        .mockResolvedValueOnce('success');

      await withRetry(fn, { maxAttempts: 3, onRetry });

      expect(onRetry).toHaveBeenCalledTimes(1);
      expect(onRetry).toHaveBeenCalledWith(2, expect.any(ApiError));
    });

    it('should apply exponential backoff delays', async () => {
      vi.useFakeTimers();
      const delayFn = vi.fn();

      const fn = vi
        .fn()
        .mockRejectedValueOnce(new ApiError(500, 'Server Error'))
        .mockRejectedValueOnce(new ApiError(500, 'Server Error'))
        .mockResolvedValueOnce('success');

      const promise = withRetry(fn, {
        baseDelayMs: 1000,
        maxAttempts: 3,
        onRetry: delayFn,
      });

      // First retry is immediate
      await vi.advanceTimersByTimeAsync(0);
      expect(fn).toHaveBeenCalledTimes(2);

      // Second retry has 1s delay
      await vi.advanceTimersByTimeAsync(1000);
      expect(fn).toHaveBeenCalledTimes(3);

      const result = await promise;
      expect(result.success).toBe(true);
      expect(result.attempts).toBe(3);

      vi.useRealTimers();
    });
  });
});
