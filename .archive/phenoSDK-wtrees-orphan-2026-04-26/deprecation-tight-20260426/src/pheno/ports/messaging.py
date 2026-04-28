"""
Messaging ports describing the contract for NATS-based event delivery.

Adapters implementing these ports can wrap nats-py, JetStream, or compatible brokers
to provide publish/subscribe functionality to the application layer.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Protocol

MessageHandler = Callable[["InboundMessage"], Awaitable[None] | None]


class AckStrategy(StrEnum):
    """Acknowledgement modes available to subscribers."""

    AUTO = "auto"
    MANUAL = "manual"


class DeliveryGuarantee(StrEnum):
    """High-level delivery semantics supported by the adapter."""

    AT_MOST_ONCE = "at_most_once"
    AT_LEAST_ONCE = "at_least_once"


@dataclass(slots=True)
class MessageHeaders:
    """Optional headers attached to NATS messages."""

    values: dict[str, str]

    def get(self, key: str, default: str | None = None) -> str | None:
        """Convenience accessor mirroring ``dict.get``."""
        return self.values.get(key, default)


@dataclass(slots=True)
class OutboundMessage:
    """Message to publish on the broker."""

    subject: str
    payload: bytes
    headers: MessageHeaders | None = None
    reply_to: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class InboundMessage:
    """Message received from the broker."""

    subject: str
    payload: bytes
    headers: MessageHeaders | None = None
    reply_to: str | None = None
    metadata: dict[str, Any] | None = None

    def decode_json(self) -> Any:
        """Decode the payload as JSON, raising ``ValueError`` on failure."""
        import json

        return json.loads(self.payload.decode("utf-8"))


class Subscription(Protocol):
    """Handle returned to consumers to manage a subscription lifecycle."""

    async def drain(self) -> None:
        """Allow in-flight messages to finish before closing."""
        ...

    async def unsubscribe(self) -> None:
        """Cancel the subscription immediately."""
        ...


class MessageBusPort(Protocol):
    """Primary entry point for publishing to and subscribing from NATS."""

    async def publish(
        self,
        message: OutboundMessage,
        *,
        guarantee: DeliveryGuarantee = DeliveryGuarantee.AT_LEAST_ONCE,
    ) -> None:
        """Publish a message honouring the requested delivery semantics."""
        ...

    async def request(
        self,
        message: OutboundMessage,
        *,
        timeout: float = 2.0,
    ) -> InboundMessage:
        """Send a request/response style message and await the reply."""
        ...

    async def subscribe(
        self,
        subject: str,
        handler: MessageHandler,
        *,
        queue: str | None = None,
        durable: str | None = None,
        ack_strategy: AckStrategy = AckStrategy.AUTO,
    ) -> Subscription:
        """Register a handler for the provided subject."""
        ...

    async def flush(self, timeout: float | None = None) -> None:
        """Wait until pending messages are processed by the server."""
        ...

    async def close(self) -> None:
        """Close the underlying connection gracefully."""
        ...

    @property
    def is_connected(self) -> bool:
        """Return ``True`` when the adapter is connected to NATS."""
        ...


__all__ = [
    "AckStrategy",
    "DeliveryGuarantee",
    "InboundMessage",
    "MessageBusPort",
    "MessageHandler",
    "MessageHeaders",
    "OutboundMessage",
    "Subscription",
]
