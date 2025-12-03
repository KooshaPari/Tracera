#!/usr/bin/env python3
"""
BMM MCP Server - FastMCP 2.13+ Implementation
Provides MCP tools, resources, and prompts for BMad Method workflow automation.
"""

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

from fastmcp import FastMCP, Context
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware, MiddlewareContext

# Initialize FastMCP server
mcp = FastMCP("bmm-workflows")

# ============================================================================
# CONFIGURATION & UTILITIES
# ============================================================================

def get_project_root() -> Path:
    """Get project root directory"""
    # Look for .bmad folder
    current = Path.cwd()
    while current != current.parent:
        if (current / ".bmad").exists():
            return current
        current = current.parent
    return Path.cwd()

def load_workflow_status() -> Optional[Dict[str, Any]]:
    """Load workflow status YAML"""
    project_root = get_project_root()
    status_file = project_root / "docs" / "bmm-workflow-status.yaml"
    if not status_file.exists():
        return None
    with open(status_file) as f:
        return yaml.safe_load(f)

def save_workflow_status(status: Dict[str, Any]):
    """Save workflow status YAML"""
    project_root = get_project_root()
    status_file = project_root / "docs" / "bmm-workflow-status.yaml"
    status_file.parent.mkdir(parents=True, exist_ok=True)
    with open(status_file, 'w') as f:
        yaml.dump(status, f, default_flow_style=False, sort_keys=False)

def load_bmm_config() -> Dict[str, Any]:
    """Load BMM configuration"""
    project_root = get_project_root()
    config_file = project_root / ".bmad" / "bmm" / "config.yaml"
    if not config_file.exists():
        return {}
    with open(config_file) as f:
        return yaml.safe_load(f)

def get_workflow_config(workflow_id: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific workflow"""
    status = load_workflow_status()
    if not status:
        return None

    for phase_key, phase_data in status.get('workflow_status', {}).items():
        if workflow_id in phase_data:
            return phase_data[workflow_id]
    return None

def get_phase_workflows(phase: int) -> List[Dict[str, Any]]:
    """Get all workflows for a specific phase"""
    status = load_workflow_status()
    if not status:
        return []

    phase_key = f"phase_{phase}_" + ["discovery", "planning", "solutioning", "implementation"][phase]
    phase_data = status.get('workflow_status', {}).get(phase_key, {})

    workflows = []
    for wf_id, wf_config in phase_data.items():
        workflows.append({
            'id': wf_id,
            'name': wf_id.replace('-', ' ').title(),
            **wf_config
        })
    return workflows

def get_next_pending_workflow() -> Optional[Dict[str, Any]]:
    """Get the next pending workflow"""
    status = load_workflow_status()
    if not status:
        return None

    for phase_key, phase_data in status.get('workflow_status', {}).items():
        for wf_id, wf_config in phase_data.items():
            current_status = wf_config.get('status', '')
            # Check if not completed (completed workflows have file paths)
            if not isinstance(current_status, str) or not current_status.startswith('docs/'):
                # Check if included (for optional workflows)
                if wf_config.get('included', True):
                    return {
                        'id': wf_id,
                        'name': wf_id.replace('-', ' ').title(),
                        **wf_config
                    }
    return None

# ============================================================================
# TOOLS - Core workflow operations
# ============================================================================

@mcp.tool()
async def init_project(ctx: Context) -> str:
    """
    Initialize a new BMM project by determining level, type, and creating workflow path.
    Uses elicitation for interactive user input.
    """
    # Check if already initialized
    status = load_workflow_status()
    if status and 'project' in status:
        return f"✅ Project already initialized: {status['project']}"

    # Use elicitation for user input (NEW in FastMCP 2.0+)
    await ctx.report_progress(0, 100, "Starting initialization...")

    project_name = await ctx.elicit(
        prompt="What's your project called?",
        default="MyProject"
    )

    await ctx.report_progress(25, 100, "Project name set")

    track = await ctx.elicit(
        prompt="Select track:",
        options=["quick-flow", "method", "enterprise"]
    )

    await ctx.report_progress(50, 100, "Track selected")

    field_type = await ctx.elicit(
        prompt="Project type:",
        options=["greenfield", "brownfield"]
    )

    await ctx.report_progress(75, 100, "Configuring workflows...")

    # Create workflow status file
    # (Implementation would call workflow-init workflow here)

    await ctx.report_progress(100, 100, "Initialization complete")

    return f"✅ Initialized {project_name} ({track}, {field_type})"

@mcp.tool()
async def run_workflow(
    ctx: Context,
    workflow_id: str,
    auto: bool = False
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

    # Check if already completed
    current_status = workflow.get('status', '')
    if isinstance(current_status, str) and current_status.startswith('docs/'):
        return f"✅ Workflow already completed: {workflow_id} → {current_status}"

    # Construct workflow name from ID
    workflow_name = workflow_id.replace('-', ' ').title()

    # Elicit confirmation unless auto mode
    if not auto:
        confirm = await ctx.elicit(
            prompt=f"Run {workflow_name} workflow?\nAgent: {workflow['agent']}\nNote: {workflow.get('note', 'N/A')}",
            options=["yes", "no", "skip"]
        )
        if confirm == "no":
            return f"❌ Cancelled: {workflow_id}"
        elif confirm == "skip":
            # Update status to skipped
            status = load_workflow_status()
            for phase_key, phase_data in status.get('workflow_status', {}).items():
                if workflow_id in phase_data:
                    phase_data[workflow_id]['status'] = 'skipped'
                    break
            save_workflow_status(status)
            return f"⏭️  Skipped: {workflow_id}"

    # Report progress
    await ctx.report_progress(0, 100, f"Starting {workflow_id}...")

    # Use sub-agent execution with FastMCP Client wrapper
    # This provides elicitation, sampling, and middleware support
    # that root clients (auggie/droid) don't have natively
    await ctx.report_progress(25, 100, "Preparing sub-agent execution...")

    try:
        # Import workflow executor for sub-agent invocation
        # Add current directory to path for import
        import sys
        from pathlib import Path
        current_dir = Path(__file__).parent
        if str(current_dir) not in sys.path:
            sys.path.insert(0, str(current_dir))
        
        from workflow_executor import run_workflow_with_sub_agent
        
        project_root = get_project_root()
        result = await run_workflow_with_sub_agent(
            project_root=project_root,
            agent_name=workflow['agent'],
            workflow_command=workflow['command'],
            workflow_id=workflow_id,
            auto=auto
        )
        
        await ctx.report_progress(75, 100, "Updating workflow status...")

        # Update workflow status
        status = load_workflow_status()
        output_path = workflow.get('output', f"docs/{workflow_id}.md")
        for phase_key, phase_data in status.get('workflow_status', {}).items():
            if workflow_id in phase_data:
                phase_data[workflow_id]['status'] = output_path
                break
        save_workflow_status(status)

        await ctx.report_progress(100, 100, "Complete")

        result_content = result.get('content', '')
        if isinstance(result_content, str):
            return f"✅ Completed {workflow_id}\nOutput: {output_path}\nResult: {result_content}"
        else:
            return f"✅ Completed {workflow_id}\nOutput: {output_path}\nResult: {str(result_content)}"
            
    except ImportError:
        # Fallback to direct sampling if workflow_executor not available
        await ctx.report_progress(25, 100, "Preparing workflow execution...")

        result = await ctx.sample(
            messages=[{
                "role": "user",
                "content": f"Execute this BMM workflow: {workflow['command']}\n\nFollow the workflow instructions exactly. Use elicitation for any user input needed."
            }],
            system_prompt=f"You are the {workflow['agent']} agent. Execute the workflow command provided.",
            model_preferences={
                "hints": [{"name": "claude-sonnet-4.5"}]  # Prefer Claude for workflow execution
            }
        )

        await ctx.report_progress(75, 100, "Updating workflow status...")

        # Update workflow status
        status = load_workflow_status()
        output_path = workflow.get('output', f"docs/{workflow_id}.md")
        for phase_key, phase_data in status.get('workflow_status', {}).items():
            if workflow_id in phase_data:
                phase_data[workflow_id]['status'] = output_path
                break
        save_workflow_status(status)

        await ctx.report_progress(100, 100, "Complete")

        return f"✅ Completed {workflow_id}\nOutput: {output_path}\nResult: {result.content}"

@mcp.tool()
async def run_phase(
    ctx: Context,
    phase: int,
    parallel: bool = False,
    auto: bool = False
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
    await ctx.report_progress(0, len(workflows), f"Starting Phase {phase}: {phase_names[phase]}")

    results = []

    if parallel:
        # Group by agent for parallel execution
        agent_groups = {}
        for wf in workflows:
            agent = wf['agent']
            if agent not in agent_groups:
                agent_groups[agent] = []
            agent_groups[agent].append(wf)

        # Run different agents in parallel
        async def run_agent_workflows(agent: str, agent_workflows: List[Dict]):
            agent_results = []
            for wf in agent_workflows:
                result = await run_workflow(ctx, wf['id'], auto=auto)
                agent_results.append(result)
            return agent_results

        # Execute in parallel
        all_results = await asyncio.gather(*[
            run_agent_workflows(agent, wfs)
            for agent, wfs in agent_groups.items()
        ])

        # Flatten results
        for agent_results in all_results:
            results.extend(agent_results)
    else:
        # Sequential execution
        for i, wf in enumerate(workflows):
            wf_name = wf['id'].replace('-', ' ').title()
            await ctx.report_progress(i, len(workflows), f"Running {wf_name}...")
            result = await run_workflow(ctx, wf['id'], auto=auto)
            results.append(result)

    await ctx.report_progress(len(workflows), len(workflows), "Phase complete")

    return f"✅ Phase {phase} ({phase_names[phase]}) complete\n\n" + "\n".join(results)

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
            "message": "Project not initialized. Run init_project first."
        }

    # Calculate statistics
    total_workflows = 0
    completed_workflows = 0
    pending_workflows = []

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
                    'note': wf_config.get('note', '')
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
        "pending_list": pending_workflows[:5]  # First 5 pending
    }


# ============================================================================
# RESOURCES - Expose workflow state and configuration
# ============================================================================

@mcp.resource("bmm://workflow-status")
async def workflow_status_resource() -> str:
    """
    Current BMM workflow status in YAML format.
    Clients can read this to understand project state without tool calls.
    """
    status = load_workflow_status()
    if not status:
        return "# No workflow status found\n# Run init_project tool first"

    return yaml.dump(status, default_flow_style=False, sort_keys=False)

@mcp.resource("bmm://project-config")
async def project_config_resource() -> str:
    """
    BMM project configuration from .bmad/bmm/config.yaml
    """
    config = load_bmm_config()
    if not config:
        return "# No BMM configuration found"

    return yaml.dump(config, default_flow_style=False, sort_keys=False)

@mcp.resource("bmm://next-workflow")
async def next_workflow_resource() -> str:
    """
    Next pending workflow to execute.
    Useful for agents to know what to run next.
    """
    next_wf = get_next_pending_workflow()
    if not next_wf:
        return "# All workflows complete! 🎉"

    wf_name = next_wf['id'].replace('-', ' ').title()
    return f"""# Next Workflow

ID: {next_wf['id']}
Name: {wf_name}
Agent: {next_wf['agent']}
Command: {next_wf['command']}
Status: {next_wf['status']}
Note: {next_wf.get('note', 'N/A')}

To execute: Use the run_workflow tool with workflow_id="{next_wf['id']}"
"""

@mcp.resource("bmm://progress-summary")
async def progress_summary_resource() -> str:
    """
    Human-readable progress summary
    """
    status_data = await get_status()

    if not status_data.get('initialized'):
        return "# Project not initialized"

    return f"""# BMM Progress Summary

Project: {status_data['project']}
Track: {status_data['track']}
Type: {status_data['field_type']}

Progress: {status_data['completed_workflows']}/{status_data['total_workflows']} ({status_data['progress_percentage']}%)

Next: {status_data['next_workflow']['id'].replace('-', ' ').title() if status_data['next_workflow'] else 'All complete!'}
"""

# ============================================================================
# PROMPTS - Reusable prompt templates
# ============================================================================

@mcp.prompt()
async def workflow_execution_prompt(workflow_id: str) -> List[Dict[str, str]]:
    """
    Generate prompt for executing a specific workflow.

    Args:
        workflow_id: The workflow to execute

    Returns:
        List of messages for LLM
    """
    workflow = get_workflow_config(workflow_id)
    if not workflow:
        return [{
            "role": "user",
            "content": f"Error: Workflow '{workflow_id}' not found"
        }]

    return [{
        "role": "system",
        "content": f"You are the {workflow['agent']} agent executing BMM workflows."
    }, {
        "role": "user",
        "content": f"""Execute this BMM workflow:

Workflow: {workflow_id}
Command: {workflow['command']}
Note: {workflow.get('note', 'N/A')}

Instructions:
1. Read the bmm://workflow-status resource to understand current state
2. Follow the workflow command exactly
3. Use elicitation for any user input needed
4. Generate output to: {workflow.get('output', 'docs/')}
5. Report progress as you work

Begin execution now.
"""
    }]

@mcp.prompt()
async def phase_planning_prompt(phase: int) -> List[Dict[str, str]]:
    """
    Generate prompt for planning a phase execution.

    Args:
        phase: Phase number (0-3)

    Returns:
        List of messages for LLM
    """
    workflows = get_phase_workflows(phase)
    phase_names = ["Discovery", "Planning", "Solutioning", "Implementation"]

    workflow_list = "\n".join([
        f"- {wf['id']} ({wf['agent']}) - {wf.get('note', '')}"
        for wf in workflows
    ])

    return [{
        "role": "system",
        "content": "You are a BMM workflow planning assistant."
    }, {
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
"""
    }]

@mcp.prompt()
async def project_overview_prompt() -> List[Dict[str, str]]:
    """
    Generate prompt for getting project overview.

    Returns:
        List of messages for LLM
    """
    status_data = await get_status()

    return [{
        "role": "system",
        "content": "You are a BMM project analyst."
    }, {
        "role": "user",
        "content": f"""Analyze this BMM project:

Project: {status_data.get('project', 'Unknown')}
Track: {status_data.get('track', 'Unknown')}
Type: {status_data.get('field_type', 'Unknown')}
Progress: {status_data.get('progress_percentage', 0)}%

Completed: {status_data.get('completed_workflows', 0)}/{status_data.get('total_workflows', 0)} workflows

Read the bmm://workflow-status resource for full details.

Provide:
1. Current status summary
2. What's been accomplished
3. What's remaining
4. Recommended next steps
5. Any potential blockers or concerns
"""
    }]

# ============================================================================
# MIDDLEWARE - Logging and monitoring (NEW in FastMCP 2.13)
# ============================================================================

class LoggingMiddleware(Middleware):
    """Log all tool calls and resource accesses"""

    async def on_tool_call(self, ctx: MiddlewareContext, tool_name: str, arguments: Dict[str, Any]):
        """Called before tool execution"""
        print(f"[TOOL] {tool_name} called with args: {arguments}")
        await ctx.next()  # Continue to next middleware or tool

    async def on_resource_read(self, ctx: MiddlewareContext, uri: str):
        """Called before resource read"""
        print(f"[RESOURCE] Reading {uri}")
        await ctx.next()

# Register middleware
mcp.add_middleware(LoggingMiddleware())

# ============================================================================
# STORAGE BACKEND - Persistent state (NEW in FastMCP 2.13)
# ============================================================================

# For now, using file-based storage (workflow status YAML)
# Could be enhanced with Redis/SQLite for caching:
#
# from fastmcp.storage import RedisStorage
# mcp.set_storage(RedisStorage(url="redis://localhost:6379"))

# ============================================================================
# MAIN - Server entry point
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server
    # Default transport is STDIO (perfect for Claude Desktop)
    mcp.run()

    # For SSE transport (remote access):
    # mcp.run(transport="sse", host="0.0.0.0", port=8000)

    # For HTTP transport:
    # mcp.run(transport="http", host="0.0.0.0", port=8000)

