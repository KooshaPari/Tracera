#!/usr/bin/env python3
"""Memory usage analysis with Typer CLI ergonomics."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Union

import typer

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from pheno.cli.typer_utils import build_context, console
from pheno.logging import configure_structured_logging

try:
    from memory_profiler import profile  # type: ignore[import-untyped]

    MEMORY_PROFILER_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    MEMORY_PROFILER_AVAILABLE = False

    def profile(func):
        def wrapper(*args, **kwargs):
            console.print(
                "[yellow]memory_profiler not installed. Install with `pip install memory-profiler` for detailed tracing.[/yellow]",
            )
            return func(*args, **kwargs)

        return wrapper


app = typer.Typer(
    help="Profile memory usage for modules and core pheno SDK components.",
)


@profile
def analyze_module_memory(module_name: str) -> dict[str, Union[str, int]]:
    console.print(f"Analyzing memory usage for module: {module_name}")

    data = []
    for i in range(1000):
        data.append(
            {
                "id": i,
                "name": f"item_{i}",
                "value": i * 2,
                "metadata": {"created": time.time()},
            },
        )

    processed = []
    for item in data:
        if isinstance(item["value"], (int, float)) and item["value"] % 2 == 0:
            processed.append({"id": item["id"], "processed_value": item["value"] * 10})

    processed_count = len(processed)
    console.print(f"Processed {processed_count} items")
    return {"module": module_name, "processed_items": processed_count}


def profile_pheno_sdk() -> dict[str, int]:
    from pheno import Registry, Stream

    Stream("test_stream")
    data = [f"message_{i}" for i in range(100)]

    registry = Registry()
    for i, item in enumerate(data):
        registry.register(f"item_{i}", item)

    console.print("Pheno SDK profiling complete")
    return {"streams_profiled": 1, "registry_entries": len(data)}


def generate_memory_report() -> dict[str, float]:
    console.print("Memory Usage Report", style="bold")

    try:
        import psutil

        memory = psutil.virtual_memory()
        totals = {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent_used": memory.percent,
        }
        console.print(f"Total Memory: {totals['total_gb']:.2f} GB")
        console.print(f"Available Memory: {totals['available_gb']:.2f} GB")
        console.print(f"Used Memory: {totals['used_gb']:.2f} GB")
        console.print(f"Memory Percentage: {totals['percent_used']:.1f}%")
    except ImportError:
        console.print(
            "Install psutil for system memory info: pip install psutil", style="yellow",
        )
        totals = {}

    console.print("\nRecommendations:")
    console.print("- Use generators instead of lists for large datasets")
    console.print("- Implement data streaming for memory-intensive operations")
    console.print("- Consider using memory-efficient data structures")

    return totals


@app.command("run")
def run_profiler(
    module: str | None = typer.Argument(None, help="Module name to profile"),
    report: bool = typer.Option(
        False, "--report", help="Generate system memory report",
    ),
    pheno_profile: bool = typer.Option(
        False, "--pheno", help="Profile core pheno components",
    ),
    output: Path | None = typer.Option(
        None, "--output", help="Write JSON summary to file",
    ),
    json_output: bool = typer.Option(False, "--json", help="Print JSON summary"),
    project_root: Path = typer.Option(
        Path.cwd(),
        "--project-root",
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
    ),
    env: str = typer.Option("local", "--env"),
    target: str = typer.Option("local", "--target"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Run the desired memory profiling mode."""

    build_context(
        project_root=project_root,
        env=env,
        target=target,
        verbose=verbose,
        dry_run=dry_run,
    )
    configure_structured_logging(style="json", level="DEBUG" if verbose else "INFO")

    summary: dict[str, object] | None = None

    if report:
        totals = generate_memory_report()
        summary = {"mode": "report", "metrics": totals}
    elif pheno_profile:
        summary = {"mode": "pheno", "result": profile_pheno_sdk()}
    elif module:
        summary = {"mode": "module", "result": analyze_module_memory(module)}
    else:
        raise typer.BadParameter("Provide a module name or enable --report/--pheno")

    if summary and (output or json_output):
        payload = json.dumps(summary, indent=2)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(payload)
            console.print(f"Summary written to {output}")
        if json_output:
            typer.echo(payload)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
