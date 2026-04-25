"""Ingest command for Tracera CLI."""

import typer

app = typer.Typer(help="Ingest data from sources")


@app.command()
def ingest_data(
    source: str = typer.Argument(..., help="Data source"),
) -> None:
    """Ingest data from source."""
    typer.echo(f"Ingesting from {source}")
