"""
Event system adapters - implementations for event publishing.

Contains adapter implementations for event publishers, stores, and buses
that implement the ports defined in pheno.ports.events.
"""

# Auto-register adapters
from ..registry import AdapterType, get_registry
from .memory_publisher import InMemoryEventPublisher
from .redis_publisher import RedisEventPublisher

registry = get_registry()
registry.register_adapter(AdapterType.EVENT, "memory", InMemoryEventPublisher)
registry.register_adapter(AdapterType.EVENT, "redis", RedisEventPublisher)

__all__ = [
    "InMemoryEventPublisher",
    "RedisEventPublisher",
]
