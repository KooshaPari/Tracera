"""Watch command for Tracera CLI."""

import typer

app = typer.Typer(help="Watch items for changes")


@app.command()
def watch_items(
    query: str = typer.Option(..., help="Watch query"),
) -> None:
    """Watch items matching query."""
    typer.echo(f"Watching: {query}")
