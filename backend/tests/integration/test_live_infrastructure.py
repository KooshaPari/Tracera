import asyncio

# This test suite specifically targets the LIVE services managed by process-compose
# It avoids mocks where possible and uses the local infrastructure directly.
from typing import Any
from uuid import uuid4

import pytest
from sqlalchemy import text


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_postgres_access(db_session: Any) -> None:
    """Verify we can reach the real local Postgres and perform a simple query."""
    result = await db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_neo4j_access(neo4j_driver: Any) -> None:
    """Verify we can reach the real local Neo4j."""
    async with neo4j_driver.session() as session:
        result = await session.run("RETURN 1 AS val")
        record = await result.single()
        assert record["val"] == 1


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_redis_access(redis_client: Any) -> None:
    """Verify we can reach the real local Redis."""
    key = f"live_test_{uuid4()}"
    await redis_client.set(key, "alive")
    val = await redis_client.get(key)
    assert val == "alive"
    await redis_client.delete(key)


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_nats_access(nats_client: Any) -> None:
    """Verify we can reach the real local NATS."""
    received = asyncio.Event()

    async def cb(_msg: Any) -> None:
        received.set()

    await nats_client.subscribe("live.python.test", cb=cb)
    await nats_client.publish("live.python.test", b"ping")

    try:
        await asyncio.wait_for(received.wait(), timeout=2.0)
    except TimeoutError:
        pytest.fail("Timed out waiting for NATS message on live service")


@pytest.mark.live
@pytest.mark.asyncio
async def test_live_full_infra_check(db_session: Any, neo4j_driver: Any, redis_client: Any, nats_client: Any) -> None:
    """A combined check to ensure the whole local stack is healthy and interconnected."""
    # This is a smoke test for the process-compose environment
    assert db_session is not None
    assert neo4j_driver is not None
    assert redis_client is not None
    assert nats_client is not None

    # Simple cross-verify: store in PG, notify via NATS
    session_id = str(uuid4())
    await db_session.execute(
        text("INSERT INTO agent_sessions (id, project_id, user_id, status) VALUES (:id, :pid, :uid, :status)"),
        {"id": session_id, "pid": str(uuid4()), "uid": str(uuid4()), "status": "testing"},
    )
    await db_session.commit()

    await nats_client.publish("session.live_check", f"created:{session_id}".encode())

    # Verify cleanup works on real DB
    await db_session.execute(text("DELETE FROM agent_sessions WHERE id = :id"), {"id": session_id})
    await db_session.commit()
