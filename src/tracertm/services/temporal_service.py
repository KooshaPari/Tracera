"""Temporal workflow orchestration service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable
from uuid import uuid4

from temporalio.client import (
    Client,
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleIntervalSpec,
    ScheduleSpec,
)


@dataclass(frozen=True)
class TemporalSettings:
    host: str
    namespace: str
    timeout_seconds: float
    task_queue: str
    ui_url: str


class TemporalService:
    """Service for interacting with Temporal workflows."""

    def __init__(self, settings: TemporalSettings | None = None):
        self.settings = settings or self._load_settings()
        self._client: Client | None = None

    @staticmethod
    def _load_settings() -> TemporalSettings | None:
        """Load Temporal settings from environment variables."""
        host = os.getenv("TEMPORAL_HOST", "localhost:7233")
        namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
        timeout_seconds = float(os.getenv("TEMPORAL_TIMEOUT", "20"))
        task_queue = os.getenv("TEMPORAL_TASK_QUEUE", "tracertm-tasks")
        ui_url = os.getenv("TEMPORAL_UI_URL", "http://localhost:8233")
        return TemporalSettings(
            host=host,
            namespace=namespace,
            timeout_seconds=timeout_seconds,
            task_queue=task_queue,
            ui_url=ui_url,
        )

    def enabled(self) -> bool:
        """Check if Temporal is configured and enabled."""
        return self.settings is not None

    async def get_client(self) -> Client:
        """Get or create Temporal client.

        Returns:
            Temporal client instance
        """
        if self._client is None and self.settings:
            self._client = await Client.connect(
                self.settings.host,
                namespace=self.settings.namespace,
            )
        if self._client is None:
            raise RuntimeError("Temporal client not initialized")
        return self._client

    async def health_check(self) -> dict[str, Any]:
        """Check Temporal connection health.

        Returns:
            dict: Health status information
        """
        if not self.settings:
            return {"enabled": False, "status": "missing_configuration"}

        try:
            client = await self.get_client()
            # Access the namespace property as a health check
            # (namespace is a property, not a method)
            _ = client.namespace
            return {
                "enabled": True,
                "status": "ready",
                "host": self.settings.host,
                "namespace": self.settings.namespace,
                "task_queue": self.settings.task_queue,
                "ui_url": self.settings.ui_url,
            }
        except Exception as exc:
            return {
                "enabled": True,
                "status": "error",
                "error": str(exc),
            }

    async def start_workflow(
        self,
        workflow_name: str,
        workflow_id: str | None = None,
        task_queue: str | None = None,
        **workflow_args: Any,
    ) -> dict[str, Any]:
        """Start a Temporal workflow.

        Args:
            workflow_name: Name of the workflow to start
            workflow_id: Optional workflow ID (auto-generated if not provided)
            task_queue: Task queue name (uses TEMPORAL_TASK_QUEUE env var if not provided)
            **workflow_args: Workflow input parameters

        Returns:
            dict: Workflow execution information
        """
        if not self.settings:
            raise ValueError("Temporal not configured")

        client = await self.get_client()

        # Use configured task queue if not provided
        if not task_queue:
            task_queue = self.settings.task_queue

        # Generate workflow ID if not provided
        if not workflow_id:
            workflow_id = f"{workflow_name}-{uuid4()}"

        # Map workflow names to workflow classes
        from tracertm.workflows.workflows import (
            AgentExecutionResumeWorkflow,
            AgentExecutionWorkflow,
            AgentRunWorkflow,
            AnalysisWorkflow,
            BulkSnapshotWorkflow,
            GraphDiffWorkflow,
            GraphExportWorkflow,
            GraphSnapshotWorkflow,
            GraphValidationWorkflow,
            IndexingWorkflow,
            IntegrationRetryWorkflow,
            IntegrationSyncWorkflow,
            SandboxSnapshotWorkflow,
            SnapshotCleanupWorkflow,
        )

        workflow_map = {
            "AgentRunWorkflow": AgentRunWorkflow,
            "AgentExecutionWorkflow": AgentExecutionWorkflow,
            "AgentExecutionResumeWorkflow": AgentExecutionResumeWorkflow,
            "SandboxSnapshotWorkflow": SandboxSnapshotWorkflow,
            "BulkSnapshotWorkflow": BulkSnapshotWorkflow,
            "SnapshotCleanupWorkflow": SnapshotCleanupWorkflow,
            "IndexingWorkflow": IndexingWorkflow,
            "AnalysisWorkflow": AnalysisWorkflow,
            "GraphSnapshotWorkflow": GraphSnapshotWorkflow,
            "GraphValidationWorkflow": GraphValidationWorkflow,
            "GraphExportWorkflow": GraphExportWorkflow,
            "GraphDiffWorkflow": GraphDiffWorkflow,
            "IntegrationSyncWorkflow": IntegrationSyncWorkflow,
            "IntegrationRetryWorkflow": IntegrationRetryWorkflow,
        }

        workflow_class = workflow_map.get(workflow_name)
        if not workflow_class:
            raise ValueError(f"Unknown workflow: {workflow_name}")

        # Start workflow execution
        # Type ignore: workflow classes have @workflow.run decorated methods which type checker can't infer
        handle = await client.start_workflow(
            workflow_class.run,  # type: ignore[attr-defined]
            **workflow_args,
            id=workflow_id,
            task_queue=task_queue,
        )

        return {
            "workflow_id": handle.id,
            "workflow_name": workflow_name,
            "run_id": handle.result_run_id,
            "status": "started",
        }

    def _build_schedule_action(
        self,
        workflow_name: str,
        args: Iterable[Any],
        task_queue: str | None = None,
        workflow_id: str | None = None,
    ) -> ScheduleActionStartWorkflow:
        if not self.settings:
            raise ValueError("Temporal not configured")

        return ScheduleActionStartWorkflow(
            workflow_name,
            args=list(args),
            id=workflow_id,
            task_queue=task_queue or self.settings.task_queue,
        )

    async def create_schedule(
        self,
        schedule_id: str,
        workflow_name: str,
        args: Iterable[Any],
        cron_expressions: list[str] | None = None,
        interval_seconds: int | None = None,
        timezone: str | None = None,
        trigger_immediately: bool = False,
        task_queue: str | None = None,
        workflow_id: str | None = None,
        start_at: datetime | None = None,
        end_at: datetime | None = None,
    ) -> dict[str, Any]:
        if not self.settings:
            raise ValueError("Temporal not configured")

        client = await self.get_client()
        if not cron_expressions and interval_seconds is None:
            raise ValueError("Schedule must include cron expressions or interval seconds")

        intervals: list[ScheduleIntervalSpec] = []
        if interval_seconds is not None:
            intervals.append(ScheduleIntervalSpec(every=timedelta(seconds=interval_seconds)))

        spec = ScheduleSpec(
            cron_expressions=cron_expressions or [],
            intervals=intervals,
            time_zone_name=timezone,
            start_at=start_at,
            end_at=end_at,
        )

        action = self._build_schedule_action(
            workflow_name,
            args=args,
            task_queue=task_queue,
            workflow_id=workflow_id,
        )

        schedule = Schedule(action=action, spec=spec)
        await client.create_schedule(
            schedule_id,
            schedule,
            trigger_immediately=trigger_immediately,
        )

        return {
            "schedule_id": schedule_id,
            "workflow_name": workflow_name,
            "task_queue": task_queue or self.settings.task_queue,
            "cron_expressions": cron_expressions or [],
            "interval_seconds": interval_seconds,
            "timezone": timezone,
            "status": "created",
        }

    async def delete_schedule(self, schedule_id: str) -> None:
        if not self.settings:
            raise ValueError("Temporal not configured")
        client = await self.get_client()
        handle = client.get_schedule_handle(schedule_id)
        await handle.delete()

    async def list_schedules(self, query: str | None = None) -> list[dict[str, Any]]:
        if not self.settings:
            raise ValueError("Temporal not configured")
        client = await self.get_client()
        schedules: list[dict[str, Any]] = []
        async for schedule in client.list_schedules(query=query):
            schedules.append(
                {
                    "id": schedule.id,
                    "memo": schedule.memo,
                }
            )
        return schedules

    async def list_schedules_summary(self, limit: int = 200) -> dict[str, Any]:
        if not self.settings:
            raise ValueError("Temporal not configured")
        client = await self.get_client()
        schedules: list[dict[str, Any]] = []
        count = 0
        async for schedule in client.list_schedules():
            schedules.append({"id": schedule.id})
            count += 1
            if count >= limit:
                break
        return {"count": count, "items": schedules}

    async def list_workflows_summary(self, limit: int = 100) -> dict[str, Any]:
        if not self.settings:
            raise ValueError("Temporal not configured")
        client = await self.get_client()
        status_counts: dict[str, int] = {}
        workflows: list[dict[str, Any]] = []
        async for wf in client.list_workflows(limit=limit):
            status = wf.status.name if wf.status else "UNKNOWN"
            status_counts[status] = status_counts.get(status, 0) + 1
            workflows.append(
                {
                    "id": wf.id,
                    "run_id": wf.run_id,
                    "workflow_type": wf.workflow_type,
                    "status": status,
                    "task_queue": wf.task_queue,
                    "start_time": wf.start_time.isoformat(),
                    "close_time": wf.close_time.isoformat() if wf.close_time else None,
                }
            )
        return {"counts": status_counts, "items": workflows}

    async def get_summary(self, workflow_limit: int = 100, schedule_limit: int = 200) -> dict[str, Any]:
        health = await self.health_check()
        schedules = await self.list_schedules_summary(limit=schedule_limit)
        workflows = await self.list_workflows_summary(limit=workflow_limit)
        return {
            "health": health,
            "schedules": schedules,
            "workflows": workflows,
            "task_queue": self.settings.task_queue if self.settings else None,
            "ui_url": self.settings.ui_url if self.settings else None,
        }

    async def get_workflow_result(self, workflow_id: str) -> dict[str, Any]:
        """Get the result of a workflow execution.

        Args:
            workflow_id: Workflow ID to query

        Returns:
            dict: Workflow result
        """
        if not self.settings:
            raise ValueError("Temporal not configured")

        client = await self.get_client()

        # Get workflow handle
        handle = client.get_workflow_handle(workflow_id)

        # Get workflow description for status
        description = await handle.describe()

        # Extract status safely with null checks
        status_name = "unknown"
        if description.status and hasattr(description.status, 'name') and description.status.name:
            status_name = description.status.name.lower()

        result: dict[str, Any] = {
            "workflow_id": workflow_id,
            "status": status_name,
        }

        # If workflow is completed, get the result
        if description.status and hasattr(description.status, 'name') and description.status.name == "COMPLETED":
            workflow_result = await handle.result()
            result["result"] = workflow_result

        return result

    async def close(self) -> None:
        """Close the Temporal client connection.

        Note: Temporal Python SDK 1.19.0+ does not require explicit client closure.
        The client will be automatically cleaned up when the object is destroyed.
        This method is kept for API compatibility but is now a no-op.
        """
        # In Temporal SDK 1.19.0+, client.close() has been removed
        # The client is automatically cleaned up by the SDK
        self._client = None
