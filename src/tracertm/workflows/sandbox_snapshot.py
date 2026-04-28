"""Temporal workflow for scheduled sandbox snapshot creation.

This workflow handles periodic snapshot creation for agent sessions,
uploading sandbox state to MinIO for backup and recovery purposes.
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import TemporalError

# Import activity functions for workflow execution
with workflow.unsafe.imports_passed_through():
    from tracertm.workflows import checkpoint_activities

logger = logging.getLogger(__name__)


@workflow.defn(name="SandboxSnapshotWorkflow")
class SandboxSnapshotWorkflow:
    """Scheduled workflow for creating sandbox snapshots.

    Features:
    - Periodic snapshot creation (default: every 15 minutes)
    - Upload to MinIO/S3 storage (prepared for Phase 4)
    - Session metadata updates with snapshot references
    - Automatic cleanup of old snapshots
    - Graceful handling of inactive sessions
    """

    @workflow.run
    async def run(
        self,
        session_id: str,
        snapshot_name: str | None = None,
        include_sandbox: bool = True,
        compression: str = "gzip",
        retention_days: int = 30,
    ) -> dict[str, Any]:
        """Create sandbox snapshot for session.

        Args:
            session_id: Agent session ID
            snapshot_name: Optional custom snapshot name (auto-generated if None)
            include_sandbox: Whether to include full sandbox directory
            compression: Compression algorithm (gzip, bzip2, or none)
            retention_days: Days to retain snapshot before cleanup

        Returns:
            dict: Snapshot creation result with S3 key and metadata
        """
        workflow.logger.info(
            "Creating sandbox snapshot for session %s (compression=%s, retention=%sd)",
            session_id,
            compression,
            retention_days,
        )

        # Generate snapshot name if not provided
        if not snapshot_name:
            workflow_run_id = workflow.info().run_id
            snapshot_name = f"snapshot-{session_id}-{workflow_run_id}"

        # Create snapshot (Phase 4 will implement actual MinIO upload)
        try:
            snapshot_result = await workflow.execute_activity(
                checkpoint_activities.create_sandbox_snapshot,
                args=[
                    session_id,
                    snapshot_name,
                    include_sandbox,
                    compression,
                    retention_days,
                ],
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(seconds=30),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=5),
                    maximum_interval=timedelta(seconds=30),
                    backoff_coefficient=2.0,
                    non_retryable_error_types=["ValueError", "FileNotFoundError"],
                ),
            )

            # Update session with snapshot reference
            if snapshot_result.get("s3_key"):
                await workflow.execute_activity(
                    checkpoint_activities.update_session_snapshot_ref,
                    args=[
                        session_id,
                        snapshot_result["s3_key"],
                        snapshot_result.get("snapshot_metadata", {}),
                    ],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        maximum_attempts=2,
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=5),
                        backoff_coefficient=2.0,
                    ),
                )

            workflow.logger.info("Snapshot created successfully: %s", snapshot_result.get("s3_key"))
            return {
                "status": "success",
                "session_id": session_id,
                "snapshot_name": snapshot_name,
                "s3_key": snapshot_result.get("s3_key"),
                "size_bytes": snapshot_result.get("size_bytes", 0),
                "compression": compression,
                "created_at": snapshot_result.get("created_at"),
            }

        except (KeyError, TemporalError, TypeError, ValueError) as e:
            workflow.logger.error("Snapshot creation failed: %s", e)
            return {
                "status": "failed",
                "session_id": session_id,
                "snapshot_name": snapshot_name,
                "error": str(e),
            }


@workflow.defn(name="BulkSnapshotWorkflow")
class BulkSnapshotWorkflow:
    """Bulk snapshot creation for multiple sessions.

    Use for scheduled backups of all active agent sessions.
    """

    @workflow.run
    async def run(
        self,
        session_ids: list[str] | None = None,
        max_concurrent: int = 5,
        compression: str = "gzip",
        retention_days: int = 30,
    ) -> dict[str, Any]:
        """Create snapshots for multiple sessions.

        Args:
            session_ids: List of session IDs (or None to snapshot all active sessions)
            max_concurrent: Maximum concurrent snapshot operations
            compression: Compression algorithm
            retention_days: Snapshot retention period

        Returns:
            dict: Bulk snapshot results with success/failure counts
        """
        workflow.logger.info(
            "Starting bulk snapshot workflow "
            f"(sessions={len(session_ids) if session_ids else 'all'}, "
            f"max_concurrent={max_concurrent})",
        )

        # Get list of active sessions if not provided
        if not session_ids:
            session_list_result = await workflow.execute_activity(
                checkpoint_activities.list_active_sessions,
                start_to_close_timeout=timedelta(seconds=60),
            )
            session_ids = session_list_result.get("session_ids", [])

        if not session_ids:
            workflow.logger.info("No active sessions found for snapshot")
            return {
                "status": "success",
                "total_sessions": 0,
                "successful": 0,
                "failed": 0,
                "results": [],
            }

        # Create snapshots in batches to limit concurrency
        successful = 0
        failed = 0
        results = []

        for i in range(0, len(session_ids), max_concurrent):
            batch = session_ids[i : i + max_concurrent]
            batch_tasks = []

            # Start snapshot workflows for batch
            for session_id in batch:
                task = workflow.execute_child_workflow(
                    SandboxSnapshotWorkflow.run,
                    args=[session_id, None, True, compression, retention_days],
                    id=f"snapshot-{session_id}-{workflow.info().run_id}",
                    task_queue=workflow.info().task_queue,
                    execution_timeout=timedelta(minutes=15),
                )
                batch_tasks.append((session_id, task))

            # Wait for batch to complete
            for session_id, task in batch_tasks:
                try:
                    result = await task
                    if result.get("status") == "success":
                        successful += 1
                    else:
                        failed += 1
                    results.append(result)
                except (KeyError, TemporalError, TypeError, ValueError) as e:
                    workflow.logger.error("Snapshot failed for session %s: %s", session_id, e)
                    failed += 1
                    results.append({
                        "status": "failed",
                        "session_id": session_id,
                        "error": str(e),
                    })

        workflow.logger.info("Bulk snapshot completed: %s successful, %s failed", successful, failed)

        return {
            "status": "success",
            "total_sessions": len(session_ids),
            "successful": successful,
            "failed": failed,
            "results": results,
        }


@workflow.defn(name="SnapshotCleanupWorkflow")
class SnapshotCleanupWorkflow:
    """Cleanup old snapshots based on retention policy.

    Scheduled workflow to remove expired snapshots from MinIO/S3.
    """

    @workflow.run
    async def run(
        self,
        retention_days: int = 30,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Clean up snapshots older than retention period.

        Args:
            retention_days: Keep snapshots from last N days
            dry_run: If True, only report what would be deleted

        Returns:
            dict: Cleanup results with count of deleted snapshots
        """
        workflow.logger.info("Starting snapshot cleanup workflow (retention=%sd, dry_run=%s)", retention_days, dry_run)

        # Execute cleanup activity (Phase 4 will implement MinIO deletion)
        cleanup_result = await workflow.execute_activity(
            checkpoint_activities.cleanup_old_snapshots,
            args=[retention_days, dry_run],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(
                maximum_attempts=2,
                initial_interval=timedelta(seconds=5),
                maximum_interval=timedelta(seconds=30),
                backoff_coefficient=2.0,
            ),
        )

        deleted_count = cleanup_result.get("deleted_count", 0)
        workflow.logger.info(
            "Cleanup %s: ",
            "completed"
            if not dry_run
            else f"simulated{deleted_count} snapshots {'deleted' if not dry_run else 'would be deleted'}",
        )

        return {
            "status": "success",
            "deleted_count": deleted_count,
            "dry_run": dry_run,
            "retention_days": retention_days,
            "snapshots": cleanup_result.get("snapshots", []),
        }
