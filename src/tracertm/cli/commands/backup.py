"""
Backup and restore CLI commands.

Handles project backup, restore, and validation.
"""

import gzip
import json
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from sqlalchemy import text
from sqlalchemy.orm import Session

from tracertm.config.manager import ConfigManager
from tracertm.storage import LocalStorageManager

app = typer.Typer(help="Backup and restore commands")
console = Console()


@app.command("backup")
def backup_project(
    output: Path | None = typer.Option(
        None, "--output", "-o", help="Output file path (default: tracertm_backup_TIMESTAMP.json.gz)"
    ),
    compress: bool = typer.Option(
        True, "--compress/--no-compress", help="Compress backup (default: compress)"
    ),
    project_id: str | None = typer.Option(
        None, "--project-id", help="Project ID to backup (default: current project)"
    ),
) -> None:
    """
    Backup project data to a file.

    Creates a JSON backup of all project data including items, links, and configuration.

    Examples:
        # Create compressed backup
        rtm backup backup

        # Create uncompressed backup
        rtm backup backup --no-compress --output my_backup.json

        # Backup specific project
        rtm backup backup --project-id proj-12345
    """
    try:
        config_manager = ConfigManager()
        database_url = config_manager.get("database_url")

        if not database_url:
            console.print(
                "[red]✗[/red] No database configured. Run 'rtm config init' first."
            )
            raise typer.Exit(code=1)

        # Get current project if not specified
        if not project_id:
            project_id = config_manager.get("current_project_id")
            if not project_id:
                console.print(
                    "[red]✗[/red] No current project. Specify --project-id or initialize a project."
                )
                raise typer.Exit(code=1)

        # Generate output filename if not provided
        if not output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            suffix = ".json.gz" if compress else ".json"
            output = Path(f"tracertm_backup_{timestamp}{suffix}")

        storage = LocalStorageManager()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating backup...", total=None)

            # Export all data
            backup_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "project_id": project_id,
                "tables": {},
            }

            # Get all table names
            with storage.get_session() as session:
                result = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                tables = [row[0] for row in result]

                # Export each table
                for table in tables:
                    if table.startswith("alembic"):
                        continue

                    result = session.execute(text(f"SELECT * FROM {table}"))
                    rows = [dict(row._mapping) for row in result]

                    # Convert datetime objects to ISO format
                    for row in rows:
                        for key, value in row.items():
                            if isinstance(value, datetime):
                                row[key] = value.isoformat()

                    backup_data["tables"][table] = rows

            progress.update(task, description="Writing backup file...")

            # Write backup
            if compress:
                with gzip.open(output, "wt", encoding="utf-8") as f:
                    json.dump(backup_data, f, indent=2, default=str)
            else:
                with open(output, "w", encoding="utf-8") as f:
                    json.dump(backup_data, f, indent=2, default=str)

        file_size = output.stat().st_size / 1024  # KB
        console.print("[green]✓[/green] Backup created successfully!")
        console.print(f"[dim]File: {output}[/dim]")
        console.print(f"[dim]Size: {file_size:.2f} KB[/dim]")
        console.print(f"[dim]Tables: {len(backup_data['tables'])}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Backup failed: {e}")
        raise typer.Exit(code=1)


@app.command("restore")
def restore_project(
    backup_file: Path = typer.Argument(..., help="Backup file path (.json or .json.gz)"),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force restore without confirmation prompt"
    ),
) -> None:
    """
    Restore project data from a backup file.

    ⚠️  WARNING: This will overwrite existing data!

    Examples:
        # Restore from backup (with confirmation)
        rtm backup restore backup.json

        # Force restore without confirmation
        rtm backup restore backup.json.gz --force
    """
    try:
        if not backup_file.exists():
            console.print(f"[red]✗[/red] Backup file not found: {backup_file}")
            raise typer.Exit(code=1)

        # Confirm restore
        if not force:
            confirm = typer.confirm(
                "⚠️  This will overwrite existing data. Continue?", default=False
            )
            if not confirm:
                console.print("[yellow]Restore cancelled.[/yellow]")
                raise typer.Exit(code=0)

        config_manager = ConfigManager()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Loading backup...", total=None)

            # Load backup
            if backup_file.suffix == ".gz":
                with gzip.open(backup_file, "rt", encoding="utf-8") as f:
                    backup_data = json.load(f)
            else:
                with open(backup_file, encoding="utf-8") as f:
                    backup_data = json.load(f)

            progress.update(task, description="Validating backup...")

            # Validate backup format
            if not isinstance(backup_data, dict) or "version" not in backup_data:
                console.print("[red]✗[/red] Invalid backup file format")
                raise typer.Exit(code=1)

            if "tables" not in backup_data or not isinstance(backup_data["tables"], dict):
                console.print("[red]✗[/red] Backup missing table data")
                raise typer.Exit(code=1)

            progress.update(task, description="Clearing existing data...")

            # Restore tables in correct order (respecting foreign keys)
            storage = LocalStorageManager()
            with storage.get_session() as session:
                # Get all existing tables
                result = session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table'")
                )
                existing_tables = [row[0] for row in result]

                # Delete data from tables (skip migration tables)
                for table in existing_tables:
                    if not table.startswith("alembic"):
                        try:
                            session.execute(text(f"DELETE FROM {table}"))
                        except Exception as e:
                            console.print(f"[yellow]⚠[/yellow] Could not clear {table}: {e}")

                session.commit()

                progress.update(task, description="Restoring data...")

                # Restore tables
                tables_restored = 0
                for table, rows in backup_data.get("tables", {}).items():
                    if not rows:
                        continue

                    try:
                        # Get column names from first row
                        columns = list(rows[0].keys())
                        col_str = ", ".join(columns)
                        placeholders = ", ".join(["?" for _ in columns])

                        # Insert rows
                        for row in rows:
                            values = [row.get(col) for col in columns]
                            session.execute(
                                text(
                                    f"INSERT INTO {table} ({col_str}) VALUES ({placeholders})"
                                ),
                                values
                            )

                        tables_restored += 1
                    except Exception as e:
                        console.print(f"[yellow]⚠[/yellow] Error restoring {table}: {e}")

                session.commit()

            console.print("[green]✓[/green] Restore completed successfully!")
            console.print(f"[dim]Project ID: {backup_data.get('project_id')}[/dim]")
            console.print(f"[dim]Backup date: {backup_data.get('timestamp')}[/dim]")
            console.print(f"[dim]Tables restored: {tables_restored}[/dim]")

    except Exception as e:
        console.print(f"[red]✗[/red] Restore failed: {e}")
        raise typer.Exit(code=1)
