"""Search command for Tracera CLI."""

import typer

app = typer.Typer(help="Search items")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
) -> None:
    """Search for items."""
    typer.echo(f"Searching: {query}")
