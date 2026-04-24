"""Feature flag management using Redis."""

import logging

from redis.asyncio import Redis

logger = logging.getLogger(__name__)

# Common feature flags
FLAG_NATS_EVENTS = "nats_events"
FLAG_CROSS_BACKEND_CALLS = "cross_backend_calls"
FLAG_SHARED_CACHE = "shared_cache"
FLAG_PYTHON_SPEC_ANALYTICS = "python_spec_analytics"
FLAG_GO_GRAPH_ANALYSIS = "go_graph_analysis"
FLAG_ENHANCED_LOGGING = "enhanced_logging"
FLAG_METRICS_COLLECTION = "metrics_collection"
FLAG_DISTRIBUTED_TRACING = "distributed_tracing"


class FeatureFlagStore:
    """Manages feature flags in Redis."""

    def __init__(self, redis: Redis) -> None:
        """Initialize feature flag store.

        Args:
            redis: Async Redis client
        """
        self.redis = redis
        self.prefix = "feature:flag:"

    async def is_enabled(self, flag_name: str) -> bool:
        """Check if flag is enabled, default to False.

        Args:
            flag_name: Name of the feature flag

        Returns:
            True if flag is enabled, False otherwise
        """
        try:
            val = await self.redis.get(f"{self.prefix}{flag_name}")
        except Exception:
            # Default to disabled on error
            return False
        else:
            return val == b"true" if val else False

    async def set_flag(self, flag_name: str, enabled: bool) -> None:
        """Set flag value.

        Args:
            flag_name: Name of the feature flag
            enabled: Whether to enable or disable the flag
        """
        value = "true" if enabled else "false"
        await self.redis.set(f"{self.prefix}{flag_name}", value)

    async def enable_flag(self, flag_name: str) -> None:
        """Enable a feature flag.

        Args:
            flag_name: Name of the feature flag
        """
        await self.set_flag(flag_name, True)

    async def disable_flag(self, flag_name: str) -> None:
        """Disable a feature flag.

        Args:
            flag_name: Name of the feature flag
        """
        await self.set_flag(flag_name, False)

    async def get_flag(self, flag_name: str) -> tuple[bool, bool]:
        """Get flag value and existence status.

        Args:
            flag_name: Name of the feature flag

        Returns:
            Tuple of (value, exists) where value is the flag state
            and exists indicates if the flag is set
        """
        try:
            val = await self.redis.get(f"{self.prefix}{flag_name}")
            if val is None:
                return False, False
        except Exception:
            return False, False
        else:
            return val == b"true", True

    async def delete_flag(self, flag_name: str) -> None:
        """Remove a feature flag.

        Args:
            flag_name: Name of the feature flag
        """
        await self.redis.delete(f"{self.prefix}{flag_name}")

    async def list_flags(self) -> dict[str, bool]:
        """List all feature flags and their values.

        Returns:
            Dictionary mapping flag names to their enabled state
        """
        pattern = f"{self.prefix}*"
        flags = {}

        try:
            cursor = 0
            while True:
                cursor, keys = await self.redis.scan(cursor=cursor, match=pattern, count=100)

                for key in keys:
                    val = await self.redis.get(key)
                    if val is not None:
                        # Remove prefix from key
                        flag_name = key.decode("utf-8")[len(self.prefix) :]
                        flags[flag_name] = val == b"true"

                if cursor == 0:
                    break

        except Exception as e:
            logger.warning("Failed to list feature flags from Redis: %s", e)

        return flags

    async def set_flag_with_ttl(self, flag_name: str, enabled: bool, ttl_seconds: int) -> None:
        """Set flag with expiration time.

        Args:
            flag_name: Name of the feature flag
            enabled: Whether to enable or disable the flag
            ttl_seconds: Time to live in seconds
        """
        value = "true" if enabled else "false"
        await self.redis.setex(f"{self.prefix}{flag_name}", ttl_seconds, value)

    async def initialize_default_flags(self) -> None:
        """Initialize default feature flags if they don't exist."""
        defaults = {
            FLAG_NATS_EVENTS: True,
            FLAG_CROSS_BACKEND_CALLS: True,
            FLAG_SHARED_CACHE: True,
            FLAG_PYTHON_SPEC_ANALYTICS: True,
            FLAG_GO_GRAPH_ANALYSIS: True,
            FLAG_ENHANCED_LOGGING: False,
            FLAG_METRICS_COLLECTION: True,
            FLAG_DISTRIBUTED_TRACING: True,
        }

        for flag, default_value in defaults.items():
            # Only set if flag doesn't exist
            _, exists = await self.get_flag(flag)
            if not exists:
                await self.set_flag(flag, default_value)
