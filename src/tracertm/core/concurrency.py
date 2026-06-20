"""Concurrency control for TraceRTM (optimistic locking)."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class ConcurrencyError(Exception):
    """Raised when optimistic lock fails (version mismatch)."""


async def update_with_retry[T](
    update_fn: Callable[[], Awaitable[T]],
    max_retries: int = 3,
    base_delay: float = 0.1,
) -> T:
    """Execute update function with automatic retry on ConcurrencyError.

    Uses exponential backoff with jitter to prevent thundering herd.

    Args:
        update_fn: Async function that performs the update
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (doubled each retry)

    Returns:
        Result of update_fn

    Raises:
        ConcurrencyError: If all retries fail
    """
    for attempt in range(max_retries):
        try:
            return await update_fn()
        except ConcurrencyError as e:
            if attempt == max_retries - 1:
                # Last attempt failed, re-raise
                msg = f"Failed after {max_retries} retries: {e!s}"
                raise ConcurrencyError(msg) from e

            # Calculate delay with exponential backoff and jitter
            delay = base_delay * (2**attempt)
            jitter = delay * 0.1  # 10% jitter
            await asyncio.sleep(delay + jitter)

    # Should never reach here, but satisfy type checker
    msg = f"Failed after {max_retries} retries"
    raise ConcurrencyError(msg)
