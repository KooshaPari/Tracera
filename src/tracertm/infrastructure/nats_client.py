"""NATS client for bidirectional Go-Python communication."""

import asyncio
import contextlib
import json
import logging
import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any

import nats

if TYPE_CHECKING:
    from nats.aio.client import Client as NATS
    from nats.js import JetStreamContext

logger = logging.getLogger(__name__)


class NATSClient:
    """NATS client for event-driven communication between Go and Python backends.

    Implements JetStream-based messaging with durable subscriptions for reliable
    event delivery across the TraceRTM system.
    """

    # Subject pattern: tracertm.bridge.{source}.{project_id}.{event_type}
    SUBJECT_PREFIX = "tracertm.bridge"
    STREAM_NAME = "TRACERTM_BRIDGE"

    def __init__(self, url: str | None = None, creds_path: str | None = None) -> None:
        """Initialize NATS client.

        Args:
            url: NATS server URL (defaults to NATS_URL env var or nats://localhost:4222)
            creds_path: Path to NATS credentials file (defaults to NATS_CREDS_PATH env var)
        """
        self.url = url or os.getenv("NATS_URL", "nats://localhost:4222")
        self.creds_path = creds_path or os.getenv("NATS_CREDS_PATH")

        self._nc: NATS | None = None
        self._js: JetStreamContext | None = None
        self._subscriptions: dict[str, Any] = {}
        self._message_tasks: list[asyncio.Task[None]] = []

    async def connect(self) -> None:
        """Connect to NATS server and initialize JetStream.

        Uses file-based credentials if NATS_CREDS_PATH is provided, otherwise
        connects without authentication (for local development).
        """
        try:
            # Build connection options
            options: dict[str, Any] = {
                "servers": [self.url],
                "name": "TraceRTM-Python",
            }

            # Add credentials if provided
            if self.creds_path and Path(self.creds_path).exists():
                options["user_credentials"] = self.creds_path
                logger.info("Connecting to NATS with credentials: %s", self.creds_path)
            else:
                logger.info("Connecting to NATS without credentials: %s", self.url)

            # Connect to NATS
            self._nc = await nats.connect(**options)
            logger.info("Connected to NATS at %s", self.url)

            # Initialize JetStream
            self._js = self._nc.jetstream()

            # Ensure the stream exists
            await self._ensure_stream()

        except Exception:
            logger.exception("Failed to connect to NATS")
            raise

    async def _ensure_stream(self) -> None:
        """Create or update the JetStream stream for bridge events."""
        if not self._js:
            msg = "JetStream not initialized"
            raise RuntimeError(msg)

        try:
            stream_name = self.STREAM_NAME
            subjects = [f"{self.SUBJECT_PREFIX}.>"]
            # nats-py expects seconds and converts to nanoseconds internally
            max_age = 7 * 24 * 60 * 60  # 7 days in seconds

            try:
                await self._js.add_stream(
                    name=stream_name,
                    subjects=subjects,
                    retention="interest",
                    storage="file",
                    max_age=max_age,
                )
                logger.info("Created JetStream stream: %s", stream_name)
            except Exception as e:
                # Stream might already exist, try to update it
                if "already in use" in str(e) or "stream name already in use" in str(e):
                    await self._js.update_stream(
                        name=stream_name,
                        subjects=subjects,
                        retention="interest",
                        storage="file",
                        max_age=max_age,
                    )
                    logger.info("Updated JetStream stream: %s", stream_name)
                else:
                    raise

        except Exception:
            logger.exception("Failed to ensure stream")
            raise

    async def publish(
        self,
        event_type: str,
        project_id: str,
        entity_id: str,
        entity_type: str,
        data: dict[str, Any],
        source: str = "python",
    ) -> None:
        """Publish an event to NATS with standard format.

        Args:
            event_type: Type of event (e.g., "spec.created", "ai.analysis.complete")
            project_id: Project UUID
            entity_id: Entity UUID
            entity_type: Entity type (e.g., "specification", "test_result")
            data: Event payload
            source: Event source ("python" or "go")
        """
        if not self._js:
            msg = "Not connected to NATS"
            raise RuntimeError(msg)

        # Build subject: tracertm.bridge.{source}.{project_id}.{event_type}
        subject = f"{self.SUBJECT_PREFIX}.{source}.{project_id}.{event_type}"

        # Build event payload matching Go Event struct
        event = {
            "type": event_type,
            "project_id": project_id,
            "entity_id": entity_id,
            "entity_type": entity_type,
            "data": data,
            "source": source,
        }

        try:
            # Publish to JetStream
            payload = json.dumps(event).encode("utf-8")
            ack = await self._js.publish(subject, payload)
            logger.debug("Published event %s to %s (stream=%s, seq=%s)", event_type, subject, ack.stream, ack.seq)
        except Exception:
            logger.exception("Failed to publish event to %s", subject)
            raise

    async def subscribe(
        self,
        subject_pattern: str,
        durable_name: str,
        callback: Callable[[dict[str, Any]], Awaitable[None] | None],
    ) -> None:
        """Subscribe to events with a durable JetStream consumer.

        Args:
            subject_pattern: Subject pattern to subscribe to (e.g., "tracertm.bridge.go.*.item.created")
            durable_name: Durable consumer name (must be unique per subscriber)
            callback: Sync or async callback function to handle events
        """
        if not self._js:
            msg = "Not connected to NATS"
            raise RuntimeError(msg)

        try:
            # Create durable consumer
            psub = await self._js.subscribe(
                subject_pattern,
                durable=durable_name,
                stream=self.STREAM_NAME,
            )

            # Store subscription
            self._subscriptions[durable_name] = psub

            logger.info("Subscribed to %s with durable consumer %s", subject_pattern, durable_name)

            # Run message loop in background so subscribe() returns and startup can complete
            async def message_loop() -> None:
                try:
                    async for msg in psub.messages:
                        try:
                            event = json.loads(msg.data.decode("utf-8"))
                            result = callback(event)
                            if asyncio.iscoroutine(result):
                                await result
                            await msg.ack()
                        except json.JSONDecodeError:
                            logger.exception("Failed to decode event")
                            await msg.nak()
                        except Exception:
                            logger.exception("Error processing event")
                            await msg.nak()
                except asyncio.CancelledError:
                    pass
                except Exception:
                    logger.exception("Message loop error for %s", subject_pattern)

            task = asyncio.create_task(message_loop())
            self._message_tasks.append(task)

        except Exception:
            logger.exception("Failed to subscribe to %s", subject_pattern)
            raise

    async def unsubscribe(self, durable_name: str) -> None:
        """Unsubscribe from a durable consumer.

        Args:
            durable_name: Name of the durable consumer to unsubscribe from
        """
        if durable_name in self._subscriptions:
            try:
                await self._subscriptions[durable_name].unsubscribe()
                del self._subscriptions[durable_name]
                logger.info("Unsubscribed from %s", durable_name)
            except Exception:
                logger.exception("Failed to unsubscribe from %s", durable_name)
                raise

    async def close(self) -> None:
        """Close all subscriptions and disconnect from NATS."""
        # Cancel message loop tasks first
        for task in self._message_tasks:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
        self._message_tasks.clear()

        # Unsubscribe from all
        for durable_name in list(self._subscriptions.keys()):
            try:
                await self.unsubscribe(durable_name)
            except Exception:
                logger.exception("Error unsubscribing from %s", durable_name)

        # Close connection
        if self._nc:
            await self._nc.close()
            logger.info("Closed NATS connection")

    @property
    def is_connected(self) -> bool:
        """Check if connected to NATS."""
        return self._nc is not None and self._nc.is_connected

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on NATS connection.

        Returns:
            dict with connection status and statistics
        """
        if not self._nc or not self._nc.is_connected:
            return {
                "connected": False,
                "error": "Not connected to NATS",
            }

        stats = self._nc.stats
        return {
            "connected": True,
            "url": self.url,
            "subscriptions": len(self._subscriptions),
            "in_msgs": stats["in_msgs"],
            "out_msgs": stats["out_msgs"],
            "in_bytes": stats["in_bytes"],
            "out_bytes": stats["out_bytes"],
            "reconnects": stats["reconnects"],
        }
