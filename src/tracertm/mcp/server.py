"""
Unified FastMCP Server definition for TraceRTM.

This module re-exports the single MCP server instance and imports tool modules
to register them. The param tools have been split into domain-specific modules
for faster loading and better organization.
"""

from tracertm.mcp.core import mcp

# Register tool/resource/prompt modules that decorate the shared `mcp` instance.
from tracertm.mcp.tools import core_tools  # noqa: F401
from tracertm.mcp.tools import bmm_workflows  # noqa: F401
from tracertm.mcp.resources import bmm as bmm_resources  # noqa: F401
from tracertm.mcp.resources import tracertm as tracertm_resources  # noqa: F401
from tracertm.mcp.prompts import bmm as bmm_prompts  # noqa: F401
from tracertm.mcp.tools import specifications  # noqa: F401
from tracertm.mcp.tools import streaming  # noqa: F401

# Load param tools from split modules (much faster than single 62KB file)
from tracertm.mcp.tools.params import project  # noqa: F401
from tracertm.mcp.tools.params import item  # noqa: F401
from tracertm.mcp.tools.params import link  # noqa: F401
from tracertm.mcp.tools.params import trace  # noqa: F401
from tracertm.mcp.tools.params import graph  # noqa: F401
from tracertm.mcp.tools.params import specification  # noqa: F401
from tracertm.mcp.tools.params import config  # noqa: F401
from tracertm.mcp.tools.params import storage  # noqa: F401
from tracertm.mcp.tools.params import io_operations  # noqa: F401
from tracertm.mcp.tools.params import database  # noqa: F401
from tracertm.mcp.tools.params import agent  # noqa: F401
from tracertm.mcp.tools.params import query_test  # noqa: F401
from tracertm.mcp.tools.params import ui  # noqa: F401
from tracertm.mcp.tools.params import system  # noqa: F401

__all__ = ["mcp"]
