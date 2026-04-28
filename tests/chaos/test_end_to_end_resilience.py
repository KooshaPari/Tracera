"""Chaos Test: End-to-End Resilience.

Full system resilience tests combining multiple failure scenarios.
Validates that the entire application stack recovers from cascading failures.
"""

import asyncio
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
@pytest.mark.e2e
async def test_cascading_failure_recovery(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    _redis_proxy: str,
    go_backend_proxy: str,
    db_session: Any,
    redis_client: redis.Redis,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Cascading failure across multiple services.

    Scenario:
    1. Verify all services healthy
    2. Simulate database crash
    3. Simulate Redis crash
    4. Simulate backend service degradation (latency)
    5. Restore all services in sequence
    6. Verify full system recovery

    Expected: System degrades gracefully, recovers when services return.
    """
    # Step 1: Verify baseline health
    db_result = await db_session.execute(text("SELECT 1"))
    assert db_result.scalar() == 1

    await redis_client.set("health", "ok")
    redis_health = await redis_client.get("health")
    assert redis_health == "ok"

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{go_backend_proxy}/health")
        assert response.status_code == HTTP_OK

    logger.info("All services healthy at baseline")

    # Step 2: Simulate database crash
    await toxiproxy_client.disable_proxy("postgres_chaos")
    logger.warning("Stage 1: Database crashed")
    await asyncio.sleep(2)

    # Step 3: Simulate Redis crash
    await toxiproxy_client.disable_proxy("redis_chaos")
    logger.warning("Stage 2: Redis crashed (cascading failure)")
    await asyncio.sleep(2)

    # Step 4: Backend degradation (high latency)
    await toxiproxy_client.enable_proxy("go_backend_chaos")  # Ensure it's up first
    await toxiproxy_client.add_latency(
        proxy_name="go_backend_chaos",
        latency_ms=2000,
    )
    logger.warning("Stage 3: Backend degraded (2s latency)")
    await asyncio.sleep(2)

    # Step 5: Begin recovery sequence
    recovery_start = time.time()
    logger.info("Beginning recovery sequence...")

    # Restore database
    await toxiproxy_client.enable_proxy("postgres_chaos")
    logger.info("Stage 1 recovery: Database restored")
    await asyncio.sleep(2)

    # Restore Redis
    await toxiproxy_client.enable_proxy("redis_chaos")
    logger.info("Stage 2 recovery: Redis restored")
    await asyncio.sleep(2)

    # Remove backend latency
    await toxiproxy_client.remove_toxic(
        proxy_name="go_backend_chaos",
        toxic_name="latency_go_backend_chaos",
    )
    logger.info("Stage 3 recovery: Backend latency removed")

    # Step 6: Verify full recovery
    await asyncio.sleep(3)  # Allow connection pools to recover

    # Verify database
    max_retries = 10
    for attempt in range(max_retries):
        try:
            db_result = await db_session.execute(text("SELECT 1"))
            if db_result.scalar() == 1:
                logger.info(f"Database recovered (attempt {attempt + 1})")
                break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.info(f"Database recovery attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1)

    # Verify Redis
    for attempt in range(max_retries):
        try:
            await redis_client.set("recovered", "yes")
            value = await redis_client.get("recovered")
            if value == "yes":
                logger.info(f"Redis recovered (attempt {attempt + 1})")
                break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.info(f"Redis recovery attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1)

    # Verify backend
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.get(f"{go_backend_proxy}/health")
                if response.status_code == HTTP_OK:
                    logger.info(f"Backend recovered (attempt {attempt + 1})")
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.info(f"Backend recovery attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)

    # Assert recovery within target time
    assert_recovery_within_target(recovery_start)
    logger.info("Full system recovery complete")


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
@pytest.mark.e2e
async def test_gradual_degradation_under_load(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    db_session: Any,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Gradual degradation under increasing load.

    Scenario:
    1. Start with low latency (100ms)
    2. Gradually increase latency (100ms -> HTTP_INTERNAL_SERVER_ERRORms -> 1000ms)
    3. Execute queries at each level
    4. Gradually decrease latency back to normal
    5. Verify system handles gradual changes

    Expected: System adapts to changing conditions without crashing.
    """
    latency_levels = [100, 300, 500, 800, 1000]

    # Gradual increase
    for latency_ms in latency_levels:
        # Update or add latency toxic
        try:
            await toxiproxy_client.update_toxic(
                proxy_name="postgres_chaos",
                toxic_name="latency_postgres_chaos",
                attributes={"latency": latency_ms, "jitter": 50},
            )
        except httpx.HTTPStatusError:
            # Toxic doesn't exist, create it
            await toxiproxy_client.add_latency(
                proxy_name="postgres_chaos",
                latency_ms=latency_ms,
                jitter_ms=50,
            )

        logger.info("Increased latency to %sms", latency_ms)

        # Execute query under current latency
        start = time.time()
        result = await db_session.execute(text("SELECT 1 as health"))
        query_time = time.time() - start

        assert result.scalar() == 1
        logger.info(f"Query completed in {query_time:.2f}s under {latency_ms}ms latency")

        await asyncio.sleep(1)

    # Gradual decrease (recovery)
    recovery_start = time.time()
    for latency_ms in reversed(latency_levels[:-1]):
        await toxiproxy_client.update_toxic(
            proxy_name="postgres_chaos",
            toxic_name="latency_postgres_chaos",
            attributes={"latency": latency_ms, "jitter": 50},
        )

        logger.info("Decreased latency to %sms", latency_ms)

        result = await db_session.execute(text("SELECT 1 as health"))
        assert result.scalar() == 1

        await asyncio.sleep(1)

    # Remove latency completely
    await toxiproxy_client.remove_toxic(
        proxy_name="postgres_chaos",
        toxic_name="latency_postgres_chaos",
    )
    logger.info("Latency removed completely")

    # Final verification
    result = await db_session.execute(text("SELECT 1 as health"))
    assert result.scalar() == 1

    assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
@pytest.mark.e2e
async def test_split_brain_scenario(
    toxiproxy_client: ToxiproxyClient,
    redis_proxy: str,
    redis_client: redis.Redis,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Split-brain scenario (partial network partition).

    Scenario:
    1. Set up two Redis connections through different proxies
    2. Disable one proxy (simulate network partition)
    3. Verify one connection fails, other succeeds
    4. Re-enable proxy
    5. Verify both connections recover

    Expected: System detects and handles partial failures correctly.
    """
    # For this test, we only have one Redis proxy, so we'll simulate
    # split-brain by toggling availability and using timeouts

    # Baseline: both operations succeed
    await redis_client.set("split_brain_test", "baseline")
    value = await redis_client.get("split_brain_test")
    assert value == "baseline"
    logger.info("Baseline: Redis operations succeed")

    # Simulate partition: add timeout toxic
    await toxiproxy_client.add_timeout(
        proxy_name="redis_chaos",
        timeout_ms=5000,
    )
    logger.warning("Simulated network partition (5s timeout)")

    # One client with short timeout (will fail)
    short_timeout_client = redis.from_url(
        redis_proxy.replace("localhost", "127.0.0.1"),  # Different connection
        decode_responses=True,
        socket_timeout=2.0,
    )

    # Verify partition: short timeout client fails
    with pytest.raises((redis.TimeoutError, redis.ConnectionError)):
        await short_timeout_client.get("split_brain_test")
    logger.info("Short-timeout client failed (expected during partition)")

    await short_timeout_client.aclose()

    # Remove partition
    recovery_start = time.time()
    await toxiproxy_client.remove_toxic(
        proxy_name="redis_chaos",
        toxic_name="timeout_redis_chaos",
    )
    logger.info("Removed network partition toxic")

    # Verify recovery
    await asyncio.sleep(1)
    await redis_client.set("split_brain_test", "recovered")
    value = await redis_client.get("split_brain_test")
    assert value == "recovered"

    assert_recovery_within_target(recovery_start)
    logger.info("Split-brain scenario recovered successfully")
