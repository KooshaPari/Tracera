"""Entry point for python -m tracertm.mcp.

Standalone MCP is not allowed. MCP runs only as part of the backend (mounted ASGI).
Start the TraceRTM API server and use /api/v1/mcp/...
"""

from __future__ import annotations

import sys


def main() -> None:
    """Standalone MCP is not allowed."""
    sys.exit(1)


if __name__ == "__main__":
    main()
