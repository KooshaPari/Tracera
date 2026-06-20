"""BMM workflow MCP tools."""

from __future__ import annotations

import asyncio
from itertools import starmap
from typing import TYPE_CHECKING, Any, cast

from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import Progress
from fastmcp.server.elicitation import AcceptedElicitation
from fastmcp.server.tasks import TaskConfig

from tracertm.mcp.bmm_utils import (
    get_phase_workflows,
    get_project_root,
    get_status_data,
    get_workflow_config,
    load_workflow_status,
    save_workflow_status,
)
from tracertm.mcp.core import mcp
from tracertm.mcp.workflow_executor import run_workflow_with_sub_agent

if TYPE_CHECKING:
    from fastmcp import Context
    from mcp.types import SamplingMessage


@mcp.tool(task=TaskConfig(mode="forbidden"))
async def init_project(ctx: Context, progress: Any = None) -> str:
    """Initialize a new BMM project by determining level, type, and creating workflow path.

    Uses elicitation for interactive user input.
    """
    status = load_workflow_status()
    if status and "project" in status:
        return "OK: Project already initialized"

    if progress is None:
        progress = Progress()

    current_progress = 0
    await progress.set_total(100)
    await progress.set_message("Starting initialization...")

    name_result = await ctx.elicit(
        message="What's your project called?",
        response_type=None,
    )
    data = (
        name_result.data if isinstance(name_result, AcceptedElicitation) and isinstance(name_result.data, dict) else {}
    )
    project_name = data.get("value", "MyProject") if isinstance(name_result, AcceptedElicitation) else "MyProject"

    increment = 25 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 25
    await progress.set_message("Project name set")

    track_result = await ctx.elicit(
        message=f"Select track: {['quick-flow', 'method', 'enterprise']}",
        response_type=None,
    )
    track = track_result.data if isinstance(track_result, AcceptedElicitation) else "method"

    increment = 50 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 50
    await progress.set_message("Track selected")

    field_result = await ctx.elicit(
        message=f"Project type: {['greenfield', 'brownfield']}",
        response_type=None,
    )
    field_type = field_result.data if isinstance(field_result, AcceptedElicitation) else "greenfield"

    increment = 75 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 75
    await progress.set_message("Configuring workflows...")

    increment = 100 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 100
    await progress.set_message("Initialization complete")

    return f"OK: Initialized {project_name} ({track}, {field_type})"


@mcp.tool(task=TaskConfig(mode="forbidden"))
async def run_workflow(
    ctx: Context,
    workflow_id: str,
    auto: bool = False,
    progress: Any = None,
) -> str:
    """Execute a BMM workflow by ID.

    Args:
        workflow_id: Workflow identifier (e.g., 'brainstorm-project', 'prd')
        auto: If True, skip confirmation prompts

    Returns:
        Execution result message
    """
    workflow = get_workflow_config(workflow_id)
    if not workflow:
        msg = f"Workflow not found: {workflow_id}"
        raise ToolError(msg)

    current_status = workflow.get("status", "")
    if isinstance(current_status, str) and current_status.startswith("docs/"):
        return f"OK: Workflow already completed: {workflow_id} -> {current_status}"

    workflow_name = workflow_id.replace("-", " ").title()

    if not auto:
        confirm_result = await ctx.elicit(
            message=f"Run {workflow_name} workflow?\nAgent: {workflow['agent']}\nNote: {workflow.get('note', 'N/A')}\nOptions: {['yes', 'no', 'skip']}",
            response_type=None,
        )
        confirm = confirm_result.data if isinstance(confirm_result, AcceptedElicitation) else "no"
        if confirm == "no":
            return f"CANCELLED: {workflow_id}"
        if confirm == "skip":
            status = load_workflow_status()
            if status is not None:
                for phase_data in status.get("workflow_status", {}).values():  # type: ignore[attr-defined]
                    if workflow_id in phase_data:
                        phase_data[workflow_id]["status"] = "skipped"
                        break
                save_workflow_status(status)
            return f"SKIPPED: {workflow_id}"

    if progress is None:
        progress = Progress()

    current_progress = 0
    await progress.set_total(100)
    await progress.set_message(f"Starting {workflow_id}...")
    increment = 25 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 25
    await progress.set_message("Preparing sub-agent execution...")

    try:
        project_root = get_project_root()
        result = await run_workflow_with_sub_agent(
            project_root=project_root,
            agent_name=workflow["agent"],  # type: ignore[arg-type]
            workflow_command=workflow["command"],  # type: ignore[arg-type]
            workflow_id=workflow_id,
            auto=auto,
        )

        increment = 75 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 75
        await progress.set_message("Updating workflow status...")

        status = load_workflow_status()
        output_path = workflow.get("output", f"docs/{workflow_id}.md")
        if status is not None:
            for phase_data in status.get("workflow_status", {}).values():  # type: ignore[attr-defined]
                if workflow_id in phase_data:
                    phase_data[workflow_id]["status"] = output_path
                    break
            save_workflow_status(status)

        increment = 100 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 100
        await progress.set_message("Complete")

        result_content = result.get("content", "")
        formatted_result = result_content if isinstance(result_content, str) else f"{result_content!s}"

    except Exception:
        increment = 25 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 25
        await progress.set_message("Preparing workflow execution...")

        sampling_msg = cast(
            "SamplingMessage",
            {
                "role": "user",
                "content": (
                    f"Execute this BMM workflow: {workflow['command']}\n\n"
                    "Follow the workflow instructions exactly. Use elicitation for any user input needed."
                ),
            },
        )
        sample_result = await ctx.sample(
            messages=[sampling_msg],
            system_prompt=f"You are the {workflow['agent']} agent. Execute the workflow command provided.",
            model_preferences="claude-sonnet-4.5",
        )

        increment = 75 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 75
        await progress.set_message("Updating workflow status...")

        status = load_workflow_status()
        output_path = workflow.get("output", f"docs/{workflow_id}.md")
        if status is not None:
            for phase_data in status.get("workflow_status", {}).values():  # type: ignore[attr-defined]
                if workflow_id in phase_data:
                    phase_data[workflow_id]["status"] = output_path
                    break
            save_workflow_status(status)

        increment = 100 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 100
        await progress.set_message("Complete")

        result_text = getattr(sample_result, "content", None) or str(sample_result)
        return f"OK: Completed {workflow_id}\nOutput: {output_path}\nResult: {result_text}"
    else:
        return f"OK: Completed {workflow_id}\nOutput: {output_path}\nResult: {formatted_result}"


@mcp.tool(task=TaskConfig(mode="forbidden"))
async def run_phase(
    ctx: Context,
    phase: int,
    parallel: bool = False,
    auto: bool = False,
    progress: Any = None,
) -> str:
    """Execute all workflows in a phase.

    Args:
        phase: Phase number (0=Discovery, 1=Planning, 2=Solutioning, 3=Implementation)
        parallel: If True, run compatible workflows in parallel
        auto: If True, skip confirmation prompts

    Returns:
        Summary of execution results
    """
    if phase not in {0, 1, 2, 3}:
        msg = "Phase must be 0, 1, 2, or 3"
        raise ToolError(msg)

    workflows = get_phase_workflows(phase)
    if not workflows:
        return f"No workflows found for phase {phase}"

    phase_names = ["Discovery", "Planning", "Solutioning", "Implementation"]
    if progress is None:
        progress = Progress()

    current_progress = 0
    await progress.set_total(len(workflows))
    await progress.set_message(f"Starting Phase {phase}: {phase_names[phase]}")

    results: list[str] = []

    if parallel:
        agent_groups: dict[str, list[dict[str, object]]] = {}
        for wf in workflows:
            agent = wf["agent"]
            if agent not in agent_groups:
                agent_groups[agent] = []  # type: ignore[index]
            agent_groups[agent].append(wf)  # type: ignore[index]

        async def run_agent_workflows(
            _agent: str,
            agent_workflows: list[dict[str, object]],
        ) -> list[str]:
            agent_results: list[str] = []
            for wf in agent_workflows:
                wf_id = str(wf["id"])
                result = await run_workflow(ctx, wf_id, auto=auto, progress=progress)  # type: ignore[operator]
                agent_results.append(result)
            return agent_results

        all_results = await asyncio.gather(*list(starmap(run_agent_workflows, agent_groups.items())))

        for agent_results in all_results:
            results.extend(agent_results)
    else:
        for i, wf in enumerate(workflows):
            wf_name = wf["id"].replace("-", " ").title()  # type: ignore[attr-defined]
            increment = i - current_progress
            if increment > 0:
                await progress.increment(increment)
                current_progress = i
            await progress.set_message(f"Running {wf_name}...")
            result = await run_workflow(ctx, wf["id"], auto=auto, progress=progress)  # type: ignore[operator]
            results.append(result)

    increment = len(workflows) - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = len(workflows)
    await progress.set_message("Phase complete")

    return f"OK: Phase {phase} ({phase_names[phase]}) complete\n\n" + "\n".join(results)


@mcp.tool()
async def get_status() -> dict[str, object]:
    """Get comprehensive workflow status including progress, pending workflows, and completion stats.

    Returns:
        Dictionary with status information
    """
    await asyncio.sleep(0)
    return get_status_data()


__all__ = [
    "get_status",
    "init_project",
    "run_phase",
    "run_workflow",
]
