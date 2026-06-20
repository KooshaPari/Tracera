"""Tests for agent event streaming infrastructure.

This test module verifies that all agent lifecycle events are properly
published to NATS with correct payload formats and subject patterns.

Note: Uses /tmp paths for test data - safe in test context.
"""

import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from tracertm.agent.events import (
    AgentEventPublisher,
    ChatMessagePayload,
    ChatToolUsePayload,
    EventSource,
    EventType,
    SessionCheckpointPayload,
    SessionStatus,
    SnapshotCreatedPayload,
)

# Test data constants (avoid magic numbers in assertions)
EXPECTED_CHECKPOINT_TURN = 5
EXPECTED_FINAL_TURN = 10
TEST_CONTENT_PREVIEW_LEN = 500
TEST_CONTENT_LENGTH = 1000
EXPECTED_CHAT_TURN_NUMBER = 3
TEST_SNAPSHOT_SIZE_BYTES = 1024000
TEST_SNAPSHOT_FILE_COUNT = 150


class MockNATSClient:
    """Mock NATS client for testing event publishing."""

    def __init__(self) -> None:
        """Initialize the mock NATS client."""
        self.published_events: list[dict[str, Any]] = []
        self._js = MagicMock()
        self._js.publish = AsyncMock(side_effect=self._mock_publish)
        self.is_connected = True

    async def _mock_publish(self, subject: str, payload: bytes) -> MagicMock:
        """Mock publish that captures events."""
        event_data = json.loads(payload.decode("utf-8"))
        self.published_events.append({
            "subject": subject,
            "payload": event_data,
        })
        # Return mock ACK
        mock_ack = MagicMock()
        mock_ack.stream = "TRACERTM_BRIDGE"
        mock_ack.seq = len(self.published_events)
        return mock_ack


@pytest.fixture
def mock_nats() -> MockNATSClient:
    """Fixture providing mock NATS client."""
    return MockNATSClient()


@pytest.fixture
def publisher(mock_nats: MockNATSClient) -> AgentEventPublisher:
    """Fixture providing event publisher with mock NATS."""
    return AgentEventPublisher(mock_nats)


@pytest.mark.asyncio
async def test_publish_session_created(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test session created event publishing."""
    await publisher.publish_session_created(
        session_id="sess-123",
        project_id="proj-456",
        sandbox_root="/tmp/sandbox/sess-123",  # nosec B108 -- test fixture data
        provider="claude",
        model="claude-3-opus",
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.sessions.sess-123.created"
    assert event["payload"]["event_type"] == EventType.SESSION_CREATED
    assert event["payload"]["session_id"] == "sess-123"
    assert event["payload"]["project_id"] == "proj-456"
    assert event["payload"]["data"]["sandbox_root"] == "/tmp/sandbox/sess-123"  # nosec B108
    assert event["payload"]["data"]["provider"] == "claude"
    assert event["payload"]["data"]["model"] == "claude-3-opus"
    assert event["payload"]["metadata"]["source"] == EventSource.AGENT_SERVICE


@pytest.mark.asyncio
async def test_publish_session_checkpoint(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test session checkpoint event publishing."""
    payload = SessionCheckpointPayload(
        checkpoint_id="ckpt-789",
        turn_number=EXPECTED_CHECKPOINT_TURN,
        s3_key="checkpoints/sess-123/ckpt-789.json",
        metadata={"notes": "checkpoint after code generation"},
    )
    await publisher.publish_session_checkpoint(
        session_id="sess-123",
        project_id="proj-456",
        payload=payload,
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.sessions.sess-123.checkpoint"
    assert event["payload"]["event_type"] == EventType.SESSION_CHECKPOINT
    assert event["payload"]["data"]["checkpoint_id"] == "ckpt-789"
    assert event["payload"]["data"]["turn_number"] == EXPECTED_CHECKPOINT_TURN
    assert event["payload"]["data"]["s3_key"] == "checkpoints/sess-123/ckpt-789.json"
    assert event["payload"]["data"]["metadata"]["notes"] == "checkpoint after code generation"


@pytest.mark.asyncio
async def test_publish_session_destroyed(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test session destroyed event publishing."""
    await publisher.publish_session_destroyed(
        session_id="sess-123",
        project_id="proj-456",
        reason="User requested cleanup",
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.sessions.sess-123.destroyed"
    assert event["payload"]["event_type"] == EventType.SESSION_DESTROYED
    assert event["payload"]["data"]["reason"] == "User requested cleanup"


@pytest.mark.asyncio
async def test_publish_session_status_changed(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test session status change event publishing."""
    await publisher.publish_session_status_changed(
        session_id="sess-123",
        project_id="proj-456",
        old_status=SessionStatus.ACTIVE,
        new_status=SessionStatus.COMPLETED,
        details={"final_turn": 10},
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.sessions.sess-123.status_changed"
    assert event["payload"]["event_type"] == EventType.SESSION_STATUS_CHANGED
    assert event["payload"]["data"]["old_status"] == "ACTIVE"
    assert event["payload"]["data"]["new_status"] == "COMPLETED"
    assert event["payload"]["data"]["details"]["final_turn"] == EXPECTED_FINAL_TURN


@pytest.mark.asyncio
async def test_publish_chat_message(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test chat message event publishing."""
    long_content = "A" * TEST_CONTENT_LENGTH
    payload = ChatMessagePayload(
        role="user",
        content=long_content,
        turn_number=EXPECTED_CHAT_TURN_NUMBER,
        metadata={"source": "web_ui"},
    )
    await publisher.publish_chat_message(
        session_id="sess-123",
        project_id="proj-456",
        payload=payload,
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.chat.sess-123.message"
    assert event["payload"]["event_type"] == EventType.CHAT_MESSAGE
    assert event["payload"]["data"]["role"] == "user"
    # Content should be truncated to preview length
    assert len(event["payload"]["data"]["content_preview"]) == TEST_CONTENT_PREVIEW_LEN
    assert event["payload"]["data"]["content_length"] == TEST_CONTENT_LENGTH
    assert event["payload"]["data"]["turn_number"] == EXPECTED_CHAT_TURN_NUMBER


@pytest.mark.asyncio
async def test_publish_chat_tool_use(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test tool use event publishing."""
    payload = ChatToolUsePayload(
        tool_name="read_file",
        tool_input={"path": "/tmp/test.py"},  # nosec B108 -- test fixture data
        tool_output="file contents here",
        success=True,
    )
    await publisher.publish_chat_tool_use(
        session_id="sess-123",
        project_id="proj-456",
        payload=payload,
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.chat.sess-123.tool_use"
    assert event["payload"]["event_type"] == EventType.CHAT_TOOL_USE
    assert event["payload"]["data"]["tool_name"] == "read_file"
    assert event["payload"]["data"]["success"] is True
    assert event["payload"]["data"]["error"] is None


@pytest.mark.asyncio
async def test_publish_chat_error(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test chat error event publishing."""
    await publisher.publish_chat_error(
        session_id="sess-123",
        project_id="proj-456",
        error_type="ValueError",
        error_message="Invalid input format",
        stack_trace="Traceback...",
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.chat.sess-123.error"
    assert event["payload"]["event_type"] == EventType.CHAT_ERROR
    assert event["payload"]["data"]["error_type"] == "ValueError"
    assert event["payload"]["data"]["error_message"] == "Invalid input format"


@pytest.mark.asyncio
async def test_publish_snapshot_created(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test snapshot created event publishing."""
    payload = SnapshotCreatedPayload(
        snapshot_id="snap-789",
        s3_key="snapshots/sess-123/snap-789.tar.gz",
        size_bytes=TEST_SNAPSHOT_SIZE_BYTES,
        file_count=TEST_SNAPSHOT_FILE_COUNT,
    )
    await publisher.publish_snapshot_created(
        session_id="sess-123",
        project_id="proj-456",
        payload=payload,
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.sandbox.sess-123.snapshot_created"
    assert event["payload"]["event_type"] == EventType.SNAPSHOT_CREATED
    assert event["payload"]["data"]["snapshot_id"] == "snap-789"
    assert event["payload"]["data"]["s3_key"] == "snapshots/sess-123/snap-789.tar.gz"
    assert event["payload"]["data"]["size_bytes"] == TEST_SNAPSHOT_SIZE_BYTES
    assert event["payload"]["data"]["file_count"] == TEST_SNAPSHOT_FILE_COUNT


@pytest.mark.asyncio
async def test_publish_snapshot_restored(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test snapshot restored event publishing."""
    await publisher.publish_snapshot_restored(
        session_id="sess-123",
        project_id="proj-456",
        snapshot_id="snap-789",
        s3_key="snapshots/sess-123/snap-789.tar.gz",
        restored_to="/tmp/sandbox/sess-123-restored",  # nosec B108 -- test fixture data
    )

    assert len(mock_nats.published_events) == 1
    event = mock_nats.published_events[0]

    assert event["subject"] == "tracertm.sandbox.sess-123.snapshot_restored"
    assert event["payload"]["event_type"] == EventType.SNAPSHOT_RESTORED
    assert event["payload"]["data"]["restored_to"] == "/tmp/sandbox/sess-123-restored"  # nosec B108


@pytest.mark.asyncio
async def test_event_payload_structure(publisher: AgentEventPublisher, mock_nats: MockNATSClient) -> None:
    """Test that all events follow standard payload structure."""
    await publisher.publish_session_created(
        session_id="sess-123",
        project_id="proj-456",
        sandbox_root="/tmp/sandbox",  # nosec B108 -- test fixture data
        provider="claude",
    )

    event = mock_nats.published_events[0]["payload"]

    # Verify standard fields
    assert "event_id" in event
    assert "event_type" in event
    assert "timestamp" in event
    assert "session_id" in event
    assert "project_id" in event
    assert "data" in event
    assert "metadata" in event

    # Verify metadata structure
    assert "source" in event["metadata"]
    assert "version" in event["metadata"]
    assert event["metadata"]["version"] == "1.0"


@pytest.mark.asyncio
async def test_fire_and_forget_on_error(mock_nats: MockNATSClient) -> None:
    """Test that event publishing errors don't raise exceptions."""
    # Make publish fail
    mock_nats._js.publish = AsyncMock(side_effect=Exception("NATS error"))

    publisher = AgentEventPublisher(mock_nats)

    # Should not raise exception
    await publisher.publish_session_created(
        session_id="sess-123",
        project_id="proj-456",
        sandbox_root="/tmp/sandbox",  # nosec B108 -- test fixture data
        provider="claude",
    )


@pytest.mark.asyncio
async def test_publisher_disabled_when_no_nats() -> None:
    """Test that publisher gracefully handles missing NATS client."""
    publisher = AgentEventPublisher(None)

    # Should not raise exception
    await publisher.publish_session_created(
        session_id="sess-123",
        project_id="proj-456",
        sandbox_root="/tmp/sandbox",  # nosec B108 -- test fixture data
        provider="claude",
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("_mock_nats")
async def test_health_check(publisher: AgentEventPublisher) -> None:
    """Test event publisher health check."""
    health = await publisher.health_check()

    assert health["enabled"] is True
    assert health["nats_connected"] is True
    assert health["jetstream_ready"] is True


@pytest.mark.asyncio
async def test_health_check_no_nats() -> None:
    """Test health check with no NATS client."""
    publisher = AgentEventPublisher(None)
    health = await publisher.health_check()

    assert health["enabled"] is False
    assert "reason" in health


def test_event_type_enum() -> None:
    """Test event type enumeration."""
    assert EventType.SESSION_CREATED.value == "session.created"
    assert EventType.CHAT_MESSAGE.value == "chat.message"
    assert EventType.SNAPSHOT_CREATED.value == "snapshot.created"


def test_session_status_enum() -> None:
    """Test session status enumeration."""
    assert SessionStatus.ACTIVE.value == "ACTIVE"
    assert SessionStatus.COMPLETED.value == "COMPLETED"
    assert SessionStatus.FAILED.value == "FAILED"


def test_event_source_enum() -> None:
    """Test event source enumeration."""
    assert EventSource.AGENT_SERVICE.value == "agent_service"
    assert EventSource.WORKFLOW_EXECUTOR.value == "workflow_executor"
    assert EventSource.SNAPSHOT_SERVICE.value == "snapshot_service"
