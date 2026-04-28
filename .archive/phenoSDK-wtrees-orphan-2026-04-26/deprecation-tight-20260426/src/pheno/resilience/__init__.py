"""Resilience patterns for fault-tolerant Pheno applications.

This package exposes generic building blocks that projects can use to add
fault tolerance without re-implementing common patterns in each service.

Included patterns:
    • Circuit breaker with registry support
    • Retry helpers with multiple backoff strategies
    • Error categorisation, severity assessment, and metrics collection
"""

from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitBreakerManager,
    CircuitBreakerState,
)
from .error_handler import (
    ErrorCategory,
    ErrorContext,
    ErrorHandler,
    ErrorInfo,
    ErrorMetrics,
    ErrorSeverity,
)
from .retry import (
    ConstantDelayRetry,
    ExponentialBackoffRetry,
    LinearBackoffRetry,
    MaxRetriesExceededError,
    RetryConfig,
    RetryStrategy,
    retry_on_exception,
    with_retry,
)

__all__ = [
    # Circuit breaker
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitBreakerManager",
    "CircuitBreakerState",
    # Retry helpers
    "ConstantDelayRetry",
    # Error handling
    "ErrorCategory",
    "ErrorContext",
    "ErrorHandler",
    "ErrorInfo",
    "ErrorMetrics",
    "ErrorSeverity",
    "ExponentialBackoffRetry",
    "LinearBackoffRetry",
    "MaxRetriesExceededError",
    "RetryConfig",
    "RetryStrategy",
    "retry_on_exception",
    "with_retry",
]
