"""Basic Streaming Example.

Simple example showing pheno.stream usage for WebSocket and SSE.
"""

from fastapi import FastAPI
from pheno.events.streaming_helpers import add_streaming_routes

from pheno.events.streaming import StreamManager

# Create app and stream manager
app = FastAPI(title="Basic Streaming Example")
manager = StreamManager()

# Add streaming routes (SSE at /stream, WebSocket at /ws)
add_streaming_routes(app, manager)


@app.post("/send/{channel}")
async def send_message(channel: str, message: dict):
    """
    Send a message to a channel.
    """
    await manager.broadcast(channel, message)
    return {"status": "sent", "channel": channel}


@app.get("/")
async def root():
    return {
        "message": "Basic Streaming Example",
        "sse": "/stream?channels=default",
        "websocket": "/ws?channels=default",
        "send": "POST /send/{channel}",
    }


if __name__ == "__main__":
    import uvicorn

    print("Starting Basic Streaming Example on http://localhost:8000")
    print("- SSE: http://localhost:8000/stream?channels=default")
    print("- WebSocket: ws://localhost:8000/ws?channels=default")
    print("- Send: POST http://localhost:8000/send/default")

    uvicorn.run(app, host="0.0.0.0", port=8000)
