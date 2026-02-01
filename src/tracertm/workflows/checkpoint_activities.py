"""Temporal activities for agent checkpoint and snapshot management.

Activities are the actual work functions executed within workflows.
They handle database persistence, AI execution, and snapshot operations.
"""

from __future__ import annotations

import json
import logging
import os
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn(name="create_checkpoint")
async def create_checkpoint(
    session_id: str,
    turn_number: int,
    state_snapshot: dict[str, Any],
    checkpoint_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create checkpoint and save to database.

    Args:
        session_id: Agent session ID
        turn_number: Conversation turn number
        state_snapshot: Complete conversation state to save
        checkpoint_metadata: Optional metadata (model, tokens, etc.)

    Returns:
        dict: Checkpoint creation result with ID and S3 key (placeholder)
    """
    activity.logger.info(
        f"Creating checkpoint for session {session_id} at turn {turn_number}"
    )

    try:
        from tracertm.services.checkpoint_service import get_checkpoint_service

        checkpoint_service = get_checkpoint_service()

        # Create checkpoint in database
        checkpoint = await checkpoint_service.create_checkpoint(
            session_id=session_id,
            turn_number=turn_number,
            state_snapshot=state_snapshot,
            checkpoint_metadata=checkpoint_metadata or {},
        )

        # Prepare S3 key (Phase 4 will implement actual MinIO upload)
        s3_key = f"sandboxes/{session_id}/snapshots/snapshot-turn-{turn_number}.tar.gz"

        activity.logger.info(
            f"Checkpoint created: {checkpoint.id} (turn {turn_number})"
        )

        return {
            "status": "success",
            "checkpoint_id": str(checkpoint.id),
            "session_id": session_id,
            "turn_number": turn_number,
            "s3_key": s3_key,  # Placeholder - Phase 4 will populate
            "created_at": checkpoint.created_at.isoformat(),
        }

    except Exception as e:
        activity.logger.error(f"Failed to create checkpoint: {e}")
        raise


@activity.defn(name="load_latest_checkpoint")
async def load_latest_checkpoint(session_id: str) -> dict[str, Any] | None:
    """Load most recent checkpoint for session.

    Args:
        session_id: Agent session ID

    Returns:
        dict: Checkpoint data or None if no checkpoints exist
    """
    activity.logger.info(f"Loading latest checkpoint for session {session_id}")

    try:
        from tracertm.services.checkpoint_service import get_checkpoint_service

        checkpoint_service = get_checkpoint_service()
        checkpoint = await checkpoint_service.load_latest_checkpoint(session_id)

        if not checkpoint:
            activity.logger.info(f"No checkpoint found for session {session_id}")
            return None

        return {
            "checkpoint_id": str(checkpoint.id),
            "session_id": checkpoint.session_id,
            "turn_number": checkpoint.turn_number,
            "state_snapshot": checkpoint.state_snapshot,
            "checkpoint_metadata": checkpoint.checkpoint_metadata or {},
            "sandbox_snapshot_s3_key": checkpoint.sandbox_snapshot_s3_key,
            "created_at": checkpoint.created_at.isoformat(),
        }

    except Exception as e:
        activity.logger.error(f"Failed to load checkpoint: {e}")
        raise


@activity.defn(name="load_checkpoint_by_turn")
async def load_checkpoint_by_turn(
    session_id: str,
    turn_number: int,
) -> dict[str, Any] | None:
    """Load checkpoint for specific turn.

    Args:
        session_id: Agent session ID
        turn_number: Turn number to load

    Returns:
        dict: Checkpoint data or None if not found
    """
    activity.logger.info(
        f"Loading checkpoint for session {session_id} at turn {turn_number}"
    )

    try:
        from tracertm.services.checkpoint_service import get_checkpoint_service

        checkpoint_service = get_checkpoint_service()
        checkpoint = await checkpoint_service.load_checkpoint_by_turn(
            session_id, turn_number
        )

        if not checkpoint:
            return None

        return {
            "checkpoint_id": str(checkpoint.id),
            "session_id": checkpoint.session_id,
            "turn_number": checkpoint.turn_number,
            "state_snapshot": checkpoint.state_snapshot,
            "checkpoint_metadata": checkpoint.checkpoint_metadata or {},
            "sandbox_snapshot_s3_key": checkpoint.sandbox_snapshot_s3_key,
            "created_at": checkpoint.created_at.isoformat(),
        }

    except Exception as e:
        activity.logger.error(f"Failed to load checkpoint: {e}")
        raise


@activity.defn(name="execute_ai_turn")
async def execute_ai_turn(
    session_id: str,
    messages: list[dict],
    model: str = "claude-sonnet-4-20250514",
    system_prompt: str | None = None,
) -> dict[str, Any]:
    """Execute one AI turn with tools in session sandbox.

    Args:
        session_id: Agent session ID
        messages: Conversation messages
        model: AI model to use
        system_prompt: Optional system prompt

    Returns:
        dict: Turn result with updated messages and metadata
    """
    activity.logger.info(
        f"Executing AI turn for session {session_id} (model={model})"
    )

    # Send heartbeat periodically during long-running execution
    activity.heartbeat("Starting AI turn")

    try:
        from tracertm.agent import get_agent_service
        from tracertm.agent.session_store import SessionSandboxStoreDB
        from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider
        from tracertm.services.ai_tools import set_allowed_paths
        from tracertm.services.ai_service import get_ai_service

        # Resolve session sandbox path
        sandbox_path = None
        try:
            from tracertm.mcp.database_adapter import get_mcp_session

            async with get_mcp_session() as db:
                store = SessionSandboxStoreDB(
                    sandbox_provider=LocalFilesystemSandboxProvider(),
                    cache_service=None,
                )
                from tracertm.agent import AgentService

                agent_svc = AgentService(session_store=store)
                sandbox_path, _ = await agent_svc.get_or_create_session_sandbox(
                    session_id, config=None, db_session=db
                )
        except (ValueError, RuntimeError, Exception) as e:
            logger.debug(
                f"DB session resolution failed ({e}), using global store"
            )
            agent_svc = get_agent_service()
            sandbox_path, _ = await agent_svc.get_or_create_session_sandbox(
                session_id
            )

        # Set allowed paths for file operations
        if sandbox_path:
            set_allowed_paths([sandbox_path])

        activity.heartbeat("Sandbox resolved, executing AI")

        # Execute AI turn with tools
        ai_service = get_ai_service()
        response = await ai_service.run_chat_turn_with_tools(
            messages=messages,
            model=model,
            system_prompt=system_prompt,
            max_tokens=4096,
            working_directory=sandbox_path,
            db_session=None,
            max_tool_iterations=10,
        )

        # Update messages with assistant response
        updated_messages = messages + [{"role": "assistant", "content": response}]

        # Check if conversation should end (simple heuristic)
        done = False
        if isinstance(response, str):
            # Conversation ends if response contains completion markers
            done = any(
                marker in response.lower()
                for marker in ["goodbye", "task complete", "finished", "done with"]
            )

        activity.logger.info(f"AI turn completed (done={done})")

        return {
            "status": "success",
            "messages": updated_messages,
            "done": done,
            "metadata": {
                "model": model,
                "sandbox_path": sandbox_path,
                "response_length": len(response) if isinstance(response, str) else 0,
            },
        }

    except Exception as e:
        activity.logger.error(f"AI turn execution failed: {e}")
        # Return error result instead of raising to allow graceful handling
        return {
            "status": "error",
            "messages": messages,
            "done": True,
            "error": str(e),
            "metadata": {"model": model},
        }


@activity.defn(name="create_sandbox_snapshot")
async def create_sandbox_snapshot(
    session_id: str,
    snapshot_name: str,
    include_sandbox: bool = True,
    compression: str = "gzip",
    retention_days: int = 30,
) -> dict[str, Any]:
    """Create snapshot of session sandbox.

    Args:
        session_id: Agent session ID
        snapshot_name: Snapshot identifier
        include_sandbox: Whether to include full sandbox directory
        compression: Compression algorithm (gzip, bzip2, none)
        retention_days: Retention period in days

    Returns:
        dict: Snapshot result with S3 key and metadata
    """
    activity.logger.info(
        f"Creating sandbox snapshot: {snapshot_name} (compression={compression})"
    )

    # Send heartbeat for long-running operation
    activity.heartbeat("Starting snapshot creation")

    try:
        from tracertm.agent import get_agent_service

        agent_svc = get_agent_service()
        sandbox_path, _ = await agent_svc.get_or_create_session_sandbox(session_id)

        if not sandbox_path or not os.path.exists(sandbox_path):
            raise FileNotFoundError(f"Sandbox not found for session {session_id}")

        # Prepare S3 key (Phase 4 will upload to MinIO)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        s3_key = f"sandboxes/{session_id}/snapshots/{snapshot_name}-{timestamp}.tar.gz"

        # Create temporary snapshot archive
        snapshot_size = 0
        if include_sandbox:
            activity.heartbeat("Creating archive")

            with tempfile.NamedTemporaryFile(
                delete=False, suffix=".tar.gz"
            ) as temp_file:
                temp_path = temp_file.name

            try:
                # Create tar archive
                compression_mode = {
                    "gzip": "w:gz",
                    "bzip2": "w:bz2",
                    "none": "w",
                }.get(compression, "w:gz")

                with tarfile.open(temp_path, compression_mode) as tar:
                    tar.add(sandbox_path, arcname=os.path.basename(sandbox_path))

                snapshot_size = os.path.getsize(temp_path)
                activity.logger.info(
                    f"Snapshot archive created: {snapshot_size} bytes"
                )

                # Phase 4: Upload to MinIO here
                # For now, we'll just track metadata

            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        snapshot_metadata = {
            "snapshot_name": snapshot_name,
            "session_id": session_id,
            "compression": compression,
            "retention_days": retention_days,
            "sandbox_path": sandbox_path,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        activity.logger.info(f"Snapshot created: {s3_key}")

        return {
            "status": "success",
            "s3_key": s3_key,  # Placeholder - Phase 4 will populate
            "size_bytes": snapshot_size,
            "snapshot_metadata": snapshot_metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        activity.logger.error(f"Snapshot creation failed: {e}")
        raise


@activity.defn(name="update_session_snapshot_ref")
async def update_session_snapshot_ref(
    session_id: str,
    s3_key: str,
    snapshot_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Update session with snapshot S3 reference.

    Args:
        session_id: Agent session ID
        s3_key: S3 object key
        snapshot_metadata: Snapshot metadata

    Returns:
        dict: Update result
    """
    activity.logger.info(f"Updating session {session_id} with snapshot ref {s3_key}")

    try:
        # Phase 4 will implement actual session update with S3 reference
        # For now, just log the operation
        activity.logger.info(
            f"Snapshot reference updated for session {session_id}"
        )

        return {
            "status": "success",
            "session_id": session_id,
            "s3_key": s3_key,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        activity.logger.error(f"Failed to update snapshot reference: {e}")
        raise


@activity.defn(name="list_active_sessions")
async def list_active_sessions() -> dict[str, Any]:
    """List all active agent sessions.

    Returns:
        dict: List of active session IDs
    """
    activity.logger.info("Listing active agent sessions")

    try:
        from tracertm.mcp.database_adapter import get_mcp_session
        from sqlalchemy import select
        from tracertm.models.agent_session import AgentSession

        async with get_mcp_session() as db:
            result = await db.execute(
                select(AgentSession.session_id).order_by(
                    AgentSession.updated_at.desc()
                )
            )
            session_ids = [row[0] for row in result.all()]

        activity.logger.info(f"Found {len(session_ids)} active sessions")

        return {
            "status": "success",
            "session_ids": session_ids,
            "count": len(session_ids),
        }

    except Exception as e:
        activity.logger.error(f"Failed to list sessions: {e}")
        # Return empty list on error
        return {"status": "error", "session_ids": [], "count": 0, "error": str(e)}


@activity.defn(name="cleanup_old_snapshots")
async def cleanup_old_snapshots(
    retention_days: int = 30,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Clean up snapshots older than retention period.

    Args:
        retention_days: Keep snapshots from last N days
        dry_run: If True, only report what would be deleted

    Returns:
        dict: Cleanup results
    """
    activity.logger.info(
        f"Cleaning up snapshots older than {retention_days} days (dry_run={dry_run})"
    )

    # Send heartbeat for long-running cleanup
    activity.heartbeat("Starting cleanup scan")

    try:
        # Phase 4 will implement actual MinIO cleanup
        # For now, return placeholder results

        activity.logger.info("Snapshot cleanup completed")

        return {
            "status": "success",
            "deleted_count": 0,  # Placeholder
            "dry_run": dry_run,
            "snapshots": [],  # Phase 4 will populate
        }

    except Exception as e:
        activity.logger.error(f"Cleanup failed: {e}")
        raise
