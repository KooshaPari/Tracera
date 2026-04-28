"""
Streaming module - hexagonal architecture for data streaming.

This module provides streaming and event processing capabilities
following hexagonal architecture principles.

Domain concepts (this module):
- StreamProcessor: Stream processing abstraction
- EventStream: Event stream abstraction
- MessageQueue: Message queuing abstraction
- StreamConfig: Stream configuration

Ports (pheno.ports.stream):
- StreamProvider: Interface for stream implementations
- QueueProvider: Interface for message queuing
- ProcessorProvider: Interface for stream processing

Adapters (stream-kit implementations):
- KafkaProvider, RedisStreamProvider → StreamProvider implementations
"""

from .stream_manager import StreamManager
from .types import (
    EventStream,
    MessageQueue,
    StreamConfig,
    StreamMessage,
    StreamProcessor,
)

__all__ = [
    "EventStream",
    "MessageQueue",
    "StreamConfig",
    # Manager
    "StreamManager",
    "StreamMessage",
    # Domain types
    "StreamProcessor",
]
