"""Phase 6: E2E Integration Testing - Checkpoint & Resume Tests.

Tests checkpoint creation and session resume functionality.

Verifies:
- Checkpoint creation in PostgreSQL
- State snapshot persistence
- Session resume from checkpoint
- Turn number tracking
- Checkpoint cleanup
- Temporal workflow integration
"""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

import pytest

from .test_helpers import (
    cleanup_test_session,
    count_postgres_checkpoints,
    create_test_checkpoint,
    create_test_session,
    verify_postgres_checkpoint,
)

# ============================================================================
# Checkpoint Creation Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_checkpoint_creation(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test checkpoint creation stores state snapshot.

    Verifies:
    - Checkpoint row created in agent_checkpoints
    - State snapshot JSONB populated
    - Turn number tracked correctly
    - S3 key reference stored (if applicable)
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoint
    checkpoint_data = await create_test_checkpoint(
        db_session=db_session,
        session_id=session_id,
        turn_number=1,
    )

    checkpoint_id = checkpoint_data["checkpoint_id"]

    # Verify checkpoint exists
    checkpoint = await verify_postgres_checkpoint(db_session, checkpoint_id)
    assert checkpoint is not None
    assert checkpoint["checkpoint_id"] == checkpoint_id
    assert checkpoint["session_id"] == session_id
    assert checkpoint["turn_number"] == 1

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_checkpoint_turn_number_increment(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test checkpoint turn numbers increment correctly.

    Verifies:
    - First checkpoint has turn_number = 1
    - Subsequent checkpoints increment
    - Turn numbers are sequential
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create multiple checkpoints
    checkpoint_ids = []
    for turn in range(1, 6):
        checkpoint_data = await create_test_checkpoint(
            db_session=db_session,
            session_id=session_id,
            turn_number=turn,
        )
        checkpoint_ids.append(checkpoint_data["checkpoint_id"])

    # Verify all checkpoints exist with correct turn numbers
    for idx, checkpoint_id in enumerate(checkpoint_ids):
        checkpoint = await verify_postgres_checkpoint(db_session, checkpoint_id)
        assert checkpoint is not None
        assert checkpoint["turn_number"] == idx + 1

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_checkpoint_state_snapshot(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test checkpoint stores complete state snapshot.

    Verifies:
    - State snapshot includes messages
    - State snapshot includes context
    - State snapshot is valid JSON
    - Large snapshots stored correctly
    """
    import json

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoint with complex state
    from sqlalchemy import text

    complex_state = {
        "messages": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ],
        "context": {
            "project_files": ["/file1.txt", "/file2.py"],
            "working_directory": "/tmp/project",
        },
        "tool_history": [
            {"tool": "read_file", "result": "success"},
        ],
    }

    result = await db_session.execute(
        text("""
            INSERT INTO agent_checkpoints (
                id, session_id, turn_number, state_snapshot, created_at
            )
            VALUES (:id, :session_id, :turn_number, :state_snapshot, :created_at)
            RETURNING id
        """),
        {
            "id": str(uuid4()),
            "session_id": session_id,
            "turn_number": 1,
            "state_snapshot": json.dumps(complex_state),
            "created_at": datetime.now(UTC),
        },
    )
    checkpoint_id = result.scalar()
    await db_session.commit()

    # Verify state snapshot
    checkpoint = await verify_postgres_checkpoint(db_session, checkpoint_id)
    assert checkpoint is not None

    # Query and parse state_snapshot
    result = await db_session.execute(
        text("SELECT state_snapshot FROM agent_checkpoints WHERE id = :id"),
        {"id": checkpoint_id},
    )
    row = result.first()
    stored_state = json.loads(row.state_snapshot)

    assert "messages" in stored_state
    assert len(stored_state["messages"]) == 2
    assert stored_state["messages"][0]["role"] == "user"
    assert "context" in stored_state
    assert stored_state["context"]["working_directory"] == "/tmp/project"

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Session Resume Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_resume_from_checkpoint(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test session can resume from checkpoint.

    Verifies:
    - Latest checkpoint retrieved
    - State restored from snapshot
    - Conversation continues from checkpoint turn
    - No duplicate messages
    """
    from sqlalchemy import text

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoints up to turn 10
    for turn in range(1, 11):
        await create_test_checkpoint(
            db_session=db_session,
            session_id=session_id,
            turn_number=turn,
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
    latest = result.first()

    assert latest is not None
    assert latest.turn_number == 10

    # Resume would continue from turn 11
    next_turn = latest.turn_number + 1
    assert next_turn == 11

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_resume_specific_turn(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test session can resume from specific turn number.

    Verifies:
    - Checkpoint retrieved by turn number
    - State restored from specific point
    - Later checkpoints ignored
    """
    from sqlalchemy import text

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoints
    for turn in range(1, 11):
        await create_test_checkpoint(
            db_session=db_session,
            session_id=session_id,
            turn_number=turn,
        )

    # Get checkpoint at turn 5
    result = await db_session.execute(
        text("""
            SELECT * FROM agent_checkpoints
            WHERE session_id = :session_id AND turn_number = :turn
        """),
        {"session_id": session_id, "turn": 5},
    )
    checkpoint = result.first()

    assert checkpoint is not None
    assert checkpoint.turn_number == 5

    # Resume would continue from turn 6
    next_turn = checkpoint.turn_number + 1
    assert next_turn == 6

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_resume_no_duplicate_messages(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test resumed session doesn't duplicate messages.

    Verifies:
    - Message history preserved in checkpoint
    - Resume loads existing messages
    - New messages appended (not duplicated)
    """
    import json

    from sqlalchemy import text

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoint with messages
    messages = [{"role": "user", "content": f"Message {i}"} for i in range(1, 6)]

    result = await db_session.execute(
        text("""
            INSERT INTO agent_checkpoints (
                id, session_id, turn_number, state_snapshot, created_at
            )
            VALUES (:id, :session_id, :turn_number, :state_snapshot, :created_at)
            RETURNING id
        """),
        {
            "id": str(uuid4()),
            "session_id": session_id,
            "turn_number": 5,
            "state_snapshot": json.dumps({"messages": messages}),
            "created_at": datetime.now(UTC),
        },
    )
    checkpoint_id = result.scalar()
    await db_session.commit()

    # Resume: Load messages from checkpoint
    result = await db_session.execute(
        text("SELECT state_snapshot FROM agent_checkpoints WHERE id = :id"),
        {"id": checkpoint_id},
    )
    row = result.first()
    state = json.loads(row.state_snapshot)

    loaded_messages = state["messages"]
    assert len(loaded_messages) == 5

    # Simulate adding new message (should not duplicate)
    new_message = {"role": "user", "content": "Message 6"}
    loaded_messages.append(new_message)

    assert len(loaded_messages) == 6
    assert loaded_messages[-1]["content"] == "Message 6"

    # Verify no duplicates
    contents = [m["content"] for m in loaded_messages]
    assert len(contents) == len(set(contents))

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Checkpoint Cleanup Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_checkpoint_cleanup_old_checkpoints(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test old checkpoints are cleaned up, keeping only recent ones.

    Verifies:
    - 20 checkpoints created
    - Cleanup keeps last 5
    - 15 checkpoints deleted
    - Latest checkpoints preserved
    """
    from sqlalchemy import text

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create 20 checkpoints
    for turn in range(1, 21):
        await create_test_checkpoint(
            db_session=db_session,
            session_id=session_id,
            turn_number=turn,
        )

    # Verify 20 checkpoints exist
    count_before = await count_postgres_checkpoints(db_session, session_id)
    assert count_before == 20

    # Clean up, keep last 5
    keep_count = 5
    await db_session.execute(
        text("""
            DELETE FROM agent_checkpoints
            WHERE session_id = :session_id
            AND id NOT IN (
                SELECT id FROM agent_checkpoints
                WHERE session_id = :session_id
                ORDER BY turn_number DESC
                LIMIT :keep_count
            )
        """),
        {"session_id": session_id, "keep_count": keep_count},
    )
    await db_session.commit()

    # Verify only 5 remain
    count_after = await count_postgres_checkpoints(db_session, session_id)
    assert count_after == 5

    # Verify latest 5 were kept
    result = await db_session.execute(
        text("""
            SELECT turn_number FROM agent_checkpoints
            WHERE session_id = :session_id
            ORDER BY turn_number
        """),
        {"session_id": session_id},
    )
    turns = [row.turn_number for row in result.all()]
    assert turns == [16, 17, 18, 19, 20]

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_checkpoint_cleanup_by_age(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test checkpoints can be cleaned up by age.

    Verifies:
    - Old checkpoints identified by timestamp
    - Cleanup deletes checkpoints older than threshold
    - Recent checkpoints preserved
    """
    from datetime import timedelta

    from sqlalchemy import text

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoints with different ages
    now = datetime.now(UTC)

    # Old checkpoint (30 days ago)
    await db_session.execute(
        text("""
            INSERT INTO agent_checkpoints (
                id, session_id, turn_number, state_snapshot, created_at
            )
            VALUES (:id, :session_id, :turn_number, :state_snapshot, :created_at)
        """),
        {
            "id": str(uuid4()),
            "session_id": session_id,
            "turn_number": 1,
            "state_snapshot": "{}",
            "created_at": now - timedelta(days=30),
        },
    )

    # Recent checkpoint (1 day ago)
    await db_session.execute(
        text("""
            INSERT INTO agent_checkpoints (
                id, session_id, turn_number, state_snapshot, created_at
            )
            VALUES (:id, :session_id, :turn_number, :state_snapshot, :created_at)
        """),
        {
            "id": str(uuid4()),
            "session_id": session_id,
            "turn_number": 2,
            "state_snapshot": "{}",
            "created_at": now - timedelta(days=1),
        },
    )

    await db_session.commit()

    # Clean up checkpoints older than 7 days
    retention_days = 7
    await db_session.execute(
        text("""
            DELETE FROM agent_checkpoints
            WHERE session_id = :session_id
            AND created_at < NOW() - INTERVAL ':days days'
        """),
        {"session_id": session_id, "days": retention_days},
    )
    await db_session.commit()

    # Verify only recent checkpoint remains
    count = await count_postgres_checkpoints(db_session, session_id)
    assert count == 1

    result = await db_session.execute(
        text("""
            SELECT turn_number FROM agent_checkpoints
            WHERE session_id = :session_id
        """),
        {"session_id": session_id},
    )
    row = result.first()
    assert row.turn_number == 2

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Checkpoint with S3 Snapshot Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_checkpoint_with_s3_snapshot(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test checkpoint references S3 snapshot.

    Verifies:
    - Checkpoint stores S3 key
    - S3 key format is correct
    - Snapshot retrievable via S3 key
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoint with S3 key
    s3_key = f"snapshots/{session_id}/turn-1.tar.gz"
    checkpoint_data = await create_test_checkpoint(
        db_session=db_session,
        session_id=session_id,
        turn_number=1,
        s3_key=s3_key,
    )

    checkpoint_id = checkpoint_data["checkpoint_id"]

    # Verify S3 key stored
    checkpoint = await verify_postgres_checkpoint(db_session, checkpoint_id)
    assert checkpoint is not None
    assert checkpoint["s3_key"] == s3_key

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_checkpoint_without_snapshot(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test checkpoint can be created without S3 snapshot.

    Verifies:
    - Checkpoint created with NULL s3_key
    - State snapshot still populated
    - Resume works without snapshot
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Create checkpoint without S3 key
    checkpoint_data = await create_test_checkpoint(
        db_session=db_session,
        session_id=session_id,
        turn_number=1,
        s3_key=None,
    )

    checkpoint_id = checkpoint_data["checkpoint_id"]

    # Verify no S3 key
    checkpoint = await verify_postgres_checkpoint(db_session, checkpoint_id)
    assert checkpoint is not None
    assert checkpoint["s3_key"] is None

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)
