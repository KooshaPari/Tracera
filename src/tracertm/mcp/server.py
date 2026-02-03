"""
Unified FastMCP Server definition for TraceRTM.

This module re-exports the single MCP server instance and imports tool modules
to register them. The param tools have been split into domain-specific modules
for faster loading and better organization.
"""

from tracertm.mcp.core import mcp
from tracertm.mcp.prompts import bmm as bmm_prompts  # noqa: F401
from tracertm.mcp.resources import bmm as bmm_resources  # noqa: F401
from tracertm.mcp.resources import tracertm as tracertm_resources  # noqa: F401

# Register tool/resource/prompt modules that decorate the shared `mcp` instance.
from tracertm.mcp.tools import (
    bmm_workflows,  # noqa: F401
    core_tools,  # noqa: F401
    specifications,  # noqa: F401
    streaming,  # noqa: F401
)

# Load param tools from split modules (much faster than single 62KB file)
from tracertm.mcp.tools.params import (
    agent,  # noqa: F401
    config,  # noqa: F401
    database,  # noqa: F401
    graph,  # noqa: F401
    io_operations,  # noqa: F401
    item,  # noqa: F401
    link,  # noqa: F401
    project,  # noqa: F401
    query_test,  # noqa: F401
    specification,  # noqa: F401
    storage,  # noqa: F401
    system,  # noqa: F401
    trace,  # noqa: F401
    ui,  # noqa: F401
)

__all__ = ["mcp"]
