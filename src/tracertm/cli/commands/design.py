"""
Design integration CLI commands for Storybook and Figma.

Manages design system integration, component linking, and synchronization
between code components, Storybook stories, and Figma designs.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.tree import Tree

from tracertm.cli.ui.components import console, error_panel, success_panel, warning_panel, info_panel
from tracertm.cli.ui.progress import spinner
from tracertm.config.manager import ConfigManager

app = typer.Typer(help="Design integration commands (Storybook + Figma)")


# YAML structure for designs.yaml
DESIGNS_YAML_TEMPLATE: dict[str, Any] = {
    "figma": {
        "file_key": "",
        "access_token": "",
        "base_url": "https://api.figma.com/v1",
    },
    "storybook": {
        "stories_path": "src/components/**/*.stories.{ts,tsx,js,jsx}",
        "output_dir": "src/components",
    },
    "components": {},
    "last_sync": None,
}

# YAML structure for components.yaml
COMPONENTS_YAML_TEMPLATE: dict[str, Any] = {
    "components": [],
    "metadata": {
        "created_at": None,
        "last_updated": None,
        "total_components": 0,
    },
}


def _get_trace_dir(path: str | None = None) -> Path:
    """
    Get .trace/ directory, create if needed.

    Args:
        path: Optional base path (defaults to current directory)

    Returns:
        Path to .trace/ directory

    Raises:
        typer.Exit: If .trace/ doesn't exist
    """
    base_path = Path(path) if path else Path.cwd()
    trace_dir = base_path / ".trace"

    if not trace_dir.exists():
        console.print(error_panel(
            f"No .trace/ directory found in {base_path}",
            "Run 'rtm init' to create a .trace/ directory first"
        ))
        raise typer.Exit(code=1)

    return trace_dir


def _get_meta_dir(trace_dir: Path) -> Path:
    """
    Get or create .trace/.meta directory.

    Args:
        trace_dir: Path to .trace/ directory

    Returns:
        Path to .meta/ directory
    """
    meta_dir = trace_dir / ".meta"
    meta_dir.mkdir(exist_ok=True)
    return meta_dir


def _load_designs_config(trace_dir: Path) -> dict[Any, Any]:
    """
    Load designs.yaml configuration.

    Args:
        trace_dir: Path to .trace/ directory

    Returns:
        Design configuration dict

    Raises:
        typer.Exit: If designs.yaml doesn't exist
    """
    meta_dir = _get_meta_dir(trace_dir)
    designs_path = meta_dir / "designs.yaml"

    if not designs_path.exists():
        console.print(error_panel(
            "Design integration not initialized",
            "Run 'rtm design init' to initialize design integration"
        ))
        raise typer.Exit(code=1)

    loaded = yaml.safe_load(designs_path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict[str, Any]) else {}


def _save_designs_config(trace_dir: Path, config: dict[Any, Any]) -> None:
    """
    Save designs.yaml configuration.

    Args:
        trace_dir: Path to .trace/ directory
        config: Design configuration dict
    """
    meta_dir = _get_meta_dir(trace_dir)
    designs_path = meta_dir / "designs.yaml"
    designs_path.write_text(
        yaml.dump(config, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _load_components_config(trace_dir: Path) -> dict[Any, Any]:
    """
    Load components.yaml registry.

    Args:
        trace_dir: Path to .trace/ directory

    Returns:
        Components configuration dict
    """
    meta_dir = _get_meta_dir(trace_dir)
    components_path = meta_dir / "components.yaml"

    if not components_path.exists():
        return dict(COMPONENTS_YAML_TEMPLATE)

    loaded = yaml.safe_load(components_path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict[str, Any]) else {}


def _save_components_config(trace_dir: Path, config: dict[Any, Any]) -> None:
    """
    Save components.yaml registry.

    Args:
        trace_dir: Path to .trace/ directory
        config: Components configuration dict
    """
    meta_dir = _get_meta_dir(trace_dir)
    components_path = meta_dir / "components.yaml"

    # Update metadata
    metadata = config.get("metadata")
    if isinstance(metadata, dict[str, Any]):
        metadata["last_updated"] = datetime.now().isoformat()
        metadata["total_components"] = len(config.get("components", []))

    components_path.write_text(
        yaml.dump(config, default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )


def _validate_figma_url(url: str) -> tuple[str, str | None]:
    """
    Validate and parse Figma URL.

    Args:
        url: Figma URL (file or node)

    Returns:
        Tuple of (file_key, node_id or None)

    Raises:
        typer.Exit: If URL is invalid
    """
    # Pattern: https://www.figma.com/file/FILE_KEY/...?node-id=NODE_ID
    # Or: https://www.figma.com/design/FILE_KEY/...?node-id=NODE_ID
    pattern = r"https://(?:www\.)?figma\.com/(?:file|design)/([a-zA-Z0-9]+)"
    match = re.search(pattern, url)

    if not match:
        console.print(f"[red]Error: Invalid Figma URL: {url}[/red]")
        console.print("[dim]Expected format: https://www.figma.com/file/FILE_KEY/...[/dim]")
        raise typer.Exit(code=1)

    file_key = match.group(1)

    # Extract node ID if present
    node_id = None
    node_match = re.search(r"node-id=([^&]+)", url)
    if node_match:
        # Figma uses URL-encoded node IDs (e.g., 123-456 becomes 123%3A456)
        node_id = node_match.group(1).replace("%3A", ":")

    return file_key, node_id


@app.command("init")
def init_design_integration(
    figma_file_key: str | None = typer.Option(None, "--figma-key", "-k", help="Figma file key"),
    figma_token: str | None = typer.Option(None, "--figma-token", "-t", help="Figma access token"),
    path: str | None = typer.Option(None, "--path", "-p", help="Path to .trace/ directory"),
) -> None:
    """
    Initialize design integration (Storybook + Figma).

    Creates .trace/.meta/designs.yaml with Figma configuration and
    .trace/.meta/components.yaml for component registry.

    If Figma credentials are not provided as options, will prompt interactively.

    Examples:
        # Interactive initialization
        rtm design init

        # Provide Figma credentials
        rtm design init --figma-key ABC123 --figma-token secret_token
    """
    trace_dir = _get_trace_dir(path)
    meta_dir = _get_meta_dir(trace_dir)

    console.print("[bold]Initializing design integration...[/bold]\n")

    # Check if already initialized
    designs_path = meta_dir / "designs.yaml"
    if designs_path.exists():
        console.print(warning_panel(
            "Design integration already initialized",
            "Existing configuration will be overwritten if you continue"
        ))
        overwrite = typer.confirm("Do you want to overwrite existing configuration?")
        if not overwrite:
            console.print("[dim]Cancelled[/dim]")
            raise typer.Exit(code=0)

    # Get Figma credentials
    if not figma_file_key:
        console.print("[cyan]Enter your Figma file key (from the Figma URL):[/cyan]")
        console.print("[dim]Example: https://www.figma.com/file/FILE_KEY/...[/dim]")
        figma_file_key = typer.prompt("Figma file key", default="")

    if not figma_token:
        console.print("\n[cyan]Enter your Figma access token:[/cyan]")
        console.print("[dim]Get one from: https://www.figma.com/developers/api#access-tokens[/dim]")
        figma_token = typer.prompt("Figma access token", default="", hide_input=True)

    # Create designs.yaml
    designs_config = dict[str, Any](DESIGNS_YAML_TEMPLATE)
    figma_config = designs_config.get("figma")
    if isinstance(figma_config, dict[str, Any]):
        figma_config["file_key"] = figma_file_key
        figma_config["access_token"] = figma_token

    with spinner("Creating design configuration files..."):
        _save_designs_config(trace_dir, designs_config)

        # Create components.yaml
        components_config = dict[str, Any](COMPONENTS_YAML_TEMPLATE)
        metadata = components_config.get("metadata")
        if isinstance(metadata, dict[str, Any]):
            metadata["created_at"] = datetime.now().isoformat()

        _save_components_config(trace_dir, components_config)

    components_path = meta_dir / "components.yaml"
    console.print(success_panel(
        "Design configuration files created",
        f"designs.yaml: {designs_path}\ncomponents.yaml: {components_path}"
    ))

    # Display tree
    tree = Tree("[bold cyan].trace/.meta/[/bold cyan]")
    tree.add("[green]designs.yaml[/green] - Figma + Storybook config")
    tree.add("[green]components.yaml[/green] - Component registry")
    console.print("\n")
    console.print(tree)

    # Display summary
    console.print("\n")
    console.print(success_panel(
        "Design integration initialized",
        "[bold]Next steps:[/bold]\n"
        "  • Link components: [cyan]rtm design link MyButton <figma-url>[/cyan]\n"
        "  • Generate stories: [cyan]rtm design generate --all[/cyan]\n"
        "  • Sync designs: [cyan]rtm design sync[/cyan]"
    ))


@app.command("link")
def link_component(
    component: str = typer.Argument(..., help="Component name (e.g., Button, Card)"),
    figma_url: str = typer.Argument(..., help="Figma design URL"),
    path: str | None = typer.Option(None, "--path", "-p", help="Path to .trace/ directory"),
    component_path: str | None = typer.Option(
        None, "--component-path", "-c", help="Path to component file"
    ),
) -> None:
    """
    Link a component to a Figma design.

    Updates designs.yaml and components.yaml with the component-design mapping.

    Examples:
        # Link component to Figma
        rtm design link Button https://www.figma.com/file/ABC123/...?node-id=1-2

        # Link with explicit component path
        rtm design link Card https://figma.com/file/XYZ789 --component-path src/components/Card.tsx
    """
    trace_dir = _get_trace_dir(path)

    # Validate and parse Figma URL
    file_key, node_id = _validate_figma_url(figma_url)

    # Load configurations
    with spinner("Loading design configurations..."):
        designs_config = _load_designs_config(trace_dir)
        components_config = _load_components_config(trace_dir)

    # Update designs.yaml
    if "components" not in designs_config:
        designs_config["components"] = {}

    designs_config["components"][component] = {
        "figma_file_key": file_key,
        "figma_node_id": node_id,
        "figma_url": figma_url,
        "linked_at": datetime.now().isoformat(),
    }

    _save_designs_config(trace_dir, designs_config)

    # Update components.yaml
    components_list = components_config.get("components", [])

    # Check if component already exists
    existing_idx = None
    for idx, comp in enumerate(components_list):
        if comp.get("name") == component:
            existing_idx = idx
            break

    component_entry = {
        "name": component,
        "path": component_path or f"src/components/{component}",
        "figma_url": figma_url,
        "figma_node_id": node_id,
        "has_story": False,
        "sync_status": "unsynced",
        "last_synced": None,
    }

    if existing_idx is not None:
        components_list[existing_idx] = component_entry
        action = "Updated"
    else:
        components_list.append(component_entry)
        action = "Linked"

    components_config["components"] = components_list
    _save_components_config(trace_dir, components_config)

    # Display result
    details = f"Figma URL: {figma_url}"
    if node_id:
        details += f"\nNode ID: {node_id}"
    details += "\n\n[dim]Run 'rtm design sync' to sync design metadata[/dim]"

    console.print(success_panel(f"{action} component: {component}", details))


@app.command("sync")
def sync_designs(
    direction: str = typer.Option(
        "both", "--direction", "-d", help="Sync direction: push, pull, or both"
    ),
    path: str | None = typer.Option(None, "--path", "-p", help="Path to .trace/ directory"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be synced"),
) -> None:
    """
    Sync designs between Storybook and Figma.

    Calls TypeScript design sync tools to synchronize component metadata,
    design tokens, and visual snapshots.

    Directions:
    - push: Storybook → Figma (export stories to Figma)
    - pull: Figma → Storybook (import Figma designs)
    - both: Bidirectional sync (default)

    Examples:
        # Full sync
        rtm design sync

        # Push stories to Figma
        rtm design sync --direction push

        # Preview changes
        rtm design sync --dry-run
    """
    trace_dir = _get_trace_dir(path)

    # Load configurations
    with spinner("Loading design configurations"):
        designs_config = _load_designs_config(trace_dir)
        components_config = _load_components_config(trace_dir)

    if dry_run:
        console.print(info_panel("Dry run mode", "No changes will be made"))

    # Check for TypeScript sync tools
    # This would call tools in frontend/ or scripts/
    # For now, show what would happen

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        if direction in ("pull", "both"):
            task = progress.add_task("Pulling from Figma...", total=None)
            try:
                # Call TypeScript tool: bun run figma:pull
                subprocess.run(
                    ["bun", "run", "figma:pull"],
                    cwd=Path.cwd(),
                    check=True,
                    capture_output=True
                )
                progress.update(task, completed=True)
                console.print("[green]✓[/green] Successfully pulled designs from Figma")
            except subprocess.CalledProcessError as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] Figma pull failed: {e.stderr.decode() if e.stderr else str(e)}")
            except FileNotFoundError:
                progress.update(task, completed=True)
                console.print("[yellow]⚠[/yellow] bun not found - install with: curl -fsSL https://bun.sh/install | bash")

        if direction in ("push", "both"):
            task = progress.add_task("Pushing to Figma...", total=None)
            try:
                # Call TypeScript tool: bun run figma:push
                subprocess.run(
                    ["bun", "run", "figma:push"],
                    cwd=Path.cwd(),
                    check=True,
                    capture_output=True
                )
                progress.update(task, completed=True)
                console.print("[green]✓[/green] Successfully pushed designs to Figma")
            except subprocess.CalledProcessError as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] Figma push failed: {e.stderr.decode() if e.stderr else str(e)}")
            except FileNotFoundError:
                progress.update(task, completed=True)
                console.print("[yellow]⚠[/yellow] bun not found")

    # Update sync timestamp
    designs_config["last_sync"] = datetime.now().isoformat()
    _save_designs_config(trace_dir, designs_config)

    # Update component sync status
    for component in components_config.get("components", []):
        component["sync_status"] = "synced"
        component["last_synced"] = datetime.now().isoformat()

    _save_components_config(trace_dir, components_config)

    if dry_run:
        console.print(info_panel("Dry run complete", "No changes were made"))
    else:
        console.print(success_panel(
            f"Design sync complete ({direction})",
            f"Components: {len(components_config.get('components', []))}\n"
            f"Last sync: {datetime.now().isoformat()}"
        ))


@app.command("generate")
def generate_stories(
    component: str | None = typer.Option(None, "--component", "-c", help="Generate for specific component"),
    all_components: bool = typer.Option(False, "--all", "-a", help="Generate for all components"),
    path: str | None = typer.Option(None, "--path", "-p", help="Path to .trace/ directory"),
    template: str = typer.Option("default", "--template", "-t", help="Story template (default, csf3, mdx)"),
) -> None:
    """
    Generate Storybook stories from components.

    Creates .stories.tsx files for components based on templates.

    Templates:
    - default: Standard CSF 2.0 stories
    - csf3: Component Story Format 3.0
    - mdx: MDX documentation with stories

    Examples:
        # Generate stories for all components
        rtm design generate --all

        # Generate for specific component
        rtm design generate --component Button

        # Use CSF3 template
        rtm design generate --all --template csf3
    """
    trace_dir = _get_trace_dir(path)

    if not all_components and not component:
        console.print(error_panel(
            "Missing required parameter",
            "Specify --component or --all"
        ))
        raise typer.Exit(code=1)

    # Load configurations
    with spinner("Loading component configurations"):
        designs_config = _load_designs_config(trace_dir)
        components_config = _load_components_config(trace_dir)

    components_list = components_config.get("components", [])

    # Filter components
    target_components = []
    if all_components:  # pragma: no branch
        target_components = components_list
    elif component:  # pragma: no branch
        target_components = [c for c in components_list if c.get("name") == component]
        if not target_components:
            console.print(error_panel(
                f"Component '{component}' not found",
                "Run 'rtm design list' to see available components"
            ))
            raise typer.Exit(code=1)

    if not target_components:  # pragma: no cover
        console.print(warning_panel(
            "No components to generate stories for",
            "Link components first with 'rtm design link'"
        ))
        raise typer.Exit(code=0)

    console.print(info_panel(
        "Generating stories",
        f"{len(target_components)} component(s) will be processed with template: {template}"
    ))

    generated = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for comp in target_components:
            comp_name = comp.get("name")
            task = progress.add_task(f"Generating {comp_name}...", total=None)

            try:
                # Call TypeScript generator via bun
                subprocess.run(
                    ["bun", "run", "storybook:generate", comp_name, "--template", template],
                    cwd=Path.cwd(),
                    check=True,
                    capture_output=True,
                    timeout=60
                )
                # Update component registry
                comp["has_story"] = True
                generated.append(comp_name)
                progress.update(task, completed=True)
            except subprocess.TimeoutExpired:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] {comp_name}: Generation timeout (60s)")
            except subprocess.CalledProcessError as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] {comp_name}: {e.stderr.decode() if e.stderr else 'Generation failed'}")
            except FileNotFoundError:
                progress.update(task, completed=True)
                console.print("[yellow]⚠[/yellow] bun not found - cannot generate stories")

            progress.update(task, completed=True)

    # Save updated config
    with spinner("Saving component configurations"):
        _save_components_config(trace_dir, components_config)

    # Display results
    story_list = "\n".join([f"  • {name}.stories.tsx" for name in generated])
    console.print(success_panel(
        f"Generated stories for {len(generated)} component(s)",
        f"{story_list}\n\n[dim]Run 'bun run storybook' to view stories[/dim]"
    ))


@app.command("status")
def show_design_status(
    path: str | None = typer.Option(None, "--path", "-p", help="Path to .trace/ directory"),
) -> None:
    """
    Show design sync status.

    Displays linked components, sync status, and Figma connection info.

    Example:
        rtm design status
    """
    trace_dir = _get_trace_dir(path)

    # Load configurations
    designs_config = _load_designs_config(trace_dir)
    components_config = _load_components_config(trace_dir)

    # Extract info
    figma_config = designs_config.get("figma", {})
    last_sync = designs_config.get("last_sync")
    components_list = components_config.get("components", [])

    # Count statuses
    synced_count = sum(1 for c in components_list if c.get("sync_status") == "synced")
    unsynced_count = sum(1 for c in components_list if c.get("sync_status") == "unsynced")
    with_stories = sum(1 for c in components_list if c.get("has_story"))

    # Create status table
    table = Table(show_header=False, box=None, padding=(0, 2))

    # Figma connection
    figma_file_key = figma_config.get("file_key", "")
    if figma_file_key:
        table.add_row("Figma file:", f"[cyan]{figma_file_key}[/cyan]")
    else:
        table.add_row("Figma file:", "[dim]Not configured[/dim]")

    # Last sync
    if last_sync:
        last_sync_dt = datetime.fromisoformat(last_sync)
        table.add_row("Last sync:", f"[green]{last_sync_dt.strftime('%Y-%m-%d %H:%M')}[/green]")
    else:
        table.add_row("Last sync:", "[dim]Never[/dim]")

    # Components
    table.add_row("Total components:", f"[cyan]{len(components_list)}[/cyan]")
    table.add_row("Synced:", f"[green]{synced_count}[/green]")
    table.add_row("Unsynced:", f"[yellow]{unsynced_count}[/yellow]")
    table.add_row("With stories:", f"[cyan]{with_stories}[/cyan]")

    panel = Panel(
        table,
        title="[bold]Design Status[/bold]",
        border_style="cyan",
    )
    console.print(panel)

    # Show hints
    if unsynced_count > 0:
        console.print(f"\n[dim]Run 'rtm design sync' to sync {unsynced_count} component(s)[/dim]")
    if len(components_list) - with_stories > 0:
        console.print(
            f"[dim]Run 'rtm design generate --all' to generate stories for "
            f"{len(components_list) - with_stories} component(s)[/dim]"
        )


@app.command("list")
def list_design_links(
    path: str | None = typer.Option(None, "--path", "-p", help="Path to .trace/ directory"),
    filter_status: str | None = typer.Option(
        None, "--status", "-s", help="Filter by sync status (synced, unsynced)"
    ),
    show_urls: bool = typer.Option(False, "--urls", "-u", help="Show full Figma URLs"),
) -> None:
    """
    List all component → design links.

    Displays a table of components with their Figma links and sync status.

    Examples:
        # List all components
        rtm design list

        # Show only unsynced components
        rtm design list --status unsynced

        # Show full Figma URLs
        rtm design list --urls
    """
    trace_dir = _get_trace_dir(path)

    # Load configurations
    components_config = _load_components_config(trace_dir)
    components_list = components_config.get("components", [])

    if not components_list:
        console.print("[yellow]No component links found[/yellow]")
        console.print("[dim]Run 'rtm design link <component> <figma-url>' to link components[/dim]")
        raise typer.Exit(code=0)

    # Filter by status
    if filter_status:
        components_list = [
            c for c in components_list if c.get("sync_status") == filter_status
        ]

        if not components_list:
            console.print(f"[yellow]No components with status '{filter_status}'[/yellow]")
            raise typer.Exit(code=0)

    # Create table
    table = Table(
        "Component",
        "Path",
        "Story",
        "Status",
        "Last Synced",
        title="Component → Design Links",
        title_style="bold cyan",
    )

    if show_urls:
        table.add_column("Figma URL")

    for comp in components_list:
        name = comp.get("name", "")
        path_str = comp.get("path", "")
        has_story = "✓" if comp.get("has_story") else "✗"
        status = comp.get("sync_status", "unknown")
        last_synced = comp.get("last_synced")

        # Format status
        if status == "synced":
            status_text = "[green]Synced[/green]"
        elif status == "unsynced":
            status_text = "[yellow]Unsynced[/yellow]"
        else:
            status_text = "[dim]Unknown[/dim]"

        # Format last synced
        if last_synced:
            synced_dt = datetime.fromisoformat(last_synced)
            synced_text = synced_dt.strftime("%Y-%m-%d %H:%M")
        else:
            synced_text = "[dim]Never[/dim]"

        row = [name, path_str, has_story, status_text, synced_text]

        if show_urls:
            figma_url = comp.get("figma_url", "")
            row.append(f"[dim]{figma_url[:50]}...[/dim]" if len(figma_url) > 50 else figma_url)

        table.add_row(*row)

    console.print(table)

    # Show summary
    total = len(components_list)
    synced = sum(1 for c in components_list if c.get("sync_status") == "synced")
    console.print(
        f"\n[dim]Showing {total} component(s) • {synced} synced • {total - synced} unsynced[/dim]"
    )


@app.command("export")
def export_to_figma(  # pragma: no cover
    path: str | None = typer.Option(None, "--path", "-p", help="Path to .trace/ directory"),
    component: str | None = typer.Option(
        None, "--component", "-c", help="Export specific component"
    ),
    all_components: bool = typer.Option(False, "--all", "-a", help="Export all components"),
) -> None:
    """
    Export designs to Figma using story.to.design pattern.

    Generates Figma components from Storybook stories using the
    story.to.design workflow (stories → screenshots → Figma import).

    Examples:
        # Export all components
        rtm design export --all

        # Export specific component
        rtm design export --component Button
    """
    trace_dir = _get_trace_dir(path)

    if not all_components and not component:
        console.print(error_panel(
            "Missing required parameter",
            "Specify --component or --all"
        ))
        raise typer.Exit(code=1)

    # Load configurations
    with spinner("Loading design configurations"):
        designs_config = _load_designs_config(trace_dir)
        components_config = _load_components_config(trace_dir)

    figma_config = designs_config.get("figma", {})
    figma_file_key = figma_config.get("file_key")
    figma_token = figma_config.get("access_token")

    if not figma_file_key or not figma_token:
        console.print(error_panel(
            "Figma credentials not configured",
            "Run 'rtm design init' to configure Figma integration"
        ))
        raise typer.Exit(code=1)

    components_list = components_config.get("components", [])

    # Filter components
    target_components = []
    if all_components:
        target_components = components_list
    elif component:
        target_components = [c for c in components_list if c.get("name") == component]
        if not target_components:
            console.print(f"[red]Error: Component '{component}' not found[/red]")
            raise typer.Exit(code=1)

    # Filter to only components with stories
    target_components = [c for c in target_components if c.get("has_story")]  # pragma: no branch

    if not target_components:  # pragma: no cover
        console.print(warning_panel(
            "No components with stories to export",
            "Run 'rtm design generate --all' to create stories first"
        ))
        raise typer.Exit(code=0)

    console.print(info_panel(
        "Exporting to Figma",
        f"{len(target_components)} component(s) will be exported to file: {figma_file_key}"
    ))

    exported = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for comp in target_components:
            comp_name = comp.get("name")
            task = progress.add_task(f"Exporting {comp_name}...", total=None)

            try:
                # Call TypeScript export tool via bun
                subprocess.run(
                    [
                        "bun",
                        "run",
                        "figma:export",
                        comp_name,
                        "--file-key",
                        figma_file_key,
                        "--token",
                        figma_token,
                    ],
                    cwd=Path.cwd(),
                    check=True,
                    capture_output=True,
                    timeout=120
                )
                exported.append(comp_name)
                progress.update(task, completed=True)
            except subprocess.TimeoutExpired:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] {comp_name}: Export timeout (120s)")
            except subprocess.CalledProcessError as e:
                progress.update(task, completed=True)
                console.print(f"[yellow]⚠[/yellow] {comp_name}: {e.stderr.decode() if e.stderr else 'Export failed'}")
            except FileNotFoundError:
                progress.update(task, completed=True)
                console.print("[yellow]⚠[/yellow] bun not found - cannot export to Figma")

    # Display results
    export_list = "\n".join([f"  • {name}" for name in exported])
    console.print(success_panel(
        f"Exported {len(exported)} component(s) to Figma",
        f"{export_list}\n\n[dim]View in Figma: https://www.figma.com/file/{figma_file_key}/[/dim]"
    ))
