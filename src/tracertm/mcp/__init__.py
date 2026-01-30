"""
TraceRTM MCP Server - FastMCP 3.0.0b1 based MCP server for AI-native CLI.

This module provides:
- Tools: Actions the AI can perform (CRUD, analysis, verification)
- Resources: Data the AI can access (projects, graphs, reports)
- Prompts: Reusable prompt templates (ADR creation, analysis)
"""

from __future__ import annotations


def run_server() -> None:
    """Run the MCP server.

    This is the entry point for the `tracertm-mcp` and `rtm-mcp` CLI commands.
    """
    try:
        from tracertm.mcp.server import mcp
        mcp.run()
    except ImportError as e:
        import sys
        print(f"Error: Failed to start MCP server: {e}", file=sys.stderr)
        print("Make sure FastMCP is installed: pip install 'fastmcp>=3.0.0b1'", file=sys.stderr)
        sys.exit(1)


try:
    from tracertm.mcp.server import mcp
except Exception:  # pragma: no cover - allow imports in limited test envs
    mcp = None

__all__ = ["mcp", "run_server"]
