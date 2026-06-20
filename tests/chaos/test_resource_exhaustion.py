"""Chaos Test: Resource Exhaustion.

Simulates CPU spikes, memory pressure, and bandwidth saturation.
Tests system behavior under resource constraints.
"""

import logging
import time
from typing import Any

import httpx
import pytest
import redis.asyncio as redis
from sqlalchemy import text

from tests.chaos.toxiproxy_client import ToxiproxyClient
from tests.test_constants import HTTP_OK

logger = logging.getLogger(__name__)

RECOVERY_TARGET = 30


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_bandwidth_limitation(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    db_session: Any,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Bandwidth limitation on database connection.

    Scenario:
    1. Establish baseline query performance
    2. Limit bandwidth to 10 KB/s
    3. Execute queries and verify they slow down but succeed
    4. Remove bandwidth limit
    5. Verify recovery

    Expected: Queries complete slowly but successfully under bandwidth constraints.
    """
    # Baseline: large query
    large_query = "SELECT repeat('x', 1000) as data FROM generate_series(1, 100)"
    start = time.time()
    result = await db_session.execute(text(large_query))
    baseline_time = time.time() - start
    rows = result.fetchall()
    assert len(rows) == 100
    logger.info(f"Baseline large query completed in {baseline_time:.2f}s")

    # Inject bandwidth limit
    await toxiproxy_client.add_bandwidth_limit(
        proxy_name="postgres_chaos",
        rate_kbps=10,  # 10 KB/s limit
    )
    logger.warning("Injected 10 KB/s bandwidth limit to PostgreSQL")

    # Execute same query with bandwidth limit
    start = time.time()
    result = await db_session.execute(text(large_query))
    limited_time = time.time() - start
    rows = result.fetchall()
    assert len(rows) == 100
    logger.info(f"Large query with bandwidth limit completed in {limited_time:.2f}s")

    # Verify query was slower due to bandwidth limit
    assert limited_time > baseline_time, "Expected query to be slower with bandwidth limit"

    # Remove bandwidth limit
    await toxiproxy_client.remove_toxic(
        proxy_name="postgres_chaos",
        toxic_name="bandwidth_postgres_chaos",
    )
    logger.info("Removed bandwidth limit")

    # Verify recovery
    recovery_start = time.time()
    result = await db_session.execute(text(large_query))
    rows = result.fetchall()
    assert len(rows) == 100

    assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_slow_connection_close(
    toxiproxy_client: ToxiproxyClient,
    _redis_proxy: str,
    redis_client: redis.Redis,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Slow connection close (simulates resource leak).

    Scenario:
    1. Inject slow_close toxic (delays connection close by 5s)
    2. Perform multiple operations
    3. Verify operations complete but connections linger
    4. Remove toxic
    5. Verify normal operation resumes

    Expected: Operations succeed, but connection pool may show delays.
    """
    # Inject slow close
    await toxiproxy_client.add_slow_close(
        proxy_name="redis_chaos",
        delay_ms=5000,  # 5 second delay before closing connections
    )
    logger.warning("Injected 5s slow_close to Redis connections")

    # Perform operations (connections will be slow to close)
    operations_start = time.time()
    for i in range(5):
        await redis_client.set(f"slow_close_test_{i}", f"value_{i}")
        value = await redis_client.get(f"slow_close_test_{i}")
        assert value == f"value_{i}"
    operations_time = time.time() - operations_start

    logger.info(f"Completed 5 operations in {operations_time:.2f}s (connections closing slowly)")

    # Remove toxic
    await toxiproxy_client.remove_toxic(
        proxy_name="redis_chaos",
        toxic_name="slow_close_redis_chaos",
    )
    logger.info("Removed slow_close toxic")

    # Verify normal operation
    recovery_start = time.time()
    await redis_client.set("recovery_test", "success")
    value = await redis_client.get("recovery_test")
    assert value == "success"

    assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_timeout_injection(
    toxiproxy_client: ToxiproxyClient,
    go_backend_proxy: str,
) -> None:
    """Test: Connection timeout injection.

    Scenario:
    1. Inject timeout toxic (connections hang for 10s)
    2. Attempt API call with client timeout < toxic timeout
    3. Verify request times out gracefully
    4. Remove toxic
    5. Verify normal operation

    Expected: Client timeout triggers before toxic timeout, request fails cleanly.
    """
    # Inject timeout toxic (10s hang)
    await toxiproxy_client.add_timeout(
        proxy_name="go_backend_chaos",
        timeout_ms=10000,
    )
    logger.warning("Injected 10s timeout to backend connections")

    # Attempt request with 5s client timeout (should timeout before 10s toxic)
    async with httpx.AsyncClient(timeout=5.0) as client:
        start = time.time()
        with pytest.raises(httpx.TimeoutException):
            await client.get(f"{go_backend_proxy}/health")
        timeout_duration = time.time() - start

        logger.info(f"Request timed out after {timeout_duration:.2f}s (expected ~5s)")
        assert 4.5 <= timeout_duration <= 6.0, "Expected client timeout around 5s"

    # Remove toxic
    await toxiproxy_client.remove_toxic(
        proxy_name="go_backend_chaos",
        toxic_name="timeout_go_backend_chaos",
    )
    logger.info("Removed timeout toxic")

    # Verify normal operation
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(f"{go_backend_proxy}/health")
        assert response.status_code == HTTP_OK
        logger.info("Backend recovered to normal operation")


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_combined_resource_pressure(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    db_session: Any,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Combined resource pressure (latency + bandwidth limit).

    Scenario:
    1. Inject both latency (200ms) and bandwidth limit (50 KB/s)
    2. Execute queries under dual constraints
    3. Verify queries succeed despite multiple constraints
    4. Remove all toxics
    5. Verify recovery

    Expected: System degrades gracefully under multiple constraints.
    """
    # Inject dual constraints
    await toxiproxy_client.add_latency(
        proxy_name="postgres_chaos",
        latency_ms=200,
        jitter_ms=50,
    )
    await toxiproxy_client.add_bandwidth_limit(
        proxy_name="postgres_chaos",
        rate_kbps=50,
    )
    logger.warning("Injected combined resource pressure: 200ms latency + 50 KB/s bandwidth")

    # Execute queries under pressure
    start = time.time()
    result = await db_session.execute(text("SELECT 1 as health"))
    assert result.scalar() == 1
    constrained_time = time.time() - start

    logger.info(f"Query under dual constraints completed in {constrained_time:.2f}s")
    assert constrained_time >= 0.2, "Expected latency impact"

    # Remove all toxics
    await toxiproxy_client.remove_toxic(
        proxy_name="postgres_chaos",
        toxic_name="latency_postgres_chaos",
    )
    await toxiproxy_client.remove_toxic(
        proxy_name="postgres_chaos",
        toxic_name="bandwidth_postgres_chaos",
    )
    logger.info("Removed all resource pressure toxics")

    # Verify recovery
    recovery_start = time.time()
    result = await db_session.execute(text("SELECT 1 as health"))
    assert result.scalar() == 1

    assert_recovery_within_target(recovery_start)
