"""
pheno.events - Event bus and webhook management

Unified event handling for Python applications with support for:
- In-memory event bus
- Event persistence
- Webhook management with signatures
- NATS/JetStream integration (optional)

Migrated from event-kit into pheno namespace.

Usage:
    from pheno.events import EventBus, SimpleEventBus, Event

    # Create event bus
    bus = SimpleEventBus()

    # Subscribe to events
    @bus.subscribe("user.created")
    async def handle_user_created(event: Event):
        print(f"User created: {event.data}")

    # Publish events
    await bus.publish(Event(type="user.created", data={"id": 123}))

Webhooks:
    from pheno.events import WebhookManager, WebhookSigner

    # Create webhook manager
    manager = WebhookManager(signer=WebhookSigner(secret="my-secret"))

    # Register webhook
    await manager.register("https://example.com/webhook", events=["user.created"])

    # Deliver webhook
    await manager.deliver("user.created", {"id": 123})

NATS Integration:
    from pheno.events import NatsEventBus, NATSConnectionFactory

    # Create NATS connection
    factory = NATSConnectionFactory(servers=["nats://localhost:4222"])
    nc = await factory.connect()

    # Create NATS event bus
    bus = NatsEventBus(nc, stream_name="events")
    await bus.publish(Event(type="user.created", data={"id": 123}))
"""

from __future__ import annotations

from .core.event_bus import Event, EventBus, SimpleEventBus
from .core.event_store import EventStore, StoredEvent
from .webhooks.signature import WebhookReceiver, WebhookSigner
from .webhooks.webhook_manager import WebhookDelivery, WebhookManager

# Optional NATS/JetStream helpers (import lazily when used)
try:
    from .jetstream_utils import ensure_consumer, ensure_stream, ensure_workqueue
    from .nats_bus import NatsEventBus
    from .nats_factory import NATSConnectionFactory

    _HAS_NATS = True
except ImportError:
    _HAS_NATS = False
    NatsEventBus = None  # type: ignore
    NATSConnectionFactory = None  # type: ignore
    ensure_consumer = None  # type: ignore
    ensure_stream = None  # type: ignore
    ensure_workqueue = None  # type: ignore

__version__ = "0.1.0"

__all__ = [
    "Event",
    # Core event bus
    "EventBus",
    # Event persistence
    "EventStore",
    # Optional NATS exports
    "NATSConnectionFactory",
    "NatsEventBus",
    "SimpleEventBus",
    "StoredEvent",
    "WebhookDelivery",
    # Webhooks
    "WebhookManager",
    "WebhookReceiver",
    "WebhookSigner",
    "ensure_consumer",
    "ensure_stream",
    "ensure_workqueue",
]
