"""Export command for Tracera CLI."""

import typer

app = typer.Typer(help="Export data")


@app.command()
def export(
    format: str = typer.Option("json", help="Export format"),
) -> None:
    """Export data in specified format."""
    typer.echo(f"Exporting in {format} format")
