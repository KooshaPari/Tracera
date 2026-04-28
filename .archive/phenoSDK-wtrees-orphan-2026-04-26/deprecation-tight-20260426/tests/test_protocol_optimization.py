"""
Tests for protocol optimization module.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest

from pheno.llm.protocol import (
    BatchMetrics,
    ConnectionPool,
    ContinuousBatcher,
    OptimizedProtocol,
    PriorityQueue,
    ProtocolConfig,
    Request,
    RequestCompressor,
    get_optimized_protocol,
)


def test_protocol_config_defaults():
    """
    Test that ProtocolConfig has sensible defaults.
    """
    config = ProtocolConfig()

    assert config.enable_batching is True
    assert config.max_batch_size == 64
    assert config.batch_timeout_ms == 50
    assert config.enable_compression is True
    assert config.compression_threshold == 1024
    assert config.compression_level == 6
    assert config.enable_pooling is True
    assert config.pool_size == 10
    assert config.enable_priority_queue is True
    assert config.priority_levels == 3


def test_request_creation():
    """
    Test Request dataclass creation.
    """
    request = Request(
        id="test_123",
        payload={"model": "gpt-4", "prompt": "Hello"},
        priority=1,
    )

    assert request.id == "test_123"
    assert request.payload["model"] == "gpt-4"
    assert request.priority == 1
    assert request.callback is None
    assert isinstance(request.created_at, float)
    assert isinstance(request.metadata, dict)


def test_batch_metrics_creation():
    """
    Test BatchMetrics dataclass creation.
    """
    metrics = BatchMetrics(
        batch_id="batch_123",
        batch_size=10,
        wait_time_ms=25.5,
        process_time_ms=100.2,
        compression_ratio=0.35,
        total_requests=10,
        successful_requests=9,
        failed_requests=1,
    )

    assert metrics.batch_id == "batch_123"
    assert metrics.batch_size == 10
    assert metrics.successful_requests == 9
    assert metrics.failed_requests == 1


@pytest.mark.asyncio
async def test_continuous_batcher_add_request():
    """
    Test adding requests to continuous batcher.
    """
    config = ProtocolConfig()
    batcher = ContinuousBatcher(config)

    request = Request(id="test_1", payload={"data": "test"})
    await batcher.add_request(request)

    # Should be able to get the request back
    batch = await batcher.get_next_batch()
    assert len(batch) == 1
    assert batch[0].id == "test_1"


@pytest.mark.asyncio
async def test_continuous_batcher_timeout():
    """
    Test batcher timeout behavior.
    """
    config = ProtocolConfig(batch_timeout_ms=10)  # Very short timeout
    batcher = ContinuousBatcher(config)

    # Don't add any requests
    batch = await batcher.get_next_batch()

    # Should return empty batch after timeout
    assert len(batch) == 0


def test_request_compressor_small_payload():
    """
    Test that small payloads are not compressed.
    """
    config = ProtocolConfig(compression_threshold=1024)
    compressor = RequestCompressor(config)

    small_payload = {"model": "gpt-4", "prompt": "Hi"}
    compressed = compressor.compress_payload(small_payload)

    # Should be JSON encoded but not gzip compressed
    assert len(compressed) < 100  # Small size

    # Should be able to decompress
    decompressed = compressor.decompress_payload(compressed)
    assert decompressed["model"] == "gpt-4"


def test_request_compressor_large_payload():
    """
    Test that large payloads are compressed.
    """
    config = ProtocolConfig(compression_threshold=100)  # Low threshold
    compressor = RequestCompressor(config)

    # Create large payload
    large_payload = {
        "model": "gpt-4",
        "prompt": "Hello " * 1000,  # ~6KB
    }
    compressed = compressor.compress_payload(large_payload)

    # Should be compressed (smaller than original)
    import json

    original_size = len(json.dumps(large_payload).encode())
    assert len(compressed) < original_size

    # Should be able to decompress
    decompressed = compressor.decompress_payload(compressed)
    assert decompressed["model"] == "gpt-4"
    assert "Hello " in decompressed["prompt"]


def test_request_compressor_stats():
    """
    Test compression statistics tracking.
    """
    config = ProtocolConfig(compression_threshold=100)
    compressor = RequestCompressor(config)

    # Compress a large payload
    large_payload = {"model": "gpt-4", "prompt": "Hello " * 1000}
    compressor.compress_payload(large_payload)

    stats = compressor.get_stats()
    assert stats["total_compressed"] == 1
    assert stats["total_savings_bytes"] > 0


@pytest.mark.asyncio
async def test_connection_pool_acquire_release():
    """
    Test connection pool acquire and release.
    """
    config = ProtocolConfig(pool_size=5)
    pool = ConnectionPool(config)

    # Acquire a connection
    conn1 = await pool.acquire()
    assert conn1 is not None

    # Release it back
    await pool.release(conn1)

    # Should be able to acquire it again
    conn2 = await pool.acquire()
    assert conn2 is not None


@pytest.mark.asyncio
async def test_connection_pool_stats():
    """
    Test connection pool statistics.
    """
    config = ProtocolConfig(pool_size=5)
    pool = ConnectionPool(config)

    # Acquire and release a connection
    conn = await pool.acquire()
    await pool.release(conn)

    stats = pool.get_stats()
    assert stats["total_requests"] >= 1
    assert "cache_hit_rate" in stats
    assert stats["pool_size"] >= 0


@pytest.mark.asyncio
async def test_priority_queue_order():
    """
    Test that priority queue respects priority order.
    """
    config = ProtocolConfig(priority_levels=3)
    queue = PriorityQueue(config)

    # Add requests with different priorities
    low = Request(id="low", payload={}, priority=2)
    medium = Request(id="medium", payload={}, priority=1)
    high = Request(id="high", payload={}, priority=0)

    # Add in random order
    await queue.enqueue(low)
    await queue.enqueue(high)
    await queue.enqueue(medium)

    # Should dequeue in priority order
    req1 = await queue.dequeue()
    assert req1.id == "high"  # Priority 0 first

    req2 = await queue.dequeue()
    assert req2.id == "medium"  # Priority 1 second

    req3 = await queue.dequeue()
    assert req3.id == "low"  # Priority 2 last


@pytest.mark.asyncio
async def test_optimized_protocol_creation():
    """
    Test OptimizedProtocol initialization.
    """
    config = ProtocolConfig()
    protocol = OptimizedProtocol(config)

    assert protocol.config == config
    assert protocol.batcher is not None
    assert protocol.compressor is not None
    assert protocol.pool is not None
    assert protocol.priority_queue is not None


@pytest.mark.asyncio
async def test_optimized_protocol_send_request():
    """
    Test sending a request through optimized protocol.
    """
    protocol = OptimizedProtocol()

    response = await protocol.send_request(
        {
            "model": "gpt-4",
            "prompt": "Test prompt",
        }
    )

    assert response is not None
    assert "status" in response
    assert response["status"] == "success"


@pytest.mark.asyncio
async def test_optimized_protocol_priority_request():
    """
    Test sending priority requests.
    """
    protocol = OptimizedProtocol()

    # High priority request
    response = await protocol.send_request(
        payload={"model": "gpt-4", "prompt": "Urgent"},
        priority=0,
    )

    assert response is not None
    assert response["status"] == "success"


@pytest.mark.asyncio
async def test_optimized_protocol_stats():
    """
    Test protocol statistics collection.
    """
    protocol = OptimizedProtocol()

    # Send a request
    await protocol.send_request({"model": "gpt-4", "prompt": "Test"})

    stats = protocol.get_stats()
    assert stats["total_requests"] >= 1
    assert stats["successful_requests"] >= 1
    assert "avg_latency_ms" in stats


def test_get_optimized_protocol_singleton():
    """
    Test that get_optimized_protocol returns singleton.
    """
    protocol1 = get_optimized_protocol()
    protocol2 = get_optimized_protocol()

    # Should be the same instance
    assert protocol1 is protocol2


@pytest.mark.asyncio
async def test_optimized_protocol_with_callback():
    """
    Test protocol with callback function.
    """
    protocol = OptimizedProtocol()
    callback_called = False
    callback_response = None

    def callback(response):
        nonlocal callback_called, callback_response
        callback_called = True
        callback_response = response

    response = await protocol.send_request(
        payload={"model": "gpt-4", "prompt": "Test"},
        callback=callback,
    )

    assert response is not None
    assert callback_called is True
    assert callback_response == response


def test_protocol_config_custom():
    """
    Test custom protocol configuration.
    """
    config = ProtocolConfig(
        enable_batching=False,
        enable_compression=False,
        enable_pooling=False,
        enable_priority_queue=False,
    )

    protocol = OptimizedProtocol(config)

    assert protocol.batcher is None
    assert protocol.compressor is None
    assert protocol.pool is None
    assert protocol.priority_queue is None


@pytest.mark.asyncio
async def test_optimized_protocol_disabled_features():
    """
    Test protocol with all optimizations disabled.
    """
    config = ProtocolConfig(
        enable_batching=False,
        enable_compression=False,
        enable_pooling=False,
        enable_priority_queue=False,
    )

    protocol = OptimizedProtocol(config)

    # Should still work without optimizations
    response = await protocol.send_request(
        {
            "model": "gpt-4",
            "prompt": "Test",
        }
    )

    assert response is not None
    assert response["status"] == "success"


if __name__ == "__main__":
    # Run basic tests
    test_protocol_config_defaults()
    test_request_creation()
    test_batch_metrics_creation()

    # Run async tests
    asyncio.run(test_continuous_batcher_add_request())
    asyncio.run(test_continuous_batcher_timeout())
    asyncio.run(test_connection_pool_acquire_release())
    asyncio.run(test_priority_queue_order())
    asyncio.run(test_optimized_protocol_send_request())
    asyncio.run(test_optimized_protocol_stats())

    print("All basic tests passed!")
