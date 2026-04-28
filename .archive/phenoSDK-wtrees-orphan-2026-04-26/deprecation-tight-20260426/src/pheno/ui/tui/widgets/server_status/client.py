"""
Client adapter protocol for server status monitoring.
"""

from __future__ import annotations

from typing import Any, Protocol


class ClientAdapter(Protocol):
    """
    Protocol for MCP client adapters used by the server status widget.
    """

    @property
    def endpoint(self) -> str: ...

    async def list_tools(self) -> list[dict[str, Any]]: ...


__all__ = ["ClientAdapter"]
