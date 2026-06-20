"""Agent event streaming infrastructure for real-time agent lifecycle events.

This module provides comprehensive event publishing for agent sessions, checkpoints,
tool executions, snapshots, and chat interactions via NATS JetStream.

Event Subject Schema:
    tracertm.sessions.{session_id}.created
    tracertm.sessions.{session_id}.checkpoint
    tracertm.sessions.{session_id}.destroyed
    tracertm.sessions.{session_id}.status_changed
    tracertm.chat.{session_id}.message
    tracertm.chat.{session_id}.tool_use
    tracertm.chat.{session_id}.error
    tracertm.sandbox.{session_id}.snapshot_created
    tracertm.sandbox.{session_id}.snapshot_restored
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Max length for content/tool summaries in event payloads (avoid huge NATS messages)
MAX_CONTENT_PREVIEW_LENGTH = 500


@dataclass(frozen=True)
class SessionCheckpointPayload:
    """Payload for session checkpoint event."""

    checkpoint_id: str
    turn_number: int
    s3_key: str | None = None
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ChatMessagePayload:
    """Payload for chat message event."""

    role: str
    content: str
    turn_number: int
    metadata: dict[str, Any] | None = None


@dataclass(frozen=True)
class ChatToolUsePayload:
    """Payload for chat tool use event."""

    tool_name: str
    tool_input: dict[str, Any]
    tool_output: object | None = None
    success: bool = True
    error: str | None = None


@dataclass(frozen=True)
class SnapshotCreatedPayload:
    """Payload for snapshot created event."""

    snapshot_id: str
    s3_key: str
    size_bytes: int
    file_count: int


class EventType(StrEnum):
    """Agent event types."""

    # Session lifecycle
    SESSION_CREATED = "session.created"
    SESSION_CHECKPOINT = "session.checkpoint"
    SESSION_DESTROYED = "session.destroyed"
    SESSION_STATUS_CHANGED = "session.status_changed"

    # Chat events
    CHAT_MESSAGE = "chat.message"
    CHAT_TOOL_USE = "chat.tool_use"
    CHAT_ERROR = "chat.error"

    # Sandbox events
    SNAPSHOT_CREATED = "snapshot.created"
    SNAPSHOT_RESTORED = "snapshot.restored"


class EventSource(StrEnum):
    """Event source identifiers."""

    AGENT_SERVICE = "agent_service"
    GRAPH_SESSION_STORE = "graph_session_store"
    WORKFLOW_EXECUTOR = "workflow_executor"
    SNAPSHOT_SERVICE = "snapshot_service"
    CHAT_HANDLER = "chat_handler"


class SessionStatus(StrEnum):
    """Session status values."""

    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DESTROYED = "DESTROYED"


class EventMetadata(BaseModel):
    """Standard metadata for all events."""

    source: EventSource
    version: str = "1.0"
    environment: str | None = None


class BaseEvent(BaseModel):
    """Base event payload structure."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: EventType
    timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    session_id: str
    project_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: EventMetadata


class AgentEventPublisher:
    """Publisher for agent lifecycle events to NATS.

    This class provides type-safe methods for publishing various agent events
    with standardized payload formats. All publishing is fire-and-forget with
    error logging to avoid blocking operations.

    Example:
        >>> publisher = AgentEventPublisher(nats_client)
        >>> await publisher.publish_session_created(
        ...     session_id="sess-123",
        ...     project_id="proj-456",
        ...     sandbox_root="/tmp/sandbox",
        ...     provider="claude",
        ...     model="claude-3-opus",
        ... )
    """

    # Subject patterns
    SESSION_SUBJECT_PREFIX = "tracertm.sessions"
    CHAT_SUBJECT_PREFIX = "tracertm.chat"
    SANDBOX_SUBJECT_PREFIX = "tracertm.sandbox"

    def __init__(self, nats_client: object) -> None:
        """Initialize event publisher.

        Args:
            nats_client: Connected NATSClient instance
        """
        self.nats = nats_client
        self._enabled = nats_client is not None

    async def publish_session_created(
        self,
        session_id: str,
        project_id: str | None,
        sandbox_root: str,
        provider: str,
        model: str | None = None,
    ) -> None:
        """Publish session created event.

        Args:
            session_id: Unique session identifier
            project_id: Associated project ID (optional)
            sandbox_root: Path to sandbox directory
            provider: AI provider name (e.g., "claude", "openai")
            model: Model identifier (e.g., "claude-3-opus")
        """
        if not self._enabled:
            return

        event = BaseEvent(
            event_type=EventType.SESSION_CREATED,
            session_id=session_id,
            project_id=project_id,
            data={
                "sandbox_root": sandbox_root,
                "provider": provider,
                "model": model,
            },
            metadata=EventMetadata(source=EventSource.AGENT_SERVICE),
        )

        await self._publish(
            f"{self.SESSION_SUBJECT_PREFIX}.{session_id}.created",
            event,
        )

    async def publish_session_checkpoint(
        self,
        session_id: str,
        project_id: str | None,
        payload: SessionCheckpointPayload,
    ) -> None:
        """Publish session checkpoint event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            payload: Checkpoint data (checkpoint_id, turn_number, s3_key, metadata)
        """
        if not self._enabled:
            return

        event = BaseEvent(
            event_type=EventType.SESSION_CHECKPOINT,
            session_id=session_id,
            project_id=project_id,
            data={
                "checkpoint_id": payload.checkpoint_id,
                "turn_number": payload.turn_number,
                "s3_key": payload.s3_key,
                "metadata": payload.metadata or {},
            },
            metadata=EventMetadata(source=EventSource.WORKFLOW_EXECUTOR),
        )

        await self._publish(
            f"{self.SESSION_SUBJECT_PREFIX}.{session_id}.checkpoint",
            event,
        )

    async def publish_session_destroyed(
        self,
        session_id: str,
        project_id: str | None,
        reason: str | None = None,
    ) -> None:
        """Publish session destroyed event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            reason: Optional reason for destruction
        """
        if not self._enabled:
            return

        event = BaseEvent(
            event_type=EventType.SESSION_DESTROYED,
            session_id=session_id,
            project_id=project_id,
            data={
                "reason": reason,
            },
            metadata=EventMetadata(source=EventSource.AGENT_SERVICE),
        )

        await self._publish(
            f"{self.SESSION_SUBJECT_PREFIX}.{session_id}.destroyed",
            event,
        )

    async def publish_session_status_changed(
        self,
        session_id: str,
        project_id: str | None,
        old_status: SessionStatus,
        new_status: SessionStatus,
        details: dict[str, object] | None = None,
    ) -> None:
        """Publish session status change event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            old_status: Previous session status
            new_status: New session status
            details: Optional additional details
        """
        if not self._enabled:
            return

        event = BaseEvent(
            event_type=EventType.SESSION_STATUS_CHANGED,
            session_id=session_id,
            project_id=project_id,
            data={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "details": details or {},
            },
            metadata=EventMetadata(source=EventSource.GRAPH_SESSION_STORE),
        )

        await self._publish(
            f"{self.SESSION_SUBJECT_PREFIX}.{session_id}.status_changed",
            event,
        )

    async def publish_chat_message(
        self,
        session_id: str,
        project_id: str | None,
        payload: ChatMessagePayload,
    ) -> None:
        """Publish chat message event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            payload: Message data (role, content, turn_number, metadata)
        """
        if not self._enabled:
            return

        content = payload.content
        content_preview = content[:MAX_CONTENT_PREVIEW_LENGTH] if len(content) > MAX_CONTENT_PREVIEW_LENGTH else content

        event = BaseEvent(
            event_type=EventType.CHAT_MESSAGE,
            session_id=session_id,
            project_id=project_id,
            data={
                "role": payload.role,
                "content_preview": content_preview,
                "content_length": len(content),
                "turn_number": payload.turn_number,
                "metadata": payload.metadata or {},
            },
            metadata=EventMetadata(source=EventSource.CHAT_HANDLER),
        )

        await self._publish(
            f"{self.CHAT_SUBJECT_PREFIX}.{session_id}.message",
            event,
        )

    async def publish_chat_tool_use(
        self,
        session_id: str,
        project_id: str | None,
        payload: ChatToolUsePayload,
    ) -> None:
        """Publish tool use event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            payload: Tool use data (tool_name, tool_input, tool_output, success, error)
        """
        if not self._enabled:
            return

        input_summary = str(payload.tool_input)[:MAX_CONTENT_PREVIEW_LENGTH]
        output_summary = str(payload.tool_output)[:MAX_CONTENT_PREVIEW_LENGTH] if payload.tool_output else None

        event = BaseEvent(
            event_type=EventType.CHAT_TOOL_USE,
            session_id=session_id,
            project_id=project_id,
            data={
                "tool_name": payload.tool_name,
                "input_summary": input_summary,
                "output_summary": output_summary,
                "success": payload.success,
                "error": payload.error,
            },
            metadata=EventMetadata(source=EventSource.CHAT_HANDLER),
        )

        await self._publish(
            f"{self.CHAT_SUBJECT_PREFIX}.{session_id}.tool_use",
            event,
        )

    async def publish_chat_error(
        self,
        session_id: str,
        project_id: str | None,
        error_type: str,
        error_message: str,
        stack_trace: str | None = None,
    ) -> None:
        """Publish chat error event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            error_type: Type/class of error
            error_message: Error message
            stack_trace: Optional stack trace
        """
        if not self._enabled:
            return

        event = BaseEvent(
            event_type=EventType.CHAT_ERROR,
            session_id=session_id,
            project_id=project_id,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "stack_trace": stack_trace,
            },
            metadata=EventMetadata(source=EventSource.CHAT_HANDLER),
        )

        await self._publish(
            f"{self.CHAT_SUBJECT_PREFIX}.{session_id}.error",
            event,
        )

    async def publish_snapshot_created(
        self,
        session_id: str,
        project_id: str | None,
        payload: SnapshotCreatedPayload,
    ) -> None:
        """Publish snapshot created event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            payload: Snapshot data (snapshot_id, s3_key, size_bytes, file_count)
        """
        if not self._enabled:
            return

        event = BaseEvent(
            event_type=EventType.SNAPSHOT_CREATED,
            session_id=session_id,
            project_id=project_id,
            data={
                "snapshot_id": payload.snapshot_id,
                "s3_key": payload.s3_key,
                "size_bytes": payload.size_bytes,
                "file_count": payload.file_count,
            },
            metadata=EventMetadata(source=EventSource.SNAPSHOT_SERVICE),
        )

        await self._publish(
            f"{self.SANDBOX_SUBJECT_PREFIX}.{session_id}.snapshot_created",
            event,
        )

    async def publish_snapshot_restored(
        self,
        session_id: str,
        project_id: str | None,
        snapshot_id: str,
        s3_key: str,
        restored_to: str,
    ) -> None:
        """Publish snapshot restored event.

        Args:
            session_id: Session identifier
            project_id: Associated project ID
            snapshot_id: Snapshot identifier
            s3_key: S3 storage key
            restored_to: Path where snapshot was restored
        """
        if not self._enabled:
            return

        event = BaseEvent(
            event_type=EventType.SNAPSHOT_RESTORED,
            session_id=session_id,
            project_id=project_id,
            data={
                "snapshot_id": snapshot_id,
                "s3_key": s3_key,
                "restored_to": restored_to,
            },
            metadata=EventMetadata(source=EventSource.SNAPSHOT_SERVICE),
        )

        await self._publish(
            f"{self.SANDBOX_SUBJECT_PREFIX}.{session_id}.snapshot_restored",
            event,
        )

    async def _publish(self, subject: str, event: BaseEvent) -> None:
        """Internal method to publish event with error handling.

        Events are fire-and-forget - failures are logged but don't block operations.

        Args:
            subject: NATS subject to publish to
            event: Event payload
        """
        try:
            if not self.nats or not hasattr(self.nats, "_js") or not self.nats._js:
                logger.debug("NATS not available, skipping event: %s", subject)
                return

            payload = event.model_dump_json().encode("utf-8")
            ack = await self.nats._js.publish(subject, payload)

            logger.debug(
                "Published %s to %s (stream=%s, seq=%s, event_id=%s)",
                event.event_type,
                subject,
                ack.stream,
                ack.seq,
                event.event_id,
            )

        except Exception as e:
            # Fire-and-forget: log error but don't raise
            logger.warning(
                "Failed to publish event %s to %s: %s",
                event.event_type,
                subject,
                e,
                exc_info=True,
            )

    async def health_check(self) -> dict[str, Any]:
        """Check event publisher health.

        Returns:
            dict with connection status
        """
        if not self.nats:
            return {"enabled": False, "reason": "NATS client not configured"}

        return {
            "enabled": True,
            "nats_connected": self.nats.is_connected if hasattr(self.nats, "is_connected") else False,
            "jetstream_ready": bool(self.nats._js) if hasattr(self.nats, "_js") else False,
        }
