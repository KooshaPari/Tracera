#!/usr/bin/env python3
"""
BMM CLI - Beautiful command-line interface using Typer + Rich
Uses droid exec (Factory headless CLI) with MCP server attached for workflow execution
"""

import asyncio
import subprocess
import sys
from pathlib import Path
from typing import Optional

import typer
from fastmcp.client import Client
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.tree import Tree
from rich import box

# Import server utility functions directly (for status/read operations)
sys.path.insert(0, str(Path(__file__).parent))
from bmm_server import (
    load_workflow_status,
    get_next_pending_workflow,
    get_workflow_config,
    get_project_root
)

# Initialize Typer app
app = typer.Typer(
    name="bmm",
    help="🚀 BMad Method Workflow Automation - Beautiful CLI",
    add_completion=False,
    rich_markup_mode="rich"
)

console = Console()

# ============================================================================
# AGENT CLI DETECTION & SETUP
# ============================================================================

def detect_agent_cli() -> str:
    """Detect available agent CLI (droid exec)"""
    if subprocess.run(["which", "droid"], capture_output=True).returncode == 0:
        return "droid"
    else:
        raise RuntimeError("droid CLI not found. Please install: curl -fsSL https://app.factory.ai/cli | sh")

def get_mcp_server_path() -> Path:
    """Get path to MCP server script"""
    return Path(__file__).parent / "bmm_server.py"

def build_droid_command(
    instruction: str,
    project_root: Path,
    mcp_server: Path,
    auto_level: str = "low",
    output_format: str = "text"
) -> tuple[list[str], dict[str, str]]:
    """
    Build droid exec command with MCP server attached.
    
    Note: Droid may handle MCP servers via environment variables or config.
    For now, we pass the MCP server path in the instruction and set environment.
    
    Args:
        instruction: Instruction for the agent
        project_root: Project root directory
        mcp_server: Path to MCP server script
        auto_level: Autonomy level (low|medium|high)
        output_format: Output format (text|json|debug)
    """
    cmd = [
        "droid", "exec",
        "--output-format", output_format,
        "--auto", auto_level,
        "--cwd", str(project_root),
        instruction
    ]
    
    # Set MCP server path in environment for droid to discover
    # Droid may use FACTORY_MCP_SERVERS or similar env var
    # Also include in instruction so agent knows where to find tools
    import os
    env = os.environ.copy()
    env["BMM_MCP_SERVER"] = str(mcp_server)
    # Some MCP clients use this pattern
    env["MCP_SERVER_PATH"] = str(mcp_server)
    
    return cmd, env

def get_mcp_client() -> Client:
    """Get MCP client for informational commands (read-only operations)"""
    return Client(get_mcp_server_path())

# ============================================================================
# COMMANDS
# ============================================================================

@app.command()
def init(
    auto_level: str = typer.Option("low", "--auto", "-a", help="Autonomy level: low|medium|high")
):
    """
    🚀 Initialize BMM project with interactive setup
    Uses droid exec with MCP server attached
    """
    console.print(Panel.fit(
        "[bold cyan]BMad Method Initialization[/bold cyan]\n"
        "Setting up your project workflow...",
        border_style="cyan"
    ))

    try:
        detect_agent_cli()  # Verify droid is available
        project_root = get_project_root()
        mcp_server = get_mcp_server_path()

        # Build droid exec command
        # Droid will use MCP server tools if configured. The instruction references the tool directly.
        instruction = f"""Use the init_project tool from the BMM MCP server (located at {mcp_server}) to initialize this project.
        
The MCP server provides tools for BMM workflow automation. Call the init_project tool to set up the project."""
        cmd, env = build_droid_command(
            instruction=instruction,
            project_root=project_root,
            mcp_server=mcp_server,
            auto_level=auto_level,
            output_format="text"
        )

        with console.status("[bold green]Initializing project..."):
            result = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                console.print(Panel(
                    result.stdout if result.stdout else "✅ Project initialized successfully",
                    title="✅ Initialization Complete",
                    border_style="green"
                ))
            else:
                console.print("[bold red]Error:[/bold red] Initialization failed")
                if result.stderr:
                    console.print(f"[dim]{result.stderr}[/dim]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def status():
    """
    📊 Show current workflow status and progress
    Uses direct server function calls (read-only operation)
    """
    try:
        status = load_workflow_status()

        if not status:
            console.print("[yellow]Project not initialized. Run 'bmm init' first.[/yellow]")
            return

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

        progress_pct = round((completed_workflows / total_workflows * 100) if total_workflows > 0 else 0, 1)

        # Create beautiful status display
        console.print()
        console.print(Panel.fit(
            f"[bold cyan]{status.get('project', 'Unknown')}[/bold cyan]\n"
            f"Track: {status.get('selected_track', 'Unknown')} | Type: {status.get('field_type', 'Unknown')}",
            border_style="cyan"
        ))

        console.print(f"\n[bold]Progress:[/bold] {completed_workflows}/{total_workflows} workflows ({progress_pct}%)")

        # Create progress bar
        from rich.progress import Progress as ProgressBar
        progress_bar = ProgressBar()
        task_id = progress_bar.add_task("", total=100, completed=progress_pct)
        console.print(progress_bar.make_tasks_table([progress_bar.tasks[task_id]]))

        # Next workflow
        next_wf = get_next_pending_workflow()
        if next_wf:
            console.print(f"\n[bold green]Next:[/bold green] {next_wf['id'].replace('-', ' ').title()} ({next_wf['agent']})")
            console.print(f"  {next_wf.get('note', '')}")
        else:
            console.print("\n[bold green]✅ All workflows complete![/bold green]")

        # Pending workflows table
        if pending_workflows[:5]:
            console.print("\n[bold]Pending Workflows:[/bold]")
            table = Table(box=box.ROUNDED)
            table.add_column("Workflow", style="cyan")
            table.add_column("Agent", style="magenta")
            table.add_column("Type", style="yellow")

            for wf in pending_workflows[:5]:
                table.add_row(
                    wf['name'],
                    wf['agent'],
                    wf['status_type']
                )

            console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def run(
    workflow_id: Optional[str] = typer.Argument(None, help="Workflow ID to run"),
    phase: Optional[int] = typer.Option(None, "--phase", "-p", help="Run entire phase (0-3)"),
    parallel: bool = typer.Option(False, "--parallel", help="Run workflows in parallel"),
    auto_level: str = typer.Option("low", "--auto", "-a", help="Autonomy level: low|medium|high"),
    output_format: str = typer.Option("text", "--output-format", "-o", help="Output format: text|json|debug"),
):
    """
    ⚙️  Run BMM workflows using droid exec with MCP server attached

    Examples:
        bmm run                          # Run next workflow
        bmm run prd                      # Run specific workflow
        bmm run --phase 0                # Run Phase 0 (Discovery)
        bmm run --phase 0 --parallel     # Run Phase 0 in parallel
        bmm run --auto medium            # Medium autonomy level
        bmm run -o json                  # JSON output format
    """
    try:
        detect_agent_cli()  # Verify droid is available
        project_root = get_project_root()
        mcp_server = get_mcp_server_path()

        if phase is not None:
            # Run entire phase
            phase_names = ["Discovery", "Planning", "Solutioning", "Implementation"]
            console.print(f"\n[bold cyan]Running Phase {phase}: {phase_names[phase]}[/bold cyan]")

            # Build instruction for agent to use run_phase tool
            instruction = f"""Use the run_phase tool from the BMM MCP server (located at {mcp_server}) with:
- phase={phase}
- parallel={str(parallel).lower()}
- auto=True

The MCP server provides workflow automation tools. Call run_phase to execute all workflows in phase {phase}."""

            cmd, env = build_droid_command(
                instruction=instruction,
                project_root=project_root,
                mcp_server=mcp_server,
                auto_level=auto_level,
                output_format=output_format
            )

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                task = progress.add_task(f"Phase {phase}...", total=100)
                result = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
                progress.update(task, completed=100)

            if result.returncode == 0:
                if output_format == "json":
                    try:
                        import json
                        data = json.loads(result.stdout)
                        console.print(Panel(
                            json.dumps(data, indent=2),
                            title="✅ Phase Complete",
                            border_style="green"
                        ))
                    except json.JSONDecodeError:
                        console.print(Panel(result.stdout, title="✅ Phase Complete", border_style="green"))
                else:
                    console.print(Panel(result.stdout if result.stdout else "✅ Phase Complete", title="✅ Phase Complete", border_style="green"))
            else:
                console.print("[bold red]Error:[/bold red] Phase execution failed")
                if result.stderr:
                    console.print(f"[dim]{result.stderr}[/dim]")

        elif workflow_id:
            # Run specific workflow
            console.print(f"\n[bold cyan]Running workflow: {workflow_id}[/bold cyan]")

            workflow = get_workflow_config(workflow_id)
            if not workflow:
                console.print(f"[bold red]Error:[/bold red] Workflow '{workflow_id}' not found")
                return

            # Build instruction for agent to use run_workflow tool
            instruction = f"""Use the run_workflow tool from the BMM MCP server (located at {mcp_server}) with:
- workflow_id='{workflow_id}'
- auto=True

The MCP server provides workflow automation tools. Call run_workflow to execute the '{workflow_id}' workflow."""

            cmd, env = build_droid_command(
                instruction=instruction,
                project_root=project_root,
                mcp_server=mcp_server,
                auto_level=auto_level,
                output_format=output_format
            )

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task(f"{workflow_id}...", total=None)
                result = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
                progress.update(task, completed=True)

            if result.returncode == 0:
                if output_format == "json":
                    try:
                        import json
                        data = json.loads(result.stdout)
                        console.print(Panel(
                            json.dumps(data, indent=2),
                            title="✅ Complete",
                            border_style="green"
                        ))
                    except json.JSONDecodeError:
                        console.print(Panel(result.stdout, title="✅ Complete", border_style="green"))
                else:
                    console.print(Panel(result.stdout if result.stdout else "✅ Complete", title="✅ Complete", border_style="green"))
            else:
                console.print("[bold red]Error:[/bold red] Workflow execution failed")
                if result.stderr:
                    console.print(f"[dim]{result.stderr}[/dim]")

        else:
            # Run next workflow
            console.print("\n[bold cyan]Running next workflow...[/bold cyan]")

            next_wf = get_next_pending_workflow()
            if not next_wf:
                console.print("[green]All workflows complete! 🎉[/green]")
                return

            wf_name = next_wf['id'].replace('-', ' ').title()
            console.print(f"Next: [bold]{wf_name}[/bold] ({next_wf['agent']})")

            # Build instruction for agent to use run_workflow tool
            instruction = f"""Use the run_workflow tool from the BMM MCP server (located at {mcp_server}) with:
- workflow_id='{next_wf['id']}'
- auto=True

The MCP server provides workflow automation tools. Call run_workflow to execute the next pending workflow."""

            cmd, env = build_droid_command(
                instruction=instruction,
                project_root=project_root,
                mcp_server=mcp_server,
                auto_level=auto_level,
                output_format=output_format
            )

            result = subprocess.run(cmd, cwd=project_root, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                if output_format == "json":
                    try:
                        import json
                        data = json.loads(result.stdout)
                        console.print(Panel(
                            json.dumps(data, indent=2),
                            title="✅ Complete",
                            border_style="green"
                        ))
                    except json.JSONDecodeError:
                        console.print(Panel(result.stdout, title="✅ Complete", border_style="green"))
                else:
                    console.print(Panel(result.stdout if result.stdout else "✅ Complete", title="✅ Complete", border_style="green"))
            else:
                console.print("[bold red]Error:[/bold red] Workflow execution failed")
                if result.stderr:
                    console.print(f"[dim]{result.stderr}[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def next(
    auto_level: str = typer.Option("low", "--auto", "-a", help="Autonomy level: low|medium|high")
):
    """
    ▶️  Run the next pending workflow
    """
    run(workflow_id=None, phase=None, parallel=False, auto_level=auto_level, output_format="text")

@app.command()
def resources():
    """
    📚 List available MCP resources
    """
    async def _list_resources():
        client = get_mcp_client()
        async with client:
            return await client.list_resources()

    try:
        # List resources
        resource_list = asyncio.run(_list_resources())

        console.print("\n[bold cyan]Available Resources:[/bold cyan]\n")

        tree = Tree("📚 BMM Resources")
        for resource in resource_list:
            tree.add(f"[cyan]{resource['uri']}[/cyan] - {resource.get('description', 'No description')}")

        console.print(tree)
        console.print("\n[dim]Use 'bmm read <uri>' to read a resource[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def read(uri: str):
    """
    📖 Read an MCP resource

    Example: bmm read bmm://workflow-status
    """
    async def _read_resource(u: str):
        client = get_mcp_client()
        async with client:
            return await client.read_resource(u)

    try:
        content = asyncio.run(_read_resource(uri))

        console.print(Panel(
            content,
            title=f"📖 {uri}",
            border_style="cyan"
        ))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def prompts():
    """
    💬 List available MCP prompts
    """
    async def _list_prompts():
        client = get_mcp_client()
        async with client:
            return await client.list_prompts()

    try:
        prompt_list = asyncio.run(_list_prompts())

        console.print("\n[bold cyan]Available Prompts:[/bold cyan]\n")

        table = Table(box=box.ROUNDED)
        table.add_column("Prompt", style="cyan")
        table.add_column("Description", style="white")

        for prompt in prompt_list:
            table.add_row(
                prompt['name'],
                prompt.get('description', 'No description')
            )

        console.print(table)
        console.print("\n[dim]Prompts can be used by LLM clients for consistent workflow execution[/dim]")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def tools():
    """
    🔧 List available MCP tools
    """
    async def _list_tools():
        client = get_mcp_client()
        async with client:
            return await client.list_tools()

    try:
        tool_list = asyncio.run(_list_tools())

        console.print("\n[bold cyan]Available Tools:[/bold cyan]\n")

        table = Table(box=box.ROUNDED)
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="white")
        table.add_column("Icon", style="yellow")

        for tool in tool_list:
            table.add_row(
                tool['name'],
                tool.get('description', 'No description'),
                tool.get('icon', '')
            )

        console.print(table)

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def config():
    """
    ⚙️  Show BMM configuration
    """
    async def _read_config():
        client = get_mcp_client()
        async with client:
            return await client.read_resource("bmm://project-config")

    try:
        config_content = asyncio.run(_read_config())

        console.print(Panel(
            config_content,
            title="⚙️  BMM Configuration",
            border_style="cyan"
        ))

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")

@app.command()
def server():
    """
    🖥️  Start BMM MCP server (for debugging)
    """
    console.print("[bold cyan]Starting BMM MCP Server...[/bold cyan]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    import subprocess
    server_path = Path(__file__).parent / "bmm_server.py"

    try:
        subprocess.run(["python3", str(server_path)])
    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/yellow]")

if __name__ == "__main__":
    app()

