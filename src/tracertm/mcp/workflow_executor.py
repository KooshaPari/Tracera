"""Workflow Executor - Wraps sub-agent execution with FastMCP Client.

Handles elicitation, sampling, middleware, and I/O between main agent and sub-agents.
"""

import asyncio
from pathlib import Path

from fastmcp.client import Client


class WorkflowExecutor:
    """Executes workflows using FastMCP Client to invoke sub-agents.

    Provides elicitation, sampling, and middleware support that root clients don't have.
    """

    def __init__(self, project_root: Path, agent_name: str) -> None:
        """Initialize."""
        self.project_root = project_root
        self.agent_name = agent_name
        self.agent_config_path = self._find_agent_config()

    def _find_agent_config(self) -> Path | None:
        """Find agent configuration file."""
        # Check .bmad/bmm/agents first
        bmm_agents = self.project_root / ".bmad" / "bmm" / "agents" / f"{self.agent_name}.agent.yaml"
        if bmm_agents.exists():
            return bmm_agents

        # Check .bmad/core/agents
        core_agents = self.project_root / ".bmad" / "core" / "agents" / f"{self.agent_name}.agent.yaml"
        if core_agents.exists():
            return core_agents

        return None

    async def execute_workflow(self, workflow_command: str, workflow_id: str, auto: bool = False) -> dict[str, object]:
        """Execute a workflow by creating a sub-agent MCP server and invoking it via FastMCP Client.

        Architecture:
        Main Agent (droid exec) -> MCP Server (bmm_server.py) -> Tool (run_workflow)
        Tool (run_workflow) -> FastMCP Client -> Sub-agent MCP Server -> Sub-agent execution

        The sub-agent MCP server provides:
        - Elicitation for user input
        - Sampling for LLM execution
        - Middleware for logging/monitoring
        - Progress reporting

        These features are not natively supported by droid exec (root client),
        so we wrap them in a 2nd MCP client layer using FastMCP Client.
        """
        # Create a workflow-specific MCP server that provides FastMCP features
        workflow_server = self._create_workflow_server(workflow_command, workflow_id, auto)

        # Use FastMCP Client (2nd layer) to connect to the workflow server
        # This client supports elicitation, sampling, middleware that root clients don't
        client = Client(workflow_server)

        async with client:
            # Invoke the workflow execution tool
            # The tool will use elicitation/sampling/middleware internally
            result = await client.call_tool(
                "execute_workflow",
                {"workflow_command": workflow_command, "workflow_id": workflow_id, "auto": auto},
            )

            # Extract result content
            if result.structured_content:
                content: object = result.structured_content
            elif result.data:
                content = result.data
            else:
                content = str(result.content) if result.content else ""

            return {
                "success": True,
                "content": content,
                "output_path": None,  # Will be set by workflow server
            }

    def _create_workflow_server(self, _workflow_command: str, workflow_id: str, _auto: bool) -> Path:
        """Create a temporary FastMCP server script for workflow execution.

        This server has full FastMCP features (elicitation, sampling, middleware).
        """
        server_script = self.project_root / ".bmad" / "tmp" / f"workflow_{workflow_id}_server.py"
        server_script.parent.mkdir(parents=True, exist_ok=True)

        server_code = f'''#!/usr/bin/env python3
"""
Temporary workflow execution server for {workflow_id}
Provides FastMCP features (elicitation, sampling, middleware) for sub-agent execution.

This server is invoked by FastMCP Client (2nd layer) from the main agent's MCP server.
It provides features that droid exec (root client) doesn't support natively.
"""

import asyncio
import sys
from pathlib import Path
from typing import Any, Dict

# Add project root to path
project_root = Path("{self.project_root}")
sys.path.insert(0, str(project_root))

from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import Progress
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

# Create workflow-specific MCP server with middleware support
mcp = FastMCP("workflow-{workflow_id}")

# Add middleware for logging/monitoring
class WorkflowMiddleware(Middleware):
    """Middleware for workflow execution logging"""

    async def on_tool_call(self, ctx: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]):
        print(f'[WORKFLOW] {{tool_name}} called with args: {{arguments}}')
        await ctx.next()

mcp.add_middleware(WorkflowMiddleware())

@mcp.tool()
async def execute_workflow(
    ctx: Context,
    workflow_command: str,
    workflow_id: str,
    auto: bool = False,
    progress: Progress = Progress(),
) -> str:
    """
    Execute a workflow step using FastMCP features (elicitation, sampling, middleware).

    This tool is invoked by FastMCP Client from the main agent's MCP server.
    It provides:
    - Elicitation for user input (not supported by droid exec)
    - Sampling for LLM execution with full FastMCP features
    - Middleware for logging and monitoring
    - Progress reporting

    Architecture:
    Droid Exec -> MCP Server -> FastMCP Client -> This Server -> Sub-agent execution
    """
    # Report progress (worker-safe via Progress dependency)
    current_progress = 0
    await progress.set_total(100)
    await progress.set_message(f"Starting workflow: {{workflow_id}}")

    # Elicit user input if needed (unless auto mode)
    # This is a FastMCP feature not available in droid exec
    if not auto:
        confirm = await ctx.elicit(
            prompt=f"Execute workflow: {{workflow_id}}?\\nCommand: {{workflow_command}}\\n\\nThis will execute the workflow step. Continue?",
            options=["yes", "no", "skip"]
        )
        if confirm == "no":
            return f"CANCELLED: Cancelled: {{workflow_id}}"
        elif confirm == "skip":
            return f"SKIPPED:  Skipped: {{workflow_id}}"

    increment = 25 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 25
    await progress.set_message("Preparing workflow execution...")

    # Use sampling to execute workflow with the agent
    # Sampling provides full FastMCP features during LLM execution
    # This allows the sub-agent to use elicitation, progress reporting, etc.
    result = await ctx.sample(
        messages=[{{
            "role": "user",
            "content": f"Execute this BMM workflow: {{workflow_command}}\\n\\nFollow the workflow instructions exactly. Use elicitation for any user input needed. Report progress as you work."
        }}],
        system_prompt=f"You are executing workflow {{workflow_id}}. Follow the instructions carefully. Use elicitation for user input when needed.",
        model_preferences={{
            "hints": [{{"name": "claude-sonnet-4.5"}}]
        }}
    )

    increment = 100 - current_progress
    if increment > 0:
        await progress.increment(increment)
        current_progress = 100
    await progress.set_message("Complete")

    # Extract content from result
    content = result.content if hasattr(result, 'content') else str(result)

    return f"OK: Completed {{workflow_id}}\\nResult: {{content}}"

if __name__ == "__main__":
    mcp.run()
'''

        server_script.write_text(server_code)
        server_script.chmod(0o755)

        return server_script


async def run_workflow_with_sub_agent(
    project_root: Path,
    agent_name: str,
    workflow_command: str,
    workflow_id: str,
    auto: bool = False,
) -> dict[str, object]:
    """Main entry point for executing a workflow with sub-agent support.

    This function:
    1. Creates a WorkflowExecutor
    2. Executes the workflow using FastMCP Client
    3. Returns results to the main agent
    """
    executor = WorkflowExecutor(project_root, agent_name)
    return await executor.execute_workflow(workflow_command, workflow_id, auto)


if __name__ == "__main__":
    # CLI interface for direct testing
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, required=True)
    parser.add_argument("--agent", required=True)
    parser.add_argument("--workflow-command", required=True)
    parser.add_argument("--workflow-id", required=True)
    parser.add_argument("--auto", action="store_true")

    args = parser.parse_args()

    result = asyncio.run(
        run_workflow_with_sub_agent(args.project_root, args.agent, args.workflow_command, args.workflow_id, args.auto),
    )
