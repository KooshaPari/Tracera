"""
Fallback mechanisms for resilient operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = get_logger("pheno.resilience.fallback")


@dataclass(slots=True)
class FallbackConfig:
    """
    Configuration for fallback handling.
    """

    enable_fallback: bool = True
    fallback_timeout: float | None = None
    max_fallback_attempts: int = 1
    fallback_on_exceptions: tuple = (Exception,)


class FallbackError(Exception):
    """
    Raised when fallback operations fail.
    """



class FallbackStrategy(ABC):
    """
    Abstract base class for fallback strategies.
    """

    @abstractmethod
    async def execute_fallback(self, original_error: Exception, context: dict[str, Any]) -> Any:
        """
        Execute fallback logic.
        """


class FallbackHandler:
    """
    Handles fallback mechanisms for operations.
    """

    def __init__(self, config: FallbackConfig | None = None):
        self.config = config or FallbackConfig()
        self._fallbacks: dict[str, FallbackStrategy] = {}
        self._default_fallback: FallbackStrategy | None = None

    def add_fallback(self, operation: str, strategy: FallbackStrategy) -> None:
        """
        Add fallback strategy for operation.
        """
        self._fallbacks[operation] = strategy
        logger.debug(f"Added fallback for operation '{operation}'")

    def set_default_fallback(self, strategy: FallbackStrategy) -> None:
        """
        Set default fallback strategy.
        """
        self._default_fallback = strategy
        logger.debug("Set default fallback strategy")

    async def execute_with_fallback(
        self, operation: str, func: Callable[..., Awaitable[Any]], *args, **kwargs,
    ) -> Any:
        """
        Execute function with fallback.
        """
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            if not self.config.enable_fallback:
                raise

            if not isinstance(e, self.config.fallback_on_exceptions):
                raise

            logger.warning(f"Operation '{operation}' failed, attempting fallback: {e}")

            # Get fallback strategy
            strategy = self._fallbacks.get(operation, self._default_fallback)
            if not strategy:
                raise FallbackError(f"No fallback strategy for operation '{operation}'")

            # Execute fallback
            try:
                context = {
                    "operation": operation,
                    "original_error": e,
                    "args": args,
                    "kwargs": kwargs,
                }

                return await strategy.execute_fallback(e, context)

            except Exception as fallback_error:
                logger.exception(f"Fallback for operation '{operation}' failed: {fallback_error}")
                raise FallbackError(f"Fallback failed: {fallback_error}") from e
