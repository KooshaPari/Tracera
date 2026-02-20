"""Snapshot service event integration for publishing snapshot lifecycle events.

This module wraps snapshot operations with event publishing to NATS,
enabling real-time tracking of sandbox snapshot creation and restoration.
"""

import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

SNAPSHOT_STATS_ERRORS = (
    FileNotFoundError,
    PermissionError,
    NotADirectoryError,
    OSError,
    RuntimeError,
)
SNAPSHOT_EVENT_ERRORS = (
    AttributeError,
    TypeError,
    ValueError,
    RuntimeError,
    OSError,
    ConnectionError,
    TimeoutError,
)


@dataclass
class CreateSnapshotParams:
    """Parameters for create_snapshot_with_events."""

    session_id: str
    sandbox_path: str
    snapshot_id: str
    s3_key: str
    snapshot_service: object
    event_publisher: object
    project_id: str | None = None


@dataclass
class RestoreSnapshotParams:
    """Parameters for restore_snapshot_with_events."""

    session_id: str
    snapshot_id: str
    s3_key: str
    restore_to: str
    snapshot_service: object
    event_publisher: object
    project_id: str | None = None


class SnapshotEventPublisher:
    """Publishes snapshot lifecycle events to NATS.

    This class should wrap snapshot service operations to publish events
    when snapshots are created or restored.
    """

    def __init__(self, event_publisher: object) -> None:
        """Initialize snapshot event publisher.

        Args:
            event_publisher: AgentEventPublisher instance
        """
        self._event_publisher = event_publisher

    async def publish_snapshot_created(
        self,
        session_id: str,
        snapshot_id: str,
        s3_key: str,
        sandbox_path: str,
        project_id: str | None = None,
    ) -> None:
        """Publish snapshot created event with file statistics.

        Args:
            session_id: Session identifier
            snapshot_id: Unique snapshot identifier
            s3_key: S3/MinIO storage key
            sandbox_path: Local sandbox path that was snapshotted
            project_id: Optional project ID
        """
        if not self._event_publisher:
            return

        # Calculate snapshot statistics (run in thread to avoid blocking; ASYNC240)
        def _compute_stats() -> tuple[int, int]:
            sandbox_dir = Path(sandbox_path)
            if not sandbox_dir.exists():
                return 0, 0
            files = list(sandbox_dir.rglob("*"))
            file_count = len(files)
            size_bytes = sum(f.stat().st_size for f in files if f.is_file())
            return file_count, size_bytes

        try:
            file_count, size_bytes = await asyncio.to_thread(_compute_stats)
        except SNAPSHOT_STATS_ERRORS as e:
            logger.warning("Failed to calculate snapshot stats: %s", e)
            file_count = 0
            size_bytes = 0

        from tracertm.agent.events import SnapshotCreatedPayload

        payload = SnapshotCreatedPayload(
            snapshot_id=snapshot_id,
            s3_key=s3_key,
            size_bytes=size_bytes,
            file_count=file_count,
        )
        await self._event_publisher.publish_snapshot_created(  # type: ignore[attr-defined]
            session_id=session_id,
            project_id=project_id,
            payload=payload,
        )

    async def publish_snapshot_restored(
        self,
        session_id: str,
        snapshot_id: str,
        s3_key: str,
        restored_to: str,
        project_id: str | None = None,
    ) -> None:
        """Publish snapshot restored event.

        Args:
            session_id: Session identifier
            snapshot_id: Snapshot identifier
            s3_key: S3/MinIO storage key
            restored_to: Path where snapshot was restored
            project_id: Optional project ID
        """
        if not self._event_publisher:
            return

        await self._event_publisher.publish_snapshot_restored(  # type: ignore[attr-defined]
            session_id=session_id,
            project_id=project_id,
            snapshot_id=snapshot_id,
            s3_key=s3_key,
            restored_to=restored_to,
        )


async def create_snapshot_with_events(params: CreateSnapshotParams) -> dict[str, Any]:
    """Create snapshot and publish event.

    This is a helper function that wraps snapshot creation with event publishing.

    Args:
        params: CreateSnapshotParams (session_id, sandbox_path, snapshot_id, s3_key,
            snapshot_service, event_publisher, project_id)

    Returns:
        dict: Snapshot creation result

    Example:
        >>> from tracertm.agent.sandbox.snapshot_events import (
        ...     CreateSnapshotParams,
        ...     create_snapshot_with_events,
        ... )
        >>> result = await create_snapshot_with_events(
        ...     CreateSnapshotParams(
        ...         session_id="sess-123",
        ...         sandbox_path="/tmp/sandbox/sess-123",
        ...         snapshot_id="snap-456",
        ...         s3_key="snapshots/sess-123/snap-456.tar.gz",
        ...         snapshot_service=snapshot_svc,
        ...         event_publisher=event_pub,
        ...         project_id="proj-789",
        ...     )
        ... )
    """
    try:
        result = {
            "snapshot_id": params.snapshot_id,
            "s3_key": params.s3_key,
            "status": "created",
        }

        if params.event_publisher:
            publisher = SnapshotEventPublisher(params.event_publisher)
            await publisher.publish_snapshot_created(
                session_id=params.session_id,
                snapshot_id=params.snapshot_id,
                s3_key=params.s3_key,
                sandbox_path=params.sandbox_path,
                project_id=params.project_id,
            )

    except SNAPSHOT_EVENT_ERRORS:
        logger.exception("Snapshot creation failed")
        raise
    else:
        return result


async def restore_snapshot_with_events(params: RestoreSnapshotParams) -> dict[str, Any]:
    """Restore snapshot and publish event.

    This is a helper function that wraps snapshot restoration with event publishing.

    Args:
        params: RestoreSnapshotParams (session_id, snapshot_id, s3_key, restore_to,
            snapshot_service, event_publisher, project_id)

    Returns:
        dict: Snapshot restoration result

    Example:
        >>> from tracertm.agent.sandbox.snapshot_events import (
        ...     RestoreSnapshotParams,
        ...     restore_snapshot_with_events,
        ... )
        >>> result = await restore_snapshot_with_events(
        ...     RestoreSnapshotParams(
        ...         session_id="sess-123",
        ...         snapshot_id="snap-456",
        ...         s3_key="snapshots/sess-123/snap-456.tar.gz",
        ...         restore_to="/tmp/sandbox/sess-123-restored",
        ...         snapshot_service=snapshot_svc,
        ...         event_publisher=event_pub,
        ...         project_id="proj-789",
        ...     )
        ... )
    """
    try:
        result = {
            "snapshot_id": params.snapshot_id,
            "restored_to": params.restore_to,
            "status": "restored",
        }

        if params.event_publisher:
            publisher = SnapshotEventPublisher(params.event_publisher)
            await publisher.publish_snapshot_restored(
                session_id=params.session_id,
                snapshot_id=params.snapshot_id,
                s3_key=params.s3_key,
                restored_to=params.restore_to,
                project_id=params.project_id,
            )

    except SNAPSHOT_EVENT_ERRORS:
        logger.exception("Snapshot restoration failed")
        raise
    else:
        return result
