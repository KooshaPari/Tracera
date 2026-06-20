"""Utilities for resilient event publishing."""

import asyncio
import logging
from typing import Any

from tracertm.infrastructure.event_bus import EventBus

logger = logging.getLogger(__name__)


async def publish_with_retry(
    event_bus: EventBus,
    event_type: str,
    project_id: str,
    entity_id: str,
    entity_type: str,
    data: dict[str, Any],
    max_retries: int = 3,
) -> None:
    """Publish event with retry logic for resilience.

    Args:
        event_bus: EventBus instance
        event_type: Type of event (use EventBus.EVENT_* constants)
        project_id: Project UUID
        entity_id: Entity UUID
        entity_type: Entity type (e.g., "specification", "test_result")
        data: Event payload
        max_retries: Maximum number of retry attempts (default: 3)

    Raises:
        Exception: If all retry attempts fail
    """
    for attempt in range(max_retries):
        try:
            await event_bus.publish(event_type, project_id, entity_id, entity_type, data)
            logger.debug("Published %s event on attempt %s", event_type, attempt + 1)
        except Exception as e:
            if attempt == max_retries - 1:
                logger.exception("Failed to publish %s after %s attempts", event_type, max_retries)
                raise
            logger.warning("Failed to publish %s (attempt %s/%s): %s", event_type, attempt + 1, max_retries, e)
            await asyncio.sleep(0.1 * (attempt + 1))
        else:
            return


async def safe_publish(
    event_bus: EventBus,
    event_type: str,
    project_id: str,
    entity_id: str,
    entity_type: str,
    data: dict[str, Any],
) -> None:
    """Publish event without failing the request if publishing fails.

    This is a fire-and-forget approach that logs errors but doesn't raise exceptions.

    Args:
        event_bus: EventBus instance
        event_type: Type of event
        project_id: Project UUID
        entity_id: Entity UUID
        entity_type: Entity type
        data: Event payload
    """
    if event_bus is None:
        msg = "EventBus is required but not initialized"
        raise RuntimeError(msg)

    try:
        await event_bus.publish(event_type, project_id, entity_id, entity_type, data)
    except Exception:
        logger.exception("Failed to publish %s event (non-blocking)", event_type)


async def safe_publish_with_retry(
    event_bus: EventBus,
    event_type: str,
    project_id: str,
    entity_id: str,
    entity_type: str,
    data: dict[str, Any],
    max_retries: int = 3,
) -> None:
    """Combine safe_publish with retry logic.

    Attempts to publish with retries but never raises exceptions to caller.

    Args:
        event_bus: EventBus instance
        event_type: Type of event
        project_id: Project UUID
        entity_id: Entity UUID
        entity_type: Entity type
        data: Event payload
        max_retries: Maximum number of retry attempts
    """
    if event_bus is None:
        msg = "EventBus is required but not initialized"
        raise RuntimeError(msg)

    try:
        await publish_with_retry(event_bus, event_type, project_id, entity_id, entity_type, data, max_retries)
    except Exception:
        logger.exception("Failed to publish %s event after retries (non-blocking)", event_type)
