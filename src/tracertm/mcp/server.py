"""
Unified FastMCP Server definition for TraceRTM.

This module re-exports the single MCP server instance and imports all tool
modules to register them. All MCP tools should import `mcp` from here.
"""

from tracertm.mcp.core import mcp

# Register tool/resource/prompt modules that decorate the shared `mcp` instance.
from tracertm.mcp.tools import core_tools  # noqa: F401
from tracertm.mcp.tools import bmm_workflows  # noqa: F401
from tracertm.mcp.resources import bmm as bmm_resources  # noqa: F401
from tracertm.mcp.resources import tracertm as tracertm_resources  # noqa: F401
from tracertm.mcp.prompts import bmm as bmm_prompts  # noqa: F401
from tracertm.mcp.tools import specifications  # noqa: F401
from tracertm.mcp.tools import param  # noqa: F401
from tracertm.mcp.tools import streaming  # noqa: F401

__all__ = ["mcp"]
