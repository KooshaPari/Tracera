# CLI Builder Kit

## At a Glance
- **Purpose:** Rapidly build async-friendly command line interfaces with structured commands and argument parsing.
- **Best For:** Developer tooling, internal automation scripts, and cross-platform CLIs.
- **Key Building Blocks:** `CLI`, `@command` decorator, argument schemas, formatters, validation helpers.

## Core Capabilities
- Declarative command registration using decorators or builder APIs.
- Built-in argument types (string, int, bool, enums) with custom validators.
- Async execution support with automatic event loop management.
- Output formatters (table, JSON, plain text) for consistent UX.
- Extensible backends for Typer, argparse, or custom runners.

## Getting Started

### Installation
```
pip install cli-builder-kit
```

### Minimal Example
```python
from cli_builder import CLI

cli = CLI(name="pheno", description="Pheno-SDK helper")

@cli.command("hello", args=["name"], description="Greet a user")
async def hello(name: str) -> None:
    print(f"Hello {name}")

if __name__ == "__main__":
    cli.run()
```

## How It Works
- `cli_builder.cli.CLI` stores command metadata and orchestrates parsing.
- Commands are represented by `Command` objects; decorators wrap callables and attach metadata.
- Argument schemas live in `cli_builder.args` and support defaults, optional parameters, and validation.
- Backends convert the internal representation to a runner (default is asyncio-based custom runner).

## Usage Recipes
- Implement multi-level subcommands using `cli.group("admin")` to create nested CLIs.
- Stream long-running operations with observability-kit metrics or progress bars from `cli_builder.formatters`.
- Embed CLI routines inside workflow-kit tasks to reuse logic in automation pipelines.
- Generate shell completion scripts via `cli.generate_completion("bash")`.

## Interoperability
- Load configuration per command through config-kit models.
- Use adapter-kit injection to pull shared services (databases, loggers) into command handlers.
- Publish CLI actions through event-kit to keep audit trails.

## Operations & Observability
- Inject `StructuredLogger` into commands to produce structured output.
- Emit exit codes and timing metrics using observability-kit counters and histograms.
- Package CLI apps with deploy-kit to ship as standalone binaries or containers.

## Testing & QA
- Use `cli_builder.testing.invoke(cli, args)` to run commands in tests.
- Mock dependencies via adapter-kit container overrides.
- Validate argument parsing edge cases and error messages in unit tests.

## Troubleshooting
- **Event loop already running:** use `await cli.run_async(args)` inside async contexts.
- **Unknown command:** confirm command registration occurs before `cli.run()` (import order matters).
- **Custom formatter not showing:** ensure the formatter is registered via `cli.formatters.register()`.

## Primary API Surface
- `CLI(name, description, version=None)`
- `@cli.command(name, args, description, options)`
- `cli.run(args=None)` / `await cli.run_async(args=None)`
- `cli.group(name)` for nested command groups
- `cli.add_argument(name, type, default, help)` for imperative registration
- Formatters: `formatters.TableFormatter`, `formatters.JSONFormatter`

## Additional Resources
- Examples: `cli-builder-kit/examples/`
- Tests: `cli-builder-kit/tests/`
- Related concepts: [Patterns](../concepts/patterns.md)
