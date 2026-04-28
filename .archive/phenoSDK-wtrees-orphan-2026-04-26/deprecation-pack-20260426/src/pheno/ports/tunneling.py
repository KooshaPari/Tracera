"""
Tunneling ports describing the interaction with cloudflared-managed tunnels.

The SDK treats tunnel orchestration as an external integration so adapters can wrap
cloudflared CLI, API, or other transport providers while sharing a consistent contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(slots=True)
class TunnelConfig:
    """Declarative configuration for launching a tunnel."""

    name: str
    target_host: str
    target_port: int
    protocol: str = "http"
    hostname: str | None = None
    credentials_file: str | None = None
    tags: dict[str, str] | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class TunnelEndpoint:
    """Published hostname associated with a tunnel."""

    hostname: str
    url: str
    protocol: str = "https"
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class TunnelStatus:
    """Runtime status information for a managed tunnel."""

    name: str
    running: bool
    url: str | None = None
    pid: int | None = None
    last_heartbeat: float | None = None
    metadata: dict[str, Any] | None = None


class TunnelManagerPort(Protocol):
    """Operations available for managing cloudflared-backed tunnels."""

    async def start(self, config: TunnelConfig) -> TunnelStatus:
        """Start or attach to a tunnel described by ``config``."""
        ...

    async def stop(self, name: str) -> TunnelStatus:
        """Stop the tunnel identified by ``name`` and return final status."""
        ...

    async def restart(self, config: TunnelConfig) -> TunnelStatus:
        """Restart a tunnel using the latest configuration."""
        ...

    async def status(self, name: str) -> TunnelStatus:
        """Fetch the latest known status for ``name``."""
        ...

    async def synchronize(
        self,
        config: TunnelConfig,
        *,
        allow_create: bool = True,
    ) -> TunnelStatus:
        """Ensure a tunnel matches ``config``; optionally create if missing."""
        ...

    async def cleanup_orphans(self) -> int:
        """Terminate stray tunnel processes returning the number cleaned up."""
        ...

    async def list_active(self) -> list[TunnelStatus]:
        """Return all tracked tunnels that are currently running."""
        ...

    async def ensure_dns(self, name: str, hostname: str) -> TunnelEndpoint:
        """Ensure DNS routing exists for ``name`` and return the resolved endpoint."""
        ...

    async def rotate_credentials(self, name: str) -> str:
        """Rotate credentials for the tunnel and return the new path."""
        ...


__all__ = [
    "TunnelConfig",
    "TunnelEndpoint",
    "TunnelManagerPort",
    "TunnelStatus",
]
