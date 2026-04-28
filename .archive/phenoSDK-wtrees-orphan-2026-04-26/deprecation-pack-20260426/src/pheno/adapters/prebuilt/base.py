"""Shared primitives for prebuilt adapters.

Provides lightweight base classes and helper utilities that make it easy to
create adapters without forcing hard dependencies at import time.  Adapters
can lazily import optional packages, manage their lifecycle, and expose common
health-check hooks.
"""

from __future__ import annotations

import importlib
import logging
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from typing import TYPE_CHECKING, Any, Generic, Self, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

logger = logging.getLogger(__name__)

T = TypeVar("T")


class MissingDependencyError(RuntimeError):
    """Raised when an optional dependency is not available."""


class AdapterOperationError(RuntimeError):
    """Raised when an adapter operation fails."""


class LazyDependencyLoader(Generic[T]):
    """Simple helper that caches imported modules on demand."""

    def __init__(self):
        self._cache: dict[str, Any] = {}

    def require(self, module: str, *, install_hint: str | None = None) -> T:
        if module in self._cache:
            return self._cache[module]
        try:
            imported = importlib.import_module(module)
        except ModuleNotFoundError as exc:  # pragma: no cover - depends on env
            hint = install_hint or module
            raise MissingDependencyError(
                f"Optional dependency '{module}' is not installed. "
                f"Install via `pip install {hint}` to use this adapter.",
            ) from exc
        self._cache[module] = imported
        return imported


class BasePrebuiltAdapter(AbstractContextManager["BasePrebuiltAdapter"], AbstractAsyncContextManager):
    """Common behaviour for all prebuilt adapters."""

    name: str = "base"
    category: str = "generic"

    def __init__(self, **config: Any):
        self._config = dict(config)
        self._connected = False
        self._deps = LazyDependencyLoader()

    # ------------------------------------------------------------------
    # Lifecycle helpers
    # ------------------------------------------------------------------
    def connect(self) -> None:
        """Open any resources required by the adapter."""

        self._connected = True

    def close(self) -> None:
        """Release any allocated resources."""

        self._connected = False

    def ensure_connected(self) -> None:
        if not self._connected:
            self.connect()

    # ------------------------------------------------------------------
    # Capability hooks
    # ------------------------------------------------------------------
    def health_check(self) -> bool:
        """Simple health check hook; override for richer diagnostics."""

        return self._connected

    def describe(self) -> dict[str, Any]:
        """Return metadata that can be surfaced in documentation or UIs."""

        return {
            "name": self.name,
            "category": self.category,
            "config": {k: v for k, v in self._config.items() if v is not None},
        }

    # ------------------------------------------------------------------
    # Context manager support
    # ------------------------------------------------------------------
    def __enter__(self) -> Self:
        self.ensure_connected()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool | None:
        try:
            self.close()
        finally:
            return None

    async def __aenter__(self) -> Self:
        self.ensure_connected()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool | None:
        self.close()
        return None

    # ------------------------------------------------------------------
    # Protected helpers for subclasses
    # ------------------------------------------------------------------
    def _require(self, module: str, *, install_hint: str | None = None) -> Any:
        return self._deps.require(module, install_hint=install_hint)

    def _wrap_errors(self, operation: str, func: Callable[[], T]) -> T:
        try:
            return func()
        except MissingDependencyError:
            raise
        except Exception as exc:
            logger.debug("Adapter %s operation '%s' failed: %s", self.name, operation, exc)
            raise AdapterOperationError(f"{self.name} failed to execute '{operation}': {exc}") from exc


def summarize_adapters(instances: Iterable[BasePrebuiltAdapter]) -> list[dict[str, Any]]:
    """Utility to collect metadata from multiple adapters for docs/tests."""

    return [adapter.describe() for adapter in instances]


__all__ = [
    "AdapterOperationError",
    "BasePrebuiltAdapter",
    "LazyDependencyLoader",
    "MissingDependencyError",
    "summarize_adapters",
]
