"""
TUI-Kit Protocols - Provider protocol definitions for extensibility.

This module defines protocol interfaces for various provider types used throughout
tui-kit widgets. Implement these protocols to integrate with custom backends and
external services.

Protocols:
- OAuthCacheProvider: OAuth token cache provider
- ClientAdapter: MCP client adapter for server status monitoring
- TunnelProvider: Tunnel service provider (ngrok, Cloudflare, custom)
- ResourceProvider: Resource monitoring provider (database, cache, API)
- MetricsProvider: Metrics collection and reporting provider

Example:
    from tui_kit.protocols import ClientAdapter

    class MyMCPClient:
        @property
        def endpoint(self) -> str:
            return "http://localhost:8000/mcp"

        async def list_tools(self):
            # Implementation
            return []

    # Use with ServerStatusWidget
    widget = ServerStatusWidget(client_adapter=MyMCPClient())

Author: Koosha Pari
License: MIT
"""

from pheno.ui.tui.widget_providers import (
    ClientAdapter,
    MetricsProvider,
    OAuthCacheProvider,
    ResourceProvider,
    TunnelProvider,
)

__all__ = [
    "ClientAdapter",
    "MetricsProvider",
    "OAuthCacheProvider",
    "ResourceProvider",
    "TunnelProvider",
]
