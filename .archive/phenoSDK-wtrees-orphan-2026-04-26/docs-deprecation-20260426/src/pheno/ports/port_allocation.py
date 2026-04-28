"""Protocol definitions for coordinating network port allocation."""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Iterable


@runtime_checkable
class PortAllocatorPort(Protocol):
    """Coordinates the allocation and release lifecycle for network ports."""

    @abstractmethod
    def allocate(self, *, preferred_port: int | None = None) -> int:
        """Reserve and return an available port, optionally honoring ``preferred_port``."""

    @abstractmethod
    def release(self, port: int) -> None:
        """Return ``port`` to the available pool and free any associated resources."""


@runtime_checkable
class PortRegistryPort(Protocol):
    """Persists and tracks port usage across allocators and service boundaries."""

    @abstractmethod
    def is_available(self, port: int) -> bool:
        """Report whether ``port`` is currently free for use."""

    @abstractmethod
    def allocate(self, port: int) -> None:
        """Mark ``port`` as reserved within the registry."""

    @abstractmethod
    def release(self, port: int) -> None:
        """Remove ``port`` from the registry's reserved set."""


@runtime_checkable
class PortDiscoveryPort(Protocol):
    """Discovers viable ports based on environment constraints and policies."""

    @abstractmethod
    def find_available(self, *, candidates: Iterable[int] | None = None) -> int | None:
        """Return the first open port from ``candidates`` or search strategy, if any."""

    @abstractmethod
    def is_available(self, port: int) -> bool:
        """Validate that ``port`` is open and satisfies discovery constraints."""

    @abstractmethod
    def allocate(self, *, preferred_port: int | None = None) -> int:
        """Short-hand for discovery followed by reservation of the located port."""

    @abstractmethod
    def release(self, port: int) -> None:
        """Release ``port`` to enable subsequent discovery operations."""
