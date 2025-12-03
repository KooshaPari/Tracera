"""
Concurrent operations service for Epic 5 (Story 5.2, FR40).

Provides retry logic, exponential backoff, and concurrent operation support.
"""

import random
import time
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from sqlalchemy.orm.exc import StaleDataError

T = TypeVar('T')


class ConcurrencyError(Exception):
    """Raised when concurrent operation conflict detected."""
    pass


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 0.1,
    max_delay: float = 2.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
):
    """
    Decorator for retrying operations with exponential backoff (Story 5.3).

    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            delay = initial_delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (StaleDataError, ConcurrencyError) as e:
                    last_exception = e

                    if attempt < max_retries:
                        # Calculate delay with exponential backoff
                        if jitter:
                            # Add random jitter (±25%)
                            jitter_amount = delay * 0.25 * (2 * random.random() - 1)
                            actual_delay = delay + jitter_amount
                        else:
                            actual_delay = delay

                        # Clamp to max_delay
                        actual_delay = min(actual_delay, max_delay)

                        time.sleep(actual_delay)

                        # Exponential backoff
                        delay = min(delay * exponential_base, max_delay)
                    else:
                        # Max retries exceeded
                        raise ConcurrencyError(
                            f"Operation failed after {max_retries} retries: {e!s}"
                        ) from e
                except Exception:
                    # Non-retryable error
                    raise

            # Should never reach here
            if last_exception:
                raise last_exception
            raise RuntimeError("Unexpected retry logic failure")

        return wrapper
    return decorator


class ConcurrentOperationsService:
    """
    Service for managing concurrent operations (Story 5.2, FR40).

    Provides retry logic, conflict detection, and transaction support.
    """

    def __init__(self, session):
        """Initialize concurrent operations service."""
        self.session = session

    def execute_with_retry(
        self,
        operation: Callable[[], T],
        max_retries: int = 3,
        initial_delay: float = 0.1,
    ) -> T:
        """
        Execute operation with retry logic (Story 5.3).

        Args:
            operation: Function to execute
            max_retries: Maximum retry attempts
            initial_delay: Initial delay before retry

        Returns:
            Operation result

        Raises:
            ConcurrencyError: If all retries fail
        """
        delay = initial_delay
        last_exception = None

        for attempt in range(max_retries + 1):
            try:
                return operation()
            except (StaleDataError, ConcurrencyError) as e:
                last_exception = e

                if attempt < max_retries:
                    # Add jitter to prevent thundering herd
                    jitter = delay * 0.25 * (2 * random.random() - 1)
                    actual_delay = delay + jitter

                    time.sleep(actual_delay)
                    delay = min(delay * 2.0, 2.0)  # Exponential backoff, max 2s
                else:
                    raise ConcurrencyError(
                        f"Operation failed after {max_retries} retries: {e!s}"
                    ) from e

        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry failure")

    def execute_in_transaction(self, operations: list[Callable[[], Any]]) -> list[Any]:
        """
        Execute multiple operations in a single transaction (Story 5.2).

        Args:
            operations: List of operations to execute

        Returns:
            List of operation results

        Raises:
            Exception: If any operation fails, all are rolled back
        """
        results = []

        try:
            for operation in operations:
                result = operation()
                results.append(result)

            self.session.commit()
            return results
        except Exception:
            self.session.rollback()
            raise
