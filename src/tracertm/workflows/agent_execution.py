"""Temporal workflow for durable agent execution with checkpointing.

This workflow orchestrates long-running agent conversations with automatic
checkpoint creation every N turns, enabling session resumability and
durability across workflow restarts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.exceptions import TemporalError

# Import activity functions for workflow execution
with workflow.unsafe.imports_passed_through():
    from tracertm.workflows import checkpoint_activities

logger = logging.getLogger(__name__)


@dataclass
class AgentRunConfig:
    """Configuration for agent execution."""

    max_turns: int = 50
    checkpoint_interval: int = 5
    model: str = "claude-sonnet-4-20250514"
    system_prompt: str | None = None


@workflow.defn(name="AgentExecutionWorkflow")
class AgentExecutionWorkflow:
    """Durable agent execution workflow with automatic checkpointing.

    Features:
    - Checkpoint creation every 5 conversation turns
    - Heartbeat monitoring with 30-second timeout
    - Automatic retry on transient failures
    - Session state persistence for resumability
    - MinIO snapshot integration (prepared for Phase 4)
    """

    # Workflow state (persisted across restarts)
    _turn_count: int
    _session_id: str
    _last_checkpoint_turn: int

    def __init__(self) -> None:
        """Initialize workflow state."""
        self._turn_count = 0
        self._session_id = ""
        self._last_checkpoint_turn = 0

    @workflow.run
    async def run(
        self,
        session_id: str,
        initial_messages: list[dict[str, Any]] | None = None,
        config: AgentRunConfig | None = None,
    ) -> dict[str, Any]:
        """Execute agent with automatic checkpointing.

        Args:
            session_id: Agent session ID (must exist in database)
            initial_messages: Starting conversation messages (or resume from checkpoint)
            config: Agent run configuration

        Returns:
            dict: Execution summary with final state and checkpoint info
        """
        cfg = config or AgentRunConfig()
        self._session_id = session_id
        self._turn_count = 0
        self._last_checkpoint_turn = 0

        workflow.logger.info(
            "Starting agent execution for session %s (max_turns=%s, checkpoint_interval=%s)",
            session_id,
            cfg.max_turns,
            cfg.checkpoint_interval,
        )

        # Initialize conversation state
        messages = initial_messages or []
        conversation_state = {
            "messages": messages,
            "session_id": session_id,
            "model": cfg.model,
            "system_prompt": cfg.system_prompt,
        }

        # Try to resume from latest checkpoint if no initial messages provided
        if not initial_messages:
            try:
                checkpoint_data = await workflow.execute_activity(
                    checkpoint_activities.load_latest_checkpoint,
                    args=[session_id],
                    start_to_close_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        maximum_attempts=2,
                        initial_interval=timedelta(seconds=1),
                        maximum_interval=timedelta(seconds=5),
                        backoff_coefficient=2.0,
                    ),
                )

                if checkpoint_data and checkpoint_data.get("state_snapshot"):
                    conversation_state = checkpoint_data["state_snapshot"]
                    self._last_checkpoint_turn = checkpoint_data.get("turn_number", 0)
                    self._turn_count = self._last_checkpoint_turn
                    workflow.logger.info("Resumed from checkpoint at turn %s", self._last_checkpoint_turn)
            except (KeyError, TemporalError, TypeError, ValueError) as e:
                workflow.logger.warning("Failed to load checkpoint, starting fresh: %s", e)

        # Main conversation loop
        for turn in range(self._turn_count, cfg.max_turns):
            self._turn_count = turn + 1

            # Execute AI turn with tools
            try:
                turn_result = await workflow.execute_activity(
                    checkpoint_activities.execute_ai_turn,
                    args=[
                        session_id,
                        conversation_state["messages"],
                        cfg.model,
                        cfg.system_prompt,
                    ],
                    start_to_close_timeout=timedelta(minutes=5),
                    heartbeat_timeout=timedelta(seconds=30),
                    retry_policy=RetryPolicy(
                        maximum_attempts=3,
                        initial_interval=timedelta(seconds=2),
                        maximum_interval=timedelta(seconds=30),
                        backoff_coefficient=2.0,
                        non_retryable_error_types=["ValueError", "PermissionError"],
                    ),
                )

                # Update conversation state
                conversation_state["messages"] = turn_result.get("messages", [])
                conversation_state["last_turn_metadata"] = turn_result.get("metadata", {})

                # Check if conversation is complete
                if turn_result.get("done", False):
                    workflow.logger.info("Conversation completed at turn %s", self._turn_count)
                    # Create final checkpoint
                    await self._create_checkpoint(conversation_state)
                    return {
                        "status": "completed",
                        "session_id": session_id,
                        "turns": self._turn_count,
                        "final_state": conversation_state,
                        "reason": "conversation_complete",
                    }

            except (KeyError, TemporalError, TypeError, ValueError) as e:
                workflow.logger.error("Turn %s failed: %s", self._turn_count, e)
                # Create checkpoint on error for recovery
                await self._create_checkpoint(conversation_state, error=str(e))
                msg = f"Turn {self._turn_count} failed"
                raise RuntimeError(msg) from e

            # Create checkpoint at intervals
            if (self._turn_count - self._last_checkpoint_turn) >= cfg.checkpoint_interval:
                await self._create_checkpoint(conversation_state)

        # Max turns reached
        workflow.logger.info("Agent execution hit max_turns (%s)", cfg.max_turns)
        await self._create_checkpoint(conversation_state)
        return {
            "status": "max_turns_reached",
            "session_id": session_id,
            "turns": self._turn_count,
            "final_state": conversation_state,
            "reason": "max_turns",
        }

    async def _create_checkpoint(
        self,
        conversation_state: dict[str, Any],
        error: str | None = None,
    ) -> dict[str, Any]:
        """Create checkpoint with current conversation state.

        Args:
            conversation_state: Current conversation state to save
            error: Optional error message if checkpoint created due to failure

        Returns:
            dict: Checkpoint creation result
        """
        try:
            checkpoint_metadata = {
                "turn_count": self._turn_count,
                "workflow_id": workflow.info().workflow_id,
                "workflow_run_id": workflow.info().run_id,
                "checkpoint_reason": "error" if error else "interval",
            }

            if error:
                checkpoint_metadata["error"] = error

            result = await workflow.execute_activity(
                checkpoint_activities.create_checkpoint,
                args=[
                    self._session_id,
                    self._turn_count,
                    conversation_state,
                    checkpoint_metadata,
                ],
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=RetryPolicy(
                    maximum_attempts=3,
                    initial_interval=timedelta(seconds=1),
                    maximum_interval=timedelta(seconds=10),
                    backoff_coefficient=2.0,
                ),
            )

            self._last_checkpoint_turn = self._turn_count
            workflow.logger.info("Checkpoint created at turn %s: %s", self._turn_count, result.get("checkpoint_id"))

        except (KeyError, TemporalError, TypeError, ValueError) as e:
            workflow.logger.error("Failed to create checkpoint: %s", e)
            # Don't fail workflow on checkpoint errors
            return {"status": "failed", "error": str(e)}
        else:
            checkpoint_result: dict[str, Any] = result
            return checkpoint_result


@workflow.defn(name="AgentExecutionResumeWorkflow")
class AgentExecutionResumeWorkflow:
    """Resume agent execution from a specific checkpoint.

    Use this workflow to continue a previously interrupted agent session
    from a saved checkpoint point.
    """

    @workflow.run
    async def run(
        self,
        session_id: str,
        checkpoint_turn: int | None = None,
        max_additional_turns: int = 25,
        checkpoint_interval: int = 5,
    ) -> dict[str, Any]:
        """Resume execution from checkpoint.

        Args:
            session_id: Agent session ID
            checkpoint_turn: Specific checkpoint turn to resume from (or latest if None)
            max_additional_turns: Maximum additional turns from resume point
            checkpoint_interval: Checkpoint creation interval

        Returns:
            dict: Execution summary
        """
        workflow.logger.info(
            "Resuming agent execution for session %s from turn %s",
            session_id,
            checkpoint_turn or "latest",
        )

        # Load checkpoint
        if checkpoint_turn is not None:
            checkpoint_data = await workflow.execute_activity(
                checkpoint_activities.load_checkpoint_by_turn,
                args=[session_id, checkpoint_turn],
                start_to_close_timeout=timedelta(seconds=30),
            )
        else:
            checkpoint_data = await workflow.execute_activity(
                checkpoint_activities.load_latest_checkpoint,
                args=[session_id],
                start_to_close_timeout=timedelta(seconds=30),
            )

        if not checkpoint_data:
            msg = f"No checkpoint found for session {session_id}"
            raise ValueError(msg)

        # Resume execution using main workflow
        state = checkpoint_data.get("state_snapshot") or {}
        config = AgentRunConfig(
            max_turns=checkpoint_data.get("turn_number", 0) + max_additional_turns,
            checkpoint_interval=checkpoint_interval,
            model=state.get("model", "claude-sonnet-4-20250514"),
            system_prompt=state.get("system_prompt"),
        )
        return await AgentExecutionWorkflow().run(
            session_id=session_id,
            initial_messages=state.get("messages", []),
            config=config,
        )
