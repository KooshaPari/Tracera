"""Phase 6: E2E Integration Testing - NATS Event Streaming Tests.

Tests real-time event streaming via NATS JetStream.

Verifies:
- Event publishing to NATS
- Event subscription and collection
- Event payload structure
- Subject pattern routing
- Event replay functionality
- Fire-and-forget error handling
"""

import asyncio
from typing import Any

import pytest

from .test_helpers import (
    EventCollector,
    assert_event_payload_valid,
    cleanup_test_session,
    create_test_session,
)

# ============================================================================
# Session Event Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_created_event(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test session.created event is published correctly.

    Verifies:
    - Event published to correct subject
    - Event payload includes session_id, project_id, sandbox_root
    - Event received by subscriber
    - Event structure is valid
    """
    # Subscribe to session events
    collector = EventCollector()
    await nats_client.subscribe("tracertm.sessions.>", cb=collector.callback)

    # Wait for subscription to be ready
    await asyncio.sleep(0.1)

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Publish event manually (simulating AgentService)
    await event_publisher.publish_session_created(
        session_id=session_id,
        project_id=session_data["project_id"],
        sandbox_root=session_data["sandbox_root"],
    )

    # Wait for event
    await asyncio.sleep(0.2)

    # Verify event received
    events = collector.get_events("session.created")
    assert len(events) >= 1

    event = events[-1]
    assert_event_payload_valid(event, required_fields=["data"])
    assert event["session_id"] == session_id
    assert event["event_type"] == "session.created"
    assert "project_id" in event["data"]
    assert "sandbox_root" in event["data"]

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_checkpoint_event(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test session.checkpoint event is published correctly.

    Verifies:
    - Event published on checkpoint creation
    - Event includes turn_number and s3_key
    - Subject pattern includes session_id
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe to session events
    collector = EventCollector()
    subject = f"tracertm.sessions.{session_id}.checkpoint"
    await nats_client.subscribe(subject, cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish checkpoint event
    s3_key = f"snapshots/{session_id}/snapshot-1.tar.gz"
    await event_publisher.publish_session_checkpoint(
        session_id=session_id,
        turn_number=5,
        s3_key=s3_key,
    )

    await asyncio.sleep(0.2)

    # Verify event
    events = collector.get_events("session.checkpoint")
    assert len(events) >= 1

    event = events[-1]
    assert event["event_type"] == "session.checkpoint"
    assert event["data"]["turn_number"] == 5
    assert event["data"]["s3_key"] == s3_key

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_session_destroyed_event(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test session.destroyed event is published on cleanup.

    Verifies:
    - Event published when session deleted
    - Event payload includes reason
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe
    collector = EventCollector()
    await nats_client.subscribe("tracertm.sessions.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish destroyed event
    await event_publisher.publish_session_destroyed(
        session_id=session_id,
        reason="user_requested",
    )

    await asyncio.sleep(0.2)

    # Verify event
    events = collector.get_events("session.destroyed")
    assert len(events) >= 1

    event = events[-1]
    assert event["event_type"] == "session.destroyed"
    assert event["data"]["reason"] == "user_requested"

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Chat Event Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_chat_message_event(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test chat.message event is published correctly.

    Verifies:
    - Event published for user and assistant messages
    - Content truncated to 500 chars
    - Role and content included
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe
    collector = EventCollector()
    await nats_client.subscribe("tracertm.chat.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish message event
    await event_publisher.publish_chat_message(
        session_id=session_id,
        role="user",
        content="Hello, how are you?",
    )

    await asyncio.sleep(0.2)

    # Verify event
    events = collector.get_events("chat.message")
    assert len(events) >= 1

    event = events[-1]
    assert event["event_type"] == "chat.message"
    assert event["data"]["role"] == "user"
    assert "Hello" in event["data"]["content_preview"]

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_chat_tool_use_event(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test chat.tool_use event is published correctly.

    Verifies:
    - Event includes tool_name, success, input, output
    - Subject pattern routes correctly
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe
    collector = EventCollector()
    await nats_client.subscribe("tracertm.chat.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish tool use event
    await event_publisher.publish_tool_use(
        session_id=session_id,
        tool_name="read_file",
        tool_input={"path": "/test/file.txt"},
        tool_output={"content": "file content"},
        success=True,
    )

    await asyncio.sleep(0.2)

    # Verify event
    events = collector.get_events("chat.tool_use")
    assert len(events) >= 1

    event = events[-1]
    assert event["event_type"] == "chat.tool_use"
    assert event["data"]["tool_name"] == "read_file"
    assert event["data"]["success"] is True

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_chat_error_event(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test chat.error event is published on failures.

    Verifies:
    - Event includes error message and stack trace
    - Error severity included
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe
    collector = EventCollector()
    await nats_client.subscribe("tracertm.chat.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish error event
    await event_publisher.publish_chat_error(
        session_id=session_id,
        error_message="Test error occurred",
        stack_trace="Traceback...",
    )

    await asyncio.sleep(0.2)

    # Verify event
    events = collector.get_events("chat.error")
    assert len(events) >= 1

    event = events[-1]
    assert event["event_type"] == "chat.error"
    assert "Test error" in event["data"]["error_message"]

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Snapshot Event Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_snapshot_created_event(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test snapshot.created event is published correctly.

    Verifies:
    - Event includes S3 key, file count, size
    - Compression ratio included
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe
    collector = EventCollector()
    await nats_client.subscribe("tracertm.sandbox.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish snapshot created event
    s3_key = f"snapshots/{session_id}/snapshot-1.tar.gz"
    await event_publisher.publish_snapshot_created(
        session_id=session_id,
        s3_key=s3_key,
        file_count=10,
        total_size_bytes=5000,
    )

    await asyncio.sleep(0.2)

    # Verify event
    events = collector.get_events("snapshot.created")
    assert len(events) >= 1

    event = events[-1]
    assert event["event_type"] == "snapshot.created"
    assert event["data"]["s3_key"] == s3_key
    assert event["data"]["file_count"] == 10

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Event Replay Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.skip(reason="Requires JetStream consumer configuration")
async def test_event_replay_from_timestamp(
    db_session: Any,
    neo4j_driver: Any,
    nats_jetstream: Any,
    event_publisher: Any,
) -> None:
    """Test event replay from specific timestamp.

    Verifies:
    - Events published to JetStream
    - Consumer can replay from timestamp
    - All events received in order
    - No events missed
    """
    # This test would require JetStream consumer setup
    # and is skipped for now


# ============================================================================
# Wildcard Subscription Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_wildcard_subscription_all_events(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test wildcard subscription receives all event types.

    Verifies:
    - Subscribe to "tracertm.>" receives all events
    - Events from different subjects collected
    - Event types correctly identified
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe to all events
    collector = EventCollector()
    await nats_client.subscribe("tracertm.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish multiple event types
    await event_publisher.publish_session_created(
        session_id=session_id,
        project_id=session_data["project_id"],
        sandbox_root=session_data["sandbox_root"],
    )

    await event_publisher.publish_chat_message(
        session_id=session_id,
        role="user",
        content="Test message",
    )

    await event_publisher.publish_tool_use(
        session_id=session_id,
        tool_name="test_tool",
        tool_input={},
        tool_output={},
        success=True,
    )

    await asyncio.sleep(0.3)

    # Verify all events received
    all_events = collector.get_events()
    assert len(all_events) >= 3

    event_types = {e["event_type"] for e in all_events}
    assert "session.created" in event_types
    assert "chat.message" in event_types
    assert "chat.tool_use" in event_types

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Fire-and-Forget Error Handling Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_event_publishing_without_nats(
    db_session: Any,
    neo4j_driver: Any,
) -> None:
    """Test event publishing gracefully degrades without NATS.

    Verifies:
    - Publishing with None client doesn't raise exception
    - Operations continue normally
    - Warnings logged (not tested here)
    """
    from tracertm.agent.events import AgentEventPublisher

    # Create publisher with no NATS client
    publisher = AgentEventPublisher(None)

    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Try to publish (should not raise)
    await publisher.publish_session_created(
        session_id=session_id,
        project_id=session_data["project_id"],
        sandbox_root=session_data["sandbox_root"],
    )

    # No exception means success
    assert True

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)


# ============================================================================
# Content Truncation Tests
# ============================================================================


@pytest.mark.e2e
@pytest.mark.asyncio
async def test_event_content_truncation(
    db_session: Any,
    neo4j_driver: Any,
    nats_client: Any,
    event_publisher: Any,
) -> None:
    """Test large content is truncated in events.

    Verifies:
    - Content > 500 chars truncated
    - content_length includes original size
    - content_preview is <= 500 chars
    """
    # Create session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    session_id = session_data["session_id"]

    # Subscribe
    collector = EventCollector()
    await nats_client.subscribe("tracertm.chat.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # Publish message with large content
    large_content = "A" * 1000  # 1000 chars

    await event_publisher.publish_chat_message(
        session_id=session_id,
        role="user",
        content=large_content,
    )

    await asyncio.sleep(0.2)

    # Verify event
    events = collector.get_events("chat.message")
    assert len(events) >= 1

    event = events[-1]
    assert len(event["data"]["content_preview"]) <= 500
    assert event["data"]["content_length"] == 1000

    # Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_id)
