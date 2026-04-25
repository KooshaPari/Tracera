"""State command for Tracera CLI."""

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


app = typer.Typer(help="Manage item state transitions")


@app.command()
def transition(
    item_id: str = typer.Argument(..., help="Item ID"),
    state: str = typer.Argument(..., help="Target state"),
) -> None:
    """Transition item to new state."""
    typer.echo(f"Transitioning {item_id} to {state}")
