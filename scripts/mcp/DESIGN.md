# BMM MCP Server - Design Document

## Executive Summary

Transform BMM workflow automation from a CLI script to a **Model Context Protocol (MCP) server** using FastMCP, enabling:

1. **Native LLM Integration**: Direct tool calling from any MCP client (Claude Desktop, custom clients)
2. **Elicitation Support**: Built-in user prompting without custom JSON protocols
3. **Sampling Capability**: Server can invoke LLMs for sub-tasks
4. **Rich Resources**: Expose workflow status, documentation, and project state
5. **Reusable Prompts**: Templated prompts for common BMM operations
6. **Beautiful CLI**: Typer + Rich for enhanced terminal UX

## Why MCP Over Custom CLI?

### Current Approach (bmm-auto.py)
```
User → CLI Script → auggie/claude CLI → Agent → Workflow
                ↓
        Custom JSON Protocol
                ↓
        Manual Parsing & Handling
```

**Problems:**
- Custom JSON protocol not standard
- Limited to auggie/claude CLI
- Manual user interaction handling
- No native LLM integration
- Reinventing MCP features

### MCP Approach
```
User/LLM → MCP Client → BMM MCP Server → Workflows
                              ↓
                    FastMCP Features:
                    - Elicitation (user input)
                    - Sampling (LLM calls)
                    - Resources (state)
                    - Prompts (templates)
```

**Benefits:**
- ✅ Standard protocol (MCP)
- ✅ Works with any MCP client
- ✅ Built-in elicitation
- ✅ Built-in LLM sampling
- ✅ Native tool calling
- ✅ Resource exposure
- ✅ Prompt templates

## FastMCP Features Analysis

### 1. **Elicitation** ⭐ KEY FEATURE

**What it is:** Server can request user input mid-execution

**Example:**
```python
@mcp.tool()
async def init_project(ctx: Context):
    # Request user input
    project_name = await ctx.elicit(
        prompt="What's your project called?",
        default="MyProject"
    )
    
    track = await ctx.elicit(
        prompt="Select track:",
        options=["quick-flow", "method", "enterprise"]
    )
    
    return f"Initialized {project_name} with {track}"
```

**Replaces:** Our custom JSON `{"type": "user_input"}` protocol

### 2. **Sampling** ⭐ KEY FEATURE

**What it is:** Server can invoke LLM for sub-tasks

**Example:**
```python
@mcp.tool()
async def analyze_codebase(ctx: Context, path: str):
    # Read files
    files = scan_directory(path)
    
    # Use LLM to analyze
    analysis = await ctx.sample(
        messages=[{
            "role": "user",
            "content": f"Analyze this codebase structure:\n{files}"
        }]
    )
    
    return analysis
```

**Replaces:** Manual CLI invocations for agent tasks

### 3. **Resources**

**What it is:** Expose data/state to LLM clients

**Example:**
```python
@mcp.resource("bmm://workflow-status")
async def get_workflow_status():
    """Current BMM workflow status"""
    return read_workflow_status_file()

@mcp.resource("bmm://project-config")
async def get_project_config():
    """BMM project configuration"""
    return read_bmm_config()
```

**Use case:** LLM can read workflow status without tool calls

### 4. **Prompts**

**What it is:** Reusable prompt templates

**Example:**
```python
@mcp.prompt()
async def create_prd_prompt(project_name: str):
    """Generate PRD creation prompt"""
    return f"""You are creating a PRD for {project_name}.

Follow BMad Method guidelines:
1. Define Functional Requirements (FRs)
2. Define Non-Functional Requirements (NFRs)
3. Include acceptance criteria
4. Consider enterprise compliance

Use the bmm://workflow-status resource to check current state.
"""
```

**Use case:** Consistent prompts across different LLM clients

### 5. **Tools**

**What it is:** Functions LLM can call

**Example:**
```python
@mcp.tool()
async def run_workflow(
    ctx: Context,
    workflow_id: str,
    interactive: bool = True
) -> str:
    """Run a BMM workflow"""
    if interactive:
        confirm = await ctx.elicit(
            prompt=f"Run {workflow_id}?",
            options=["yes", "no"]
        )
        if confirm == "no":
            return "Cancelled"
    
    # Execute workflow
    result = await execute_workflow(workflow_id)
    return result
```

## Architecture Design

### MCP Server Structure

```python
# bmm_mcp_server.py
from fastmcp import FastMCP, Context
from rich.console import Console
import typer

mcp = FastMCP("bmm-workflows")
console = Console()

# ============ TOOLS ============

@mcp.tool()
async def init_project(ctx: Context) -> str:
    """Initialize BMM project with interactive setup"""
    # Use elicitation for user input
    project_name = await ctx.elicit("Project name?")
    track = await ctx.elicit(
        "Select track:",
        options=["quick-flow", "method", "enterprise"]
    )
    field_type = await ctx.elicit(
        "Project type:",
        options=["greenfield", "brownfield"]
    )
    
    # Create workflow status file
    create_workflow_status(project_name, track, field_type)
    return f"✅ Initialized {project_name}"

@mcp.tool()
async def run_workflow(
    ctx: Context,
    workflow_id: str,
    auto: bool = False
) -> str:
    """Execute a BMM workflow"""
    workflow = get_workflow_config(workflow_id)
    
    if not auto:
        confirm = await ctx.elicit(
            f"Run {workflow['name']} ({workflow['agent']})?",
            options=["yes", "no", "skip"]
        )
        if confirm != "yes":
            return f"Skipped {workflow_id}"
    
    # Use sampling to run workflow with appropriate agent
    result = await ctx.sample(
        messages=[{
            "role": "user",
            "content": f"Execute workflow: {workflow['command']}"
        }],
        system_prompt=load_agent_prompt(workflow['agent'])
    )
    
    # Update status
    update_workflow_status(workflow_id, "complete")
    return f"✅ Completed {workflow_id}"

@mcp.tool()
async def run_phase(
    ctx: Context,
    phase: int,
    parallel: bool = False
) -> str:
    """Run all workflows in a phase"""
    workflows = get_phase_workflows(phase)
    
    if parallel:
        # Run in parallel (same agent sequential, different parallel)
        results = await run_parallel_workflows(ctx, workflows)
    else:
        results = []
        for wf in workflows:
            result = await run_workflow(ctx, wf['id'])
            results.append(result)
    
    return "\n".join(results)

# ============ RESOURCES ============

@mcp.resource("bmm://workflow-status")
async def workflow_status():
    """Current workflow status and progress"""
    return read_workflow_status_yaml()

@mcp.resource("bmm://project-config")
async def project_config():
    """BMM project configuration"""
    return read_bmm_config()

@mcp.resource("bmm://next-workflow")
async def next_workflow():
    """Next pending workflow to execute"""
    return get_next_pending_workflow()

# ============ PROMPTS ============

@mcp.prompt()
async def workflow_execution_prompt(workflow_id: str):
    """Generate prompt for workflow execution"""
    workflow = get_workflow_config(workflow_id)
    return f"""Execute BMM workflow: {workflow['name']}

Agent: {workflow['agent']}
Command: {workflow['command']}

Use bmm://workflow-status resource to check current state.
Follow workflow instructions exactly.
Use elicitation for user input when needed.
"""

@mcp.prompt()
async def phase_planning_prompt(phase: int):
    """Generate prompt for phase planning"""
    workflows = get_phase_workflows(phase)
    return f"""Plan execution of Phase {phase} workflows:

{format_workflow_list(workflows)}

Consider:
- Dependencies between workflows
- Parallel execution opportunities
- User interaction points
"""
```

## Integration with Factory Models

Your `~/.factory/config.json` provides access to multiple models via `localhost:8317`:

```python
# Use factory models for sampling
@mcp.tool()
async def analyze_with_model(
    ctx: Context,
    content: str,
    model: str = "gpt-5.1-codex"
) -> str:
    """Analyze content using specific factory model"""
    
    # Configure client for factory endpoint
    result = await ctx.sample(
        messages=[{"role": "user", "content": content}],
        model_preferences={
            "hints": [{"name": model}]
        },
        # FastMCP will use client's model configuration
    )
    
    return result
```

**Available Models:**
- GPT-5 Codex variants (low/medium/high/max)
- Claude Sonnet 4.5 (with thinking mode)
- Gemini 3 Pro, 2.5 Flash
- Qwen3 variants
- GLM 4.6
- Grok variants

## CLI Enhancement with Typer + Rich

Transform the CLI into a beautiful, modern interface:

```python
# bmm_cli.py
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree

app = typer.Typer(
    name="bmm",
    help="BMad Method Workflow Automation",
    add_completion=False
)
console = Console()

@app.command()
def init():
    """Initialize BMM project"""
    with console.status("[bold green]Initializing BMM project..."):
        # Call MCP server
        result = mcp_client.call_tool("init_project")
    
    console.print(Panel(result, title="✅ Initialization Complete"))

@app.command()
def status():
    """Show workflow status"""
    # Get resource from MCP
    status_data = mcp_client.get_resource("bmm://workflow-status")
    
    # Create beautiful table
    table = Table(title="BMM Workflow Status")
    table.add_column("Workflow", style="cyan")
    table.add_column("Status", style="magenta")
    table.add_column("Agent", style="green")
    
    for workflow in status_data['workflows']:
        table.add_row(
            workflow['name'],
            workflow['status'],
            workflow['agent']
        )
    
    console.print(table)

@app.command()
def run(
    workflow_id: str = typer.Argument(None),
    phase: int = typer.Option(None, "--phase", "-p"),
    parallel: bool = typer.Option(False, "--parallel"),
    auto: bool = typer.Option(False, "--auto")
):
    """Run workflows"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        
        if phase is not None:
            task = progress.add_task(f"Running Phase {phase}...", total=None)
            result = mcp_client.call_tool("run_phase", phase=phase, parallel=parallel)
        elif workflow_id:
            task = progress.add_task(f"Running {workflow_id}...", total=None)
            result = mcp_client.call_tool("run_workflow", workflow_id=workflow_id, auto=auto)
        
        progress.update(task, completed=True)
    
    console.print(Panel(result, title="✅ Complete"))

if __name__ == "__main__":
    app()
```

## Comparison: Current vs MCP Approach

| Feature | Current (bmm-auto.py) | MCP Approach |
|---------|----------------------|--------------|
| **User Input** | Custom JSON protocol | Built-in elicitation |
| **LLM Calls** | Shell out to CLI | Built-in sampling |
| **State Exposure** | Manual file reading | MCP resources |
| **Prompt Templates** | Hardcoded strings | MCP prompts |
| **Client Support** | auggie/claude only | Any MCP client |
| **Standard Protocol** | ❌ Custom | ✅ MCP standard |
| **CLI Beauty** | Basic argparse | ✅ Typer + Rich |
| **Parallel Execution** | ✅ asyncio | ✅ asyncio + MCP |
| **Model Selection** | Limited | ✅ Factory models |

## Implementation Plan

### Phase 1: MCP Server Core
1. Create `bmm_mcp_server.py` with FastMCP
2. Implement core tools (init, run_workflow, run_phase)
3. Add resources (workflow-status, config, next-workflow)
4. Add prompts (workflow-execution, phase-planning)

### Phase 2: CLI Enhancement
1. Refactor to Typer + Rich
2. Beautiful status display
3. Progress indicators
4. Interactive prompts with Rich

### Phase 3: Integration
1. Connect to factory models (localhost:8317)
2. Test with Claude Desktop
3. Test with custom MCP clients
4. Document MCP server configuration

### Phase 4: Advanced Features
1. Implement elicitation for all user interactions
2. Use sampling for workflow execution
3. Add middleware for logging
4. Add storage backends for state

## Next Steps

1. **Create MCP server** (`bmm_mcp_server.py`)
2. **Refactor CLI** with Typer + Rich
3. **Test with Claude Desktop**
4. **Document configuration**
5. **Migrate from bmm-auto.py**

