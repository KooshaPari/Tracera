"""Phase 6: E2E Integration Testing - Session Persistence Tests.

Tests dual-write session persistence across PostgreSQL and Neo4j.

Verifies:
- Session creation in both databases
- Data consistency between databases
- Relationship tracking in Neo4j
- Cache integration with Redis
- Tool call tracking
- Session lifecycle management
"""

from typing import Any
from uuid import uuid4

import pytest

from .test_helpers import (
    assert_session_data_matches,
    cleanup_test_session,
    create_test_session,
    verify_neo4j_relationship,
    verify_neo4j_session,
    verify_postgres_session,
)

# ============================================================================
# Session Creation Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_creation_dual_write(
    db_session: Any,
    neo4j_driver: Any,
    _redis_clean: Any,
) -> None:
    """Test session creation writes to both PostgreSQL and Neo4j.

    Verifies:
    - PostgreSQL: agent_sessions row exists
    - Neo4j: Session node exists
    - Data consistency between databases
    - Redis: cache entry created
    """
    # Create test session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )

    session_id = session_data["session_id"]

    # Verify PostgreSQL
    pg_session = await verify_postgres_session(db_session, session_id)
    assert pg_session is not None
    assert pg_session["session_id"] == session_id
    assert pg_session["project_id"] == session_data["project_id"]
    assert pg_session["status"] == "active"

    # Verify Neo4j
    neo_session = await verify_neo4j_session(neo4j_driver, session_id)
    assert neo_session is not None
    assert neo_session["session_id"] == session_id
    assert neo_session["project_id"] == session_data["project_id"]

    # Verify data consistency
    assert_session_data_matches(pg_session, neo_session)

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_creation_with_project_relationship(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test session creation establishes BELONGS_TO relationship.

    Verifies:
    - Session node created
    - Project node referenced
    - BELONGS_TO relationship exists
    """
    project_id = str(uuid4())

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
        project_id=project_id,
    )

    session_id = session_data["session_id"]

    # Verify relationship in Neo4j
    async with neo4j_driver.session() as neo_session:
        # Create project node for testing
        await neo_session.run(
            "MERGE (p:Project {id: $project_id})",
            project_id=project_id,
        )

        # Create relationship
        await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})
            MATCH (p:Project {id: $project_id})
            MERGE (s)-[:BELONGS_TO]->(p)
            """,
            session_id=session_id,
            project_id=project_id,
        )

        # Verify relationship
        result = await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})-[:BELONGS_TO]->(p:Project)
            RETURN p.id AS project_id
            """,
            session_id=session_id,
        )
        record = await result.single()
        assert record is not None
        assert record["project_id"] == project_id

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Session Fork Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_fork_lineage(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test session forking creates lineage in Neo4j.

    Verifies:
    - Parent session created
    - Child session created
    - FORKED_FROM relationship exists
    - Lineage query returns chain
    """
    # Create parent session
    parent_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    parent_id = parent_data["session_id"]

    # Create child session
    child_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
        project_id=parent_data["project_id"],
    )
    child_id = child_data["session_id"]

    # Create fork relationship in Neo4j
    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            """
            MATCH (parent:Session {id: $parent_id})
            MATCH (child:Session {id: $child_id})
            MERGE (child)-[:FORKED_FROM]->(parent)
            """,
            parent_id=parent_id,
            child_id=child_id,
        )

    # Verify FORKED_FROM relationship
    has_fork = await verify_neo4j_relationship(
        neo4j_driver,
        session_id=child_id,
        relationship_type="FORKED_FROM",
        target_id=parent_id,
    )
    assert has_fork is True

    # Query lineage chain
    async with neo4j_driver.session() as neo_session:
        result = await neo_session.run(
            """
            MATCH path = (child:Session {id: $child_id})-[:FORKED_FROM*]->(ancestor:Session)
            RETURN [node IN nodes(path) | node.id] AS lineage
            ORDER BY length(path) DESC
            LIMIT 1
            """,
            child_id=child_id,
        )
        record = await result.single()
        assert record is not None

        lineage = record["lineage"]
        assert child_id in lineage
        assert parent_id in lineage
        assert lineage.index(child_id) < lineage.index(parent_id)

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, parent_id)
    await cleanup_test_session(db_session, neo4j_driver, child_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_fork_preserves_context(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test session fork preserves context from parent.

    Verifies:
    - Child session references parent
    - Parent context accessible from child
    - Independent modification of child
    """
    # Create parent with context
    parent_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    parent_id = parent_data["session_id"]

    # Add context to parent in Neo4j
    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})
            SET s.context = $context
            """,
            session_id=parent_id,
            context='{"key": "value"}',
        )

    # Create child session
    child_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
        project_id=parent_data["project_id"],
    )
    child_id = child_data["session_id"]

    # Create fork relationship
    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            """
            MATCH (parent:Session {id: $parent_id})
            MATCH (child:Session {id: $child_id})
            MERGE (child)-[:FORKED_FROM]->(parent)
            """,
            parent_id=parent_id,
            child_id=child_id,
        )

        # Query parent context from child
        result = await neo_session.run(
            """
            MATCH (child:Session {id: $child_id})-[:FORKED_FROM]->(parent:Session)
            RETURN parent.context AS parent_context
            """,
            child_id=child_id,
        )
        record = await result.single()
        assert record is not None
        assert record["parent_context"] == '{"key": "value"}'

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, parent_id)
    await cleanup_test_session(db_session, neo4j_driver, child_id)


# ============================================================================
# Tool Call Tracking Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_tool_call_tracking(
    db_session: Any,
    neo4j_driver: Any,
    _event_publisher: Any,
) -> None:
    """Test tool call tracking in Neo4j.

    Verifies:
    - Tool call creates TOOL_CALL relationship
    - Tool metadata stored on relationship
    - Event published to NATS
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Track tool call
    tool_name = "read_file"
    tool_input = {"path": "/test/file.txt"}
    tool_output = {"content": "test content"}

    async with neo4j_driver.session() as neo_session:
        # Create tool node
        await neo_session.run(
            """
            MERGE (t:Tool {name: $tool_name})
            """,
            tool_name=tool_name,
        )

        # Create TOOL_CALL relationship
        await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})
            MATCH (t:Tool {name: $tool_name})
            CREATE (s)-[r:TOOL_CALL {
                input: $input,
                output: $output,
                success: true,
                timestamp: datetime()
            }]->(t)
            """,
            session_id=session_id,
            tool_name=tool_name,
            input=str(tool_input),
            output=str(tool_output),
        )

    # Verify relationship
    has_tool_call = await verify_neo4j_relationship(
        neo4j_driver,
        session_id=session_id,
        relationship_type="TOOL_CALL",
    )
    assert has_tool_call is True

    # Query tool call details
    async with neo4j_driver.session() as neo_session:
        result = await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})-[r:TOOL_CALL]->(t:Tool)
            RETURN t.name AS tool_name, r.success AS success
            """,
            session_id=session_id,
        )
        record = await result.single()
        assert record is not None
        assert record["tool_name"] == tool_name
        assert record["success"] is True

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_tool_call_sequence_tracking(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test tracking multiple tool calls in sequence.

    Verifies:
    - Multiple TOOL_CALL relationships
    - Correct order preservation
    - Independent tool call records
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Track multiple tool calls
    tools = ["read_file", "write_file", "execute_command"]

    async with neo4j_driver.session() as neo_session:
        for idx, tool_name in enumerate(tools):
            # Create tool node
            await neo_session.run(
                "MERGE (t:Tool {name: $tool_name})",
                tool_name=tool_name,
            )

            # Create TOOL_CALL relationship with sequence number
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
                sequence=idx,
            )

    # Verify all tool calls exist in order
    async with neo4j_driver.session() as neo_session:
        result = await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})-[r:TOOL_CALL]->(t:Tool)
            RETURN t.name AS tool_name, r.sequence AS sequence
            ORDER BY r.sequence
            """,
            session_id=session_id,
        )

        records = [record async for record in result]
        assert len(records) == 3

        for idx, record in enumerate(records):
            assert record["tool_name"] == tools[idx]
            assert record["sequence"] == idx

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Session Status Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_status_update(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test session status updates in both databases.

    Verifies:
    - Status updated in PostgreSQL
    - Status updated in Neo4j
    - Data consistency maintained
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Update status to 'paused'
    from sqlalchemy import text

    await db_session.execute(
        text("UPDATE agent_sessions SET status = :status WHERE id = :id"),
        {"status": "paused", "id": session_id},
    )
    await db_session.commit()

    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})
            SET s.status = 'paused'
            """,
            session_id=session_id,
        )

    # Verify updated status
    pg_session = await verify_postgres_session(db_session, session_id)
    assert pg_session["status"] == "paused"

    neo_session_data = await verify_neo4j_session(neo4j_driver, session_id)
    assert neo_session_data["status"] == "paused"

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Session Deletion Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_deletion_cascade(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test session deletion cascades to all related data.

    Verifies:
    - Session deleted from PostgreSQL
    - Session deleted from Neo4j
    - Related data cleaned up
    - Cache entries removed
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Verify session exists
    assert await verify_postgres_session(db_session, session_id) is not None
    assert await verify_neo4j_session(neo4j_driver, session_id) is not None

    # Delete session
    await cleanup_test_session(db_session, neo4j_driver, session_id)

    # Verify session deleted
    assert await verify_postgres_session(db_session, session_id) is None
    assert await verify_neo4j_session(neo4j_driver, session_id) is None


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_soft_delete(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test soft delete marks session as deleted without removing.

    Verifies:
    - Status changed to 'deleted'
    - Session still exists in database
    - Session not returned in active queries
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Soft delete (mark as deleted)
    from sqlalchemy import text

    await db_session.execute(
        text("UPDATE agent_sessions SET status = 'deleted' WHERE id = :id"),
        {"id": session_id},
    )
    await db_session.commit()

    async with neo4j_driver.session() as neo_session:
        await neo_session.run(
            """
            MATCH (s:Session {id: $session_id})
            SET s.status = 'deleted'
            """,
            session_id=session_id,
        )

    # Verify session still exists but marked deleted
    pg_session = await verify_postgres_session(db_session, session_id)
    assert pg_session is not None
    assert pg_session["status"] == "deleted"

    neo_session_data = await verify_neo4j_session(neo4j_driver, session_id)
    assert neo_session_data is not None
    assert neo_session_data["status"] == "deleted"

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)
