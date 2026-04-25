"""Chaos command for Tracera CLI."""

import typer

app = typer.Typer(help="Manage chaos testing")


@app.command()
def run() -> None:
    """Run chaos tests."""
    typer.echo("Running chaos tests")
