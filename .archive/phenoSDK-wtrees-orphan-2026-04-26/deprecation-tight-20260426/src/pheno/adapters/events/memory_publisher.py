"""In-memory event publisher adapter.

Simple in-memory implementation of event publishing that implements the EventPublisher
port interface.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from threading import Lock
from typing import TYPE_CHECKING

from pheno.application.ports.events import (
    EventBus,
    EventPublisher,
)
from pheno.application.ports.events import EventSubscriber as EventSubscriberPort

if TYPE_CHECKING:
    from pheno.domain.base import DomainEvent

logger = logging.getLogger(__name__)


@dataclass
class EventSubscriber:
    """
    In-memory event subscriber.
    """

    handler: callable
    event_type: str


class InMemoryEventPublisher(EventPublisher, EventSubscriberPort, EventBus):
    """In-memory event publisher implementation.

    Simple event publisher that stores events in memory and delivers them to registered
    subscribers. Useful for testing and single-process applications.

    Implements EventPublisher, EventSubscriber, and EventBus ports.
    """

    def __init__(self):
        self._subscribers: dict[str, list[EventSubscriber]] = {}
        self._lock = Lock()
        self._published_events: list[DomainEvent] = []

    def subscribe(self, event_type: str, handler: callable):
        """
        Subscribe to an event type.
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []

            self._subscribers[event_type].append(
                EventSubscriber(handler=handler, event_type=event_type),
            )

            logger.info(f"Subscribed handler to event type: {event_type}")

    def unsubscribe(self, event_type: str, handler: callable):
        """
        Unsubscribe from an event type.
        """
        with self._lock:
            if event_type in self._subscribers:
                self._subscribers[event_type] = [
                    sub for sub in self._subscribers[event_type] if sub.handler != handler
                ]

                logger.info(f"Unsubscribed handler from event type: {event_type}")

    async def publish(self, event: DomainEvent) -> None:
        """Publish an event to all subscribers.

        Args:
            event: The domain event to publish
        """
        event_type = event.__class__.__name__
        logger.info(f"Publishing event: {event_type}")

        self._published_events.append(event)

        with self._lock:
            subscribers = self._subscribers.get(event_type, [])[:]

        # Publish to subscribers
        for subscriber in subscribers:
            try:
                if asyncio.iscoroutinefunction(subscriber.handler):
                    # Run async handler in background
                    asyncio.create_task(subscriber.handler(event))
                else:
                    # Run sync handler directly
                    subscriber.handler(event)
            except Exception as e:
                logger.exception(f"Error in event handler for {event_type}: {e}")

    async def publish_batch(self, events: list[DomainEvent]) -> None:
        """
        Publish multiple events.
        """
        for event in events:
            await self.publish(event)

    def get_published_events(self) -> list[DomainEvent]:
        """
        Get list of all published events (useful for testing).
        """
        return self._published_events[:]

    def clear_published_events(self):
        """
        Clear the published events list.
        """
        self._published_events.clear()

    def clear_subscribers(self):
        """
        Clear all subscribers.
        """
        with self._lock:
            self._subscribers.clear()


__all__ = ["EventSubscriber", "InMemoryEventPublisher"]
