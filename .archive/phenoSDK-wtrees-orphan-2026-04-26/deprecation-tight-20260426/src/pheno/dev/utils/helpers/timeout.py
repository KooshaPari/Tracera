"""
Async timeout utilities for integration tests.
"""

import asyncio
import functools
from collections.abc import Callable
from typing import Any


class TimeoutManager:
    """
    Manage test execution timeouts and diagnostics.
    """

    DEFAULT_TIMEOUT = 30
    SLOW_TEST_THRESHOLD = 5000

    @staticmethod
    async def run_with_timeout(
        coro,
        timeout_seconds: float,
        test_name: str = "unknown",
    ) -> dict[str, Any]:
        """
        Run a coroutine with a timeout and friendly error payloads.
        """
        try:
            return await asyncio.wait_for(coro, timeout=timeout_seconds)
        except TimeoutError:
            return {
                "success": False,
                "error": f"Test '{test_name}' timed out after {timeout_seconds}s",
                "timeout": True,
            }
        except Exception as exc:  # pragma: no cover - defensive
            return {
                "success": False,
                "error": str(exc),
            }

    @staticmethod
    def detect_slow_tests(
        results: list[dict[str, Any]],
        threshold_ms: int | None = None,
    ) -> list[tuple[str, int]]:
        """
        Return tests whose recorded durations exceed the threshold.
        """
        threshold = threshold_ms or TimeoutManager.SLOW_TEST_THRESHOLD
        slow_tests: list[tuple[str, int]] = []
        for result in results:
            duration = result.get("duration_ms", 0)
            if duration > threshold:
                slow_tests.append((result.get("test_name", "unknown"), duration))
        return slow_tests


def timeout_wrapper(timeout_seconds: float = 30):
    """
    Decorator adding a timeout to async test functions.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds,
                )
            except TimeoutError:
                return {
                    "success": False,
                    "error": f"Test '{func.__name__}' timed out after {timeout_seconds}s",
                    "timeout": True,
                }

        return wrapper

    return decorator


__all__ = ["TimeoutManager", "timeout_wrapper"]
