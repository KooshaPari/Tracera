"""Temporal activities for TraceRTM workflows.

Activities are the actual work functions that execute within workflows.
They should be idempotent and handle their own error recovery.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from temporalio import activity

from tracertm.workflows import tasks

logger = logging.getLogger(__name__)


@activity.defn(name="index_repository")
async def index_repository(repository_url: str, branch: str = "main") -> dict[str, Any]:
    """Index a repository for code analysis.

    Args:
        repository_url: URL of the repository to index
        branch: Branch to index (default: main)

    Returns:
        dict: Indexing results with status and metadata
    """
    await asyncio.sleep(0)
    activity_info = activity.info()
    logger.info("Activity %s: Indexing repository %s (branch: %s)", activity_info.activity_id, repository_url, branch)

    # Placeholder implementation - replace with actual indexing logic
    return {
        "status": "completed",
        "repository": repository_url,
        "branch": branch,
        "files_indexed": 0,
        "message": "Indexing functionality to be implemented",
    }


@activity.defn(name="analyze_quality")
async def analyze_quality(project_id: str, analysis_type: str = "full") -> dict[str, Any]:
    """Analyze code quality for a project.

    Args:
        project_id: Project ID to analyze
        analysis_type: Type of analysis to perform (default: full)

    Returns:
        dict: Analysis results with metrics and findings
    """
    await asyncio.sleep(0)
    activity_info = activity.info()
    logger.info(
        "Activity %s: Analyzing quality for project %s (type: %s)",
        activity_info.activity_id,
        project_id,
        analysis_type,
    )

    # Placeholder implementation - replace with actual analysis logic
    return {
        "status": "completed",
        "project_id": project_id,
        "analysis_type": analysis_type,
        "quality_score": 0.0,
        "findings": [],
        "message": "Quality analysis functionality to be implemented",
    }


@activity.defn(name="create_graph_snapshot")
async def create_graph_snapshot(
    project_id: str,
    graph_id: str,
    created_by: str | None = None,
    description: str | None = None,
) -> dict[str, Any]:
    """Create a snapshot of the graph state.

    Args:
        project_id: Project ID
        graph_id: Graph ID
        created_by: User creating the snapshot
        description: Optional description

    Returns:
        dict: Snapshot information
    """
    activity_info = activity.info()
    workflow_run_id = activity_info.workflow_run_id

    logger.info("Activity %s: Creating graph snapshot for %s/%s", activity_info.activity_id, project_id, graph_id)

    return await tasks.graph_snapshot_task(
        project_id=project_id,
        graph_id=graph_id,
        created_by=created_by,
        description=description,
        workflow_run_id=workflow_run_id,
    )


@activity.defn(name="validate_graph")
async def validate_graph(project_id: str, graph_id: str) -> dict[str, Any]:
    """Validate graph integrity and consistency.

    Args:
        project_id: Project ID
        graph_id: Graph ID

    Returns:
        dict: Validation results
    """
    activity_info = activity.info()
    workflow_run_id = activity_info.workflow_run_id

    logger.info("Activity %s: Validating graph %s/%s", activity_info.activity_id, project_id, graph_id)

    return await tasks.graph_validation_task(
        project_id=project_id,
        graph_id=graph_id,
        workflow_run_id=workflow_run_id,
    )


@activity.defn(name="export_graph")
async def export_graph(project_id: str) -> dict[str, Any]:
    """Export graph to JSON format.

    Args:
        project_id: Project ID

    Returns:
        dict: Export data
    """
    activity_info = activity.info()
    workflow_run_id = activity_info.workflow_run_id

    logger.info("Activity %s: Exporting graph for project %s", activity_info.activity_id, project_id)

    return await tasks.graph_export_task(
        project_id=project_id,
        workflow_run_id=workflow_run_id,
    )


@activity.defn(name="diff_graph")
async def diff_graph(
    project_id: str,
    graph_id: str,
    from_version: int,
    to_version: int,
) -> dict[str, Any]:
    """Generate diff between two graph versions.

    Args:
        project_id: Project ID
        graph_id: Graph ID
        from_version: Starting version
        to_version: Ending version

    Returns:
        dict: Diff results
    """
    activity_info = activity.info()
    workflow_run_id = activity_info.workflow_run_id

    logger.info(
        "Activity %s: Generating diff for %s/%s v%s..v%s",
        activity_info.activity_id,
        project_id,
        graph_id,
        from_version,
        to_version,
    )

    return await tasks.graph_diff_task(
        project_id=project_id,
        graph_id=graph_id,
        from_version=from_version,
        to_version=to_version,
        workflow_run_id=workflow_run_id,
    )


@activity.defn(name="sync_integrations")
async def sync_integrations(limit: int = 50) -> dict[str, Any]:
    """Process pending integration syncs.

    Args:
        limit: Maximum number of integrations to process

    Returns:
        dict: Sync results
    """
    activity_info = activity.info()
    workflow_run_id = activity_info.workflow_run_id

    logger.info("Activity %s: Processing %s pending integration syncs", activity_info.activity_id, limit)

    return await tasks.integration_sync_task(
        limit=limit,
        workflow_run_id=workflow_run_id,
    )


@activity.defn(name="retry_integrations")
async def retry_integrations(limit: int = 50) -> dict[str, Any]:
    """Retry failed integration syncs.

    Args:
        limit: Maximum number of integrations to retry

    Returns:
        dict: Retry results
    """
    activity_info = activity.info()
    workflow_run_id = activity_info.workflow_run_id

    logger.info("Activity %s: Retrying %s failed integration syncs", activity_info.activity_id, limit)

    return await tasks.integration_retry_task(
        limit=limit,
        workflow_run_id=workflow_run_id,
    )


@activity.defn(name="create_session_checkpoint")
async def create_session_checkpoint(
    session_id: str,
    turn_number: int,
    project_id: str | None = None,
    checkpoint_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a checkpoint for an agent session.

    Args:
        session_id: Session ID
        turn_number: Conversation turn number
        project_id: Optional project ID
        checkpoint_data: Additional checkpoint metadata

    Returns:
        dict: Checkpoint information including S3 key
    """
    import os

    from tracertm.agent.events import AgentEventPublisher
    from tracertm.infrastructure.nats_client import NATSClient

    activity_info = activity.info()
    checkpoint_id = f"{session_id}-t{turn_number}"

    logger.info("Activity %s: Creating checkpoint %s", activity_info.activity_id, checkpoint_id)

    # tracked: https://github.com/KooshaPari/trace/issues/223
    # For now, simulate the checkpoint creation
    s3_key = f"checkpoints/{session_id}/{checkpoint_id}.json"

    result = {
        "checkpoint_id": checkpoint_id,
        "session_id": session_id,
        "turn_number": turn_number,
        "s3_key": s3_key,
        "metadata": checkpoint_data or {},
        "status": "created",
    }

    # Publish checkpoint event
    try:
        nats_url = os.getenv("NATS_URL")
        if nats_url:
            nats_client = NATSClient(url=nats_url)
            await nats_client.connect()
            event_publisher = AgentEventPublisher(nats_client)

            from tracertm.agent.events import SessionCheckpointPayload

            payload = SessionCheckpointPayload(
                checkpoint_id=checkpoint_id,
                turn_number=turn_number,
                s3_key=s3_key,
                metadata=checkpoint_data,
            )
            await event_publisher.publish_session_checkpoint(
                session_id=session_id,
                project_id=project_id,
                payload=payload,
            )

            await nats_client.close()
    except (ConnectionError, OSError, RuntimeError, TimeoutError, ValueError) as e:
        logger.warning("Failed to publish checkpoint event: %s", e)

    return result


@activity.defn(name="run_agent_turn")
async def run_agent_turn(
    session_id: str,
    messages_json: str,
) -> dict[str, Any]:
    """Run one agent turn (resolve sandbox from DB when possible, call AI). Used by AgentRunWorkflow.

    Resolves session sandbox via DB (get_mcp_session) when available so worker can find sessions
    created by the API; falls back to global AgentService (in-memory only) when DB is not configured.
    """
    import json

    activity_info = activity.info()
    logger.info(
        "Activity %s: Agent turn for session %s",
        activity_info.activity_id,
        session_id,
    )
    try:
        from tracertm.agent import AgentService, get_agent_service
        from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider
        from tracertm.agent.session_store import SessionSandboxStoreDB
        from tracertm.services.ai_tools import set_allowed_paths

        path = None
        try:
            from tracertm.mcp.database_adapter import get_mcp_session

            async with get_mcp_session() as db:
                store = SessionSandboxStoreDB(
                    sandbox_provider=LocalFilesystemSandboxProvider(),
                    cache_service=None,
                )
                agent_svc = AgentService(session_store=store)
                path, _ = await agent_svc.get_or_create_session_sandbox(session_id, config=None, db_session=db)
                # path set; commit happens on context exit
        except (ImportError, OSError, RuntimeError, ValueError) as e:
            logger.debug("Agent turn: DB session resolution skipped (%s), using global store", e)
            agent_svc = get_agent_service()
            path, _ = await agent_svc.get_or_create_session_sandbox(session_id)

        if path:
            set_allowed_paths([path])

        messages = json.loads(messages_json) if messages_json else []
        if not isinstance(messages, list):
            messages = []

        from tracertm.services.ai_service import get_ai_service

        ai_svc = get_ai_service()
        reply = await ai_svc.run_chat_turn_with_tools(
            messages=messages,
            model="claude-sonnet-4-20250514",
            system_prompt=None,
            max_tokens=4096,
            working_directory=path,
            db_session=None,
            max_tool_iterations=10,
        )
        messages.append({"role": "assistant", "content": reply})
        return {
            "done": True,
            "messages_json": json.dumps(messages),
            "status": "completed",
            "session_id": session_id,
        }
    except (ImportError, OSError, RuntimeError, TypeError, ValueError) as e:
        logger.exception("run_agent_turn failed")
        return {
            "done": True,
            "messages_json": messages_json,
            "status": "error",
            "session_id": session_id,
            "error": str(e),
        }
