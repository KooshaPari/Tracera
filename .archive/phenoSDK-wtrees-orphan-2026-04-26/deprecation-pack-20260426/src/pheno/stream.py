"""
pheno.stream - Unified streaming API

Provides high-level streaming interface for WebSocket and SSE connections.
Built on hexagonal architecture with domain objects from pheno.ports.stream.

Usage:
    from pheno.events.streaming import StreamManager, StreamMessage, StreamMessageType

    # Create manager
    manager = StreamManager()

    # Register WebSocket
    await manager.register_websocket(conn_id, websocket, channels=["chat"])

    # Broadcast message
    await manager.broadcast("chat", {"text": "Hello"})

    # Register SSE
    queue = await manager.register_sse(conn_id, channels=["updates"])

For protocol implementations, see stream-kit package.
"""

from __future__ import annotations

import asyncio
from datetime import UTC
from typing import Any

# Import domain objects from ports
from pheno.ports.stream import (
    ConnectionInfo,
    StreamManagerProtocol,
    StreamMessage,
    StreamMessageType,
    StreamProtocol,
)


class StreamManager:
    """High-level streaming manager for WebSocket and SSE connections.

    This is a facade over the streaming infrastructure. For full protocol
    implementations, use stream-kit package.

    Example:
        manager = StreamManager()
        await manager.register_websocket("conn1", websocket, ["chat"])
        await manager.broadcast("chat", {"message": "Hello"})
    """

    def __init__(self):
        """Initialize in-memory structures for connection and channel tracking.

        The manager keeps separate indices for raw connections, channel subscriptions,
        WebSocket transport objects, and SSE queues so each protocol can be optimized
        independently while sharing the same API.
        """
        self._connections: dict[str, ConnectionInfo] = {}
        self._channels: dict[str, set[str]] = {}  # channel -> connection_ids
        self._websockets: dict[str, Any] = {}
        self._sse_queues: dict[str, asyncio.Queue] = {}
        self._sequence = 0

    async def register_websocket(
        self,
        connection_id: str,
        websocket: Any,
        channels: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a WebSocket connection and subscribe it to channels.

        Args:
            connection_id: Unique identifier supplied by the caller.
            websocket: Transport object implementing ``send_json``.
            channels: Optional list of channels to immediately subscribe to.
            metadata: Arbitrary key/value pairs attached to the connection.

        Notes:
            The manager does not own the WebSocket lifecycle; callers remain
            responsible for closing the underlying connection.
        """
        from datetime import datetime

        channels = channels or []
        self._websockets[connection_id] = websocket

        # Create connection info
        conn_info = ConnectionInfo(
            connection_id=connection_id,
            protocol="websocket",
            connected_at=datetime.now(UTC).isoformat(),
            channels=channels,
            metadata=metadata or {},
        )
        self._connections[connection_id] = conn_info

        # Subscribe to channels
        for channel in channels:
            if channel not in self._channels:
                self._channels[channel] = set()
            self._channels[channel].add(connection_id)

    async def register_sse(
        self,
        connection_id: str,
        channels: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> asyncio.Queue:
        """Register a Server-Sent Events connection and return its message queue.

        Args:
            connection_id: Identifier supplied by the caller.
            channels: Optional channel subscriptions to create immediately.
            metadata: Additional connection context stored with the record.

        Returns:
            :class:`asyncio.Queue` that receives :class:`StreamMessage` objects.
            The caller is expected to ``await queue.get()`` and stream messages
            to the SSE transport.
        """
        from datetime import datetime

        channels = channels or []
        queue: asyncio.Queue = asyncio.Queue()
        self._sse_queues[connection_id] = queue

        # Create connection info
        conn_info = ConnectionInfo(
            connection_id=connection_id,
            protocol="sse",
            connected_at=datetime.now(UTC).isoformat(),
            channels=channels,
            metadata=metadata or {},
        )
        self._connections[connection_id] = conn_info

        # Subscribe to channels
        for channel in channels:
            if channel not in self._channels:
                self._channels[channel] = set()
            self._channels[channel].add(connection_id)

        return queue

    async def broadcast(
        self,
        channel: str,
        content: dict[str, Any],
        message_type: StreamMessageType = StreamMessageType.CHANNEL_MESSAGE,
        source: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Broadcast a message to all connections subscribed to ``channel``.

        Args:
            channel: Channel name addressed by the message.
            content: Payload dictionary serialized into the stream message.
            message_type: Enum describing the logical message type.
            source: Origin identifier (e.g., service name or user id).
            metadata: Optional additional context to embed in the message.

        Notes:
            No message is sent when the channel currently has no subscribers.
        """
        if channel not in self._channels:
            return

        # Create message
        message = StreamMessage.create(
            type=message_type,
            channel=channel,
            content=content,
            source=source,
            sequence=self._sequence,
            metadata=metadata,
        )
        self._sequence += 1

        # Send to all subscribers
        connection_ids = list(self._channels[channel])
        for conn_id in connection_ids:
            await self._send_to_connection(conn_id, message)

    async def _send_to_connection(self, connection_id: str, message: StreamMessage) -> None:
        """Deliver a message to the specified connection, handling transport types.

        WebSocket transports receive JSON dictionaries, whereas SSE connections
        get the :class:`StreamMessage` object enqueued for later flushing by the
        HTTP response coroutine.
        """
        # WebSocket
        if connection_id in self._websockets:
            ws = self._websockets[connection_id]
            try:
                await ws.send_json(message.to_dict())
            except Exception:
                # Connection closed, clean up
                await self.unregister(connection_id)

        # SSE
        elif connection_id in self._sse_queues:
            queue = self._sse_queues[connection_id]
            try:
                await queue.put(message)
            except Exception:
                # Queue closed, clean up
                await self.unregister(connection_id)

    async def unregister(self, connection_id: str) -> None:
        """Remove a connection from the manager and clean up its subscriptions.

        Args:
            connection_id: Identifier of the connection to remove.
        """
        # Remove from channels
        if connection_id in self._connections:
            conn_info = self._connections[connection_id]
            for channel in conn_info.channels:
                if channel in self._channels:
                    self._channels[channel].discard(connection_id)
                    if not self._channels[channel]:
                        del self._channels[channel]

        # Clean up connection data
        self._connections.pop(connection_id, None)
        self._websockets.pop(connection_id, None)
        self._sse_queues.pop(connection_id, None)

    def get_connection(self, connection_id: str) -> ConnectionInfo | None:
        """Retrieve the metadata stored for a connection.

        Args:
            connection_id: Identifier to look up.

        Returns:
            :class:`ConnectionInfo` describing the connection, or ``None`` if
            the connection has been removed.
        """
        return self._connections.get(connection_id)

    def get_channel_subscribers(self, channel: str) -> list[str]:
        """List the connection identifiers subscribed to ``channel``.

        Args:
            channel: Channel name to inspect.

        Returns:
            List of connection identifiers currently subscribed.
        """
        return list(self._channels.get(channel, set()))


__all__ = [
    "ConnectionInfo",
    # Manager
    "StreamManager",
    "StreamManagerProtocol",
    # Domain objects (re-exported from ports)
    "StreamMessage",
    "StreamMessageType",
    # Protocols (re-exported from ports)
    "StreamProtocol",
]
