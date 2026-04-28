# CLI Builder Documentation

## Overview

The CLI Builder provides a flexible, adapter-based system for creating command-line interfaces with support for multiple backends including Typer, Click, Rich, and Argparse.

## Key Features

- **Multiple Backends**: Typer, Click, Rich CLI, Argparse support
- **Declarative API**: Simple decorator-based command definition
- **Rich UI**: Progress bars, tables, formatted output
- **Interactive Mode**: REPL and interactive prompts
- **Auto-completion**: Shell completion for all backends
- **Type Safety**: Full type hints and validation

## Quick Start

```python
from pheno.cli import CLIBuilder
from pheno.cli.adapters import TyPerAdapter

# Create CLI with chosen backend
cli = CLIBuilder(adapter=TyPerAdapter())

@cli.command()
@cli.option("--name", default="World", help="Name to greet")
async def hello(name: str):
    """Say hello"""
    print(f"Hello, {name}!")

@cli.command()
@cli.argument("source", help="Source file")
@cli.argument("destination", help="Destination file")
@cli.option("--overwrite", "-f", is_flag=True, help="Overwrite existing")
async def copy(source: str, destination: str, overwrite: bool = False):
    """Copy files"""
    # Implementation
    pass

if __name__ == "__main__":
    cli.run()
```

## Command Groups

```python
@cli.group()
class Database:
    """Database management commands"""

    @cli.command()
    async def migrate(self):
        """Run migrations"""
        await run_migrations()

    @cli.command()
    @cli.option("--force", is_flag=True)
    async def reset(self, force: bool = False):
        """Reset database"""
        if force or cli.confirm("Reset database?"):
            await reset_database()
```

## Rich UI Components

```python
from pheno.cli import RichCLI

cli = RichCLI()

@cli.command()
async def process():
    """Process with progress bar"""
    with cli.progress("Processing files") as progress:
        task = progress.add_task("Files", total=100)
        for i in range(100):
            await process_file(i)
            progress.advance(task)

    # Display table
    table = cli.create_table("Results", ["File", "Status", "Time"])
    table.add_row(["file1.txt", "✓", "1.2s"])
    cli.display(table)
```

## Interactive Mode

```python
@cli.command()
async def interactive():
    """Start interactive mode"""
    cli.start_repl(
        prompt="pheno> ",
        history_file="~/.pheno_history",
        auto_complete=True
    )

# In REPL
# pheno> help
# pheno> migrate --help
# pheno> process file.txt
```

## Adapter Comparison

| Feature | Typer | Click | Rich CLI | Argparse |
|---------|-------|-------|----------|----------|
| Type Hints | ✓ | Partial | ✓ | Manual |
| Async Support | ✓ | ✓ | ✓ | ✓ |
| Rich Output | Via Rich | No | Native | No |
| Completion | ✓ | ✓ | ✓ | Limited |
| Performance | Good | Excellent | Good | Best |

---

*Full documentation: [CLI Builder Guide](https://your-org.github.io/pheno-sdk/kits/cli)*
