"""
Backup and restore CLI commands for TraceRTM.
Refactored to use ProjectBackupService for core logic.
"""

import gzip
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import typer
import yaml
from rich.table import Table

from tracertm.cli.ui import (
    console,
    success_panel,
    error_panel,
    warning_panel,
    info_panel,
    spinner,
    format_filesize,
)
from tracertm.config.manager import ConfigManager
from tracertm.storage import LocalStorageManager

app = typer.Typer(help="Backup, restore, and template management")

def get_service(session: Any) -> Any:
    from tracertm.services.project_backup_service import ProjectBackupService
    return ProjectBackupService(session)

@app.command("export")
def backup_project(
    output: Path = typer.Option(
        None, "--output", "-o", help="Output file path (default: tracertm_backup_TIMESTAMP.json.gz)"
    ),
    compress: bool = typer.Option(
        True, "--compress/--no-compress", help="Compress backup (default: compress)"
    ),
    project_id: Optional[str] = typer.Option(
        None, "--project-id", help="Project ID to backup (default: current project)"
    ),
    include_history: bool = typer.Option(False, "--history", help="Include event history"),
    include_agents: bool = typer.Option(False, "--agents", help="Include agent data"),
) -> None:
    """
    Backup project data to a file.
    """
    storage = LocalStorageManager()
    config_manager = ConfigManager()
    
    if not project_id:
        project_id = config_manager.get("current_project_id")
        if not project_id:
            console.print(error_panel("No current project found. Use --project-id.", "Backup Error"))
            raise typer.Exit(1)

    if not output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix = ".json.gz" if compress else ".json"
        output = Path(f"tracertm_backup_{timestamp}{suffix}")

    try:
        with storage.get_session() as session:
            service = get_service(session)
            with spinner(f"Backing up project {project_id}..."):
                backup_data = service.backup_project(
                    project_id, 
                    include_history=include_history, 
                    include_agents=include_agents
                )

            with spinner("Writing backup file..."):
                if compress:
                    with gzip.open(output, "wt", encoding="utf-8") as f:
                        json.dump(backup_data, f, indent=2, default=str)
                else:
                    with open(output, "w", encoding="utf-8") as f:
                        json.dump(backup_data, f, indent=2, default=str)

        file_size = output.stat().st_size
        console.print(success_panel(
            f"Backup created: [cyan]{output}[/cyan]",
            f"Size: {format_filesize(file_size)} | Items: {len(backup_data.get('items', []))} | Links: {len(backup_data.get('links', []))}"
        ))
    except Exception as e:
        console.print(error_panel(f"Backup failed: {e}", "Error"))
        raise typer.Exit(1)

@app.command("import")
def restore_project(
    backup_file: Path = typer.Argument(..., help="Backup file path (.json or .json.gz)"),
    project_name: Optional[str] = typer.Option(None, "--name", "-n", help="New name for the restored project"),
    force: bool = typer.Option(False, "--force", "-f", help="Force restore without confirmation"),
)->  None:
    """
    Restore a project from a backup file.
    """
    if not backup_file.exists():
        console.print(error_panel(f"File not found: {backup_file}", "Restore Error"))
        raise typer.Exit(1)

    if not force:
        if not typer.confirm(f"Are you sure you want to restore from {backup_file}?"):
            raise typer.Exit(0)

    storage = LocalStorageManager()
    try:
        with spinner("Loading and validating backup..."):
            if backup_file.suffix == ".gz":
                with gzip.open(backup_file, "rt", encoding="utf-8") as f:
                    backup_data = json.load(f)
            else:
                with open(backup_file, encoding="utf-8") as f:
                    backup_data = json.load(f)

        with storage.get_session() as session:
            service = get_service(session)
            with spinner("Restoring project..."):
                new_id = service.restore_project(backup_data, project_name=project_name)
            
        console.print(success_panel(
            f"Project restored successfully!",
            f"New Project ID: [cyan]{new_id}[/cyan]\nUse [bold]rtm project use {new_id}[/bold] to switch to it."
        ))
    except Exception as e:
        console.print(error_panel(f"Restore failed: {e}", "Error"))
        raise typer.Exit(1)

@app.command("clone")
def clone_project(
    source_id: str = typer.Argument(..., help="Source project ID to clone"),
    target_name: str = typer.Argument(..., help="Name for the new cloned project"),
    no_items: bool = typer.Option(False, "--no-items", help="Do not clone items"),
    no_links: bool = typer.Option(False, "--no-links", help="Do not clone links"),
)->  None:
    """
    Clone an existing project.
    """
    storage = LocalStorageManager()
    try:
        with storage.get_session() as session:
            service = get_service(session)
            with spinner(f"Cloning project {source_id} to '{target_name}'..."):
                new_id = service.clone_project(
                    source_id, 
                    target_name, 
                    include_items=not no_items, 
                    include_links=not no_links
                )
        
        console.print(success_panel(
            f"Project cloned successfully!",
            f"New Project ID: [cyan]{new_id}[/cyan]"
        ))
    except Exception as e:
        console.print(error_panel(f"Clone failed: {e}", "Error"))
        raise typer.Exit(1)

@app.command("template")
def create_template(
    project_id: str = typer.Argument(..., help="Project ID to use as template"),
    template_name: str = typer.Argument(..., help="Name for the template"),
)->  None:
    """
    Create a project template from an existing project.
    """
    storage = LocalStorageManager()
    try:
        with storage.get_session() as session:
            service = get_service(session)
            with spinner(f"Creating template '{template_name}'..."):
                template_id = service.create_template(project_id, template_name)
        
        console.print(success_panel(
            f"Template '{template_name}' created!",
            f"Template ID: [cyan]{template_id}[/cyan]"
        ))
    except Exception as e:
        console.print(error_panel(f"Template creation failed: {e}", "Error"))
        raise typer.Exit(1)

@app.command("list-templates")
def list_templates() -> None:
    """
    List all available project templates.
    """
    storage = LocalStorageManager()
    try:
        with storage.get_session() as session:
            service = get_service(session)
            templates = service.list_templates()
        
        if not templates:
            console.print(info_panel("No templates found.", "Templates"))
            return

        table = Table(title="Project Templates")
        table.add_column("ID", style="dim")
        table.add_column("Template Name", style="cyan")
        table.add_column("Description")
        
        for t in templates:
            table.add_row(t["id"], t["template_name"], t["description"] or "")
            
        console.print(table)
    except Exception as e:
        console.print(error_panel(f"Failed to list templates: {e}", "Error"))
        raise typer.Exit(1)
