"""FastMCP HTTP/SSE Transport Layer for TraceRTM.

This module provides HTTP and SSE transport capabilities using FastMCP 3.0's
native HTTP support. It integrates with the existing FastAPI router while
maintaining the ability to run MCP in standalone HTTP mode.

Key Features:
- Dual transport support (STDIO + HTTP/SSE)
- JSON-RPC 2.0 message format
- SSE streaming for progress updates
- FastAPI integration for auth and middleware
- Standalone HTTP server mode
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Literal

from tracertm.mcp.core import mcp

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import FastAPI
    from starlette.applications import Starlette

logger = logging.getLogger(__name__)

# =============================================================================
# HTTP Transport Configuration
# =============================================================================

DEFAULT_HTTP_HOST = "127.0.0.1"
DEFAULT_HTTP_PORT = 8765
DEFAULT_MCP_PATH = "/mcp"


# =============================================================================
# Standalone HTTP Server
# =============================================================================


_STANDALONE_DISALLOWED_MSG = (
    "Standalone MCP is not allowed. MCP is only available as part of the backend (mounted ASGI process). "
    "Start the TraceRTM API server (e.g. uvicorn tracertm.api.main:app, or rtm dev) and use /api/v1/mcp/..."
)


def create_standalone_http_app(
    *,
    _path: str = DEFAULT_MCP_PATH,
    _transport: Literal["http", "streamable-http", "sse"] = "streamable-http",
    _enable_cors: bool = True,
) -> Starlette:
    """Standalone MCP is not allowed. MCP runs only as part of the backend (mounted ASGI)."""
    raise RuntimeError(_STANDALONE_DISALLOWED_MSG)


async def run_http_server(
    *,
    _host: str = DEFAULT_HTTP_HOST,
    _port: int = DEFAULT_HTTP_PORT,
    _path: str = DEFAULT_MCP_PATH,
    _transport: Literal["http", "streamable-http", "sse"] = "streamable-http",
    _log_level: str = "info",
) -> None:
    """Standalone MCP is not allowed. MCP runs only as part of the backend (mounted ASGI)."""
    await asyncio.sleep(0)
    raise RuntimeError(_STANDALONE_DISALLOWED_MSG)


# =============================================================================
# FastAPI Integration
# =============================================================================


def mount_mcp_to_fastapi(
    app: FastAPI,
    *,
    path: str = DEFAULT_MCP_PATH,
    transport: Literal["http", "streamable-http", "sse"] = "streamable-http",
) -> None:
    """Mount MCP HTTP transport to an existing FastAPI app.

    This allows MCP to be served from the same FastAPI app as the REST API,
    enabling shared middleware, auth, and other FastAPI features.

    Args:
        app: FastAPI application instance
        path: Path to mount MCP (default: /mcp)
        transport: Transport type (default: streamable-http)

    Example:
        >>> from fastapi import FastAPI
        >>> app = FastAPI()
        >>> mount_mcp_to_fastapi(app, path="/api/v1/mcp")
    """
    logger.info("Mounting MCP to FastAPI at %s with transport: %s", path, transport)

    # Create the MCP HTTP app
    mcp_app = mcp.http_app(
        path="/",  # Root path inside mounted sub-app
        transport=transport,
        json_response=True,
        stateless_http=False,
    )

    # Mount the MCP app to FastAPI
    app.mount(path, mcp_app)

    # Expose the mounted MCP app for callers that want to drive its lifespan.
    app.state.mcp_app = mcp_app

    # Ensure parent app uses MCP lifespan (FastMCP expects this).
    app.router.lifespan_context = mcp_app.lifespan

    logger.info("MCP mounted successfully at %s", path)


# =============================================================================
# SSE Progress Streaming
# =============================================================================


async def create_progress_stream(
    task_id: str,
    generator_func: AsyncGenerator[dict[str, object], None],
) -> AsyncGenerator[dict[str, object], None]:
    """Create an SSE stream for progress updates.

    This wraps a progress generator to format events for SSE streaming.
    Works with FastMCP's ctx.report_progress() for streaming tool execution.

    Args:
        task_id: Unique task identifier
        generator_func: Async generator yielding progress updates

    Yields:
        SSE-formatted events with progress data

    Example:
        >>> async def my_task():
        >>>     for i in range(10):
        >>>         yield {"progress": i, "total": 10, "message": f"Step {i}"}
        >>>
        >>> async for event in create_progress_stream("task-123", my_task()):
        >>>     print(event)
    """
    try:
        # Send stream start event
        yield {
            "event": "stream_start",
            "data": {
                "task_id": task_id,
                "status": "started",
            },
        }

        # Stream progress updates
        async for progress_data in generator_func:
            yield {
                "event": "progress",
                "data": {
                    "task_id": task_id,
                    **progress_data,
                },
            }

        # Send completion event
        yield {
            "event": "stream_complete",
            "data": {
                "task_id": task_id,
                "status": "completed",
            },
        }

    except asyncio.CancelledError:
        logger.info("Progress stream cancelled for task: %s", task_id)
        yield {
            "event": "stream_cancelled",
            "data": {
                "task_id": task_id,
                "status": "cancelled",
            },
        }
        raise

    except Exception as e:
        logger.exception("Error in progress stream for task %s", task_id)
        yield {
            "event": "stream_error",
            "data": {
                "task_id": task_id,
                "status": "error",
                "error": str(e),
            },
        }


# =============================================================================
# Transport Selection
# =============================================================================


def get_transport_type() -> Literal["http", "streamable-http", "sse"]:
    """Determine which transport to use based on environment/config.

    Returns:
        Transport type string (http only; stdio not supported)

    Priority:
        1. TRACERTM_MCP_TRANSPORT environment variable
        2. Default to "http"
    """
    import os

    raw_transport = os.getenv("TRACERTM_MCP_TRANSPORT", "http").lower()

    # Validate transport (stdio not supported)
    valid_transports: dict[str, Literal["http", "streamable-http", "sse"]] = {
        "http": "http",
        "streamable-http": "streamable-http",
        "sse": "sse",
    }
    transport = valid_transports.get(raw_transport)
    if transport is None:
        logger.warning(
            "Invalid transport '%s', defaulting to 'http'. Valid options: %s", raw_transport, list(valid_transports)
        )
        transport = "http"

    logger.info("Using MCP transport: %s", transport)
    return transport


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "DEFAULT_HTTP_HOST",
    "DEFAULT_HTTP_PORT",
    "DEFAULT_MCP_PATH",
    "create_progress_stream",
    "create_standalone_http_app",
    "get_transport_type",
    "mount_mcp_to_fastapi",
    "run_http_server",
]
