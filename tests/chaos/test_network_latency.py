"""Chaos Test: Network Latency Injection.

Tests system resilience when network latency is introduced to various services.
Verifies that applications handle slow networks gracefully and recover within SLA.
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

# Recovery time target: 30 seconds
RECOVERY_TARGET = 30


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_database_latency_injection(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    db_session: Any,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Inject 500ms latency to PostgreSQL connections.

    Scenario:
    1. Establish baseline connection (healthy)
    2. Inject 500ms latency toxic
    3. Execute queries and measure response time
    4. Remove toxic
    5. Verify recovery within 30s

    Expected: Application handles latency gracefully, queries eventually succeed.
    """
    # Baseline: verify connection works
    result = await db_session.execute(text("SELECT 1 as health"))
    assert result.scalar() == 1
    logger.info("Baseline database connection OK")

    # Inject latency
    await toxiproxy_client.add_latency(
        proxy_name="postgres_chaos",
        latency_ms=500,
        jitter_ms=100,
    )
    logger.warning("Injected 500ms latency to PostgreSQL")

    # Measure query time with latency
    start = time.time()
    result = await db_session.execute(text("SELECT 1 as health"))
    latency_query_time = time.time() - start

    assert result.scalar() == 1
    assert latency_query_time >= 0.5, "Expected query to be delayed by latency"
    logger.info(f"Query completed with latency in {latency_query_time:.2f}s")

    # Remove toxic
    await toxiproxy_client.remove_toxic(
        proxy_name="postgres_chaos",
        toxic_name="latency_postgres_chaos",
    )
    logger.info("Removed latency toxic")

    # Verify recovery
    recovery_start = time.time()
    result = await db_session.execute(text("SELECT 1 as health"))
    assert result.scalar() == 1

    assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_redis_latency_injection(
    toxiproxy_client: ToxiproxyClient,
    _redis_proxy: str,
    redis_client: redis.Redis,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Inject 300ms latency to Redis connections.

    Scenario:
    1. Verify Redis is responsive (baseline)
    2. Inject latency toxic
    3. Perform cache operations and measure response
    4. Remove toxic and verify recovery

    Expected: Cache operations slow down but complete successfully.
    """
    # Baseline
    await redis_client.set("chaos_test", "baseline")
    value = await redis_client.get("chaos_test")
    assert value == "baseline"
    logger.info("Baseline Redis connection OK")

    # Inject latency
    await toxiproxy_client.add_latency(
        proxy_name="redis_chaos",
        latency_ms=300,
        jitter_ms=50,
    )
    logger.warning("Injected 300ms latency to Redis")

    # Measure operation time with latency
    start = time.time()
    await redis_client.set("chaos_test", "with_latency")
    latency_op_time = time.time() - start

    assert latency_op_time >= 0.3, "Expected operation to be delayed"
    logger.info(f"Redis SET completed with latency in {latency_op_time:.2f}s")

    # Remove toxic
    await toxiproxy_client.remove_toxic(
        proxy_name="redis_chaos",
        toxic_name="latency_redis_chaos",
    )
    logger.info("Removed latency toxic")

    # Verify recovery
    recovery_start = time.time()
    await redis_client.set("chaos_test", "recovered")
    value = await redis_client.get("chaos_test")
    assert value == "recovered"

    assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_backend_api_latency(
    toxiproxy_client: ToxiproxyClient,
    go_backend_proxy: str,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Inject latency to Go backend API.

    Scenario:
    1. Call health endpoint (baseline)
    2. Inject 1000ms latency
    3. Make API calls and verify they still succeed (slowly)
    4. Remove latency and verify recovery

    Expected: API responses are delayed but requests succeed.
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Baseline
        response = await client.get(f"{go_backend_proxy}/health")
        assert response.status_code == HTTP_OK
        logger.info("Baseline backend health check OK")

        # Inject latency
        await toxiproxy_client.add_latency(
            proxy_name="go_backend_chaos",
            latency_ms=1000,
            jitter_ms=200,
        )
        logger.warning("Injected 1000ms latency to Go backend")

        # Measure request time with latency
        start = time.time()
        response = await client.get(f"{go_backend_proxy}/health")
        latency_request_time = time.time() - start

        assert response.status_code == HTTP_OK
        assert latency_request_time >= 1.0, "Expected request to be delayed"
        logger.info(f"Health check completed with latency in {latency_request_time:.2f}s")

        # Remove toxic
        await toxiproxy_client.remove_toxic(
            proxy_name="go_backend_chaos",
            toxic_name="latency_go_backend_chaos",
        )
        logger.info("Removed latency toxic")

        # Verify recovery
        recovery_start = time.time()
        response = await client.get(f"{go_backend_proxy}/health")
        assert response.status_code == HTTP_OK

        assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_variable_latency_spikes(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    db_session: Any,
) -> None:
    """Test: Variable latency spikes (simulates intermittent network issues).

    Scenario:
    1. Inject latency with high jitter (500ms ± 300ms)
    2. Execute multiple queries
    3. Verify all succeed despite variable latency
    4. Measure distribution of response times

    Expected: System handles variable latency, no requests fail.
    """
    # Inject variable latency
    await toxiproxy_client.add_latency(
        proxy_name="postgres_chaos",
        latency_ms=500,
        jitter_ms=300,  # High jitter: 200ms - 800ms range
    )
    logger.warning("Injected variable latency (500ms ± 300ms) to PostgreSQL")

    # Execute multiple queries and measure response times
    response_times = []
    for i in range(10):
        start = time.time()
        result = await db_session.execute(text(f"SELECT {i} as num"))
        elapsed = time.time() - start
        response_times.append(elapsed)

        assert result.scalar() == i
        logger.info(f"Query {i + 1}/10 completed in {elapsed:.3f}s")

    # Verify response times are variable and within expected range
    min_time = min(response_times)
    max_time = max(response_times)
    avg_time = sum(response_times) / len(response_times)

    logger.info(f"Response time stats: min={min_time:.3f}s, max={max_time:.3f}s, avg={avg_time:.3f}s")

    assert min_time >= 0.2, "Expected minimum latency from jitter"
    assert max_time <= 1.5, "Expected maximum latency within reasonable bounds"
    assert avg_time >= 0.4, "Expected average latency around 500ms"

    # Cleanup
    await toxiproxy_client.remove_toxic(
        proxy_name="postgres_chaos",
        toxic_name="latency_postgres_chaos",
    )
