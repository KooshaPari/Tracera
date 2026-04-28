"""Redis-based event publisher adapter.

Distributed event publisher that uses Redis as the event transport layer, implementing
the EventPublisherPort interface for distributed systems.
"""

import asyncio
import logging
from typing import Any

import orjson as json

logger = logging.getLogger(__name__)


class RedisEventPublisher:
    """Redis-based event publisher implementation.

    Publishes events to Redis channels for distributed consumption. Requires redis-py
    library and a Redis server.
    """

    def __init__(self, redis_client=None, channel_prefix: str = "pheno:events"):
        """Initialize the Redis publisher.

        Args:
            redis_client: Redis client instance
            channel_prefix: Prefix for Redis channels
        """
        self.redis_client = redis_client
        self.channel_prefix = channel_prefix

        if self.redis_client is None:
            try:
                import redis

                self.redis_client = redis.Redis()
            except ImportError:
                raise ImportError("redis-py library required for RedisEventPublisher")

    async def publish(self, event_type: str, event_data: dict[str, Any]):
        """Publish an event to Redis channel.

        Args:
            event_type: Type of event being published
            event_data: Event data as dictionary
        """
        if self.redis_client is None:
            logger.warning("Redis client not available, skipping event publication")
            return

        channel = f"{self.channel_prefix}:{event_type}"

        try:
            # Serialize event data
            message = json.dumps(event_data)

            # Publish to Redis channel
            await self.redis_client.publish(channel, message)

            logger.info(f"Published event {event_type} to Redis channel {channel}")

        except Exception as e:
            logger.exception(f"Failed to publish event {event_type} to Redis: {e}")

    def publish_sync(self, event_type: str, event_data: dict[str, Any]):
        """
        Synchronous version of publish.
        """
        asyncio.run(self.publish(event_type, event_data))


__all__ = ["RedisEventPublisher"]
