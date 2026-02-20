"""Tests for agent execution workflow with checkpointing.

Tests workflow execution, checkpoint creation, and session resumability.
"""

import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4

import pytest

from tests.test_constants import COUNT_FIVE, COUNT_FOUR, COUNT_TEN, COUNT_THREE, COUNT_TWO
from tracertm.models.agent_session import AgentSession
from tracertm.services.checkpoint_service import CheckpointService


class TestCheckpointService:
    """Test checkpoint service CRUD operations."""

    @pytest.mark.asyncio
    async def test_create_checkpoint(self, db_session: Any) -> None:
        """Test creating a checkpoint."""
        # Create test session
        session_id = f"test-session-{uuid4()}"
        session = AgentSession(
            session_id=session_id,
            sandbox_root=str(Path(tempfile.gettempdir()) / "sandboxes" / session_id),
        )
        db_session.add(session)
        await db_session.flush()

        # Create checkpoint
        service = CheckpointService(db_session)
        state = {
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"},
            ],
            "model": "claude-sonnet-4-20250514",
        }

        checkpoint = await service.create_checkpoint(
            session_id=session_id,
            turn_number=1,
            state_snapshot=state,
            checkpoint_metadata={"model": "claude-sonnet-4-20250514"},
            description="Test checkpoint",
        )

        assert checkpoint.session_id == session_id
        assert checkpoint.turn_number == 1
        assert checkpoint.state_snapshot == state
        meta = checkpoint.checkpoint_metadata
        assert meta is not None
        assert meta["model"] == "claude-sonnet-4-20250514"
        assert checkpoint.description == "Test checkpoint"
        assert checkpoint.sandbox_snapshot_s3_key is not None

    @pytest.mark.asyncio
    async def test_load_latest_checkpoint(self, db_session: Any) -> None:
        """Test loading the most recent checkpoint."""
        # Create test session
        session_id = f"test-session-{uuid4()}"
        session = AgentSession(
            session_id=session_id,
            sandbox_root=str(Path(tempfile.gettempdir()) / "sandboxes" / session_id),
        )
        db_session.add(session)
        await db_session.flush()

        service = CheckpointService(db_session)

        # Create multiple checkpoints
        for turn in range(1, 4):
            await service.create_checkpoint(
                session_id=session_id,
                turn_number=turn,
                state_snapshot={"messages": [], "turn": turn},
            )

        # Load latest
        latest = await service.load_latest_checkpoint(session_id)

        assert latest is not None
        assert latest.turn_number == COUNT_THREE
        assert latest.state_snapshot["turn"] == COUNT_THREE

    @pytest.mark.asyncio
    async def test_load_checkpoint_by_turn(self, db_session: Any) -> None:
        """Test loading checkpoint for specific turn."""
        # Create test session
        session_id = f"test-session-{uuid4()}"
        session = AgentSession(
            session_id=session_id,
            sandbox_root=str(Path(tempfile.gettempdir()) / "sandboxes" / session_id),
        )
        db_session.add(session)
        await db_session.flush()

        service = CheckpointService(db_session)

        # Create checkpoints
        for turn in range(1, 4):
            await service.create_checkpoint(
                session_id=session_id,
                turn_number=turn,
                state_snapshot={"messages": [], "turn": turn},
            )

        # Load specific turn
        checkpoint = await service.load_checkpoint_by_turn(session_id, 2)

        assert checkpoint is not None
        assert checkpoint.turn_number == COUNT_TWO
        assert checkpoint.state_snapshot["turn"] == COUNT_TWO

    @pytest.mark.asyncio
    async def test_list_checkpoints(self, db_session: Any) -> None:
        """Test listing all checkpoints for a session."""
        # Create test session
        session_id = f"test-session-{uuid4()}"
        session = AgentSession(
            session_id=session_id,
            sandbox_root=str(Path(tempfile.gettempdir()) / "sandboxes" / session_id),
        )
        db_session.add(session)
        await db_session.flush()

        service = CheckpointService(db_session)

        # Create checkpoints
        for turn in range(1, 6):
            await service.create_checkpoint(
                session_id=session_id,
                turn_number=turn,
                state_snapshot={"messages": [], "turn": turn},
            )

        # List checkpoints
        checkpoints = await service.list_checkpoints(session_id, limit=10)

        assert len(checkpoints) == COUNT_FIVE
        # Should be ordered by turn number descending
        assert checkpoints[0].turn_number == COUNT_FIVE
        assert checkpoints[-1].turn_number == 1

    @pytest.mark.asyncio
    async def test_cleanup_old_checkpoints(self, db_session: Any) -> None:
        """Test cleaning up old checkpoints."""
        # Create test session
        session_id = f"test-session-{uuid4()}"
        session = AgentSession(
            session_id=session_id,
            sandbox_root=str(Path(tempfile.gettempdir()) / "sandboxes" / session_id),
        )
        db_session.add(session)
        await db_session.flush()

        service = CheckpointService(db_session)

        # Create 10 checkpoints
        for turn in range(1, 11):
            await service.create_checkpoint(
                session_id=session_id,
                turn_number=turn,
                state_snapshot={"messages": [], "turn": turn},
            )

        # Cleanup, keeping only 3 most recent
        deleted_count = await service.cleanup_old_checkpoints(
            session_id=session_id,
            keep_count=3,
        )

        assert deleted_count == 7

        # Verify only 3 remain
        remaining = await service.list_checkpoints(session_id)
        assert len(remaining) == COUNT_THREE
        assert remaining[0].turn_number == COUNT_TEN
        assert remaining[-1].turn_number == 8

    @pytest.mark.asyncio
    async def test_get_checkpoint_stats(self, db_session: Any) -> None:
        """Test getting checkpoint statistics."""
        # Create test session
        session_id = f"test-session-{uuid4()}"
        session = AgentSession(
            session_id=session_id,
            sandbox_root=str(Path(tempfile.gettempdir()) / "sandboxes" / session_id),
        )
        db_session.add(session)
        await db_session.flush()

        service = CheckpointService(db_session)

        # Create checkpoints
        for turn in [1, 3, 5, 10]:
            await service.create_checkpoint(
                session_id=session_id,
                turn_number=turn,
                state_snapshot={"messages": [], "turn": turn},
            )

        # Get stats
        stats = await service.get_checkpoint_stats(session_id)

        assert stats["session_id"] == session_id
        assert stats["total_checkpoints"] == COUNT_FOUR
        assert stats["latest_turn"] == COUNT_TEN
        assert stats["oldest_turn"] == 1
        assert "latest_checkpoint_at" in stats

    @pytest.mark.asyncio
    async def test_duplicate_checkpoint_raises_error(self, db_session: Any) -> None:
        """Test that creating duplicate checkpoint raises error."""
        # Create test session
        session_id = f"test-session-{uuid4()}"
        session = AgentSession(
            session_id=session_id,
            sandbox_root=str(Path(tempfile.gettempdir()) / "sandboxes" / session_id),
        )
        db_session.add(session)
        await db_session.flush()

        service = CheckpointService(db_session)

        # Create first checkpoint
        await service.create_checkpoint(
            session_id=session_id,
            turn_number=1,
            state_snapshot={"messages": []},
        )

        # Try to create duplicate - should raise ValueError
        with pytest.raises(ValueError, match="already exists"):
            await service.create_checkpoint(
                session_id=session_id,
                turn_number=1,
                state_snapshot={"messages": []},
            )
