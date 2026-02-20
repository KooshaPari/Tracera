"""Temporal workflows for TraceRTM.

Workflows orchestrate activities and define the business logic.
They are durable and can run for long periods, surviving server restarts.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Any, cast

from temporalio import common as temporalio_common
from temporalio import workflow

# RetryPolicy lives in temporalio.common, not temporalio.workflow (type checker)
RetryPolicy = temporalio_common.RetryPolicy

# Import activity functions - note we import them as types for workflow execution
with workflow.unsafe.imports_passed_through():
    from tracertm.workflows import activities

# Import agent execution workflows


@workflow.defn(name="IndexingWorkflow")
class IndexingWorkflow:
    """Workflow for indexing repositories."""

    @workflow.run
    async def run(self, repository_url: str, branch: str = "main") -> dict[str, Any]:
        """Execute the indexing workflow.

        Args:
            repository_url: URL of the repository to index
            branch: Branch to index (default: main)

        Returns:
            dict: Indexing results
        """
        workflow.logger.info("Starting indexing workflow for %s (branch: %s)", repository_url, branch)

        # Execute indexing activity with timeout and retry policy
        result: dict[str, Any] = await workflow.execute_activity(
            activities.index_repository,
            args=[repository_url, branch],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Indexing workflow completed: %s", result.get("status"))
        return result


@workflow.defn(name="AnalysisWorkflow")
class AnalysisWorkflow:
    """Workflow for quality analysis."""

    @workflow.run
    async def run(self, project_id: str, analysis_type: str = "full") -> dict[str, Any]:
        """Execute the analysis workflow.

        Args:
            project_id: Project ID to analyze
            analysis_type: Type of analysis to perform

        Returns:
            dict: Analysis results
        """
        workflow.logger.info("Starting analysis workflow for project %s (type: %s)", project_id, analysis_type)

        # Execute analysis activity with timeout and retry policy
        result: dict[str, Any] = await workflow.execute_activity(
            activities.analyze_quality,
            args=[project_id, analysis_type],
            start_to_close_timeout=timedelta(minutes=20),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Analysis workflow completed: %s", result.get("status"))
        return result


@workflow.defn(name="GraphSnapshotWorkflow")
class GraphSnapshotWorkflow:
    """Workflow for creating graph snapshots."""

    @workflow.run
    async def run(
        self,
        project_id: str,
        graph_id: str,
        created_by: str | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        """Execute the graph snapshot workflow.

        Args:
            project_id: Project ID
            graph_id: Graph ID
            created_by: User creating the snapshot
            description: Optional description

        Returns:
            dict: Snapshot information
        """
        workflow.logger.info("Creating snapshot for graph %s/%s", project_id, graph_id)

        result: dict[str, Any] = await workflow.execute_activity(
            activities.create_graph_snapshot,
            args=[project_id, graph_id, created_by, description],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Snapshot created: version %s", result.get("version"))
        return result


@workflow.defn(name="GraphValidationWorkflow")
class GraphValidationWorkflow:
    """Workflow for validating graphs."""

    @workflow.run
    async def run(self, project_id: str, graph_id: str) -> dict[str, Any]:
        """Execute the graph validation workflow.

        Args:
            project_id: Project ID
            graph_id: Graph ID

        Returns:
            dict: Validation results
        """
        workflow.logger.info("Validating graph %s/%s", project_id, graph_id)

        result: dict[str, Any] = await workflow.execute_activity(
            activities.validate_graph,
            args=[project_id, graph_id],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Validation completed: %s", result)
        return result


@workflow.defn(name="GraphExportWorkflow")
class GraphExportWorkflow:
    """Workflow for exporting graphs."""

    @workflow.run
    async def run(self, project_id: str) -> dict[str, Any]:
        """Execute the graph export workflow.

        Args:
            project_id: Project ID

        Returns:
            dict: Export data
        """
        workflow.logger.info("Exporting graph for project %s", project_id)

        result: dict[str, Any] = await workflow.execute_activity(
            activities.export_graph,
            args=[project_id],
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Export completed: %s", result.get("format"))
        return result


@workflow.defn(name="GraphDiffWorkflow")
class GraphDiffWorkflow:
    """Workflow for generating graph diffs."""

    @workflow.run
    async def run(
        self,
        project_id: str,
        graph_id: str,
        from_version: int,
        to_version: int,
    ) -> dict[str, Any]:
        """Execute the graph diff workflow.

        Args:
            project_id: Project ID
            graph_id: Graph ID
            from_version: Starting version
            to_version: Ending version

        Returns:
            dict: Diff results
        """
        workflow.logger.info("Generating diff for %s/%s v%s..v%s", project_id, graph_id, from_version, to_version)

        result: dict[str, Any] = await workflow.execute_activity(
            activities.diff_graph,
            args=[project_id, graph_id, from_version, to_version],
            start_to_close_timeout=timedelta(minutes=10),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Diff completed")
        return result


@workflow.defn(name="IntegrationSyncWorkflow")
class IntegrationSyncWorkflow:
    """Workflow for processing integration syncs."""

    @workflow.run
    async def run(self, limit: int = 50) -> dict[str, Any]:
        """Execute the integration sync workflow.

        Args:
            limit: Maximum number of integrations to process

        Returns:
            dict: Sync results
        """
        workflow.logger.info("Processing %s pending integration syncs", limit)

        result: dict[str, Any] = await workflow.execute_activity(
            activities.sync_integrations,
            args=[limit],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Sync completed: %s", result)
        return result


@workflow.defn(name="IntegrationRetryWorkflow")
class IntegrationRetryWorkflow:
    """Workflow for retrying failed integration syncs."""

    @workflow.run
    async def run(self, limit: int = 50) -> dict[str, Any]:
        """Execute the integration retry workflow.

        Args:
            limit: Maximum number of integrations to retry

        Returns:
            dict: Retry results
        """
        workflow.logger.info("Retrying %s failed integration syncs", limit)

        result: dict[str, Any] = await workflow.execute_activity(
            activities.retry_integrations,
            args=[limit],
            start_to_close_timeout=timedelta(minutes=30),
            retry_policy=RetryPolicy(
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=10),
                backoff_coefficient=2.0,
            ),
        )

        workflow.logger.info("Retry completed: %s", result)
        return result


@workflow.defn(name="AgentRunWorkflow")
class AgentRunWorkflow:
    """Durable agent run with checkpointing: each turn is an activity, workflow state survives restarts.

    Use for long-running or resumable agent sessions. Input: session_id, optional message history
    pointer; each turn runs as an activity so Temporal persists state between turns.
    """

    @workflow.run
    async def run(
        self,
        session_id: str,
        initial_messages_json: str | None = None,
        max_turns: int = 10,
    ) -> dict[str, Any]:
        """Execute agent run with checkpointing.

        Args:
            session_id: Agent session ID (sandbox path resolved in activity).
            initial_messages_json: Optional JSON list of messages to start from.
            max_turns: Maximum tool/response turns.

        Returns:
            dict: Final status and output summary.
        """
        workflow.logger.info("Starting agent run for session %s (max_turns=%s)", session_id, max_turns)
        messages = initial_messages_json or "[]"
        for turn in range(max_turns):
            result: dict[str, Any] = await workflow.execute_activity(
                activities.run_agent_turn,
                args=[session_id, messages],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(
                    maximum_attempts=2,
                    initial_interval=timedelta(seconds=2),
                    maximum_interval=timedelta(seconds=30),
                    backoff_coefficient=2.0,
                ),
            )
            messages = result.get("messages_json", messages)
            if result.get("done", False):
                workflow.logger.info("Agent run completed at turn %s", turn + 1)
                return result
        workflow.logger.info("Agent run hit max_turns")
        return {"status": "max_turns", "session_id": session_id, "turns": max_turns}


# Re-export sandbox workflows so worker can use workflows.SnapshotCleanupWorkflow etc.
from tracertm.workflows.sandbox_snapshot import (  # noqa: E402
    BulkSnapshotWorkflow,
    SandboxSnapshotWorkflow,
    SnapshotCleanupWorkflow,
)

__all__ = [
    "AgentRunWorkflow",
    "AnalysisWorkflow",
    "BulkSnapshotWorkflow",
    "GraphDiffWorkflow",
    "GraphExportWorkflow",
    "GraphSnapshotWorkflow",
    "GraphValidationWorkflow",
    "IndexingWorkflow",
    "IntegrationRetryWorkflow",
    "IntegrationSyncWorkflow",
    "SandboxSnapshotWorkflow",
    "SnapshotCleanupWorkflow",
]
