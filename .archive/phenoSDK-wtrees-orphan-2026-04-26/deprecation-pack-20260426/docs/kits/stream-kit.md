# Stream Kit

## At a Glance
- **Purpose:** Provide unified streaming APIs for WebSocket and Server-Sent Events with channel management and middleware.
- **Best For:** Real-time dashboards, collaborative tools, and long-running agent updates.
- **Key Building Blocks:** `StreamingManager`, protocol adapters (`WebSocketProtocol`, `SSEProtocol`), channels, middleware, encoders.

## Core Capabilities
- Manage connections, subscriptions, and channel broadcasts.
- Support multiple protocols (WebSocket, SSE) through a single API.
- Middleware stack for authentication, rate limiting, and transformation.
- Encoders for JSON, MessagePack, and custom formats.
- Message buffering with ring buffers for replaying recent history.
- Statistics and introspection on active connections and channels.

## Getting Started

### Installation
```
pip install stream-kit
# Optional extras
pip install "stream-kit[fastapi]" "stream-kit[flask]" "stream-kit[client]"
```

### Minimal Example
```python
from stream_kit import StreamingManager, StreamMessageType
from stream_kit.protocols import WebSocketProtocol

manager = StreamingManager()
manager.register_protocol("websocket", WebSocketProtocol())

await manager.broadcast(
    channel="chat",
    content={"msg": "hello"},
    message_type=StreamMessageType.CHANNEL_MESSAGE,
)
```

## How It Works
- `StreamingManager` keeps track of connections and channels; protocols implement send/receive semantics.
- Channels (`stream_kit.channels.BroadcastChannel`) handle message filtering, transformation, and buffering.
- Middleware wraps protocol operations to enforce policies or enrich messages.
- Encoders transform payloads before transmission.

## Usage Recipes
- Integrate with FastAPI:
  ```python
  from fastapi import FastAPI, WebSocket
  from stream_kit import StreamingManager
  from stream_kit.protocols import WebSocketProtocol

  app = FastAPI()
  manager = StreamingManager()
  protocol = WebSocketProtocol()

  @app.websocket("/ws/{channel}")
  async def websocket_endpoint(ws: WebSocket, channel: str):
      await manager.register_websocket(ws, channels=[channel], protocol=protocol)
  ```
- Use SSE for read-only event streams with `SSEProtocol` and `StreamingResponse`.
- Add middleware for authentication: `manager.add_middleware(AuthMiddleware(...))`.
- Replay recent messages with `manager.get_recent_messages("chat", limit=50)`.

## Interoperability
- Observability-kit records metrics/trace spans for streaming operations.
- Event-kit can publish events that stream-kit broadcasts to clients.
- Works with workflow-kit/orchestrator-kit to push progress updates for long-running tasks.
- Storage-kit can persist message history if durable logs are required.

## Operations & Observability
- Monitor connection and channel counts via `manager.get_stats()`.
- Emit Prometheus metrics for message throughput and connection churn.
- Configure heartbeat messages to detect stale connections.
- Implement backpressure by inspecting queue sizes and applying rate limiting.

## Testing & QA
- Use provided test utilities (`tests/utils.py`) to simulate clients.
- Mock protocols to verify middleware behavior without opening real sockets.
- Ensure message schemas remain compatible by validating against JSON schemas.

## Troubleshooting
- **Connections dropped:** check heartbeat intervals and network timeouts; configure reconnection strategy on clients.
- **Message encoding issues:** verify encoders/decoders align (e.g., MessagePack vs JSON).
- **Channel leaks:** call `await manager.shutdown()` on service shutdown to cleanly close connections.

## Primary API Surface
- `StreamingManager()`
- `register_websocket(connection_id, websocket, channels=None, metadata=None)`
- `register_sse(connection_id, channels=None, metadata=None)`
- `subscribe(connection_id, channel)` / `unsubscribe`
- `broadcast(channel, content, message_type, source=None, metadata=None)`
- `send_to_connection(connection_id, content, channel=None, message_type=None)`
- `get_stats()` / `get_recent_messages(channel, limit)`
- Protocols: `protocols.WebSocketProtocol`, `protocols.SSEProtocol`
- Encoders: `encoders.JSONEncoder`, `encoders.MessagePackEncoder`

## Additional Resources
- Examples: `stream-kit/examples/`
- Tests: `stream-kit/tests/`
- Related guides: [Operations](../guides/operations.md), [Patterns](../concepts/patterns.md)
