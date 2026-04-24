"""Temporal worker for TraceRTM workflows.

Run with: python -m tracertm.workflows.worker
"""

from __future__ import annotations

import asyncio
import logging
import os

from temporalio.client import Client
from temporalio.worker import Worker

from tracertm.workflows import activities, checkpoint_activities, workflows
from tracertm.workflows.agent_execution import AgentExecutionResumeWorkflow, AgentExecutionWorkflow

logger = logging.getLogger(__name__)

# Task queue name for TraceRTM workflows
TASK_QUEUE = os.getenv("TEMPORAL_TASK_QUEUE", "tracertm-tasks")


async def main() -> None:
    """Connect to Temporal server and start worker."""
    # Get Temporal configuration from environment
    temporal_host = os.getenv("TEMPORAL_HOST", "localhost:7233")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE", "default")

    logger.info("Connecting to Temporal at %s (namespace: %s)", temporal_host, temporal_namespace)

    try:
        # Connect to Temporal server
        client = await Client.connect(
            temporal_host,
            namespace=temporal_namespace,
        )

        logger.info("Connected to Temporal server at %s", temporal_host)

        # Create worker with all workflows and activities
        worker = Worker(
            client,
            task_queue=TASK_QUEUE,
            workflows=[
                workflows.IndexingWorkflow,
                workflows.AnalysisWorkflow,
                workflows.GraphSnapshotWorkflow,
                workflows.GraphValidationWorkflow,
                workflows.GraphExportWorkflow,
                workflows.GraphDiffWorkflow,
                workflows.IntegrationSyncWorkflow,
                workflows.IntegrationRetryWorkflow,
                workflows.AgentRunWorkflow,
                # Phase 3: Agent Execution Workflows
                AgentExecutionWorkflow,
                AgentExecutionResumeWorkflow,
                workflows.SandboxSnapshotWorkflow,
                workflows.BulkSnapshotWorkflow,
                workflows.SnapshotCleanupWorkflow,
            ],
            activities=[
                activities.index_repository,
                activities.analyze_quality,
                activities.create_graph_snapshot,
                activities.validate_graph,
                activities.export_graph,
                activities.diff_graph,
                activities.sync_integrations,
                activities.retry_integrations,
                activities.run_agent_turn,
                # Phase 3: Checkpoint Activities
                checkpoint_activities.create_checkpoint,
                checkpoint_activities.load_latest_checkpoint,
                checkpoint_activities.load_checkpoint_by_turn,
                checkpoint_activities.execute_ai_turn,
                checkpoint_activities.create_sandbox_snapshot,
                checkpoint_activities.update_session_snapshot_ref,
                checkpoint_activities.list_active_sessions,
                checkpoint_activities.cleanup_old_snapshots,
            ],
        )

        logger.info("Starting Temporal worker on task queue: %s", TASK_QUEUE)
        logger.info(
            "Registered workflows: IndexingWorkflow, AnalysisWorkflow, GraphSnapshotWorkflow, "
            "GraphValidationWorkflow, GraphExportWorkflow, GraphDiffWorkflow, "
            "IntegrationSyncWorkflow, IntegrationRetryWorkflow, AgentRunWorkflow, "
            "AgentExecutionWorkflow, AgentExecutionResumeWorkflow, SandboxSnapshotWorkflow, "
            "BulkSnapshotWorkflow, SnapshotCleanupWorkflow",
        )
        logger.info(
            "Registered activities: index_repository, analyze_quality, create_graph_snapshot, "
            "validate_graph, export_graph, diff_graph, sync_integrations, retry_integrations, "
            "run_agent_turn, create_checkpoint, load_latest_checkpoint, load_checkpoint_by_turn, "
            "execute_ai_turn, create_sandbox_snapshot, update_session_snapshot_ref, "
            "list_active_sessions, cleanup_old_snapshots",
        )

        # Run worker until interrupted
        await worker.run()

    except Exception:
        logger.exception("Failed to start Temporal worker")
        raise


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    asyncio.run(main())
