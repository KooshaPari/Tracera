/**
 * Retry Policy Implementation for Frontend
 *
 * Provides automatic retry logic with exponential backoff and jitter
 * for handling transient failures.
 */

export interface RetryPolicyConfig {
  /** Maximum number of retry attempts */
  maxRetries: number;

  /** Initial delay before first retry (ms) */
  initialDelay: number;

  /** Maximum delay between retries (ms) */
  maxDelay: number;

  /** Exponential backoff multiplier */
  multiplier: number;

  /** Jitter percentage (0-100) to prevent thundering herd */
  jitterPercent: number;

  /** HTTP status codes that should trigger a retry */
  retryableStatusCodes: number[];

  /** Custom function to determine if an error is retryable */
  isRetryable?: ((error: Error) => boolean) | undefined;

  /** Callback for each retry attempt */
  onRetry?: ((attempt: number, delay: number, error: Error) => void) | undefined;
}

export class RetryPolicy {
  private config: RetryPolicyConfig;

  constructor(config: Partial<RetryPolicyConfig> = {}) {
    this.config = {
      maxRetries: config.maxRetries ?? 3,
      initialDelay: config.initialDelay ?? 1000,
      maxDelay: config.maxDelay ?? 16000,
      multiplier: config.multiplier ?? 2.0,
      jitterPercent: config.jitterPercent ?? 20,
      retryableStatusCodes: config.retryableStatusCodes ?? [429, 500, 502, 503, 504],
      isRetryable: config.isRetryable,
      onRetry: config.onRetry,
    };
  }

  /**
   * Execute a function with retry logic
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error as Error;

        // Check if we should retry
        if (attempt >= this.config.maxRetries) {
          break; // No more retries left
        }

        if (!this.shouldRetry(error as Error)) {
          throw error; // Not retryable, throw immediately
        }

        // Calculate delay with exponential backoff and jitter
        const delay = this.calculateDelay(attempt);

        // Call retry callback
        this.config.onRetry?.(attempt + 1, delay, error as Error);

        console.warn(
          `🔄 Retry attempt ${attempt + 1}/${this.config.maxRetries} in ${delay}ms`,
          error,
        );

        // Wait before retrying
        await this.sleep(delay);
      }
    }

    throw new Error(
      `Operation failed after ${this.config.maxRetries} retries: ${lastError?.message}`,
    );
  }

  /**
   * Execute a fetch request with retry logic
   */
  async fetch(url: string, options?: RequestInit): Promise<Response> {
    return this.execute(async () => {
      const response = await fetch(url, options);

      // Check if status code is retryable
      if (!response.ok && this.config.retryableStatusCodes.includes(response.status)) {
        throw new RetryableError(`HTTP ${response.status}: ${response.statusText}`);
      }

      return response;
    });
  }

  /**
   * Calculate delay with exponential backoff and jitter
   */
  private calculateDelay(attempt: number): number {
    // Calculate exponential backoff: initialDelay * multiplier^attempt
    let delay = this.config.initialDelay * Math.pow(this.config.multiplier, attempt);

    // Cap at max delay
    delay = Math.min(delay, this.config.maxDelay);

    // Add jitter to prevent thundering herd
    if (this.config.jitterPercent > 0) {
      const jitterRange = delay * (this.config.jitterPercent / 100);
      const jitter = (Math.random() * 2 - 1) * jitterRange; // Random between -jitterRange and +jitterRange
      delay += jitter;
    }

    // Ensure delay is non-negative
    return Math.max(0, delay);
  }

  /**
   * Determine if an error should trigger a retry
   */
  private shouldRetry(error: Error): boolean {
    // Check custom retry function first
    if (this.config.isRetryable) {
      return this.config.isRetryable(error);
    }

    // Check if error is explicitly retryable
    if (error instanceof RetryableError) {
      return true;
    }

    // Check for network errors
    if (
      error.message.includes('fetch') ||
      error.message.includes('network') ||
      error.message.includes('timeout')
    ) {
      return true;
    }

    return false;
  }

  /**
   * Sleep for a specified duration
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

/**
 * RetryableError indicates an error that can be retried
 */
export class RetryableError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RetryableError';
  }
}

/**
 * Predefined retry policies for common scenarios
 */
export const RetryPolicies = {
  /** Default retry policy for general use */
  default: new RetryPolicy(),

  /** Aggressive retry policy for critical operations */
  aggressive: new RetryPolicy({
    maxRetries: 5,
    initialDelay: 500,
    maxDelay: 32000,
  }),

  /** Conservative retry policy for less critical operations */
  conservative: new RetryPolicy({
    maxRetries: 2,
    initialDelay: 2000,
    maxDelay: 10000,
  }),

  /** Quick retry policy for fast-failing operations */
  quick: new RetryPolicy({
    maxRetries: 2,
    initialDelay: 500,
    maxDelay: 2000,
    multiplier: 1.5,
  }),
};

/**
 * Retry with exponential backoff (convenience function)
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  config?: Partial<RetryPolicyConfig>,
): Promise<T> {
  const policy = new RetryPolicy(config);
  return policy.execute(fn);
}

/**
 * Create a fetch wrapper with automatic retry
 */
export function createRetryFetch(config?: Partial<RetryPolicyConfig>) {
  const policy = new RetryPolicy(config);

  return async (url: string, options?: RequestInit): Promise<Response> => {
    return policy.fetch(url, options);
  };
}

/**
 * Retry budget to prevent retry storms
 */
export class RetryBudget {
  private maxRetries: number;
  private currentCount: number = 0;
  private windowStart: number = Date.now();
  private windowDuration: number;

  constructor(maxRetries: number, windowDuration: number = 60000) {
    this.maxRetries = maxRetries;
    this.windowDuration = windowDuration;
  }

  /**
   * Check if retry budget allows another retry
   */
  canRetry(): boolean {
    this.resetIfNeeded();
    return this.currentCount < this.maxRetries;
  }

  /**
   * Record a retry attempt
   */
  recordRetry(): void {
    this.resetIfNeeded();
    this.currentCount++;
  }

  /**
   * Reset budget if window has expired
   */
  private resetIfNeeded(): void {
    const now = Date.now();
    if (now - this.windowStart > this.windowDuration) {
      this.currentCount = 0;
      this.windowStart = now;
    }
  }

  /**
   * Get remaining retry budget
   */
  getRemainingBudget(): number {
    this.resetIfNeeded();
    return Math.max(0, this.maxRetries - this.currentCount);
  }
}

/**
 * Generate idempotency key for safe retries
 */
export function generateIdempotencyKey(requestId: string, attempt: number): string {
  return `${requestId}-retry-${attempt}-${Date.now()}`;
}

/**
 * Add idempotency key to request headers
 */
export function withIdempotencyKey(options: RequestInit, key: string): RequestInit {
  return {
    ...options,
    headers: {
      ...options.headers,
      'Idempotency-Key': key,
    },
  };
}
