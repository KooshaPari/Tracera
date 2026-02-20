"""Unified FastMCP Server definition for TraceRTM.

This module re-exports the single MCP server instance and imports tool modules
to register them. The param tools have been split into domain-specific modules
for faster loading and better organization.
"""

from tracertm.mcp.core import mcp

# Register tool/resource/prompt modules that decorate the shared `mcp` instance.

# Load param tools from split modules (much faster than single 62KB file)

__all__ = ["mcp"]
