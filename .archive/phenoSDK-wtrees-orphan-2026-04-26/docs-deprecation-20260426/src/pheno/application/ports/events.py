"""
Event port definitions.
"""

from collections.abc import Awaitable, Callable
from typing import Any, Protocol


class EventPublisher(Protocol):
    """Event publisher protocol.

    Defines the contract for publishing domain events. Adapters can implement this to
    publish events to message queues, event stores, or other event-driven systems.
    """

    async def publish(self, event: Any) -> None:
        """Publish a domain event.

        Args:
            event: Domain event to publish

        Raises:
            EventPublishError: If publishing fails
        """
        ...

    async def publish_batch(self, events: list[Any]) -> None:
        """Publish multiple domain events.

        Args:
            events: List of domain events to publish

        Raises:
            EventPublishError: If publishing fails
        """
        ...


class EventSubscriber(Protocol):
    """Event subscriber protocol.

    Defines the contract for subscribing to domain events.
    """

    async def subscribe(
        self,
        event_type: type[Any],
        handler: Callable[[Any], Awaitable[None]],
    ) -> None:
        """Subscribe to a specific event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Async function to handle the event

        Raises:
            EventSubscriptionError: If subscription fails
        """
        ...

    async def unsubscribe(
        self,
        event_type: type[Any],
        handler: Callable[[Any], Awaitable[None]],
    ) -> None:
        """Unsubscribe from a specific event type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove

        Raises:
            EventSubscriptionError: If unsubscription fails
        """
        ...


class EventBus(Protocol):
    """Event bus protocol.

    Combines publishing and subscribing capabilities. Provides in-process event
    distribution.
    """

    async def publish(self, event: Any) -> None:
        """Publish an event to all subscribers.

        Args:
            event: Event to publish

        Raises:
            EventPublishError: If publishing fails
        """
        ...

    async def subscribe(
        self,
        event_type: type[Any],
        handler: Callable[[Any], Awaitable[None]],
    ) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Async function to handle the event
        """
        ...

    async def unsubscribe(
        self,
        event_type: type[Any],
        handler: Callable[[Any], Awaitable[None]],
    ) -> None:
        """Unsubscribe from an event type.

        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
        """
        ...

    async def clear_subscribers(self, event_type: type[Any]) -> None:
        """Clear all subscribers for an event type.

        Args:
            event_type: Type of event to clear subscribers for
        """
        ...

    def get_subscriber_count(self, event_type: type[Any]) -> int:
        """Get number of subscribers for an event type.

        Args:
            event_type: Type of event

        Returns:
            Number of subscribers
        """
        ...
