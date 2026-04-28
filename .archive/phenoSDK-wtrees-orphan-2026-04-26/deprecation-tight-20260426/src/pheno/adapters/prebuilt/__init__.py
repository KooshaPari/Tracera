"""Prebuilt adapter library.

This package exposes ready-to-use adapters for common infrastructure
components—HTTP clients, databases, message queues, ML inference providers,
file storage backends, caches, and monitoring stacks.  Adapters are lazily
initialised and only require their optional third-party dependencies when they
are actually used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pheno.core.registry.adapters import (
    AdapterRegistry,
    AdapterType,
    get_adapter_registry,
)

from .caching import InMemoryCacheAdapter, MemcachedAdapter, RedisCacheAdapter
from .databases import PostgreSQLAdapter, SQLiteAdapter
from .databases import RedisAdapter as RedisDatabaseAdapter
from .file_storage import GCSStorageAdapter, LocalFileStorageAdapter, S3StorageAdapter
from .http_clients import AiohttpHTTPAdapter, HttpxHTTPAdapter, RequestsHTTPAdapter
from .message_queues import KafkaAdapter, NATSAdapter, RabbitMQAdapter
from .ml_inference import MLXAdapter, OllamaAdapter, OpenAIInferenceAdapter, VLLMAdapter
from .monitoring import CustomMonitoringAdapter, DatadogAdapter, PrometheusAdapter

if TYPE_CHECKING:
    from collections.abc import Iterable


@dataclass(frozen=True)
class PrebuiltAdapter:
    name: str
    adapter_type: AdapterType
    cls: type
    metadata: dict[str, Any]


_PREBUILT: tuple[PrebuiltAdapter, ...] = (
    # HTTP clients
    PrebuiltAdapter(
        name="requests",
        adapter_type=AdapterType.HTTP,
        cls=RequestsHTTPAdapter,
        metadata={"category": "http", "dependencies": ["requests"]},
    ),
    PrebuiltAdapter(
        name="httpx",
        adapter_type=AdapterType.HTTP,
        cls=HttpxHTTPAdapter,
        metadata={"category": "http", "dependencies": ["httpx"]},
    ),
    PrebuiltAdapter(
        name="aiohttp",
        adapter_type=AdapterType.HTTP,
        cls=AiohttpHTTPAdapter,
        metadata={"category": "http", "dependencies": ["aiohttp"]},
    ),
    # Databases
    PrebuiltAdapter(
        name="postgresql",
        adapter_type=AdapterType.DATABASE,
        cls=PostgreSQLAdapter,
        metadata={"category": "database", "dependencies": ["psycopg[binary]"]},
    ),
    PrebuiltAdapter(
        name="redis",
        adapter_type=AdapterType.DATABASE,
        cls=RedisDatabaseAdapter,
        metadata={"category": "database", "dependencies": ["redis"]},
    ),
    PrebuiltAdapter(
        name="sqlite",
        adapter_type=AdapterType.DATABASE,
        cls=SQLiteAdapter,
        metadata={"category": "database", "dependencies": []},
    ),
    # Message queues
    PrebuiltAdapter(
        name="nats",
        adapter_type=AdapterType.MESSAGE_QUEUE,
        cls=NATSAdapter,
        metadata={"category": "message_queue", "dependencies": ["nats-py"]},
    ),
    PrebuiltAdapter(
        name="rabbitmq",
        adapter_type=AdapterType.MESSAGE_QUEUE,
        cls=RabbitMQAdapter,
        metadata={"category": "message_queue", "dependencies": ["pika"]},
    ),
    PrebuiltAdapter(
        name="kafka",
        adapter_type=AdapterType.MESSAGE_QUEUE,
        cls=KafkaAdapter,
        metadata={"category": "message_queue", "dependencies": ["kafka-python"]},
    ),
    # ML inference
    PrebuiltAdapter(
        name="ollama",
        adapter_type=AdapterType.ML,
        cls=OllamaAdapter,
        metadata={"category": "ml", "dependencies": ["httpx", "requests"], "singleton": False},
    ),
    PrebuiltAdapter(
        name="vllm",
        adapter_type=AdapterType.ML,
        cls=VLLMAdapter,
        metadata={"category": "ml", "dependencies": ["httpx", "requests"], "singleton": False},
    ),
    PrebuiltAdapter(
        name="mlx",
        adapter_type=AdapterType.ML,
        cls=MLXAdapter,
        metadata={"category": "ml", "dependencies": ["mlx", "mlx-lm"]},
    ),
    PrebuiltAdapter(
        name="openai",
        adapter_type=AdapterType.ML,
        cls=OpenAIInferenceAdapter,
        metadata={"category": "ml", "dependencies": ["openai"], "singleton": True},
    ),
    # File storage
    PrebuiltAdapter(
        name="local",
        adapter_type=AdapterType.STORAGE,
        cls=LocalFileStorageAdapter,
        metadata={"category": "storage", "dependencies": []},
    ),
    PrebuiltAdapter(
        name="s3",
        adapter_type=AdapterType.STORAGE,
        cls=S3StorageAdapter,
        metadata={"category": "storage", "dependencies": ["boto3"]},
    ),
    PrebuiltAdapter(
        name="gcs",
        adapter_type=AdapterType.STORAGE,
        cls=GCSStorageAdapter,
        metadata={"category": "storage", "dependencies": ["google-cloud-storage"]},
    ),
    # Caching
    PrebuiltAdapter(
        name="in_memory",
        adapter_type=AdapterType.CACHE,
        cls=InMemoryCacheAdapter,
        metadata={"category": "cache", "dependencies": []},
    ),
    PrebuiltAdapter(
        name="redis",
        adapter_type=AdapterType.CACHE,
        cls=RedisCacheAdapter,
        metadata={"category": "cache", "dependencies": ["redis"]},
    ),
    PrebuiltAdapter(
        name="memcached",
        adapter_type=AdapterType.CACHE,
        cls=MemcachedAdapter,
        metadata={"category": "cache", "dependencies": ["pymemcache"]},
    ),
    # Monitoring
    PrebuiltAdapter(
        name="prometheus",
        adapter_type=AdapterType.MONITORING,
        cls=PrometheusAdapter,
        metadata={"category": "monitoring", "dependencies": ["prometheus-client"]},
    ),
    PrebuiltAdapter(
        name="datadog",
        adapter_type=AdapterType.MONITORING,
        cls=DatadogAdapter,
        metadata={"category": "monitoring", "dependencies": ["datadog"]},
    ),
    PrebuiltAdapter(
        name="custom",
        adapter_type=AdapterType.MONITORING,
        cls=CustomMonitoringAdapter,
        metadata={"category": "monitoring", "dependencies": []},
    ),
)


def iter_prebuilt_adapters() -> Iterable[PrebuiltAdapter]:
    """Return an iterable of all prebuilt adapter definitions."""

    return tuple(_PREBUILT)


def register_prebuilt_adapters(
    registry: AdapterRegistry | None = None,
    *,
    replace: bool = False,
) -> AdapterRegistry:
    """Register all prebuilt adapters with the shared adapter registry."""

    registry = registry or get_adapter_registry()
    for adapter in _PREBUILT:
        registry.register_adapter(
            adapter.adapter_type,
            adapter.name,
            adapter.cls,
            replace=replace,
            metadata=adapter.metadata,
        )
    return registry


__all__ = [
    "PrebuiltAdapter",
    "iter_prebuilt_adapters",
    "register_prebuilt_adapters",
]
