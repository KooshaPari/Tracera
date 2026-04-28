# CLI Migration to Typer

Goal: Rebase CLI experiences on Typer while preserving pheno-sdk UX conventions and wrappers.

## Why Typer
- Modern, typed, async-friendly CLI.
- Autocomplete, parameter parsing, help UX handled by library.

## Scope
- Replace internal CLI command scaffolding in cli-builder-kit with Typer-based wrappers.
- Migrate pheno_cli commands to Typer.
- Remove all legacy/compatibility shims and back-compat entry points.

## Plan
1) Make `typer` a direct dependency of pheno_cli.
2) Create thin wrapper conventions in Typer entrypoint:
   - Global `--verbose/--debug` flags hooked to logging.
   - Config bootstrap and DI wiring as needed.
3) Migrate pheno_cli:
   - app = Typer(help=...)
   - Port commands to `@app.command()`; inject config/di via helpers.
   - Remove legacy console entry points.
4) Update examples and docs; add tests for commands and options.

## Example Skeleton
```python
import typer
from adapter_kit import Container
from config_kit import AppConfig

app = typer.Typer(help="Pheno CLI")
container = Container()

@app.command()
def hello(name: str = "world"):
    typer.echo(f"Hello {name}")

if __name__ == "__main__":
    app()
```

## Rollout
- Phase 1: Land wrappers + migrate pheno_cli core commands.
- Phase 2: Migrate cli-builder-kit examples/tests; deprecate old base classes.
- Phase 3: Announce in CHANGELOG; provide migration guide for downstreams.

## Notes
- Do not install dependencies globally; use per-kit extras.
- Preserve entry points to avoid breaking scripts.
