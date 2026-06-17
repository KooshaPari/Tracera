"""TraceRTM CLI — main entry point."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="tracera",
    help="TraceRTM — Agent-native, multi-view requirements traceability CLI.",
    invoke_without_command=True,
)


@app.callback()
def callback(version: bool = typer.Option(False, "--version", help="Show version and exit")) -> None:
    """TraceRTM CLI entry point."""
    if version:
        try:
            from tracertm import __version__
            typer.echo(f"tracera-cli {__version__}")
        except ImportError:
            typer.echo("tracera-cli (tracertm not installed)")
        raise typer.Exit(0)


@app.command()
def status() -> None:
    """Show TraceRTM system status."""
    typer.echo("[tracera] status: stub — implementation pending")


@app.command()
def list_artifacts() -> None:
    """List all tracked artifacts."""
    typer.echo("[tracera] list_artifacts: stub — implementation pending")


if __name__ == "__main__":
    app()
