"""
Retry strategies and error handling for resilient operations.
"""

from __future__ import annotations

import asyncio
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger("pheno.resilience.retry")


@dataclass(slots=True)
class RetryConfig:
    """
    Configuration for retry strategies.
    """

    # Retry settings
    max_attempts: int = 3
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    jitter: bool = True  # Add randomness to delays

    # Exception handling
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()

    # Callbacks
    on_retry: Callable[[int, Exception], None] | None = None
    on_failure: Callable[[Exception], None] | None = None
    on_success: Callable[[Any], None] | None = None

    # Timeout
    timeout: float | None = None  # seconds


class RetryError(Exception):
    """
    Base exception for retry errors.
    """



class MaxRetriesExceededError(RetryError):
    """
    Raised when maximum retries are exceeded.
    """

    def __init__(self, max_attempts: int, last_exception: Exception):
        self.max_attempts = max_attempts
        self.last_exception = last_exception
        super().__init__(f"Maximum retries ({max_attempts}) exceeded. Last error: {last_exception}")


class RetryStrategy(ABC):
    """
    Abstract base class for retry strategies.
    """

    def __init__(self, config: RetryConfig):
        self.config = config

    @abstractmethod
    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate delay for the given attempt number.
        """

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """
        Determine if we should retry after the given exception.
        """
        # Check max attempts
        if attempt >= self.config.max_attempts:
            return False

        # Check if exception is retryable
        if isinstance(exception, self.config.non_retryable_exceptions):
            return False

        return isinstance(exception, self.config.retryable_exceptions)

    def apply_jitter(self, delay: float) -> float:
        """
        Apply jitter to the delay.
        """
        if not self.config.jitter:
            return delay

        # Add ±25% jitter
        jitter_factor = random.uniform(0.75, 1.25)
        return delay * jitter_factor

    def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute function with retry logic.
        """
        return self._execute_call(func, args, kwargs, is_async=False)

    async def execute_async(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Execute async function with retry logic.
        """
        return await self._execute_call(func, args, kwargs, is_async=True)

    def _execute_call(
        self, func: Callable[..., Any], args: tuple, kwargs: dict, is_async: bool,
    ) -> Any:
        """
        Execute a call with retry logic.
        """
        last_exception = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                logger.debug(f"Retry attempt {attempt}/{self.config.max_attempts}")

                # Execute the function
                if is_async:
                    result = asyncio.run(func(*args, **kwargs))
                else:
                    result = func(*args, **kwargs)

                # Success
                if self.config.on_success:
                    try:
                        self.config.on_success(result)
                    except Exception as e:
                        logger.warning(f"Success callback failed: {e}")

                logger.debug(f"Function succeeded on attempt {attempt}")
                return result

            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt} failed: {e}")

                # Check if we should retry
                if not self.should_retry(attempt, e):
                    logger.exception(f"Not retrying: {e}")
                    break

                # Calculate delay for next attempt
                if attempt < self.config.max_attempts:
                    delay = self.calculate_delay(attempt)
                    delay = min(delay, self.config.max_delay)
                    delay = self.apply_jitter(delay)

                    logger.debug(f"Waiting {delay:.2f}s before retry")

                    # Call retry callback
                    if self.config.on_retry:
                        try:
                            self.config.on_retry(attempt, e)
                        except Exception as callback_e:
                            logger.warning(f"Retry callback failed: {callback_e}")

                    # Wait before retry
                    if is_async:
                        asyncio.run(asyncio.sleep(delay))
                    else:
                        time.sleep(delay)

        # All retries failed
        if self.config.on_failure:
            try:
                self.config.on_failure(last_exception)
            except Exception as e:
                logger.warning(f"Failure callback failed: {e}")

        raise MaxRetriesExceededError(self.config.max_attempts, last_exception)


class ExponentialBackoffRetry(RetryStrategy):
    """
    Exponential backoff retry strategy.
    """

    def __init__(self, config: RetryConfig, multiplier: float = 2.0):
        super().__init__(config)
        self.multiplier = multiplier

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate exponential backoff delay.
        """
        delay = self.config.base_delay * (self.multiplier ** (attempt - 1))
        return min(delay, self.config.max_delay)


class LinearBackoffRetry(RetryStrategy):
    """
    Linear backoff retry strategy.
    """

    def __init__(self, config: RetryConfig, increment: float = 1.0):
        super().__init__(config)
        self.increment = increment

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate linear backoff delay.
        """
        delay = self.config.base_delay + (self.increment * (attempt - 1))
        return min(delay, self.config.max_delay)


class ConstantDelayRetry(RetryStrategy):
    """
    Constant delay retry strategy.
    """

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate constant delay.
        """
        return self.config.base_delay


class FibonacciBackoffRetry(RetryStrategy):
    """
    Fibonacci backoff retry strategy.
    """

    def __init__(self, config: RetryConfig):
        super().__init__(config)
        self._fib_cache = {0: 0, 1: 1}

    def _fibonacci(self, n: int) -> int:
        """
        Calculate Fibonacci number.
        """
        if n in self._fib_cache:
            return self._fib_cache[n]

        self._fib_cache[n] = self._fibonacci(n - 1) + self._fibonacci(n - 2)
        return self._fib_cache[n]

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate Fibonacci backoff delay.
        """
        fib_value = self._fibonacci(attempt)
        delay = self.config.base_delay * fib_value
        return min(delay, self.config.max_delay)


class AdaptiveRetry(RetryStrategy):
    """
    Adaptive retry strategy that adjusts based on success/failure patterns.
    """

    def __init__(self, config: RetryConfig):
        super().__init__(config)
        self._success_count = 0
        self._failure_count = 0
        self._consecutive_failures = 0
        self._consecutive_successes = 0

    def calculate_delay(self, attempt: int) -> float:
        """
        Calculate adaptive delay.
        """
        # Increase delay based on consecutive failures
        if self._consecutive_failures > 0:
            delay = self.config.base_delay * (2 ** min(self._consecutive_failures, 6))
        else:
            delay = self.config.base_delay

        return min(delay, self.config.max_delay)

    def should_retry(self, attempt: int, exception: Exception) -> bool:
        """
        Adaptive retry logic.
        """
        # Update counters
        self._failure_count += 1
        self._consecutive_failures += 1
        self._consecutive_successes = 0

        # More aggressive retry for transient errors
        if "timeout" in str(exception).lower() or "connection" in str(exception).lower():
            return attempt < self.config.max_attempts + 2

        return super().should_retry(attempt, exception)

    def _execute_call(
        self, func: Callable[..., Any], args: tuple, kwargs: dict, is_async: bool,
    ) -> Any:
        """
        Execute with adaptive retry logic.
        """
        result = super()._execute_call(func, args, kwargs, is_async)

        # Update success counters
        self._success_count += 1
        self._consecutive_successes += 1
        self._consecutive_failures = 0

        return result


class RetryManager:
    """
    Manages multiple retry strategies.
    """

    def __init__(self):
        self._strategies: dict[str, RetryStrategy] = {}
        self._default_strategy: RetryStrategy | None = None

    def add_strategy(self, name: str, strategy: RetryStrategy) -> None:
        """
        Add a retry strategy.
        """
        self._strategies[name] = strategy
        logger.info(f"Added retry strategy '{name}'")

    def get_strategy(self, name: str) -> RetryStrategy | None:
        """
        Get a retry strategy by name.
        """
        return self._strategies.get(name)

    def set_default_strategy(self, strategy: RetryStrategy) -> None:
        """
        Set the default retry strategy.
        """
        self._default_strategy = strategy
        logger.info("Set default retry strategy")

    def execute_with_strategy(
        self, strategy_name: str, func: Callable[..., Any], *args, **kwargs,
    ) -> Any:
        """
        Execute function with specific strategy.
        """
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"Retry strategy '{strategy_name}' not found")

        return strategy.execute(func, *args, **kwargs)

    async def execute_async_with_strategy(
        self, strategy_name: str, func: Callable[..., Awaitable[Any]], *args, **kwargs,
    ) -> Any:
        """
        Execute async function with specific strategy.
        """
        strategy = self.get_strategy(strategy_name)
        if not strategy:
            raise ValueError(f"Retry strategy '{strategy_name}' not found")

        return await strategy.execute_async(func, *args, **kwargs)

    def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute function with default strategy.
        """
        if not self._default_strategy:
            raise ValueError("No default retry strategy set")

        return self._default_strategy.execute(func, *args, **kwargs)

    async def execute_async(self, func: Callable[..., Awaitable[Any]], *args, **kwargs) -> Any:
        """
        Execute async function with default strategy.
        """
        if not self._default_strategy:
            raise ValueError("No default retry strategy set")

        return await self._default_strategy.execute_async(func, *args, **kwargs)

    def list_strategies(self) -> list[str]:
        """
        List all strategy names.
        """
        return list(self._strategies.keys())


# Convenience functions
def with_retry(config: RetryConfig, strategy_type: str = "exponential"):
    """
    Decorator for adding retry logic to functions.
    """

    def decorator(func):
        if strategy_type == "exponential":
            strategy = ExponentialBackoffRetry(config)
        elif strategy_type == "linear":
            strategy = LinearBackoffRetry(config)
        elif strategy_type == "constant":
            strategy = ConstantDelayRetry(config)
        elif strategy_type == "fibonacci":
            strategy = FibonacciBackoffRetry(config)
        elif strategy_type == "adaptive":
            strategy = AdaptiveRetry(config)
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

        if asyncio.iscoroutinefunction(func):

            async def async_wrapper(*args, **kwargs):
                return await strategy.execute_async(func, *args, **kwargs)

            return async_wrapper

        def sync_wrapper(*args, **kwargs):
            return strategy.execute(func, *args, **kwargs)

        return sync_wrapper

    return decorator


def retry_on_exception(exception_types: tuple = (Exception,), max_attempts: int = 3):
    """
    Simple retry decorator for specific exceptions.
    """
    config = RetryConfig(max_attempts=max_attempts, retryable_exceptions=exception_types)
    return with_retry(config, "exponential")
