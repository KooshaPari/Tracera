"""Streaming Gateway Example.

Demonstrates pheno.stream integration with pheno.gateway for real-time WebSocket and SSE
streaming with rate limiting, CORS, and metrics.
"""

import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from pheno.events.streaming_helpers import create_sse_stream, handle_websocket
from pheno.gateway import add_asgi_gateway, add_http_metrics_middleware
from starlette.requests import Request

from pheno.events.streaming import StreamManager
from pheno.observability import add_prometheus_endpoint, configure_structlog

# Initialize FastAPI app
app = FastAPI(title="Streaming Gateway Example")

# Configure structured logging
configure_structlog(service_name="streaming-gateway", environment="dev")

# Add HTTP metrics middleware
add_http_metrics_middleware(app)

# Add gateway middleware
add_asgi_gateway(
    app,
    rate_limit={"max_requests": 100, "window_seconds": 60},
    rate_limit_key="client_ip",
    cors={
        "allow_origins": ["http://localhost:3000", "http://localhost:8080"],
        "allow_methods": ["GET", "POST"],
        "allow_headers": ["*"],
        "allow_credentials": True,
    },
    timeout={"timeout_seconds": 300},  # Longer timeout for streaming
)

# Add Prometheus metrics endpoint
add_prometheus_endpoint(app)

# Create stream manager
stream_manager = StreamManager()


# === Streaming Endpoints ===


@app.get("/stream/sse")
async def sse_endpoint(request: Request, channels: str = "default"):
    """Server-Sent Events streaming endpoint.

    Query params:
        channels: Comma-separated list of channels to subscribe to

    Example:
        curl http://localhost:8000/stream/sse?channels=chat,notifications
    """
    import uuid

    connection_id = str(uuid.uuid4())
    channel_list = [c.strip() for c in channels.split(",")]

    return StreamingResponse(
        create_sse_stream(stream_manager, connection_id, channel_list, timeout=30),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@app.websocket("/stream/ws")
async def websocket_endpoint(websocket: WebSocket, channels: str = "default"):
    """WebSocket streaming endpoint.

    Query params:
        channels: Comma-separated list of channels to subscribe to

    Example:
        const ws = new WebSocket('ws://localhost:8000/stream/ws?channels=chat');
    """
    import uuid

    await websocket.accept()
    connection_id = str(uuid.uuid4())
    channel_list = [c.strip() for c in channels.split(",")]

    await handle_websocket(stream_manager, websocket, connection_id, channel_list)


# === API Endpoints ===


@app.post("/broadcast/{channel}")
async def broadcast_message(channel: str, message: dict):
    """Broadcast a message to all subscribers of a channel.

    Example:
        curl -X POST http://localhost:8000/broadcast/chat \
             -H "Content-Type: application/json" \
             -d '{"text": "Hello, world!"}'
    """
    from pheno.ports.stream import StreamMessageType

    await stream_manager.broadcast(
        channel=channel,
        content=message,
        message_type=StreamMessageType.CHANNEL_MESSAGE,
        source="api",
    )

    return {"status": "broadcasted", "channel": channel}


@app.get("/channels/{channel}/subscribers")
async def get_channel_subscribers(channel: str):
    """
    Get list of subscribers for a channel.
    """
    subscribers = stream_manager.get_channel_subscribers(channel)
    return {
        "channel": channel,
        "subscriber_count": len(subscribers),
        "subscribers": subscribers,
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Streaming Gateway Example",
        "endpoints": {
            "sse": "/stream/sse?channels=default",
            "websocket": "/stream/ws?channels=default",
            "broadcast": "POST /broadcast/{channel}",
            "subscribers": "/channels/{channel}/subscribers",
            "metrics": "/metrics",
            "docs": "/docs",
        },
    }


# === Background Task: Demo Broadcaster ===


async def demo_broadcaster():
    """
    Background task that broadcasts demo messages.
    """
    import time

    await asyncio.sleep(2)  # Wait for startup

    counter = 0
    while True:
        counter += 1

        # Broadcast to default channel
        await stream_manager.broadcast(
            channel="default",
            content={
                "message": f"Demo message #{counter}",
                "timestamp": time.time(),
            },
        )

        # Broadcast to chat channel
        await stream_manager.broadcast(
            channel="chat",
            content={
                "user": "system",
                "text": f"Chat message #{counter}",
                "timestamp": time.time(),
            },
        )

        await asyncio.sleep(5)  # Broadcast every 5 seconds


@app.on_event("startup")
async def startup_event():
    """
    Start background broadcaster on startup.
    """
    asyncio.create_task(demo_broadcaster())


if __name__ == "__main__":
    import uvicorn

    print("Starting Streaming Gateway Example...")
    print("- API: http://localhost:8000")
    print("- Docs: http://localhost:8000/docs")
    print("- Metrics: http://localhost:8000/metrics")
    print("- SSE: http://localhost:8000/stream/sse?channels=default")
    print("- WebSocket: ws://localhost:8000/stream/ws?channels=default")
    print("\nFeatures enabled:")
    print("  ✓ Server-Sent Events (SSE)")
    print("  ✓ WebSocket streaming")
    print("  ✓ Rate limiting (100 req/min per IP)")
    print("  ✓ CORS")
    print("  ✓ HTTP metrics")
    print("  ✓ Structured logging")
    print("  ✓ Demo broadcaster (every 5s)")
    print("\nTry:")
    print("  curl http://localhost:8000/stream/sse?channels=chat")
    print(
        "  curl -X POST http://localhost:8000/broadcast/chat -H 'Content-Type: application/json' -d '{\"text\":\"Hello!\"}'",
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)
