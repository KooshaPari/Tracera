"""Chaos Test: Connection Failures & Pod Kills.

Simulates service crashes, container kills, and connection drops.
Tests automatic reconnection, retry logic, and graceful degradation.
"""

import asyncio
import logging
import time
from typing import Any

import httpx
import pytest
import redis.asyncio as redis
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, OperationalError

from tests.chaos.toxiproxy_client import ToxiproxyClient
from tests.test_constants import HTTP_OK

logger = logging.getLogger(__name__)

RECOVERY_TARGET = 30


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_database_connection_drop(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    db_session: Any,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Simulate database connection drop (pod kill).

    Scenario:
    1. Establish connection and execute query
    2. Disable proxy (simulate database crash)
    3. Attempt query (should fail)
    4. Re-enable proxy (simulate database restart)
    5. Verify reconnection and recovery

    Expected: Application detects failure, reconnects when database is back.
    """
    # Baseline
    result = await db_session.execute(text("SELECT 1 as health"))
    assert result.scalar() == 1
    logger.info("Baseline database connection OK")

    # Simulate database crash: disable proxy
    await toxiproxy_client.disable_proxy("postgres_chaos")
    logger.warning("Simulated database crash (disabled proxy)")

    # Wait a moment for connection to break
    await asyncio.sleep(1)

    # Attempt to use broken connection (should fail)
    with pytest.raises((OperationalError, DBAPIError, OSError)):
        await db_session.execute(text("SELECT 1"))
    logger.info("Confirmed connection failure detected")

    # Simulate database restart: re-enable proxy
    recovery_start = time.time()
    await toxiproxy_client.enable_proxy("postgres_chaos")
    logger.info("Simulated database restart (re-enabled proxy)")

    # Wait for connection pool to recover
    await asyncio.sleep(2)

    # Verify recovery (may need new session for reconnect)
    max_retries = 10
    for attempt in range(max_retries):
        try:
            result = await db_session.execute(text("SELECT 1 as health"))
            if result.scalar() == 1:
                logger.info(f"Database reconnected after {attempt + 1} attempts")
                break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.info(f"Reconnection attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1)

    assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_redis_connection_drop(
    toxiproxy_client: ToxiproxyClient,
    _redis_proxy: str,
    redis_client: redis.Redis,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Simulate Redis connection drop.

    Scenario:
    1. Verify Redis connection
    2. Disable proxy (simulate Redis crash)
    3. Attempt operations (should fail or timeout)
    4. Re-enable proxy
    5. Verify reconnection

    Expected: Redis client reconnects automatically.
    """
    # Baseline
    await redis_client.set("chaos_test", "baseline")
    value = await redis_client.get("chaos_test")
    assert value == "baseline"
    logger.info("Baseline Redis connection OK")

    # Simulate Redis crash
    await toxiproxy_client.disable_proxy("redis_chaos")
    logger.warning("Simulated Redis crash (disabled proxy)")

    await asyncio.sleep(1)

    # Attempt operation (should fail)
    with pytest.raises((redis.ConnectionError, redis.TimeoutError, OSError)):
        await redis_client.get("chaos_test")
    logger.info("Confirmed Redis connection failure")

    # Simulate Redis restart
    recovery_start = time.time()
    await toxiproxy_client.enable_proxy("redis_chaos")
    logger.info("Simulated Redis restart (re-enabled proxy)")

    # Wait for reconnection
    await asyncio.sleep(2)

    # Verify recovery with retries
    max_retries = 10
    for attempt in range(max_retries):
        try:
            await redis_client.set("chaos_test", "recovered")
            value = await redis_client.get("chaos_test")
            if value == "recovered":
                logger.info(f"Redis reconnected after {attempt + 1} attempts")
                break
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.info(f"Reconnection attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(1)

    assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_backend_service_restart(
    toxiproxy_client: ToxiproxyClient,
    go_backend_proxy: str,
    assert_recovery_within_target: Any,
) -> None:
    """Test: Simulate backend service restart (pod kill).

    Scenario:
    1. Verify backend is healthy
    2. Disable proxy (simulate pod termination)
    3. Attempt API calls (should fail)
    4. Re-enable proxy (simulate pod restart)
    5. Verify service recovery

    Expected: Clients detect failure and retry when service is back.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Baseline
        response = await client.get(f"{go_backend_proxy}/health")
        assert response.status_code == HTTP_OK
        logger.info("Baseline backend health OK")

        # Simulate pod kill
        await toxiproxy_client.disable_proxy("go_backend_chaos")
        logger.warning("Simulated backend pod kill (disabled proxy)")

        await asyncio.sleep(1)

        # Attempt request (should fail)
        with pytest.raises((httpx.ConnectError, httpx.TimeoutException)):
            await client.get(f"{go_backend_proxy}/health")
        logger.info("Confirmed backend connection failure")

        # Simulate pod restart
        recovery_start = time.time()
        await toxiproxy_client.enable_proxy("go_backend_chaos")
        logger.info("Simulated backend pod restart (re-enabled proxy)")

        # Wait for service to be ready
        await asyncio.sleep(3)

        # Verify recovery with retries
        max_retries = 10
        for attempt in range(max_retries):
            try:
                response = await client.get(f"{go_backend_proxy}/health")
                if response.status_code == HTTP_OK:
                    logger.info(f"Backend service recovered after {attempt + 1} attempts")
                    break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                logger.info(f"Recovery attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(1)

        assert_recovery_within_target(recovery_start)


@pytest.mark.asyncio
@pytest.mark.chaos
@pytest.mark.slow
async def test_intermittent_connection_drops(
    toxiproxy_client: ToxiproxyClient,
    _postgres_proxy: str,
    db_session: Any,
) -> None:
    """Test: Intermittent connection drops (flapping network).

    Scenario:
    1. Repeatedly toggle proxy on/off
    2. Attempt queries during each cycle
    3. Verify application handles flapping gracefully

    Expected: Some queries fail, but system doesn't crash; retries succeed.
    """
    successful_queries = 0
    failed_queries = 0

    for cycle in range(5):
        # Enable proxy
        await toxiproxy_client.enable_proxy("postgres_chaos")
        await asyncio.sleep(0.5)

        # Try query while connection is up
        try:
            result = await db_session.execute(text(f"SELECT {cycle} as num"))
            if result.scalar() == cycle:
                successful_queries += 1
                logger.info(f"Cycle {cycle + 1}: Query succeeded")
        except Exception as e:
            failed_queries += 1
            logger.info(f"Cycle {cycle + 1}: Query failed - {e}")

        # Disable proxy (simulate connection drop)
        await toxiproxy_client.disable_proxy("postgres_chaos")
        await asyncio.sleep(0.5)

        # Try query while connection is down (expected to fail)
        try:
            await db_session.execute(text("SELECT 1"))
            logger.warning(f"Cycle {cycle + 1}: Unexpected success during outage")
        except Exception:
            logger.info(f"Cycle {cycle + 1}: Expected failure during outage")

    # Re-enable for cleanup
    await toxiproxy_client.enable_proxy("postgres_chaos")

    logger.info(
        "Flapping test complete: %s succeeded, %s failed (as expected during outages)",
        successful_queries,
        failed_queries,
    )

    # At least some queries should have succeeded
    assert successful_queries > 0, "Expected at least some queries to succeed"
