"""Phase 6: E2E Integration Testing - Test Helpers.

Utility functions for integration tests including:
- Database state verification
- S3 object verification
- NATS event subscription helpers
- Test session creation
- Data assertions
"""

import asyncio
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from minio import Minio
from nats.aio.client import Client as NATSClient
from nats.js import JetStreamContext
from neo4j import AsyncDriver
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# ============================================================================
# Session Helpers
# ============================================================================


async def create_test_session(
    db_session: AsyncSession,
    neo4j_driver: AsyncDriver,
    project_id: str | None = None,
    user_id: str | None = None,
    sandbox_root: str | None = None,
) -> dict[str, Any]:
    """Create a test session in both PostgreSQL and Neo4j.

    Returns session data dict.
    """
    session_id = str(uuid4())
    project_id = project_id or str(uuid4())
    user_id = user_id or str(uuid4())
    sandbox_root = sandbox_root or f"/tmp/test-{session_id}"

    # Create in PostgreSQL
    result = await db_session.execute(
        text("""
            INSERT INTO agent_sessions (
                id, project_id, user_id, sandbox_root, status, created_at
            )
            VALUES (:id, :project_id, :user_id, :sandbox_root, :status, :created_at)
            RETURNING id, project_id, user_id, sandbox_root, status, created_at
        """),
        {
            "id": session_id,
            "project_id": project_id,
            "user_id": user_id,
            "sandbox_root": sandbox_root,
            "status": "active",
            "created_at": datetime.now(UTC),
        },
    )
    row = result.first()
    await db_session.commit()

    # Create in Neo4j
    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            """
            CREATE (s:Session:TestSession {
                id: $session_id,
                project_id: $project_id,
                user_id: $user_id,
                sandbox_root: $sandbox_root,
                status: 'active',
                created_at: datetime()
            })
            """,
            session_id=session_id,
            project_id=project_id,
            user_id=user_id,
            sandbox_root=sandbox_root,
        )

    return {
        "session_id": session_id,
        "project_id": project_id,
        "user_id": user_id,
        "sandbox_root": sandbox_root,
        "status": "active",
        "created_at": row.created_at,
    }


async def create_test_checkpoint(
    db_session: AsyncSession,
    session_id: str,
    turn_number: int = 1,
    s3_key: str | None = None,
) -> dict[str, Any]:
    """Create a test checkpoint in PostgreSQL.

    Returns checkpoint data dict.
    """
    checkpoint_id = str(uuid4())

    result = await db_session.execute(
        text("""
            INSERT INTO agent_checkpoints (
                id, session_id, turn_number, state_snapshot,
                sandbox_snapshot_s3_key, created_at
            )
            VALUES (
                :id, :session_id, :turn_number, :state_snapshot,
                :s3_key, :created_at
            )
            RETURNING id, session_id, turn_number, sandbox_snapshot_s3_key, created_at
        """),
        {
            "id": checkpoint_id,
            "session_id": session_id,
            "turn_number": turn_number,
            "state_snapshot": json.dumps({
                "messages": [],
                "turn": turn_number,
            }),
            "s3_key": s3_key,
            "created_at": datetime.now(UTC),
        },
    )
    row = result.first()
    await db_session.commit()

    return {
        "checkpoint_id": checkpoint_id,
        "session_id": session_id,
        "turn_number": turn_number,
        "s3_key": s3_key,
        "created_at": row.created_at,
    }


# ============================================================================
# Database Verification
# ============================================================================


async def verify_postgres_session(
    db_session: AsyncSession,
    session_id: str,
) -> dict[str, Any] | None:
    """Verify session exists in PostgreSQL.

    Returns session data or None.
    """
    result = await db_session.execute(
        text("SELECT * FROM agent_sessions WHERE id = :id"),
        {"id": session_id},
    )
    row = result.first()
    if not row:
        return None

    return {
        "session_id": row.id,
        "project_id": row.project_id,
        "user_id": row.user_id,
        "status": row.status,
        "sandbox_root": row.sandbox_root,
        "created_at": row.created_at,
    }


async def verify_postgres_checkpoint(
    db_session: AsyncSession,
    checkpoint_id: str,
) -> dict[str, Any] | None:
    """Verify checkpoint exists in PostgreSQL.

    Returns checkpoint data or None.
    """
    result = await db_session.execute(
        text("SELECT * FROM agent_checkpoints WHERE id = :id"),
        {"id": checkpoint_id},
    )
    row = result.first()
    if not row:
        return None

    return {
        "checkpoint_id": row.id,
        "session_id": row.session_id,
        "turn_number": row.turn_number,
        "s3_key": row.sandbox_snapshot_s3_key,
        "created_at": row.created_at,
    }


async def count_postgres_checkpoints(
    db_session: AsyncSession,
    session_id: str,
) -> int:
    """Count checkpoints for a session in PostgreSQL."""
    result = await db_session.execute(
        text("SELECT COUNT(*) FROM agent_checkpoints WHERE session_id = :id"),
        {"id": session_id},
    )
    return result.scalar()


async def verify_neo4j_session(
    neo4j_driver: AsyncDriver,
    session_id: str,
) -> dict[str, Any] | None:
    """Verify session exists in Neo4j.

    Returns session data or None.
    """
    async with neo4j_driver.session() as session:
        result = await session.run(
            """
            MATCH (s:Session {id: $session_id})
            RETURN s.id AS id, s.project_id AS project_id,
                   s.status AS status, s.sandbox_root AS sandbox_root
            """,
            session_id=session_id,
        )
        record = await result.single()
        if not record:
            return None

        return {
            "session_id": record["id"],
            "project_id": record["project_id"],
            "status": record["status"],
            "sandbox_root": record["sandbox_root"],
        }


async def verify_neo4j_relationship(
    neo4j_driver: AsyncDriver,
    session_id: str,
    relationship_type: str,
    target_id: str | None = None,
) -> bool:
    """Verify a relationship exists in Neo4j.

    Args:
        session_id: Source session ID
        relationship_type: Type of relationship (e.g., 'TOOL_CALL', 'FORKED_FROM')
        target_id: Optional target node ID

    Returns:
        True if relationship exists
    """
    async with neo4j_driver.session() as session:
        if target_id:
            query = f"""
            MATCH (s:Session {{id: $session_id}})-[r:{relationship_type}]->(t {{id: $target_id}})
            RETURN count(r) AS count
            """
            params = {"session_id": session_id, "target_id": target_id}
        else:
            query = f"""
            MATCH (s:Session {{id: $session_id}})-[r:{relationship_type}]->()
            RETURN count(r) AS count
            """
            params = {"session_id": session_id}

        result = await session.run(query, **params)
        record = await result.single()
        return record["count"] > 0


async def verify_redis_cache(
    redis_client: Redis,
    key: str,
) -> str | None:
    """Verify cache entry exists in Redis.

    Returns cached value or None.
    """
    return await redis_client.get(key)


# ============================================================================
# S3/MinIO Verification
# ============================================================================


def verify_s3_object(
    minio_client: Minio,
    bucket: str,
    object_key: str,
) -> dict[str, Any] | None:
    """Verify object exists in MinIO.

    Returns object metadata or None.
    """
    try:
        stat = minio_client.stat_object(bucket, object_key)
        return {
            "size": stat.size,
            "etag": stat.etag,
            "content_type": stat.content_type,
            "last_modified": stat.last_modified,
        }
    except Exception:
        return None


def download_s3_object(
    minio_client: Minio,
    bucket: str,
    object_key: str,
) -> bytes:
    """Download object from MinIO.

    Returns object data as bytes.
    """
    response = minio_client.get_object(bucket, object_key)
    try:
        return response.read()
    finally:
        response.close()
        response.release_conn()


def count_s3_objects(
    minio_client: Minio,
    bucket: str,
    prefix: str = "",
) -> int:
    """Count objects in MinIO with optional prefix."""
    objects = list(minio_client.list_objects(bucket, prefix=prefix, recursive=True))
    return len(objects)


# ============================================================================
# NATS Event Helpers
# ============================================================================


class EventCollector:
    """Helper class to collect NATS events during tests."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()

    async def callback(self, msg: Any) -> None:
        """Callback for NATS subscription."""
        async with self._lock:
            try:
                event = json.loads(msg.data.decode())
                self.events.append(event)
            except Exception:
                pass

    def get_events(self, event_type: str | None = None) -> list[dict[str, Any]]:
        """Get collected events, optionally filtered by type."""
        if event_type:
            return [e for e in self.events if e.get("event_type") == event_type]
        return self.events

    def count(self, event_type: str | None = None) -> int:
        """Count collected events, optionally filtered by type."""
        return len(self.get_events(event_type))

    def clear(self) -> None:
        """Clear collected events."""
        self.events.clear()

    def find_event(self, **criteria: Any) -> dict[str, Any] | None:
        """Find first event matching all criteria."""
        for event in self.events:
            if all(event.get(k) == v for k, v in criteria.items()):
                return event
        return None


async def subscribe_to_events(
    nats_client: NATSClient,
    subject: str,
    collector: EventCollector = None,
) -> tuple[Any, EventCollector]:
    """Subscribe to NATS events and collect them.

    Args:
        nats_client: NATS client
        subject: Subject pattern to subscribe to
        collector: Optional existing collector

    Returns:
        Tuple of (subscription, collector)
    """
    if collector is None:
        collector = EventCollector()

    subscription = await nats_client.subscribe(subject, cb=collector.callback)

    return subscription, collector


async def wait_for_event(
    collector: EventCollector,
    event_type: str,
    timeout: float = 5.0,
) -> dict[str, Any] | None:
    """Wait for a specific event type to be collected.

    Args:
        collector: Event collector
        event_type: Type of event to wait for
        timeout: Maximum time to wait in seconds

    Returns:
        First matching event or None if timeout
    """
    start = asyncio.get_event_loop().time()

    while (asyncio.get_event_loop().time() - start) < timeout:
        event = collector.find_event(event_type=event_type)
        if event:
            return event
        await asyncio.sleep(0.1)

    return None


async def verify_nats_stream_exists(
    nats_jetstream: JetStreamContext,
    stream_name: str,
) -> bool:
    """Verify NATS stream exists."""
    try:
        await nats_jetstream.stream_info(stream_name)
        return True
    except Exception:
        return False


async def get_nats_stream_messages(
    nats_jetstream: JetStreamContext,
    stream_name: str,
    _subject: str | None = None,
) -> list[dict[str, Any]]:
    """Get all messages from a NATS stream.

    Args:
        nats_jetstream: JetStream context
        stream_name: Stream name
        subject: Optional subject filter

    Returns:
        List of parsed message payloads
    """
    messages = []

    consumer = await nats_jetstream.add_consumer(
        stream=stream_name,
        config={
            "deliver_policy": "all",
            "ack_policy": "explicit",
        },
    )

    # Pull messages
    batch = await consumer.fetch(batch=100, timeout=1.0)
    for msg in batch:
        try:
            data = json.loads(msg.data.decode())
            messages.append(data)
            await msg.ack()
        except Exception:
            pass

    return messages


# ============================================================================
# Assertion Helpers
# ============================================================================


def assert_session_data_matches(
    postgres_session: dict[str, Any],
    neo4j_session: dict[str, Any],
) -> None:
    """Assert PostgreSQL and Neo4j session data matches."""
    assert postgres_session["session_id"] == neo4j_session["session_id"]
    assert postgres_session["project_id"] == neo4j_session["project_id"]
    assert postgres_session["status"] == neo4j_session["status"]
    assert postgres_session["sandbox_root"] == neo4j_session["sandbox_root"]


def assert_event_payload_valid(
    event: dict[str, Any],
    required_fields: list[str] | None = None,
) -> None:
    """Assert event payload has required structure."""
    # Standard fields
    assert "event_id" in event
    assert "event_type" in event
    assert "timestamp" in event
    assert "session_id" in event
    assert "metadata" in event

    # Custom required fields
    if required_fields:
        for field in required_fields:
            assert field in event, f"Missing required field: {field}"


# ============================================================================
# Cleanup Helpers
# ============================================================================


async def cleanup_test_session(
    db_session: AsyncSession,
    neo4j_driver: AsyncDriver,
    session_id: str,
) -> None:
    """Clean up test session from all databases."""
    # PostgreSQL
    await db_session.execute(
        text("DELETE FROM agent_checkpoints WHERE session_id = :id"),
        {"id": session_id},
    )
    await db_session.execute(
        text("DELETE FROM agent_sessions WHERE id = :id"),
        {"id": session_id},
    )
    await db_session.commit()

    # Neo4j
    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            "MATCH (s:Session {id: $session_id}) DETACH DELETE s",
            session_id=session_id,
        )


def cleanup_s3_objects(
    minio_client: Minio,
    bucket: str,
    prefix: str,
) -> None:
    """Clean up S3 objects with given prefix."""
    objects = minio_client.list_objects(bucket, prefix=prefix, recursive=True)
    for obj in objects:
        minio_client.remove_object(bucket, obj.object_name)
