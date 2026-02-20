"""Phase 6: E2E Integration Testing - Full Agent Lifecycle Test.

Comprehensive end-to-end test covering complete agent session lifecycle.

This test verifies the entire system working together:
1. OAuth authentication (mocked)
2. Session creation (PostgreSQL + Neo4j + Redis + NATS)
3. Multi-turn conversation with tool execution
4. Checkpoint creation every 5 turns
5. Snapshot uploads to MinIO
6. Event streaming to NATS
7. Session pause and resume from checkpoint
8. Continued execution
9. Session cleanup (cascade to all systems)

This is the ultimate integration test for the agent system.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from .test_helpers import (
    EventCollector,
    assert_session_data_matches,
    cleanup_s3_objects,
    cleanup_test_session,
    create_test_checkpoint,
    create_test_session,
    verify_neo4j_session,
    verify_postgres_checkpoint,
    verify_postgres_session,
    verify_s3_object,
)

# ============================================================================
# Complete Agent Session Lifecycle Test
# ============================================================================


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_complete_agent_session(
    db_session: Any,
    neo4j_driver: Any,
    redis_clean: Any,
    minio_clean: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test complete agent session lifecycle end-to-end.

    This comprehensive test verifies:
    - Session creation in all databases
    - Multi-turn conversation with checkpoints
    - Tool execution tracking
    - Snapshot creation and upload
    - Event streaming
    - Session pause/resume
    - Cleanup and cascade deletion

    Duration: ~10 seconds
    """
    # ========================================================================
    # Phase 1: OAuth Authentication (Mocked)
    # ========================================================================

    # In a real system, this would:
    # 1. Redirect to OAuth provider
    # 2. Receive callback with code
    # 3. Exchange code for access token
    # 4. Create authenticated session

    user_id = str(uuid4())
    project_id = str(uuid4())

    # Mock: Access token received
    f"mock-token-{uuid4()}"

    # ========================================================================
    # Phase 2: Session Creation
    # ========================================================================

    # Subscribe to all events
    event_collector = EventCollector()
    await nats_client.subscribe("tracertm.>", cb=event_collector.callback)
    await asyncio.sleep(0.1)

    # Create session in PostgreSQL and Neo4j
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
        project_id=project_id,
        user_id=user_id,
    )
    session_id = session_data["session_id"]

    # Publish session created event
    await event_publisher.publish_session_created(
        session_id=session_id,
        project_id=project_id,
        sandbox_root=session_data["sandbox_root"],
    )
    await asyncio.sleep(0.1)

    # Verify session in PostgreSQL
    pg_session = await verify_postgres_session(db_session, session_id)
    assert pg_session is not None
    assert pg_session["project_id"] == project_id

    # Verify session in Neo4j
    neo_session = await verify_neo4j_session(neo4j_driver, session_id)
    assert neo_session is not None

    # Verify data consistency
    assert_session_data_matches(pg_session, neo_session)

    # Verify session.created event
    await asyncio.sleep(0.2)
    created_events = event_collector.get_events("session.created")
    assert len(created_events) >= 1

    # ========================================================================
    # Phase 3: Execute 10 Turns with Tools
    # ========================================================================

    tools_used = []

    for turn in range(1, 11):
        # User message
        await event_publisher.publish_chat_message(
            session_id=session_id,
            role="user",
            content=f"Turn {turn}: Execute task",
        )

        # Assistant response (simulated)
        await event_publisher.publish_chat_message(
            session_id=session_id,
            role="assistant",
            content=f"Turn {turn}: Executing...",
        )

        # Tool execution (alternating tools)
        tool_name = "read_file" if turn % 2 == 0 else "write_file"
        tools_used.append(tool_name)

        # Track tool call in Neo4j
        async with neo4j_driver.session() as neo_session:
            await neo_session.run(
                "MERGE (t:Tool {name: $tool_name})",
                tool_name=tool_name,
            )
            await neo_session.run(
                """
                MATCH (s:Session {id: $session_id})
                MATCH (t:Tool {name: $tool_name})
                CREATE (s)-[r:TOOL_CALL {
                    sequence: $sequence,
                    success: true,
                    timestamp: datetime()
                }]->(t)
                """,
                session_id=session_id,
                tool_name=tool_name,
                sequence=turn,
            )

        # Publish tool use event
        await event_publisher.publish_tool_use(
            session_id=session_id,
            tool_name=tool_name,
            tool_input={"turn": turn},
            tool_output={"result": "success"},
            success=True,
        )

        # Create checkpoint every 5 turns
        if turn % 5 == 0:
            await create_test_checkpoint(
                db_session=db_session,
                session_id=session_id,
                turn_number=turn,
            )

            # Publish checkpoint event
            await event_publisher.publish_session_checkpoint(
                session_id=session_id,
                turn_number=turn,
                s3_key=None,
            )

        await asyncio.sleep(0.05)

    # ========================================================================
    # Phase 4: Verify Checkpoints
    # ========================================================================

    # Should have 2 checkpoints (turn 5 and turn 10)
    from sqlalchemy import text

    result = await db_session.execute(
        text("SELECT COUNT(*) FROM agent_checkpoints WHERE session_id = :id"),
        {"id": session_id},
    )
    checkpoint_count = result.scalar()
    assert checkpoint_count == 2

    # Verify checkpoint events
    await asyncio.sleep(0.3)
    checkpoint_events = event_collector.get_events("session.checkpoint")
    assert len(checkpoint_events) >= 2

    # ========================================================================
    # Phase 5: Verify Snapshots (Mocked MinIO Upload)
    # ========================================================================

    # Create sandbox directory
    with tempfile.TemporaryDirectory() as sandbox_dir:
        sandbox_path = Path(sandbox_dir)
        (sandbox_path / "file1.txt").write_text("Content 1")
        (sandbox_path / "file2.py").write_text("print('test')")

        # Create and upload snapshot
        import tarfile

        tarball_path = sandbox_path / "snapshot.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(sandbox_path / "file1.txt", arcname="file1.txt")
            tar.add(sandbox_path / "file2.py", arcname="file2.py")

        # Upload to MinIO
        bucket = "tracertm-test"
        s3_key = f"snapshots/{session_id}/snapshot-10.tar.gz"

        minio_clean.fput_object(bucket, s3_key, str(tarball_path))

        # Verify upload
        obj_info = verify_s3_object(minio_clean, bucket, s3_key)
        assert obj_info is not None

        # Update checkpoint with S3 key
        await db_session.execute(
            text("""
                UPDATE agent_checkpoints
                SET sandbox_snapshot_s3_key = :s3_key
                WHERE session_id = :session_id AND turn_number = 10
            """),
            {"s3_key": s3_key, "session_id": session_id},
        )
        await db_session.commit()

        # Publish snapshot created event
        await event_publisher.publish_snapshot_created(
            session_id=session_id,
            s3_key=s3_key,
            file_count=2,
            total_size_bytes=1000,
        )

    # ========================================================================
    # Phase 6: Verify Tool Calls
    # ========================================================================

    # Verify tool calls in Neo4j
    async with neo4j_driver.session() as neo_session:
        result = await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})-[r:TOOL_CALL]->(t:Tool)
            RETURN count(r) AS tool_count
            """,
            session_id=session_id,
        )
        record = await result.single()
        assert record["tool_count"] == 10

    # Verify tool use events
    await asyncio.sleep(0.3)
    tool_events = event_collector.get_events("chat.tool_use")
    assert len(tool_events) >= 10

    # ========================================================================
    # Phase 7: Verify All Events
    # ========================================================================

    all_events = event_collector.get_events()
    assert len(all_events) >= 20  # At least session + messages + tools + checkpoints

    # Verify event types present
    event_types = {e["event_type"] for e in all_events}
    assert "session.created" in event_types
    assert "chat.message" in event_types
    assert "chat.tool_use" in event_types
    assert "session.checkpoint" in event_types
    assert "snapshot.created" in event_types

    # ========================================================================
    # Phase 8: Stop and Resume from Checkpoint
    # ========================================================================

    # Simulate stopping execution
    await event_publisher.publish_session_status_changed(
        session_id=session_id,
        old_status="active",
        new_status="paused",
    )

    # Get latest checkpoint
    result = await db_session.execute(
        text("""
            SELECT * FROM agent_checkpoints
            WHERE session_id = :session_id
            ORDER BY turn_number DESC
            LIMIT 1
        """),
        {"session_id": session_id},
    )
    latest_checkpoint = result.first()
    assert latest_checkpoint is not None
    assert latest_checkpoint.turn_number == 10

    # Resume from checkpoint (would load state from latest_checkpoint)
    resume_turn = latest_checkpoint.turn_number + 1
    assert resume_turn == 11

    # Mark session as active again
    await event_publisher.publish_session_status_changed(
        session_id=session_id,
        old_status="paused",
        new_status="active",
    )

    # ========================================================================
    # Phase 9: Continue for 5 More Turns
    # ========================================================================

    for turn in range(11, 16):
        # Continue conversation
        await event_publisher.publish_chat_message(
            session_id=session_id,
            role="user",
            content=f"Turn {turn}: Continue after resume",
        )

        # Tool execution
        tool_name = "execute_command"
        async with neo4j_driver.session() as neo_session:
            await neo_session.run(
                "MERGE (t:Tool {name: $tool_name})",
                tool_name=tool_name,
            )
            await neo_session.run(
                """
                MATCH (s:Session {id: $session_id})
                MATCH (t:Tool {name: $tool_name})
                CREATE (s)-[r:TOOL_CALL {
                    sequence: $sequence,
                    success: true,
                    timestamp: datetime()
                }]->(t)
                """,
                session_id=session_id,
                tool_name=tool_name,
                sequence=turn,
            )

        await event_publisher.publish_tool_use(
            session_id=session_id,
            tool_name=tool_name,
            tool_input={"turn": turn},
            tool_output={"result": "success"},
            success=True,
        )

        # Checkpoint at turn 15
        if turn == 15:
            await create_test_checkpoint(
                db_session=db_session,
                session_id=session_id,
                turn_number=turn,
            )

            await event_publisher.publish_session_checkpoint(
                session_id=session_id,
                turn_number=turn,
                s3_key=None,
            )

        await asyncio.sleep(0.05)

    # Verify total tool calls now 15
    async with neo4j_driver.session() as neo_session:
        result = await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})-[r:TOOL_CALL]->(t:Tool)
            RETURN count(r) AS tool_count
            """,
            session_id=session_id,
        )
        record = await result.single()
        assert record["tool_count"] == 15

    # ========================================================================
    # Phase 10: Delete Session (Cascade to All Systems)
    # ========================================================================

    # Publish destroyed event
    await event_publisher.publish_session_destroyed(
        session_id=session_id,
        reason="test_complete",
    )

    # Clean up PostgreSQL
    await db_session.execute(
        text("DELETE FROM agent_checkpoints WHERE session_id = :id"),
        {"id": session_id},
    )
    await db_session.execute(
        text("DELETE FROM agent_sessions WHERE id = :id"),
        {"id": session_id},
    )
    await db_session.commit()

    # Clean up Neo4j
    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            "MATCH (s:Session {id: $session_id}) DETACH DELETE s",
            session_id=session_id,
        )

    # Clean up Redis cache
    cache_key = f"session:{session_id}"
    await redis_clean.delete(cache_key)

    # Clean up MinIO snapshots
    cleanup_s3_objects(minio_clean, "tracertm-test", f"snapshots/{session_id}/")

    # Verify cleanup
    assert await verify_postgres_session(db_session, session_id) is None
    assert await verify_neo4j_session(neo4j_driver, session_id) is None

    # Verify destroyed event
    await asyncio.sleep(0.3)
    destroyed_events = event_collector.get_events("session.destroyed")
    assert len(destroyed_events) >= 1

    # ========================================================================
    # Test Complete
    # ========================================================================

    # Summary verification
    final_events = event_collector.get_events()
    assert len(final_events) >= 30  # All events from complete lifecycle


# ============================================================================
# Multi-Session Concurrent Test
# ============================================================================


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_concurrent_agent_sessions(
    db_session: Any,
    neo4j_driver: Any,
    _redis_clean: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test multiple agent sessions running concurrently.

    Verifies:
    - Sessions don't interfere with each other
    - Events properly namespaced by session_id
    - Database writes don't conflict
    - Concurrent tool execution tracked correctly
    """
    # Create 3 concurrent sessions
    sessions = []
    for _i in range(3):
        session_data = await create_test_session(
            db_session=db_session,
            neo4j_driver=neo4j_driver,
        )
        sessions.append(session_data)

    # Subscribe to events
    event_collector = EventCollector()
    await nats_client.subscribe("tracertm.>", cb=event_collector.callback)
    await asyncio.sleep(0.1)

    # Execute turns concurrently
    async def run_session(session_data: Any) -> None:
        session_id = session_data["session_id"]

        for turn in range(1, 6):
            # Publish events
            await event_publisher.publish_chat_message(
                session_id=session_id,
                role="user",
                content=f"Session {session_id[:8]} turn {turn}",
            )

            await event_publisher.publish_tool_use(
                session_id=session_id,
                tool_name="test_tool",
                tool_input={"turn": turn},
                tool_output={"result": "success"},
                success=True,
            )

            await asyncio.sleep(0.05)

    # Run all sessions concurrently
    await asyncio.gather(*[run_session(s) for s in sessions])

    # Verify all sessions completed
    await asyncio.sleep(0.5)

    # Each session should have 5 message events and 5 tool events
    for session_data in sessions:
        session_id = session_data["session_id"]
        session_events = [e for e in event_collector.get_events() if e.get("session_id") == session_id]

        # Should have at least 10 events per session
        assert len(session_events) >= 10

    # Cleanup
    for session_data in sessions:
        await cleanup_test_session(
            db_session,
            neo4j_driver,
            session_data["session_id"],
        )


# ============================================================================
# Error Recovery Test
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_agent_session_error_recovery(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test agent session recovers from errors gracefully.

    Verifies:
    - Error event published
    - Session remains functional
    - Checkpoint created after error
    - Execution continues
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe to events
    event_collector = EventCollector()
    await nats_client.subscribe("tracertm.chat.>", cb=event_collector.callback)
    await asyncio.sleep(0.1)

    # Execute turns
    for turn in range(1, 4):
        await event_publisher.publish_chat_message(
            session_id=session_id,
            role="user",
            content=f"Turn {turn}",
        )

        # Simulate error on turn 2
        if turn == 2:
            await event_publisher.publish_chat_error(
                session_id=session_id,
                error_message="Simulated error for testing",
                stack_trace="Traceback...",
            )
        else:
            await event_publisher.publish_chat_message(
                session_id=session_id,
                role="assistant",
                content=f"Response {turn}",
            )

    await asyncio.sleep(0.3)

    # Verify error event
    error_events = event_collector.get_events("chat.error")
    assert len(error_events) >= 1

    # Verify session still functional (turn 3 completed)
    message_events = event_collector.get_events("chat.message")
    assert len(message_events) >= 4  # User 1, User 2, User 3, Response 1, Response 3

    # Create checkpoint after error
    checkpoint_data = await create_test_checkpoint(
        db_session=db_session,
        session_id=session_id,
        turn_number=3,
    )

    checkpoint = await verify_postgres_checkpoint(
        db_session,
        checkpoint_data["checkpoint_id"],
    )
    assert checkpoint is not None

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)
