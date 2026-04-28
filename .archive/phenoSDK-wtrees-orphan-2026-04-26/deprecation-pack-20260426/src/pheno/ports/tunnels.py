"""
Ports that define the tunnel management contracts used by orchestration layers.

These protocols split responsibilities across a lifecycle orchestrator, the
underlying tunnel provider, registry persistence, and DNS management. Adapters
implementing these interfaces must coordinate without leaking provider-specific
details into the core SDK.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pheno.ports.tunneling import TunnelConfig, TunnelEndpoint, TunnelStatus


class TunnelRecord(ABC):
    """Abstract representation of a tunnel persisted in a registry."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique tunnel identifier."""
        ...

    @property
    @abstractmethod
    def config(self) -> TunnelConfig:
        """Return the configuration used to construct the tunnel."""
        ...

    @property
    @abstractmethod
    def status(self) -> TunnelStatus | None:
        """Return the last known runtime status, if any."""
        ...

    @property
    @abstractmethod
    def endpoint(self) -> TunnelEndpoint | None:
        """Return the public endpoint associated with the tunnel."""
        ...


class DNSRecord(ABC):
    """Abstract representation of DNS state tied to a tunnel."""

    @property
    @abstractmethod
    def hostname(self) -> str:
        """Hostname that resolves to the tunnel."""
        ...

    @property
    @abstractmethod
    def target(self) -> str:
        """Origin service or tunnel target address."""
        ...


class TunnelPort(Protocol):
    """High-level tunnel lifecycle contract combining provider, registry, and DNS."""

    async def create(
        self,
        config: TunnelConfig,
        *,
        ensure_dns: bool = True,
        persist: bool = True,
    ) -> TunnelStatus:
        """Provision a tunnel and optionally register it plus publish DNS."""
        ...

    async def destroy(
        self,
        name: str,
        *,
        purge_dns: bool = True,
        remove_registry: bool = True,
    ) -> TunnelStatus | None:
        """Tear down a tunnel and optionally clean registry and DNS state."""
        ...

    async def discover(self, name: str) -> TunnelStatus | None:
        """Locate an existing tunnel by name, consulting registry and provider."""
        ...

    async def update_dns(
        self,
        name: str,
        hostname: str,
        *,
        ttl: int | None = None,
        force: bool = False,
    ) -> TunnelEndpoint:
        """Refresh DNS routing for a tunnel and return the resulting endpoint."""
        ...


class TunnelProviderPort(Protocol):
    """Contract for interacting with the tunnel runtime or external provider."""

    async def create(self, config: TunnelConfig) -> TunnelStatus:
        """Instantiate a tunnel according to the given configuration."""
        ...

    async def destroy(self, name: str) -> TunnelStatus | None:
        """Stop a tunnel by name and return its final status when available."""
        ...

    async def discover(self, name: str) -> TunnelStatus | None:
        """Query the provider for the latest status of the named tunnel."""
        ...


class TunnelRegistryPort(Protocol):
    """Persistence contract for storing and retrieving tunnel records."""

    async def create(self, record: TunnelRecord) -> TunnelRecord:
        """Persist a tunnel record and return the stored representation."""
        ...

    async def destroy(self, name: str) -> None:
        """Remove the stored record for a tunnel."""
        ...

    async def discover(self, name: str) -> TunnelRecord | None:
        """Look up a stored tunnel record by name."""
        ...


class DNSPort(Protocol):
    """Contract for managing DNS pointing to tunnel endpoints."""

    async def update_dns(
        self,
        name: str,
        hostname: str,
        *,
        ttl: int | None = None,
    ) -> TunnelEndpoint:
        """Create or update DNS routing for the tunnel."""
        ...

    async def destroy(self, hostname: str) -> None:
        """Remove DNS routing associated with the tunnel."""
        ...

    async def discover(self, hostname: str) -> DNSRecord | None:
        """Return DNS details for the supplied hostname if present."""
        ...


__all__ = [
    "DNSPort",
    "DNSRecord",
    "TunnelPort",
    "TunnelProviderPort",
    "TunnelRecord",
    "TunnelRegistryPort",
]
