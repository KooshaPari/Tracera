"""Event bus abstraction for cross-backend communication."""

import logging
from collections.abc import Callable, Coroutine
from typing import Any

from tracertm.infrastructure.nats_client import NATSClient

logger = logging.getLogger(__name__)


class EventBus:
    """High-level event bus interface for publishing and subscribing to cross-backend events.

    This class provides a simplified API on top of NATSClient for common event patterns.
    """

    # Event type constants (matches Go publisher.go constants)
    # Go-originated events
    EVENT_ITEM_CREATED = "item.created"
    EVENT_ITEM_UPDATED = "item.updated"
    EVENT_ITEM_DELETED = "item.deleted"
    EVENT_LINK_CREATED = "link.created"
    EVENT_LINK_DELETED = "link.deleted"
    EVENT_PROJECT_CREATED = "project.created"
    EVENT_PROJECT_UPDATED = "project.updated"
    EVENT_PROJECT_DELETED = "project.deleted"

    # Python-originated events
    EVENT_SPEC_CREATED = "spec.created"
    EVENT_SPEC_UPDATED = "spec.updated"
    EVENT_SPEC_DELETED = "spec.deleted"
    EVENT_AI_ANALYSIS_COMPLETE = "ai.analysis.complete"
    EVENT_EXECUTION_COMPLETED = "execution.completed"
    EVENT_EXECUTION_FAILED = "execution.failed"
    EVENT_WORKFLOW_COMPLETED = "workflow.completed"
    EVENT_AGENT_SESSION_CREATED = "agent.session.created"

    def __init__(self, nats_client: NATSClient) -> None:
        """Initialize event bus with NATS client.

        Args:
            nats_client: Connected NATSClient instance
        """
        self.nats = nats_client

    async def publish(
        self,
        event_type: str,
        project_id: str,
        entity_id: str,
        entity_type: str,
        data: dict[str, Any],
    ) -> None:
        """Publish event to NATS with standard format.

        Args:
            event_type: Type of event (use EVENT_* constants)
            project_id: Project UUID
            entity_id: Entity UUID
            entity_type: Entity type (e.g., "specification", "item")
            data: Event payload (will be serialized to JSON)
        """
        await self.nats.publish(
            event_type=event_type,
            project_id=project_id,
            entity_id=entity_id,
            entity_type=entity_type,
            data=data,
            source="python",
        )
        logger.debug("Published %s for %s %s", event_type, entity_type, entity_id)

    async def subscribe(
        self,
        event_type: str,
        handler: Callable[[dict[str, Any]], Coroutine[Any, Any, None] | None],
    ) -> None:
        """Subscribe to specific event type across all projects.

        Args:
            event_type: Event type to subscribe to (e.g., "item.created")
            handler: Async callback function to handle events
        """
        # Subscribe to: tracertm.bridge.go.*.{event_type}
        subject_pattern = f"{self.nats.SUBJECT_PREFIX}.go.*.{event_type}"
        durable_name = f"python-{event_type.replace('.', '-')}"

        await self.nats.subscribe(
            subject_pattern=subject_pattern,
            durable_name=durable_name,
            callback=handler,
        )
        logger.info("Subscribed to %s events from Go backend", event_type)

    async def subscribe_to_project(
        self,
        project_id: str,
        event_type: str,
        handler: Callable[[dict[str, Any]], None],
    ) -> None:
        """Subscribe to specific event type for a specific project.

        Args:
            project_id: Project UUID to filter events
            event_type: Event type to subscribe to
            handler: Async callback function to handle events
        """
        # Subscribe to: tracertm.bridge.go.{project_id}.{event_type}
        subject_pattern = f"{self.nats.SUBJECT_PREFIX}.go.{project_id}.{event_type}"
        durable_name = f"python-{project_id}-{event_type.replace('.', '-')}"

        await self.nats.subscribe(
            subject_pattern=subject_pattern,
            durable_name=durable_name,
            callback=handler,
        )
        logger.info("Subscribed to %s events for project %s", event_type, project_id)

    async def subscribe_all_go_events(self, handler: Callable[[dict[str, Any]], None]) -> None:
        """Subscribe to all events from Go backend (useful for monitoring/logging).

        Args:
            handler: Async callback function to handle all events
        """
        # Subscribe to: tracertm.bridge.go.>
        subject_pattern = f"{self.nats.SUBJECT_PREFIX}.go.>"
        durable_name = "python-all-go-events"

        await self.nats.subscribe(
            subject_pattern=subject_pattern,
            durable_name=durable_name,
            callback=handler,
        )
        logger.info("Subscribed to all Go backend events")

    async def health_check(self) -> dict[str, Any]:
        """Check event bus health.

        Returns:
            dict with connection status and statistics
        """
        return await self.nats.health_check()
