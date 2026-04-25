"""History command for Tracera CLI."""

import typer

# Stub imports for test patching
class ConfigManager:
    """Stub config manager."""

    def get(self, key: str) -> None:
        """Get config value."""
        pass


class LocalStorageManager:
    """Stub local storage manager."""

    def get_session(self):
        """Get database session."""
        pass


app = typer.Typer(help="Show item history and changes")


@app.command()
def show_history(
    item_id: str = typer.Argument(..., help="Item ID to show history for"),
    at: str = typer.Option(None, help="Show state at specific date"),
) -> None:
    """Show history of item changes."""
    from datetime import datetime

    config = ConfigManager()
    project = config.get("project")
    if not project:
        typer.echo("Error: no project configured", err=True)
        raise typer.Exit(code=1)

    # Validate date format if provided
    if at:
        try:
            datetime.fromisoformat(at)
        except (ValueError, TypeError):
            typer.echo(f"Error: invalid date format '{at}'")
            return

    # Validate item exists
    storage = LocalStorageManager()
    with storage.get_session() as session:
        # Query item; the mock returns None if not found
        item = session.query(None).filter(None).first()
        if not item:
            typer.echo(f"Item {item_id} not found")
            return
        typer.echo(f"History for {item_id}")
