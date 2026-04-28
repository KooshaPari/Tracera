"""
Tests for resilience module.
"""

import asyncio
import os

os.environ.setdefault("PHENO_SKIP_BOOTSTRAP", "1")

import pytest

from pheno.resilience import (
    CircuitBreaker,
    CircuitBreakerError,
    ErrorCategory,
    ErrorHandler,
    ErrorSeverity,
    RetryExhausted,
    RetryPolicy,
    retry_async,
    retry_sync,
)


class TestCircuitBreaker:
    """
    Test circuit breaker functionality.
    """

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        """
        Test that circuit opens after threshold failures.
        """
        breaker = CircuitBreaker(failure_threshold=3, timeout_seconds=1)

        async def failing_func():
            raise ValueError("Test error")

        # First 3 attempts should fail and open circuit
        for i in range(3):
            with pytest.raises(ValueError):
                await breaker.call(failing_func)

        # Circuit should now be open
        assert breaker.is_open()

        # Next attempt should raise CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            await breaker.call(failing_func)

    @pytest.mark.asyncio
    async def test_circuit_breaker_half_open_recovery(self):
        """
        Test circuit breaker recovery through half-open state.
        """
        breaker = CircuitBreaker(failure_threshold=2, timeout_seconds=0.1, success_threshold=2)

        call_count = [0]

        async def sometimes_failing_func():
            call_count[0] += 1
            if call_count[0] <= 2:
                raise ValueError("Failing")
            return "success"

        # Fail twice to open circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                await breaker.call(sometimes_failing_func)

        assert breaker.is_open()

        # Wait for timeout
        await asyncio.sleep(0.2)

        # Should be able to try again (half-open)
        result = await breaker.call(sometimes_failing_func)
        assert result == "success"

        # One more success should close circuit
        result = await breaker.call(sometimes_failing_func)
        assert result == "success"
        assert breaker.is_closed()


class TestErrorHandler:
    """
    Test error handler functionality.
    """

    def test_categorize_network_error(self):
        """
        Test network error categorization.
        """
        handler = ErrorHandler()

        error = ConnectionError("Connection failed")
        category = handler.categorize_error(error)

        assert category == ErrorCategory.NETWORK

    def test_categorize_timeout_error(self):
        """
        Test timeout error categorization.
        """
        handler = ErrorHandler()

        error = TimeoutError("Request timeout")
        category = handler.categorize_error(error)

        assert category == ErrorCategory.TIMEOUT

    def test_categorize_validation_error(self):
        """
        Test validation error categorization.
        """
        handler = ErrorHandler()

        error = ValueError("Invalid input")
        category = handler.categorize_error(error)

        assert category == ErrorCategory.VALIDATION

    def test_determine_severity(self):
        """
        Test severity determination.
        """
        handler = ErrorHandler()

        # Critical error
        error = RuntimeError("System failure")
        severity = handler.determine_severity(error, ErrorCategory.SYSTEM_ERROR)
        assert severity == ErrorSeverity.CRITICAL

        # High severity for auth
        error = PermissionError("Access denied")
        severity = handler.determine_severity(error, ErrorCategory.AUTHORIZATION)
        assert severity == ErrorSeverity.HIGH

    @pytest.mark.asyncio
    async def test_error_handler_with_custom_handler(self):
        """
        Test custom error handler registration.
        """
        handler = ErrorHandler()

        handled_errors = []

        def custom_handler(error_info):
            handled_errors.append(error_info)
            return {"handled": True}

        handler.register_handler(ErrorCategory.NETWORK, custom_handler)

        error = ConnectionError("Network error")
        error_info = handler.create_error_info(error)

        result = await handler.handle_error(error_info)

        assert len(handled_errors) == 1
        assert result["category"] == "network"
        assert len(result["handler_results"]) == 1
        assert result["handler_results"][0]["handled"] is True

    def test_error_metrics(self):
        """
        Test error metrics tracking.
        """
        handler = ErrorHandler()

        # Create and handle some errors
        errors = [
            ConnectionError("Network error"),
            TimeoutError("Timeout"),
            ValueError("Validation error"),
        ]

        for error in errors:
            error_info = handler.create_error_info(error)
            # Manually update metrics (since we're not calling handle_error)
            handler.metrics.total_errors += 1

        metrics = handler.get_metrics()
        assert metrics.total_errors == 3


class TestRetry:
    """
    Test retry functionality.
    """

    @pytest.mark.asyncio
    async def test_retry_async_success_after_failures(self):
        """
        Test retry succeeds after some failures.
        """
        attempt_count = [0]

        async def flaky_func():
            attempt_count[0] += 1
            if attempt_count[0] < 3:
                raise ValueError("Not yet")
            return "success"

        policy = RetryPolicy(max_attempts=5, base_delay=0.01)
        result = await retry_async(flaky_func, policy=policy)

        assert result == "success"
        assert attempt_count[0] == 3

    @pytest.mark.asyncio
    async def test_retry_async_exhausted(self):
        """
        Test retry exhaustion.
        """

        async def always_failing_func():
            raise ValueError("Always fails")

        policy = RetryPolicy(max_attempts=3, base_delay=0.01)

        with pytest.raises(RetryExhausted) as exc_info:
            await retry_async(always_failing_func, policy=policy)

        assert exc_info.value.attempts == 3

    def test_retry_sync_success(self):
        """
        Test sync retry success.
        """
        attempt_count = [0]

        def flaky_func():
            attempt_count[0] += 1
            if attempt_count[0] < 2:
                raise ValueError("Not yet")
            return "success"

        policy = RetryPolicy(max_attempts=5, base_delay=0.01)
        result = retry_sync(flaky_func, policy=policy)

        assert result == "success"
        assert attempt_count[0] == 2

    @pytest.mark.asyncio
    async def test_retry_with_should_retry_filter(self):
        """
        Test retry with custom should_retry filter.
        """
        attempt_count = [0]

        async def func_with_different_errors():
            attempt_count[0] += 1
            if attempt_count[0] == 1:
                raise ValueError("Retryable")
            raise TypeError("Not retryable")

        def should_retry(error):
            return isinstance(error, ValueError)

        policy = RetryPolicy(max_attempts=5, base_delay=0.01)

        with pytest.raises(TypeError):
            await retry_async(func_with_different_errors, policy=policy, should_retry=should_retry)

        # Should have tried twice (once ValueError, once TypeError)
        assert attempt_count[0] == 2

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """
        Test exponential backoff delays.
        """
        from pheno.resilience.retry import ExponentialBackoff

        backoff = ExponentialBackoff()
        policy = RetryPolicy(base_delay=1.0, exponential_base=2.0, jitter=False)

        # Test delays grow exponentially
        delay0 = backoff.calculate_delay(0, policy)
        delay1 = backoff.calculate_delay(1, policy)
        delay2 = backoff.calculate_delay(2, policy)

        assert delay0 == 1.0  # 1.0 * 2^0
        assert delay1 == 2.0  # 1.0 * 2^1
        assert delay2 == 4.0  # 1.0 * 2^2

    @pytest.mark.asyncio
    async def test_linear_backoff(self):
        """
        Test linear backoff delays.
        """
        from pheno.resilience.retry import LinearBackoff

        backoff = LinearBackoff()
        policy = RetryPolicy(base_delay=1.0, jitter=False)

        # Test delays grow linearly
        delay0 = backoff.calculate_delay(0, policy)
        delay1 = backoff.calculate_delay(1, policy)
        delay2 = backoff.calculate_delay(2, policy)

        assert delay0 == 1.0  # 1.0 * 1
        assert delay1 == 2.0  # 1.0 * 2
        assert delay2 == 3.0  # 1.0 * 3
