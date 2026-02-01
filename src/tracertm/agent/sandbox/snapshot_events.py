"""Snapshot service event integration for publishing snapshot lifecycle events.

This module wraps snapshot operations with event publishing to NATS,
enabling real-time tracking of sandbox snapshot creation and restoration.
"""

import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SnapshotEventPublisher:
    """Publishes snapshot lifecycle events to NATS.

    This class should wrap snapshot service operations to publish events
    when snapshots are created or restored.
    """

    def __init__(self, event_publisher: Any):
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
        project_id: Optional[str] = None,
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

        # Calculate snapshot statistics
        try:
            sandbox_dir = Path(sandbox_path)
            file_count = len(list(sandbox_dir.rglob("*"))) if sandbox_dir.exists() else 0
            size_bytes = sum(
                f.stat().st_size for f in sandbox_dir.rglob("*") if f.is_file()
            ) if sandbox_dir.exists() else 0
        except Exception as e:
            logger.warning(f"Failed to calculate snapshot stats: {e}")
            file_count = 0
            size_bytes = 0

        await self._event_publisher.publish_snapshot_created(
            session_id=session_id,
            project_id=project_id,
            snapshot_id=snapshot_id,
            s3_key=s3_key,
            size_bytes=size_bytes,
            file_count=file_count,
        )

    async def publish_snapshot_restored(
        self,
        session_id: str,
        snapshot_id: str,
        s3_key: str,
        restored_to: str,
        project_id: Optional[str] = None,
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

        await self._event_publisher.publish_snapshot_restored(
            session_id=session_id,
            project_id=project_id,
            snapshot_id=snapshot_id,
            s3_key=s3_key,
            restored_to=restored_to,
        )


async def create_snapshot_with_events(
    session_id: str,
    sandbox_path: str,
    snapshot_id: str,
    s3_key: str,
    snapshot_service: Any,
    event_publisher: Any,
    project_id: Optional[str] = None,
) -> dict[str, Any]:
    """Create snapshot and publish event.

    This is a helper function that wraps snapshot creation with event publishing.

    Args:
        session_id: Session identifier
        sandbox_path: Path to sandbox directory
        snapshot_id: Unique snapshot identifier
        s3_key: S3 storage key
        snapshot_service: Snapshot service instance
        event_publisher: AgentEventPublisher instance
        project_id: Optional project ID

    Returns:
        dict: Snapshot creation result

    Example:
        >>> from tracertm.agent.events import AgentEventPublisher
        >>> from tracertm.agent.sandbox.snapshot_events import create_snapshot_with_events
        >>>
        >>> result = await create_snapshot_with_events(
        ...     session_id="sess-123",
        ...     sandbox_path="/tmp/sandbox/sess-123",
        ...     snapshot_id="snap-456",
        ...     s3_key="snapshots/sess-123/snap-456.tar.gz",
        ...     snapshot_service=snapshot_svc,
        ...     event_publisher=event_pub,
        ...     project_id="proj-789"
        ... )
    """
    # Create snapshot (actual implementation depends on snapshot service)
    try:
        # TODO: Call actual snapshot service when implemented
        # result = await snapshot_service.create_snapshot(sandbox_path, s3_key)
        result = {
            "snapshot_id": snapshot_id,
            "s3_key": s3_key,
            "status": "created",
        }

        # Publish event
        if event_publisher:
            publisher = SnapshotEventPublisher(event_publisher)
            await publisher.publish_snapshot_created(
                session_id=session_id,
                snapshot_id=snapshot_id,
                s3_key=s3_key,
                sandbox_path=sandbox_path,
                project_id=project_id,
            )

        return result

    except Exception as e:
        logger.error(f"Snapshot creation failed: {e}")
        raise


async def restore_snapshot_with_events(
    session_id: str,
    snapshot_id: str,
    s3_key: str,
    restore_to: str,
    snapshot_service: Any,
    event_publisher: Any,
    project_id: Optional[str] = None,
) -> dict[str, Any]:
    """Restore snapshot and publish event.

    This is a helper function that wraps snapshot restoration with event publishing.

    Args:
        session_id: Session identifier
        snapshot_id: Snapshot identifier
        s3_key: S3 storage key
        restore_to: Path where snapshot should be restored
        snapshot_service: Snapshot service instance
        event_publisher: AgentEventPublisher instance
        project_id: Optional project ID

    Returns:
        dict: Snapshot restoration result

    Example:
        >>> from tracertm.agent.sandbox.snapshot_events import restore_snapshot_with_events
        >>>
        >>> result = await restore_snapshot_with_events(
        ...     session_id="sess-123",
        ...     snapshot_id="snap-456",
        ...     s3_key="snapshots/sess-123/snap-456.tar.gz",
        ...     restore_to="/tmp/sandbox/sess-123-restored",
        ...     snapshot_service=snapshot_svc,
        ...     event_publisher=event_pub,
        ...     project_id="proj-789"
        ... )
    """
    # Restore snapshot (actual implementation depends on snapshot service)
    try:
        # TODO: Call actual snapshot service when implemented
        # result = await snapshot_service.restore_snapshot(s3_key, restore_to)
        result = {
            "snapshot_id": snapshot_id,
            "restored_to": restore_to,
            "status": "restored",
        }

        # Publish event
        if event_publisher:
            publisher = SnapshotEventPublisher(event_publisher)
            await publisher.publish_snapshot_restored(
                session_id=session_id,
                snapshot_id=snapshot_id,
                s3_key=s3_key,
                restored_to=restore_to,
                project_id=project_id,
            )

        return result

    except Exception as e:
        logger.error(f"Snapshot restoration failed: {e}")
        raise
