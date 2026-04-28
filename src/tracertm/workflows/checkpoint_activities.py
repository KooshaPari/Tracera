"""Temporal activities for agent checkpoint and snapshot management.

Activities are the actual work functions executed within workflows.
They handle database persistence, AI execution, and snapshot operations.
"""

from __future__ import annotations

import asyncio
import logging
import tarfile
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, cast

from temporalio import activity

logger = logging.getLogger(__name__)


def _get_file_size(path: str) -> int:
    """Get file size (helper for async Path operations)."""
    return Path(path).stat().st_size


def _remove_file(path: str) -> None:
    """Remove file (helper for async Path operations)."""
    Path(path).unlink(missing_ok=True)


async def _require_existing_sandbox(session_id: str, sandbox_path: str | None) -> str:
    """Validate sandbox path and ensure it exists on disk."""
    if not sandbox_path:
        msg = f"Sandbox not found for session {session_id}"
        raise FileNotFoundError(msg)

    if not await asyncio.to_thread(Path(sandbox_path).exists):
        msg = f"Sandbox not found for session {session_id}"
        raise FileNotFoundError(msg)

    return sandbox_path


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
    activity.logger.info("Creating checkpoint for session %s at turn %s", session_id, turn_number)

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

        activity.logger.info("Checkpoint created: %s (turn %s)", checkpoint.id, turn_number)

        return {
            "status": "success",
            "checkpoint_id": str(checkpoint.id),
            "session_id": session_id,
            "turn_number": turn_number,
            "s3_key": s3_key,  # Placeholder - Phase 4 will populate
            "created_at": checkpoint.created_at.isoformat(),
        }

    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        activity.logger.error("Failed to create checkpoint: %s", e)
        msg = f"Failed to create checkpoint for session {session_id} at turn {turn_number}"
        raise RuntimeError(msg) from e


@activity.defn(name="load_latest_checkpoint")
async def load_latest_checkpoint(session_id: str) -> dict[str, Any] | None:
    """Load most recent checkpoint for session.

    Args:
        session_id: Agent session ID

    Returns:
        dict: Checkpoint data or None if no checkpoints exist
    """
    activity.logger.info("Loading latest checkpoint for session %s", session_id)

    try:
        from tracertm.services.checkpoint_service import get_checkpoint_service

        checkpoint_service = get_checkpoint_service()
        checkpoint = await checkpoint_service.load_latest_checkpoint(session_id)

        if not checkpoint:
            activity.logger.info("No checkpoint found for session %s", session_id)
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

    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        activity.logger.error("Failed to load checkpoint: %s", e)
        msg = f"Failed to load latest checkpoint for session {session_id}"
        raise RuntimeError(msg) from e


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
    activity.logger.info("Loading checkpoint for session %s at turn %s", session_id, turn_number)

    try:
        from tracertm.services.checkpoint_service import get_checkpoint_service

        checkpoint_service = get_checkpoint_service()
        checkpoint = await checkpoint_service.load_checkpoint_by_turn(session_id, turn_number)

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

    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        activity.logger.error("Failed to load checkpoint: %s", e)
        msg = f"Failed to load checkpoint for session {session_id} at turn {turn_number}"
        raise RuntimeError(msg) from e


@activity.defn(name="execute_ai_turn")
async def execute_ai_turn(
    session_id: str,
    messages: list[dict[str, Any]],
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
    activity.logger.info("Executing AI turn for session %s (model=%s)", session_id, model)

    # Send heartbeat periodically during long-running execution
    activity.heartbeat("Starting AI turn")

    try:
        from tracertm.agent import get_agent_service
        from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider
        from tracertm.agent.session_store import SessionSandboxStoreDB
        from tracertm.services.ai_service import get_ai_service
        from tracertm.services.ai_tools import set_allowed_paths

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
                sandbox_path, _ = await agent_svc.get_or_create_session_sandbox(session_id, config=None, db_session=db)
        except (ImportError, OSError, RuntimeError, ValueError) as e:
            logger.debug("DB session resolution failed (%s), using global store", e)
            agent_svc = get_agent_service()
            sandbox_path, _ = await agent_svc.get_or_create_session_sandbox(session_id)

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
        updated_messages = [*messages, {"role": "assistant", "content": response}]

        # Check if conversation should end (simple heuristic)
        done = False
        if isinstance(response, str):
            # Conversation ends if response contains completion markers
            done = any(marker in response.lower() for marker in ["goodbye", "task complete", "finished", "done with"])

        activity.logger.info("AI turn completed (done=%s)", done)

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

    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        activity.logger.error("AI turn execution failed: %s", e)
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
    activity.logger.info("Creating sandbox snapshot: %s (compression=%s)", snapshot_name, compression)

    # Send heartbeat for long-running operation
    activity.heartbeat("Starting snapshot creation")

    try:
        from tracertm.agent import get_agent_service

        agent_svc = get_agent_service()
        sandbox_path, _ = await agent_svc.get_or_create_session_sandbox(session_id)

        sandbox_path = await _require_existing_sandbox(session_id, sandbox_path)

        # Prepare S3 key (Phase 4 will upload to MinIO)
        timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
        s3_key = f"sandboxes/{session_id}/snapshots/{snapshot_name}-{timestamp}.tar.gz"

        # Create temporary snapshot archive
        snapshot_size = 0
        if include_sandbox:
            activity.heartbeat("Creating archive")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".tar.gz") as temp_file:
                temp_path = temp_file.name

            try:
                # Create tar archive
                compression_mode = cast(
                    "Literal['w', 'w:gz', 'w:bz2']",
                    {"gzip": "w:gz", "bzip2": "w:bz2", "none": "w"}.get(compression, "w:gz"),
                )

                with tarfile.open(temp_path, mode=compression_mode) as tar:
                    tar.add(sandbox_path, arcname=Path(sandbox_path).name)

                snapshot_size = await asyncio.to_thread(_get_file_size, temp_path)
                activity.logger.info("Snapshot archive created: %s bytes", snapshot_size)

                # Phase 4: Upload to MinIO here
                # For now, we'll just track metadata

            finally:
                # Clean up temporary file (run in thread to avoid ASYNC240)
                await asyncio.to_thread(_remove_file, temp_path)

        snapshot_metadata = {
            "snapshot_name": snapshot_name,
            "session_id": session_id,
            "compression": compression,
            "retention_days": retention_days,
            "sandbox_path": sandbox_path,
            "created_at": datetime.now(UTC).isoformat(),
        }

        activity.logger.info("Snapshot created: %s", s3_key)

        return {
            "status": "success",
            "s3_key": s3_key,  # Placeholder - Phase 4 will populate
            "size_bytes": snapshot_size,
            "snapshot_metadata": snapshot_metadata,
            "created_at": datetime.now(UTC).isoformat(),
        }

    except FileNotFoundError:
        raise
    except (ImportError, OSError, RuntimeError, tarfile.TarError, TypeError, ValueError) as e:
        activity.logger.error("Snapshot creation failed: %s", e)
        msg = f"Snapshot creation failed for session {session_id}"
        raise RuntimeError(msg) from e


@activity.defn(name="update_session_snapshot_ref")
async def update_session_snapshot_ref(
    session_id: str,
    s3_key: str,
    _snapshot_metadata: dict[str, Any],
) -> dict[str, Any]:
    """Update session with snapshot S3 reference.

    Args:
        session_id: Agent session ID
        s3_key: S3 object key
        snapshot_metadata: Snapshot metadata

    Returns:
        dict: Update result
    """
    await asyncio.sleep(0)
    activity.logger.info("Updating session %s with snapshot ref %s", session_id, s3_key)

    try:
        # Phase 4 will implement actual session update with S3 reference
        # For now, just log the operation
        activity.logger.info("Snapshot reference updated for session %s", session_id)

        return {
            "status": "success",
            "session_id": session_id,
            "s3_key": s3_key,
            "updated_at": datetime.now(UTC).isoformat(),
        }

    except (OSError, RuntimeError, TypeError, ValueError) as e:
        activity.logger.error("Failed to update snapshot reference: %s", e)
        msg = f"Failed to update snapshot reference for session {session_id}"
        raise RuntimeError(msg) from e


@activity.defn(name="list_active_sessions")
async def list_active_sessions() -> dict[str, Any]:
    """List all active agent sessions.

    Returns:
        dict: List of active session IDs
    """
    activity.logger.info("Listing active agent sessions")

    try:
        from sqlalchemy import select

        from tracertm.mcp.database_adapter import get_mcp_session
        from tracertm.models.agent_session import AgentSession

        async with get_mcp_session() as db:
            result = await db.execute(select(AgentSession.session_id).order_by(AgentSession.updated_at.desc()))
            session_ids = [row[0] for row in result.all()]

        activity.logger.info("Found %s active sessions", len(session_ids))

        return {
            "status": "success",
            "session_ids": session_ids,
            "count": len(session_ids),
        }

    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        activity.logger.error("Failed to list sessions: %s", e)
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
    await asyncio.sleep(0)
    activity.logger.info("Cleaning up snapshots older than %s days (dry_run=%s)", retention_days, dry_run)

    # Send heartbeat for long-running cleanup
    activity.heartbeat("Starting cleanup scan")

    try:
        # Phase 4 will implement actual MinIO cleanup
        # For now, return placeholder results

        activity.logger.info("Snapshot cleanup completed")

    except (OSError, RuntimeError, TypeError, ValueError) as e:
        activity.logger.error("Cleanup failed: %s", e)
        msg = "Snapshot cleanup activity failed"
        raise RuntimeError(msg) from e
    else:
        return {
            "status": "success",
            "deleted_count": 0,  # Placeholder
            "dry_run": dry_run,
            "snapshots": [],  # Phase 4 will populate
        }
