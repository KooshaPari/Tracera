# pheno-cli-builder

CLI Builder Kit - Command line interface builder utilities for Python.

## Overview

Provides a unified interface for building CLI applications with multiple backends.

## Installation

```bash
pip install pheno-cli-builder
```

## Usage

```python
from pheno_cli_builder import Command, Argument, Option, ArgumentType

# Create a simple command
cmd = Command(
    name="greet",
    description="Greet a user",
    arguments=[
        Argument("name", ArgumentType.STRING, "Name to greet")
    ],
    options=[
        Option("shout", ArgumentType.BOOLEAN, "Shout the greeting", is_flag=True)
    ]
)

# Add subcommands
subcmd = Command("list", "List all greetings")
cmd.add_subcommand(subcmd)
```

## Classes

### `Command`
Represents a CLI command with arguments, options, and subcommands.

### `Argument`
Defines a positional argument for a command.

### `Option`
Defines an optional flag or parameter for a command.

### `ArgumentType`
Enum of supported argument types: STRING, INTEGER, FLOAT, BOOLEAN, LIST.

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/
```

## License

MIT
