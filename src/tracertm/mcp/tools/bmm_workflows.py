"""
BMM workflow MCP tools.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastmcp import Context
from fastmcp.exceptions import ToolError
from fastmcp.server.dependencies import Progress
from fastmcp.server.tasks import TaskConfig

from tracertm.mcp.core import mcp
from tracertm.mcp.bmm_utils import (
    get_project_root,
    load_workflow_status,
    save_workflow_status,
    get_workflow_config,
    get_phase_workflows,
    get_next_pending_workflow,
)
from tracertm.mcp.workflow_executor import run_workflow_with_sub_agent


@mcp.tool(task=TaskConfig(mode="forbidden"))
async def init_project(ctx: Context, progress: Progress = Progress()) -> str:
    """
    Initialize a new BMM project by determining level, type, and creating workflow path.
    Uses elicitation for interactive user input.
    """
    status = load_workflow_status()
    if status and 'project' in status:
        return "OK: Project already initialized"

    current_progress = 0
    await progress.set_total(100)
    await progress.set_message("Starting initialization...")

    project_name = await ctx.elicit(
        prompt="What's your project called?",
        default="MyProject",
    )

    increment = 25 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 25
    await progress.set_message("Project name set")

    track = await ctx.elicit(
        prompt="Select track:",
        options=["quick-flow", "method", "enterprise"],
    )

    increment = 50 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 50
    await progress.set_message("Track selected")

    field_type = await ctx.elicit(
        prompt="Project type:",
        options=["greenfield", "brownfield"],
    )

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
    progress: Progress = Progress(),
) -> str:
    """
    Execute a BMM workflow by ID.

    Args:
        workflow_id: Workflow identifier (e.g., 'brainstorm-project', 'prd')
        auto: If True, skip confirmation prompts

    Returns:
        Execution result message
    """
    workflow = get_workflow_config(workflow_id)
    if not workflow:
        raise ToolError(f"Workflow not found: {workflow_id}")

    current_status = workflow.get('status', '')
    if isinstance(current_status, str) and current_status.startswith('docs/'):
        return f"OK: Workflow already completed: {workflow_id} -> {current_status}"

    workflow_name = workflow_id.replace('-', ' ').title()

    if not auto:
        confirm = await ctx.elicit(
            prompt=f"Run {workflow_name} workflow?\nAgent: {workflow['agent']}\nNote: {workflow.get('note', 'N/A')}",
            options=["yes", "no", "skip"],
        )
        if confirm == "no":
            return f"CANCELLED: {workflow_id}"
        if confirm == "skip":
            status = load_workflow_status()
            for phase_key, phase_data in status.get('workflow_status', {}).items():
                if workflow_id in phase_data:
                    phase_data[workflow_id]['status'] = 'skipped'
                    break
            save_workflow_status(status)
            return f"SKIPPED: {workflow_id}"

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
            agent_name=workflow['agent'],
            workflow_command=workflow['command'],
            workflow_id=workflow_id,
            auto=auto,
        )

        increment = 75 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 75
        await progress.set_message("Updating workflow status...")

        status = load_workflow_status()
        output_path = workflow.get('output', f"docs/{workflow_id}.md")
        for phase_key, phase_data in status.get('workflow_status', {}).items():
            if workflow_id in phase_data:
                phase_data[workflow_id]['status'] = output_path
                break
        save_workflow_status(status)

        increment = 100 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 100
        await progress.set_message("Complete")

        result_content = result.get('content', '')
        if isinstance(result_content, str):
            return f"OK: Completed {workflow_id}\nOutput: {output_path}\nResult: {result_content}"
        return f"OK: Completed {workflow_id}\nOutput: {output_path}\nResult: {str(result_content)}"

    except Exception:
        increment = 25 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 25
        await progress.set_message("Preparing workflow execution...")

        result = await ctx.sample(
            messages=[{
                "role": "user",
                "content": (
                    f"Execute this BMM workflow: {workflow['command']}\n\n"
                    "Follow the workflow instructions exactly. Use elicitation for any user input needed."
                ),
            }],
            system_prompt=f"You are the {workflow['agent']} agent. Execute the workflow command provided.",
            model_preferences={
                "hints": [{"name": "claude-sonnet-4.5"}],
            },
        )

        increment = 75 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 75
        await progress.set_message("Updating workflow status...")

        status = load_workflow_status()
        output_path = workflow.get('output', f"docs/{workflow_id}.md")
        for phase_key, phase_data in status.get('workflow_status', {}).items():
            if workflow_id in phase_data:
                phase_data[workflow_id]['status'] = output_path
                break
        save_workflow_status(status)

        increment = 100 - current_progress
        if increment > 0:
            await progress.increment(increment)
            current_progress = 100
        await progress.set_message("Complete")

        return f"OK: Completed {workflow_id}\nOutput: {output_path}\nResult: {result.content}"


@mcp.tool(task=TaskConfig(mode="forbidden"))
async def run_phase(
    ctx: Context,
    phase: int,
    parallel: bool = False,
    auto: bool = False,
    progress: Progress = Progress(),
) -> str:
    """
    Execute all workflows in a phase.

    Args:
        phase: Phase number (0=Discovery, 1=Planning, 2=Solutioning, 3=Implementation)
        parallel: If True, run compatible workflows in parallel
        auto: If True, skip confirmation prompts

    Returns:
        Summary of execution results
    """
    if phase not in [0, 1, 2, 3]:
        raise ToolError("Phase must be 0, 1, 2, or 3")

    workflows = get_phase_workflows(phase)
    if not workflows:
        return f"No workflows found for phase {phase}"

    phase_names = ["Discovery", "Planning", "Solutioning", "Implementation"]
    current_progress = 0
    await progress.set_total(len(workflows))
    await progress.set_message(f"Starting Phase {phase}: {phase_names[phase]}")

    results: List[str] = []

    if parallel:
        agent_groups: Dict[str, List[Dict[str, Any]]] = {}
        for wf in workflows:
            agent = wf['agent']
            if agent not in agent_groups:
                agent_groups[agent] = []
            agent_groups[agent].append(wf)

        async def run_agent_workflows(agent: str, agent_workflows: List[Dict[str, Any]]):
            agent_results = []
            for wf in agent_workflows:
                result = await run_workflow(ctx, wf['id'], auto=auto, progress=progress)
                agent_results.append(result)
            return agent_results

        all_results = await asyncio.gather(*[
            run_agent_workflows(agent, wfs)
            for agent, wfs in agent_groups.items()
        ])

        for agent_results in all_results:
            results.extend(agent_results)
    else:
        for i, wf in enumerate(workflows):
            wf_name = wf['id'].replace('-', ' ').title()
            increment = i - current_progress
            if increment > 0:
                await progress.increment(increment)
                current_progress = i
            await progress.set_message(f"Running {wf_name}...")
            result = await run_workflow(ctx, wf['id'], auto=auto, progress=progress)
            results.append(result)

    increment = len(workflows) - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = len(workflows)
    await progress.set_message("Phase complete")

    return f"OK: Phase {phase} ({phase_names[phase]}) complete\n\n" + "\n".join(results)


@mcp.tool()
async def get_status() -> Dict[str, Any]:
    """
    Get comprehensive workflow status including progress, pending workflows, and completion stats.

    Returns:
        Dictionary with status information
    """
    status = load_workflow_status()
    if not status:
        return {
            "initialized": False,
            "message": "Project not initialized. Run init_project first.",
        }

    total_workflows = 0
    completed_workflows = 0
    pending_workflows: List[Dict[str, Any]] = []

    for phase_key, phase_data in status.get('workflow_status', {}).items():
        for wf_id, wf_config in phase_data.items():
            if not wf_config.get('included', True):
                continue

            total_workflows += 1
            current_status = wf_config.get('status', '')

            if isinstance(current_status, str) and current_status.startswith('docs/'):
                completed_workflows += 1
            else:
                pending_workflows.append({
                    'id': wf_id,
                    'name': wf_id.replace('-', ' ').title(),
                    'agent': wf_config['agent'],
                    'status_type': wf_config['status'],
                    'note': wf_config.get('note', ''),
                })

    next_workflow = get_next_pending_workflow()

    return {
        "initialized": True,
        "project": status.get('project', 'Unknown'),
        "track": status.get('selected_track', 'Unknown'),
        "field_type": status.get('field_type', 'Unknown'),
        "generated": status.get('generated', 'Unknown'),
        "total_workflows": total_workflows,
        "completed_workflows": completed_workflows,
        "pending_workflows": len(pending_workflows),
        "progress_percentage": round((completed_workflows / total_workflows * 100) if total_workflows > 0 else 0, 1),
        "next_workflow": next_workflow,
        "pending_list": pending_workflows[:5],
    }


__all__ = [
    "init_project",
    "run_workflow",
    "run_phase",
    "get_status",
]
