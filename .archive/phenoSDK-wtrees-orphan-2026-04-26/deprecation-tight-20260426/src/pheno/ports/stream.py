"""
Stream ports: Clean contracts for streaming implementations.

Domain: Defines technology-agnostic streaming concepts
Ports: Contracts that stream adapters must implement
"""

from __future__ import annotations

import json
import uuid
from abc import abstractmethod
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Protocol

# ===== DOMAIN: Technology-Agnostic Value Objects =====


class StreamMessageType(Enum):
    """
    Types of streaming messages (technology-agnostic).
    """

    STATUS_UPDATE = "status_update"
    PROGRESS_UPDATE = "progress_update"
    ACTIVITY_UPDATE = "activity_update"
    ACTION_UPDATE = "action_update"
    FILE_UPDATE = "file_update"
    QUESTION_UPDATE = "question_update"
    WARNING = "warning"
    ERROR = "error"
    COMPLETION = "completion"
    HEARTBEAT = "heartbeat"
    # Channel/communication base types
    CHANNEL_MESSAGE = "channel_message"
    PRESENCE_UPDATE = "presence_update"
    TYPING = "typing"
    SCRATCHPAD_UPDATE = "scratchpad_update"
    TEAM_EVENT = "team_event"
    CUSTOM = "custom"


@dataclass(frozen=True)
class StreamMessage:
    """
    Individual streaming message (domain value object).
    """

    id: str
    type: StreamMessageType
    timestamp: str
    channel: str
    source: str
    content: dict[str, Any]
    sequence: int = 0
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["type"] = self.type.value
        return data

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_sse_format(self) -> str:
        return f"id: {self.id}\nevent: {self.type.value}\ndata: {json.dumps(self.content)}\n\n"

    @classmethod
    def create(
        cls,
        type: StreamMessageType,
        channel: str,
        content: dict[str, Any],
        source: str = "system",
        sequence: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> StreamMessage:
        return cls(
            id=str(uuid.uuid4()),
            type=type,
            timestamp=datetime.now(UTC).isoformat(),
            channel=channel,
            source=source,
            content=content,
            sequence=sequence,
            metadata=metadata or {},
        )


@dataclass(frozen=True)
class ConnectionInfo:
    """
    Information about a streaming connection (domain value object).
    """

    connection_id: str
    protocol: str  # "websocket" or "sse"
    connected_at: str
    channels: list[str]
    metadata: dict[str, Any]
    last_activity: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ===== PORTS: Contracts for Adapters =====


class StreamProtocol(Protocol):
    """Port contract: Adapters implement streaming protocols."""

    @abstractmethod
    async def send(self, connection: Any, message: StreamMessage) -> None:
        """
        Send a message through this streaming protocol.
        """
        ...

    @abstractmethod
    async def receive(self, connection: Any) -> StreamMessage | None:
        """
        Receive a message through this streaming protocol.
        """
        ...

    @abstractmethod
    async def close(self, connection: Any) -> None:
        """
        Close the streaming connection.
        """
        ...

    @abstractmethod
    def is_connected(self, connection: Any) -> bool:
        """
        Check if connection is still active.
        """
        ...


class StreamManagerProtocol(Protocol):
    """Port contract: Adapters implement connection management."""

    @abstractmethod
    async def register_websocket(
        self,
        connection_id: str,
        websocket: Any,
        channels: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register a WebSocket connection.
        """
        ...

    @abstractmethod
    async def register_sse(
        self,
        connection_id: str,
        channels: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> asyncio.Queue:
        """
        Register a Server-Sent Events connection.
        """
        ...

    @abstractmethod
    async def broadcast(
        self,
        channel: str,
        content: dict[str, Any],
        message_type: StreamMessageType = StreamMessageType.CHANNEL_MESSAGE,
        source: str = "system",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Broadcast message to channel subscribers.
        """
        ...

    @abstractmethod
    async def unregister(self, connection_id: str) -> None:
        """
        Remove connection from all subscriptions.
        """
        ...


__all__ = [
    "ConnectionInfo",
    "StreamManagerProtocol",
    # Domain objects
    "StreamMessage",
    "StreamMessageType",
    # Port contracts
    "StreamProtocol",
]
