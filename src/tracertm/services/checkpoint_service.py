"""Service for managing agent checkpoints.

Provides CRUD operations for conversation checkpoints with database persistence.


Functional Requirements: FR-AI-006
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from sqlalchemy import select

from tracertm.models.agent_checkpoint import AgentCheckpoint

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


class CheckpointService:
    """Service for checkpoint management operations.

    Handles checkpoint creation, retrieval, and cleanup for agent sessions.
    """

    def __init__(self, db_session: AsyncSession | None = None) -> None:
        """Initialize checkpoint service.

        Args:
            db_session: Optional database session (will create if not provided)
        """
        self._db_session = db_session
        self._owns_session = db_session is None

    async def _get_session(self) -> AsyncSession:
        """Get database session (create if needed).

        Note: If no session was provided during init, this will raise an error.
        Use the service via async context manager or provide a session at init.
        """
        if self._db_session is not None:
            return self._db_session

        msg = "No database session available. Provide session at init or use service via context manager."
        raise RuntimeError(msg)

    async def create_checkpoint(
        self,
        session_id: str,
        turn_number: int,
        state_snapshot: dict[str, Any],
        checkpoint_metadata: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> AgentCheckpoint:
        """Create new checkpoint for session.

        Args:
            session_id: Agent session ID
            turn_number: Conversation turn number
            state_snapshot: Complete conversation state
            checkpoint_metadata: Optional metadata (model, tokens, etc.)
            description: Optional checkpoint description

        Returns:
            AgentCheckpoint: Created checkpoint instance

        Raises:
            ValueError: If checkpoint already exists for this turn
        """
        db = await self._get_session()

        try:
            # Check if checkpoint already exists for this turn
            existing = await db.execute(
                select(AgentCheckpoint).where(
                    AgentCheckpoint.session_id == session_id,
                    AgentCheckpoint.turn_number == turn_number,
                ),
            )
            if existing.scalar_one_or_none():
                msg = f"Checkpoint already exists for session {session_id} turn {turn_number}"
                raise ValueError(msg)

            # Prepare S3 key (Phase 4 will implement actual MinIO upload)
            s3_key = f"sandboxes/{session_id}/snapshots/snapshot-turn-{turn_number}.tar.gz"

            # Create checkpoint
            checkpoint = AgentCheckpoint(
                session_id=session_id,
                turn_number=turn_number,
                state_snapshot=state_snapshot,
                sandbox_snapshot_s3_key=s3_key,  # Placeholder
                checkpoint_metadata=checkpoint_metadata or {},
                description=description,
            )

            db.add(checkpoint)
            await db.flush()
            await db.refresh(checkpoint)

            # Commit if we own the session
            if self._owns_session:
                await db.commit()

            logger.info("Created checkpoint %s for session %s at turn %s", checkpoint.id, session_id, turn_number)

        except Exception:
            if self._owns_session:
                await db.rollback()
            logger.exception("Failed to create checkpoint")
            raise
        else:
            return checkpoint

    async def load_latest_checkpoint(
        self,
        session_id: str,
    ) -> AgentCheckpoint | None:
        """Load most recent checkpoint for session.

        Args:
            session_id: Agent session ID

        Returns:
            AgentCheckpoint or None if no checkpoints exist
        """
        db = await self._get_session()

        try:
            result = await db.execute(
                select(AgentCheckpoint)
                .where(AgentCheckpoint.session_id == session_id)
                .order_by(AgentCheckpoint.turn_number.desc())
                .limit(1),
            )
            checkpoint = result.scalar_one_or_none()

            if checkpoint:
                logger.info("Loaded latest checkpoint for session %s: turn %s", session_id, checkpoint.turn_number)
            else:
                logger.info("No checkpoints found for session %s", session_id)

        except Exception:
            logger.exception("Failed to load latest checkpoint")
            raise
        else:
            return checkpoint

    async def load_checkpoint_by_turn(
        self,
        session_id: str,
        turn_number: int,
    ) -> AgentCheckpoint | None:
        """Load checkpoint for specific turn.

        Args:
            session_id: Agent session ID
            turn_number: Turn number to load

        Returns:
            AgentCheckpoint or None if not found
        """
        db = await self._get_session()

        try:
            result = await db.execute(
                select(AgentCheckpoint).where(
                    AgentCheckpoint.session_id == session_id,
                    AgentCheckpoint.turn_number == turn_number,
                ),
            )
            checkpoint = result.scalar_one_or_none()

            if checkpoint:
                logger.info("Loaded checkpoint for session %s turn %s", session_id, turn_number)
            else:
                logger.info("No checkpoint found for session %s turn %s", session_id, turn_number)

        except Exception:
            logger.exception("Failed to load checkpoint by turn")
            raise
        else:
            return checkpoint

    async def list_checkpoints(
        self,
        session_id: str,
        limit: int = 50,
    ) -> list[AgentCheckpoint]:
        """List all checkpoints for session.

        Args:
            session_id: Agent session ID
            limit: Maximum number of checkpoints to return

        Returns:
            List of checkpoints ordered by turn number (descending)
        """
        db = await self._get_session()

        try:
            result = await db.execute(
                select(AgentCheckpoint)
                .where(AgentCheckpoint.session_id == session_id)
                .order_by(AgentCheckpoint.turn_number.desc())
                .limit(limit),
            )
            checkpoints = list(result.scalars().all())

            logger.info("Listed %s checkpoints for session %s", len(checkpoints), session_id)

        except Exception:
            logger.exception("Failed to list checkpoints")
            raise
        else:
            return checkpoints

    async def delete_checkpoint(
        self,
        checkpoint_id: str,
    ) -> bool:
        """Delete specific checkpoint.

        Args:
            checkpoint_id: Checkpoint UUID

        Returns:
            bool: True if deleted, False if not found
        """
        db = await self._get_session()

        try:
            result = await db.execute(select(AgentCheckpoint).where(AgentCheckpoint.id == checkpoint_id))
            checkpoint = result.scalar_one_or_none()

            if not checkpoint:
                logger.warning("Checkpoint %s not found", checkpoint_id)
                return False

            await db.delete(checkpoint)

            if self._owns_session:
                await db.commit()

            logger.info("Deleted checkpoint %s", checkpoint_id)

        except Exception:
            if self._owns_session:
                await db.rollback()
            logger.exception("Failed to delete checkpoint")
            raise
        else:
            return True

    async def cleanup_old_checkpoints(
        self,
        session_id: str,
        keep_count: int = 10,
    ) -> int:
        """Clean up old checkpoints, keeping only the N most recent.

        Args:
            session_id: Agent session ID
            keep_count: Number of recent checkpoints to keep

        Returns:
            int: Number of checkpoints deleted
        """
        db = await self._get_session()

        try:
            # Get all checkpoints ordered by turn number
            result = await db.execute(
                select(AgentCheckpoint)
                .where(AgentCheckpoint.session_id == session_id)
                .order_by(AgentCheckpoint.turn_number.desc()),
            )
            all_checkpoints = list(result.scalars().all())

            # Determine which to delete (keep the most recent N)
            to_delete = all_checkpoints[keep_count:]

            if not to_delete:
                logger.info("No checkpoints to clean up for session %s", session_id)
                return 0

            # Delete old checkpoints
            for checkpoint in to_delete:
                await db.delete(checkpoint)

            if self._owns_session:
                await db.commit()

            logger.info("Cleaned up %s old checkpoints for session %s", len(to_delete), session_id)

            return len(to_delete)

        except Exception:
            if self._owns_session:
                await db.rollback()
            logger.exception("Failed to cleanup checkpoints")
            raise

    async def get_checkpoint_stats(
        self,
        session_id: str,
    ) -> dict[str, Any]:
        """Get checkpoint statistics for session.

        Args:
            session_id: Agent session ID

        Returns:
            dict: Statistics including count, latest turn, etc.
        """
        db = await self._get_session()

        try:
            result = await db.execute(select(AgentCheckpoint).where(AgentCheckpoint.session_id == session_id))
            checkpoints = list(result.scalars().all())

            if not checkpoints:
                return {
                    "session_id": session_id,
                    "total_checkpoints": 0,
                    "latest_turn": None,
                    "oldest_turn": None,
                }

            turns = [cp.turn_number for cp in checkpoints]

            return {
                "session_id": session_id,
                "total_checkpoints": len(checkpoints),
                "latest_turn": max(turns),
                "oldest_turn": min(turns),
                "latest_checkpoint_at": max(cp.created_at for cp in checkpoints).isoformat(),
            }

        except Exception:
            logger.exception("Failed to get checkpoint stats")
            raise

    async def close(self) -> None:
        """Close database session if owned."""
        if self._owns_session and self._db_session:
            await self._db_session.close()


# Global service instance
_checkpoint_service: CheckpointService | None = None


def get_checkpoint_service(
    db_session: AsyncSession | None = None,
) -> CheckpointService:
    """Get or create global checkpoint service instance.

    Args:
        db_session: Optional database session

    Returns:
        CheckpointService instance
    """
    global _checkpoint_service

    if db_session:
        # Return new instance with provided session
        return CheckpointService(db_session)

    if _checkpoint_service is None:
        _checkpoint_service = CheckpointService()

    return _checkpoint_service
