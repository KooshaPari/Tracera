/**
 * Robust fetch with wait+retry, timeout, and configurable backoff.
 * Use for all API and health-check calls that may see transient failures.
 */

export type RetryFetchOptions = {
  /** Max number of attempts (including first). Default 3. */
  maxRetries?: number;
  /** Initial delay in ms. Default 500. */
  initialDelayMs?: number;
  /** Max delay cap in ms. Default 10000. */
  maxDelayMs?: number;
  /** Backoff multiplier. Default 2. */
  backoffMultiplier?: number;
  /** Request timeout in ms. Default 15000. */
  timeoutMs?: number;
  /** Retry on these status codes (in addition to network/timeout). Default [408, 429, 502, 503, 504]. */
  retryStatuses?: number[];
  /** If true, add jitter to delays. Default true. */
  jitter?: boolean;
};

const DEFAULT_OPTIONS: Required<Omit<RetryFetchOptions, 'retryStatuses'>> & {
  retryStatuses: number[];
} = {
  maxRetries: 3,
  initialDelayMs: 500,
  maxDelayMs: 10_000,
  backoffMultiplier: 2,
  timeoutMs: 15_000,
  retryStatuses: [408, 429, 502, 503, 504],
  jitter: true,
};

function delay(ms: number, jitter: boolean): number {
  if (!jitter) return ms;
  const j = 0.2 * ms * (Math.random() * 2 - 1);
  return Math.max(0, Math.round(ms + j));
}

function isRetryableStatus(status: number, retryStatuses: number[]): boolean {
  return retryStatuses.includes(status) || (status >= 500 && status < 600);
}

/**
 * Creates a fetch function that retries on failure with exponential backoff.
 * - Retries on: network errors, timeouts, and configurable HTTP statuses (default 408, 429, 5xx).
 * - Does not retry on: 4xx (except 408, 429), 2xx, 3xx.
 */
export function createRetryFetch(
  baseFetch: typeof fetch,
  options: RetryFetchOptions = {},
): typeof fetch {
  const opts = { ...DEFAULT_OPTIONS, ...options };
  const {
    maxRetries,
    initialDelayMs,
    maxDelayMs,
    backoffMultiplier,
    timeoutMs,
    retryStatuses,
    jitter,
  } = opts;

  return async function retryFetch(
    input: RequestInfo | URL,
    init?: RequestInit,
  ): Promise<Response> {
    // 		const _url = typeof input === "string" ? input : input instanceof URL ? input.href : input.url;
    let lastError: unknown;
    let lastResponse: Response | undefined;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
      const controller = new AbortController();
      if (init?.signal) {
        init.signal.addEventListener('abort', () => controller.abort());
      }
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      try {
        const res = await baseFetch(input, {
          ...init,
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        const shouldRetry =
          attempt < maxRetries - 1 && isRetryableStatus(res.status, retryStatuses);

        if (shouldRetry) {
          lastResponse = res;
          const waitMs = Math.min(
            initialDelayMs * Math.pow(backoffMultiplier, attempt),
            maxDelayMs,
          );
          await new Promise((r) => setTimeout(r, delay(waitMs, jitter)));
          continue;
        }

        return res;
      } catch (e) {
        clearTimeout(timeoutId);
        lastError = e;
        const isAbort = e instanceof DOMException && e.name === 'AbortError';
        const isNetwork =
          e instanceof TypeError &&
          (e.message === 'Failed to fetch' || e.message?.includes('network'));
        if (
          attempt < maxRetries - 1 &&
          (isAbort || isNetwork || (e instanceof Error && e.message?.includes('fetch')))
        ) {
          const waitMs = Math.min(
            initialDelayMs * Math.pow(backoffMultiplier, attempt),
            maxDelayMs,
          );
          await new Promise((r) => setTimeout(r, delay(waitMs, jitter)));
          continue;
        }
        throw e;
      }
    }

    if (lastResponse) return lastResponse;
    throw lastError;
  };
}

/**
 * Get a retry fetch that uses global fetch. Call after app bootstrap if you need
 * a standalone retry fetch (e.g. in preflight before main client is loaded).
 */
export function getFetchWithRetry(options?: RetryFetchOptions): typeof fetch {
  if (typeof globalThis.fetch === 'undefined') {
    throw new Error('fetch not available');
  }
  return createRetryFetch(globalThis.fetch, {
    maxRetries: 3,
    timeoutMs: 15_000,
    ...options,
  });
}
