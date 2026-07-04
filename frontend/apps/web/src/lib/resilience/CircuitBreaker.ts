/**
 * Circuit Breaker Pattern Implementation for Frontend
 *
 * Prevents cascading failures by stopping requests to failing services
 * and allowing them time to recover.
 */

export enum CircuitState {
  CLOSED = 'closed',
  OPEN = 'open',
  HALF_OPEN = 'half-open',
}

export interface CircuitBreakerConfig {
  /** Maximum number of failures before opening circuit */
  failureThreshold: number;

  /** Time window for counting failures (ms) */
  failureWindow: number;

  /** Time to wait before attempting recovery (ms) */
  resetTimeout: number;

  /** Number of successful requests needed to close circuit in half-open state */
  successThreshold: number;

  /** Optional callback when state changes */
  onStateChange?: ((from: CircuitState, to: CircuitState) => void) | undefined;
}

interface CircuitCounts {
  failures: number;
  successes: number;
  requests: number;
  lastFailureTime: number;
}

export class CircuitBreaker {
  private config: CircuitBreakerConfig;
  private state: CircuitState = CircuitState.CLOSED;
  private counts: CircuitCounts = {
    failures: 0,
    successes: 0,
    requests: 0,
    lastFailureTime: 0,
  };
  private openedAt: number = 0;

  constructor(config: Partial<CircuitBreakerConfig> = {}) {
    this.config = {
      failureThreshold: config.failureThreshold ?? 5,
      failureWindow: config.failureWindow ?? 10000, // 10 seconds
      resetTimeout: config.resetTimeout ?? 30000, // 30 seconds
      successThreshold: config.successThreshold ?? 2,
      onStateChange: config.onStateChange,
    };
  }

  /**
   * Execute a function with circuit breaker protection
   */
  async execute<T>(fn: () => Promise<T>): Promise<T> {
    // Check if circuit should transition from OPEN to HALF_OPEN
    if (this.state === CircuitState.OPEN) {
      const timeSinceOpen = Date.now() - this.openedAt;
      if (timeSinceOpen >= this.config.resetTimeout) {
        this.transitionToHalfOpen();
      } else {
        throw new Error(
          `Circuit breaker is OPEN. Service unavailable. Retry in ${Math.ceil((this.config.resetTimeout - timeSinceOpen) / 1000)}s`,
        );
      }
    }

    // Execute the function
    this.counts.requests++;

    try {
      const result = await fn();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  /**
   * Handle successful execution
   */
  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.counts.successes++;

      // If we've had enough successes, close the circuit
      if (this.counts.successes >= this.config.successThreshold) {
        this.transitionToClosed();
      }
    } else if (this.state === CircuitState.CLOSED) {
      // Reset failure count on success
      this.resetCounts();
    }
  }

  /**
   * Handle failed execution
   */
  private onFailure(): void {
    const now = Date.now();
    this.counts.failures++;
    this.counts.lastFailureTime = now;

    if (this.state === CircuitState.HALF_OPEN) {
      // Any failure in HALF_OPEN reopens the circuit
      this.transitionToOpen();
    } else if (this.state === CircuitState.CLOSED) {
      // Check if we should open the circuit
      const timeSinceFirstFailure = now - (this.counts.lastFailureTime - this.config.failureWindow);

      if (
        this.counts.failures >= this.config.failureThreshold &&
        timeSinceFirstFailure <= this.config.failureWindow
      ) {
        this.transitionToOpen();
      }
    }
  }

  /**
   * Transition to CLOSED state
   */
  private transitionToClosed(): void {
    const oldState = this.state;
    this.state = CircuitState.CLOSED;
    this.resetCounts();
    console.log('✅ Circuit breaker CLOSED (healthy)');
    this.config.onStateChange?.(oldState, this.state);
  }

  /**
   * Transition to OPEN state
   */
  private transitionToOpen(): void {
    const oldState = this.state;
    this.state = CircuitState.OPEN;
    this.openedAt = Date.now();
    console.error('❌ Circuit breaker OPEN (service unavailable)');
    this.config.onStateChange?.(oldState, this.state);
  }

  /**
   * Transition to HALF_OPEN state
   */
  private transitionToHalfOpen(): void {
    const oldState = this.state;
    this.state = CircuitState.HALF_OPEN;
    this.counts.successes = 0;
    console.warn('⚠️  Circuit breaker HALF_OPEN (testing recovery)');
    this.config.onStateChange?.(oldState, this.state);
  }

  /**
   * Reset internal counts
   */
  private resetCounts(): void {
    this.counts = {
      failures: 0,
      successes: 0,
      requests: 0,
      lastFailureTime: 0,
    };
  }

  /**
   * Get current circuit state
   */
  getState(): CircuitState {
    return this.state;
  }

  /**
   * Get current counts
   */
  getCounts(): Readonly<CircuitCounts> {
    return { ...this.counts };
  }

  /**
   * Force reset the circuit breaker
   */
  reset(): void {
    this.transitionToClosed();
  }

  /**
   * Check if circuit is open
   */
  isOpen(): boolean {
    return this.state === CircuitState.OPEN;
  }
}

/**
 * Circuit breaker registry for managing multiple circuit breakers
 */
export class CircuitBreakerRegistry {
  private breakers = new Map<string, CircuitBreaker>();
  private defaultConfig: Partial<CircuitBreakerConfig>;

  constructor(defaultConfig: Partial<CircuitBreakerConfig> = {}) {
    this.defaultConfig = defaultConfig;
  }

  /**
   * Get or create a circuit breaker for a service
   */
  getBreaker(serviceName: string, config?: Partial<CircuitBreakerConfig>): CircuitBreaker {
    if (!this.breakers.has(serviceName)) {
      const breaker = new CircuitBreaker({
        ...this.defaultConfig,
        ...config,
        onStateChange: (from, to) => {
          console.log(`🔌 [${serviceName}] Circuit state: ${from} → ${to}`);
          config?.onStateChange?.(from, to);
        },
      });
      this.breakers.set(serviceName, breaker);
    }
    return this.breakers.get(serviceName)!;
  }

  /**
   * Execute a function with circuit breaker protection
   */
  async execute<T>(
    serviceName: string,
    fn: () => Promise<T>,
    config?: Partial<CircuitBreakerConfig>,
  ): Promise<T> {
    const breaker = this.getBreaker(serviceName, config);
    return breaker.execute(fn);
  }

  /**
   * Get all circuit breaker states
   */
  getAllStates(): Record<string, CircuitState> {
    const states: Record<string, CircuitState> = {};
    for (const [name, breaker] of this.breakers.entries()) {
      states[name] = breaker.getState();
    }
    return states;
  }

  /**
   * Check if all circuits are healthy
   */
  isHealthy(): boolean {
    for (const breaker of this.breakers.values()) {
      if (breaker.isOpen()) {
        return false;
      }
    }
    return true;
  }
}

// Global circuit breaker registry
const globalRegistry = new CircuitBreakerRegistry({
  failureThreshold: 5,
  failureWindow: 10000,
  resetTimeout: 30000,
  successThreshold: 2,
});

export { globalRegistry };
