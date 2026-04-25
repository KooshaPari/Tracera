"""Migrate command for Tracera CLI."""

import typer

app = typer.Typer(help="Manage data migrations")


@app.command()
def migrate() -> None:
    """Run data migrations."""
    typer.echo("Running migrations")
