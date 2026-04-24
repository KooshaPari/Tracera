"""BMM workflow MCP resources."""

from __future__ import annotations

import asyncio

import yaml

from tracertm.mcp.bmm_utils import (
    get_next_pending_workflow,
    get_status_data,
    load_bmm_config,
    load_workflow_status,
)
from tracertm.mcp.core import mcp


@mcp.resource("bmm://workflow-status")
async def workflow_status_resource() -> str:
    """Current BMM workflow status in YAML format.

    Clients can read this to understand project state without tool calls.
    """
    await asyncio.sleep(0)
    status = load_workflow_status()
    if not status:
        return "# No workflow status found\n# Run init_project tool first"

    return yaml.safe_dump(status, default_flow_style=False, sort_keys=False)


@mcp.resource("bmm://project-config")
async def project_config_resource() -> str:
    """BMM project configuration from .bmad/bmm/config.yaml."""
    await asyncio.sleep(0)
    config = load_bmm_config()
    if not config:
        return "# No BMM configuration found"

    return yaml.safe_dump(config, default_flow_style=False, sort_keys=False)


@mcp.resource("bmm://next-workflow")
async def next_workflow_resource() -> str:
    """Next pending workflow to execute."""
    await asyncio.sleep(0)
    next_wf = get_next_pending_workflow()
    if not next_wf:
        return "# All workflows complete!"

    if not isinstance(next_wf, dict):
        return "# Invalid workflow data"

    wf_name = str(next_wf["id"]).replace("-", " ").title()
    return f"""# Next Workflow

ID: {next_wf["id"]}
Name: {wf_name}
Agent: {next_wf["agent"]}
Command: {next_wf["command"]}
Status: {next_wf["status"]}
Note: {next_wf.get("note", "N/A")}

To execute: Use the run_workflow tool with workflow_id="{next_wf["id"]}"
"""


@mcp.resource("bmm://progress-summary")
async def progress_summary_resource() -> str:
    """Human-readable progress summary."""
    status_data = get_status_data()

    if not status_data.get("initialized"):
        return "# Project not initialized"

    next_wf = status_data.get("next_workflow")
    next_label = str(next_wf["id"]).replace("-", " ").title() if isinstance(next_wf, dict) else "All complete!"

    return f"""# BMM Progress Summary

Project: {status_data["project"]}
Track: {status_data["track"]}
Type: {status_data["field_type"]}

Progress: {status_data["completed_workflows"]}/{status_data["total_workflows"]} ({status_data["progress_percentage"]}%)

Next: {next_label}
"""


__all__ = [
    "next_workflow_resource",
    "progress_summary_resource",
    "project_config_resource",
    "workflow_status_resource",
]
