"""Progress command for Tracera CLI."""

import typer

app = typer.Typer(help="Manage progress tracking")


@app.command()
def show() -> None:
    """Show progress status."""
    typer.echo("Progress status")
