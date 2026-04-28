"""
Timeout handling utilities.
"""

from __future__ import annotations

import asyncio
import builtins
import time
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger("pheno.resilience.timeout")


@dataclass(slots=True)
class TimeoutConfig:
    """
    Configuration for timeout handling.
    """

    default_timeout: float = 30.0  # seconds
    enable_signal_timeout: bool = True
    timeout_handler: Callable[[], None] | None = None


class TimeoutError(Exception):
    """
    Base timeout error.
    """



class OperationTimeoutError(TimeoutError):
    """
    Raised when an operation times out.
    """

    def __init__(self, operation_name: str, timeout: float):
        self.operation_name = operation_name
        self.timeout = timeout
        super().__init__(f"Operation '{operation_name}' timed out after {timeout} seconds")


class TimeoutHandler:
    """
    Handles timeouts for operations.
    """

    def __init__(self, config: TimeoutConfig | None = None):
        self.config = config or TimeoutConfig()
        self._timeouts: Dict[str, float] = {}

    def set_timeout(self, operation: str, timeout: float) -> None:
        """
        Set timeout for specific operation.
        """
        self._timeouts[operation] = timeout
        logger.debug(f"Set timeout for '{operation}': {timeout}s")

    def get_timeout(self, operation: str) -> float:
        """
        Get timeout for operation.
        """
        return self._timeouts.get(operation, self.config.default_timeout)

    async def execute_with_timeout(
        self, operation: str, func: Callable[..., Awaitable[Any]], *args, **kwargs,
    ) -> Any:
        """
        Execute async function with timeout.
        """
        timeout = self.get_timeout(operation)

        try:
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout)
        except builtins.TimeoutError:
            raise OperationTimeoutError(operation, timeout)

    def execute_with_timeout_sync(
        self, operation: str, func: Callable[..., Any], *args, **kwargs,
    ) -> Any:
        """
        Execute sync function with timeout.
        """
        timeout = self.get_timeout(operation)

        # Use asyncio to handle timeout for sync functions
        async def async_wrapper():
            return func(*args, **kwargs)

        try:
            return asyncio.run(asyncio.wait_for(async_wrapper(), timeout=timeout))
        except builtins.TimeoutError:
            raise OperationTimeoutError(operation, timeout)

    @asynccontextmanager
    async def timeout_context(self, operation: str, timeout: float | None = None):
        """
        Context manager for timeout.
        """
        actual_timeout = timeout or self.get_timeout(operation)

        try:
            yield
        except builtins.TimeoutError:
            raise OperationTimeoutError(operation, actual_timeout)

    @contextmanager
    def timeout_context_sync(self, operation: str, timeout: float | None = None):
        """
        Synchronous context manager for timeout.
        """
        actual_timeout = timeout or self.get_timeout(operation)

        # This is a simplified version - in practice, you'd need proper signal handling
        start_time = time.time()

        try:
            yield
        finally:
            elapsed = time.time() - start_time
            if elapsed > actual_timeout:
                raise OperationTimeoutError(operation, actual_timeout)
