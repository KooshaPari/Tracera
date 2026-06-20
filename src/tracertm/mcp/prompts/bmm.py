"""BMM workflow MCP prompts."""

from __future__ import annotations

import asyncio

from tracertm.mcp.bmm_utils import get_phase_workflows, get_status_data, get_workflow_config
from tracertm.mcp.core import mcp


@mcp.prompt()
async def workflow_execution_prompt(workflow_id: str) -> list[dict[str, str]]:
    """Generate prompt for executing a specific workflow.

    Args:
        workflow_id: The workflow to execute

    Returns:
        List of messages for LLM
    """
    await asyncio.sleep(0)
    workflow = get_workflow_config(workflow_id)
    if not workflow:
        return [
            {
                "role": "user",
                "content": f"Error: Workflow '{workflow_id}' not found",
            },
        ]

    return [
        {
            "role": "system",
            "content": f"You are the {workflow['agent']} agent executing BMM workflows.",
        },
        {
            "role": "user",
            "content": f"""Execute this BMM workflow:

Workflow: {workflow_id}
Command: {workflow["command"]}
Note: {workflow.get("note", "N/A")}

Instructions:
1. Read the bmm://workflow-status resource to understand current state
2. Follow the workflow command exactly
3. Use elicitation for any user input needed
4. Generate output to: {workflow.get("output", "docs/")}
5. Report progress as you work

Begin execution now.
""",
        },
    ]


@mcp.prompt()
async def phase_planning_prompt(phase: int) -> list[dict[str, str]]:
    """Generate prompt for planning a phase execution.

    Args:
        phase: Phase number (0-3)

    Returns:
        List of messages for LLM
    """
    await asyncio.sleep(0)
    workflows = get_phase_workflows(phase)
    phase_names = ["Discovery", "Planning", "Solutioning", "Implementation"]

    workflow_list = "\n".join([f"- {wf['id']} ({wf['agent']}) - {wf.get('note', '')}" for wf in workflows])

    return [
        {
            "role": "system",
            "content": "You are a BMM workflow planning assistant.",
        },
        {
            "role": "user",
            "content": f"""Plan execution of Phase {phase}: {phase_names[phase]}

Workflows in this phase:
{workflow_list}

Consider:
1. Dependencies between workflows
2. Parallel execution opportunities (different agents can run in parallel)
3. User interaction points (elicitation needed)
4. Estimated time for each workflow

Provide a recommended execution strategy.
""",
        },
    ]


@mcp.prompt()
async def project_overview_prompt() -> list[dict[str, str]]:
    """Generate prompt for getting project overview.

    Returns:
        List of messages for LLM
    """
    status_data = get_status_data()

    return [
        {
            "role": "system",
            "content": "You are a BMM project analyst.",
        },
        {
            "role": "user",
            "content": f"""Analyze this BMM project:

Project: {status_data.get("project", "Unknown")}
Track: {status_data.get("track", "Unknown")}
Type: {status_data.get("field_type", "Unknown")}
Progress: {status_data.get("progress_percentage", 0)}%

Completed: {status_data.get("completed_workflows", 0)}/{status_data.get("total_workflows", 0)} workflows

Read the bmm://workflow-status resource for full details.

Provide:
1. Current status summary
2. What's been accomplished
3. What's remaining
4. Recommended next steps
5. Any potential blockers or concerns
""",
        },
    ]


__all__ = [
    "phase_planning_prompt",
    "project_overview_prompt",
    "workflow_execution_prompt",
]
