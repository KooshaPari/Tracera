"""Entry point for python -m tracertm.mcp.

Standalone MCP is not allowed. MCP runs only as part of the backend (mounted ASGI).
Start the TraceRTM API server and use /api/v1/mcp/...
"""

from __future__ import annotations

import sys


def main() -> None:
    """Standalone MCP is not allowed."""
    print("Standalone MCP is not allowed.", file=sys.stderr)
    print("MCP is only available as part of the backend (mounted ASGI process).", file=sys.stderr)
    print("Start the TraceRTM API server (e.g. uvicorn tracertm.api.main:app, or rtm dev) and use /api/v1/mcp/...", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    main()
