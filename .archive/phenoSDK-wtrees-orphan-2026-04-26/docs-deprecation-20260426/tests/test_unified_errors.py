"""
Tests for unified error handler.
"""


import pytest

from pheno.errors.unified import (
    CircuitBreaker,
    CircuitBreakerConfig,
    ErrorCategory,
    ErrorContext,
    ErrorSeverity,
    RetryConfig,
    UnifiedErrorHandler,
    with_retry,
)


def test_error_classification():
    """
    Test error classification.
    """
    handler = UnifiedErrorHandler()

    # Network errors
    assert handler.classify_error(ConnectionError("connection failed")) == ErrorCategory.NETWORK

    # Timeout errors
    assert handler.classify_error(TimeoutError("timeout")) == ErrorCategory.TIMEOUT

    # Validation errors
    assert handler.classify_error(ValueError("invalid value")) == ErrorCategory.VALIDATION


def test_error_context_creation():
    """
    Test error context creation.
    """
    handler = UnifiedErrorHandler()
    error = ValueError("test error")

    context = handler.create_context(error, operation="test_op", user_id="123")

    assert context.error == error
    assert context.operation == "test_op"
    assert context.metadata["user_id"] == "123"
    assert context.category == ErrorCategory.VALIDATION


def test_error_context_to_dict():
    """
    Test error context serialization.
    """
    error = ValueError("test error")
    context = ErrorContext(
        error=error,
        category=ErrorCategory.VALIDATION,
        severity=ErrorSeverity.MEDIUM,
        operation="test_op",
    )

    data = context.to_dict()

    assert data["error_type"] == "ValueError"
    assert data["message"] == "test error"
    assert data["category"] == "validation"
    assert data["severity"] == "medium"
    assert data["operation"] == "test_op"


def test_circuit_breaker_closed():
    """
    Test circuit breaker in closed state.
    """
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))

    assert not cb.is_open()

    # Successful calls
    result = cb.call(lambda: "success")
    assert result == "success"
    assert not cb.is_open()


def test_circuit_breaker_opens():
    """
    Test circuit breaker opens after failures.
    """
    cb = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))

    # Record failures
    for _ in range(3):
        cb.record_failure()

    assert cb.is_open()


def test_circuit_breaker_half_open():
    """
    Test circuit breaker half-open state.
    """
    import time

    cb = CircuitBreaker(
        "test",
        CircuitBreakerConfig(
            failure_threshold=2, timeout=0.1, success_threshold=2,  # 100ms timeout
        ),
    )

    # Open the circuit
    cb.record_failure()
    cb.record_failure()
    assert cb.is_open()

    # Wait for timeout
    time.sleep(0.15)

    # Should be half-open now
    assert not cb.is_open()  # Can try calls

    # Record successes to close
    cb.record_success()
    cb.record_success()

    assert not cb.is_open()


@pytest.mark.asyncio
async def test_with_retry_decorator_async():
    """
    Test retry decorator with async function.
    """
    call_count = 0

    @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
    async def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("temporary error")
        return "success"

    result = await failing_func()
    assert result == "success"
    assert call_count == 3


def test_with_retry_decorator_sync():
    """
    Test retry decorator with sync function.
    """
    call_count = 0

    @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
    def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("temporary error")
        return "success"

    result = failing_func()
    assert result == "success"
    assert call_count == 3


def test_with_retry_exhausted():
    """
    Test retry decorator when retries are exhausted.
    """
    call_count = 0

    @with_retry(max_attempts=3, min_wait=0.01, max_wait=0.1)
    def always_failing():
        nonlocal call_count
        call_count += 1
        raise ValueError("permanent error")

    with pytest.raises(ValueError, match="permanent error"):
        always_failing()

    assert call_count == 3


def test_unified_handler_get_circuit_breaker():
    """
    Test getting circuit breakers from handler.
    """
    handler = UnifiedErrorHandler()

    cb1 = handler.get_circuit_breaker("service1")
    cb2 = handler.get_circuit_breaker("service1")
    cb3 = handler.get_circuit_breaker("service2")

    # Same name returns same instance
    assert cb1 is cb2

    # Different name returns different instance
    assert cb1 is not cb3


def test_retry_config_defaults():
    """
    Test retry config defaults.
    """
    config = RetryConfig()

    assert config.max_attempts == 3
    assert config.min_wait == 1.0
    assert config.max_wait == 60.0
    assert config.exponential_base == 2.0
    assert config.jitter is True
    assert ErrorCategory.NETWORK in config.retryable_categories
    assert ErrorCategory.TIMEOUT in config.retryable_categories


def test_circuit_breaker_config_defaults():
    """
    Test circuit breaker config defaults.
    """
    config = CircuitBreakerConfig()

    assert config.failure_threshold == 5
    assert config.timeout == 60.0
    assert config.success_threshold == 3
    assert config.half_open_max_calls == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
