"""NATS adapter - wraps nats-py (Wrap-Over pattern)."""
import json
import asyncio
from nats.aio.client import Client as NATS
from ..domain.ports import EventPublisher
from ..logging import logger


class NatsPublisher(EventPublisher):
    """NATS event publisher adapter."""

    def __init__(self, nc: NATS):
        self._nc = nc

    async def publish(self, subject: str, data: bytes) -> None:
        """Publish an event."""
        await self._nc.publish(subject, data)
        logger.info("event_published", subject=subject)


class NatsAdapter:
    """NATS adapter factory."""

    def __init__(self, url: str):
        self._url = url
        self._nc: NATS | None = None

    async def connect(self) -> None:
        """Connect to NATS."""
        self._nc = NATS()
        await self._nc.connect(self._url)
        logger.info("nats_connected", url=self._url)

    async def close(self) -> None:
        """Close the adapter."""
        if self._nc:
            await self._nc.close()

    def get_publisher(self) -> NatsPublisher:
        """Get a NATS publisher."""
        if self._nc is None:
            raise RuntimeError("Not connected to NATS")
        return NatsPublisher(self._nc)
