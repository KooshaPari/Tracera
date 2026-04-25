"""TUI command for Tracera CLI."""

import typer

app = typer.Typer(help="Launch terminal UI")


@app.command()
def launch() -> None:
    """Launch the interactive TUI."""
    typer.echo("TUI launching...")
