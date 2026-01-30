"""Hatchet worker registrations for TraceRTM workflows.

Run with: python -m tracertm.workflows.hatchet_worker
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from pydantic import BaseModel

from tracertm.workflows import tasks

logger = logging.getLogger(__name__)


async def _run_task(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    return await fn(*args, **kwargs)


def _register_hatchet_v1():
    try:
        from hatchet_sdk import Hatchet  # type: ignore
    except Exception as exc:
        logger.warning("Hatchet SDK not available: %s", exc)
        return None

    hatchet = Hatchet()

    class GraphSnapshotInput(BaseModel):
        project_id: str
        graph_id: str
        created_by: str | None = None
        description: str | None = None

    class GraphValidateInput(BaseModel):
        project_id: str
        graph_id: str

    class GraphExportInput(BaseModel):
        project_id: str

    class GraphDiffInput(BaseModel):
        project_id: str
        graph_id: str
        from_version: int
        to_version: int

    class IntegrationSyncInput(BaseModel):
        limit: int = 50

    @hatchet.task(name="graph.snapshot", input_validator=GraphSnapshotInput)
    async def graph_snapshot_task(input: GraphSnapshotInput, context):  # type: ignore[no-redef]
        workflow_run_id = getattr(context, "workflow_run_id", None)
        return await tasks.graph_snapshot_task(
            input.project_id,
            input.graph_id,
            input.created_by,
            input.description,
            workflow_run_id,
        )

    @hatchet.task(name="graph.validate", input_validator=GraphValidateInput)
    async def graph_validation_task(input: GraphValidateInput, context):  # type: ignore[no-redef]
        workflow_run_id = getattr(context, "workflow_run_id", None)
        return await tasks.graph_validation_task(input.project_id, input.graph_id, workflow_run_id)

    @hatchet.task(name="graph.export", input_validator=GraphExportInput)
    async def graph_export_task(input: GraphExportInput, context):  # type: ignore[no-redef]
        workflow_run_id = getattr(context, "workflow_run_id", None)
        return await tasks.graph_export_task(input.project_id, workflow_run_id)

    @hatchet.task(name="graph.diff", input_validator=GraphDiffInput)
    async def graph_diff_task(input: GraphDiffInput, context):  # type: ignore[no-redef]
        workflow_run_id = getattr(context, "workflow_run_id", None)
        return await tasks.graph_diff_task(
            input.project_id,
            input.graph_id,
            input.from_version,
            input.to_version,
            workflow_run_id,
        )

    @hatchet.task(name="integrations.sync", input_validator=IntegrationSyncInput)
    async def integrations_sync_task(input: IntegrationSyncInput, context):  # type: ignore[no-redef]
        workflow_run_id = getattr(context, "workflow_run_id", None)
        return await tasks.integration_sync_task(limit=input.limit, workflow_run_id=workflow_run_id)

    @hatchet.task(name="integrations.retry", input_validator=IntegrationSyncInput)
    async def integrations_retry_task(input: IntegrationSyncInput, context):  # type: ignore[no-redef]
        workflow_run_id = getattr(context, "workflow_run_id", None)
        return await tasks.integration_retry_task(limit=input.limit, workflow_run_id=workflow_run_id)

    worker = hatchet.worker(
        name="tracertm-worker",
        workflows=[
            graph_snapshot_task,
            graph_validation_task,
            graph_export_task,
            graph_diff_task,
            integrations_sync_task,
            integrations_retry_task,
        ],
    )

    return worker


async def main() -> None:
    worker = _register_hatchet_v1()
    if worker is None:
        logger.error("Hatchet worker could not be initialized.")
        return

    start = getattr(worker, "start", None)
    if callable(start):
        await start()
        return

    run = getattr(worker, "run", None)
    if callable(run):
        await run()
        return

    logger.error("Hatchet worker does not expose a start/run method.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
