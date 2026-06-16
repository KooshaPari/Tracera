"""CLI application entry point."""
from typer import Typer

app = Typer(help="TracerTM CLI - Item and Link management")


@app.callback()
def main():
    """TracerTM CLI - Manage items and links."""
    pass


# Import commands
from tracertm.cli.commands.item import app as item_app
from tracertm.cli.commands.link import app as link_app

# Add sub-commands
app.add_typer(item_app, name="item")
app.add_typer(link_app, name="link")


__all__ = ["app"]
