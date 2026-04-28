"""Model Context Protocol (MCP) server adapter.

This package implements an MCP server that exposes Pheno SDK functionality through the
Model Context Protocol for AI assistants.
"""

from .handlers import (
    PromptHandler,
    ResourceHandler,
    ToolHandler,
)
from .server import MCPServer

__all__ = [
    "MCPServer",
    "PromptHandler",
    "ResourceHandler",
    "ToolHandler",
]
