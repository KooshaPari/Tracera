"""pheno.stream helpers for FastAPI/Starlette integration.

Provides convenience functions for adding streaming endpoints to web applications.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from fastapi import WebSocket
    from starlette.requests import Request

    from pheno.events.streaming import StreamManager
    from pheno.ports.stream import StreamMessage


async def create_sse_stream(
    manager: StreamManager,
    connection_id: str,
    channels: list[str],
    timeout: int = 30,
) -> AsyncGenerator[str, None]:
    """Create a Server-Sent Events stream.

    Args:
        manager: StreamManager instance
        connection_id: Unique connection identifier
        channels: List of channels to subscribe to
        timeout: Timeout in seconds for waiting for messages

    Yields:
        SSE-formatted messages

    Example:
        from fastapi import FastAPI
        from fastapi.responses import StreamingResponse
        from pheno.events.streaming import StreamManager
        from pheno.events.streaming_helpers import create_sse_stream

        app = FastAPI()
        manager = StreamManager()

        @app.get("/stream")
        async def stream_endpoint():
            return StreamingResponse(
                create_sse_stream(manager, "conn1", ["updates"]),
                media_type="text/event-stream"
            )
    """
    # Register SSE connection
    queue = await manager.register_sse(connection_id, channels=channels)

    try:
        while True:
            try:
                # Wait for message with timeout
                message: StreamMessage = await asyncio.wait_for(queue.get(), timeout=timeout)

                # Format as SSE
                yield message.to_sse_format()

            except TimeoutError:
                # Send heartbeat to keep connection alive
                yield ": heartbeat\n\n"

    finally:
        # Clean up on disconnect
        await manager.unregister(connection_id)


async def handle_websocket(
    manager: StreamManager,
    websocket: Any,
    connection_id: str,
    channels: list[str],
) -> None:
    """Handle a WebSocket connection.

    Args:
        manager: StreamManager instance
        websocket: WebSocket connection object
        connection_id: Unique connection identifier
        channels: List of channels to subscribe to

    Example:
        from fastapi import FastAPI, WebSocket
        from pheno.events.streaming import StreamManager
        from pheno.events.streaming_helpers import handle_websocket

        app = FastAPI()
        manager = StreamManager()

        @app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            await handle_websocket(manager, websocket, "conn1", ["chat"])
    """
    # Register WebSocket
    await manager.register_websocket(connection_id, websocket, channels=channels)

    try:
        while True:
            # Receive messages from client
            await websocket.receive_json()

            # Handle client messages (optional: broadcast back)
            # You can add custom logic here

    except Exception:
        # Connection closed or error
        pass
    finally:
        # Clean up on disconnect
        await manager.unregister(connection_id)


def add_streaming_routes(
    app: Any,
    manager: StreamManager,
    *,
    sse_path: str = "/stream",
    websocket_path: str = "/ws",
) -> None:
    """Add streaming routes to a FastAPI/Starlette application.

    Args:
        app: FastAPI or Starlette application
        manager: StreamManager instance
        sse_path: Path for SSE endpoint
        websocket_path: Path for WebSocket endpoint

    Example:
        from fastapi import FastAPI
        from pheno.events.streaming import StreamManager
        from pheno.events.streaming_helpers import add_streaming_routes

        app = FastAPI()
        manager = StreamManager()

        add_streaming_routes(app, manager)

        # Now you can broadcast:
        await manager.broadcast("updates", {"message": "Hello"})
    """
    try:
        from fastapi.responses import StreamingResponse
    except ImportError:
        raise ImportError(
            "FastAPI/Starlette is required for add_streaming_routes. "
            "Install with: pip install fastapi",
        )

    @app.get(sse_path)
    async def sse_endpoint(request: Request):
        """
        SSE streaming endpoint.
        """
        # Generate unique connection ID
        import uuid

        connection_id = str(uuid.uuid4())

        # Get channels from query params (default to "default")
        channels_param = request.query_params.get("channels", "default")
        channels = [c.strip() for c in channels_param.split(",")]

        return StreamingResponse(
            create_sse_stream(manager, connection_id, channels),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    @app.websocket(websocket_path)
    async def websocket_endpoint(websocket: WebSocket):
        """
        WebSocket streaming endpoint.
        """
        await websocket.accept()

        # Generate unique connection ID
        import uuid

        connection_id = str(uuid.uuid4())

        # Get channels from query params (default to "default")
        channels_param = websocket.query_params.get("channels", "default")
        channels = [c.strip() for c in channels_param.split(",")]

        await handle_websocket(manager, websocket, connection_id, channels)


__all__ = [
    "add_streaming_routes",
    "create_sse_stream",
    "handle_websocket",
]
