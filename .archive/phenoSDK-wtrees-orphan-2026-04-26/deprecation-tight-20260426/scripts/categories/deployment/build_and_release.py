#!/usr/bin/env python3
"""Typer CLI for automated build and release workflows."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

import typer

REPO_ROOT = Path(__file__).resolve().parents[4]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from pheno.cli.typer_utils import build_context, console
from pheno.logging import configure_structured_logging

app = typer.Typer(help="Build, test, and publish pheno-sdk distributions.")


def run_command(
    cmd, cwd: Path | None = None, check: bool = True,
) -> subprocess.CompletedProcess[str]:
    if isinstance(cmd, str):
        cmd = cmd.split()

    result = subprocess.run(
        cmd,
        check=False,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if check and result.returncode != 0:
        console.print(f"[red]Command failed:[/red] {' '.join(cmd)}")
        console.print(result.stdout)
        console.print(result.stderr)
        raise typer.Exit(code=result.returncode)
    return result


def build_wheel() -> None:
    console.print("🏗  Building wheel distribution...")
    run_command("python -m build")


def run_tests() -> None:
    console.print("🧪 Running tests...")
    run_command("pytest tests/ -v --tb=short")


def test_install_in_fresh_venv(dist_dir: Path) -> None:
    console.print("🧫 Verifying installation inside a fresh virtual environment...")

    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = Path(temp_dir) / "test_venv"
        venv.create(venv_path, with_pip=True)

        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
            pip_exe = venv_path / "Scripts" / "pip.exe"
        else:
            python_exe = venv_path / "bin" / "python"
            pip_exe = venv_path / "bin" / "pip"

        wheel_files = sorted(dist_dir.glob("*.whl"))
        if not wheel_files:
            raise typer.Exit("No wheel found in dist/")

        wheel_file = wheel_files[0]
        console.print(f"Installing {wheel_file}...")
        run_command(f"{pip_exe} install {wheel_file}")
        result = run_command(f"{python_exe} -c 'import pheno'", check=False)
        if result.returncode != 0:
            raise typer.Exit("Import test failed inside fresh virtualenv")


def publish_to_repository(repo_url: str | None) -> None:
    if repo_url:
        console.print(f"🚀 Publishing to private repository: {repo_url}")
        run_command(f"twine upload --repository-url {repo_url} dist/*")
    else:
        console.print("🚀 Publishing to PyPI")
        run_command("twine upload dist/*")


@app.command("run")
def run_release(
    project_root: Path = typer.Option(
        REPO_ROOT,
        "--project-root",
        help="Project root",
        exists=True,
        dir_okay=True,
        file_okay=False,
        resolve_path=True,
    ),
    skip_tests: bool = typer.Option(False, "--skip-tests", help="Skip pytest step"),
    skip_install_test: bool = typer.Option(
        False, "--skip-install-test", help="Skip fresh install verification",
    ),
    repository_url: str | None = typer.Option(
        None, "--repository-url", help="Custom repository URL",
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Build and test but skip publish",
    ),
    env: str = typer.Option("local", "--env", help="Environment label"),
    target: str = typer.Option("local", "--target", help="Deployment target"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Build, test, and optionally publish the distribution."""

    ctx = build_context(
        project_root=project_root,
        env=env,
        target=target,
        verbose=verbose,
        dry_run=dry_run,
    )
    configure_structured_logging(style="json", level="DEBUG" if verbose else "INFO")
    os.chdir(ctx.project_root)

    try:
        for folder in ("dist", "build"):
            folder_path = ctx.project_root / folder
            if folder_path.exists():
                shutil.rmtree(folder_path)

        build_wheel()

        if not skip_tests:
            run_tests()

        dist_dir = ctx.project_root / "dist"
        if not skip_install_test:
            test_install_in_fresh_venv(dist_dir)

        if dry_run:
            console.print("[yellow]Dry run enabled – skipping publish step[/yellow]")
        else:
            publish_to_repository(repository_url)

        console.print(
            "\n[bold green]🎉 Build and release process completed[/bold green]",
        )

    except Exception as exc:  # pragma: no cover - defensive logging
        console.print(f"\n[red]❌ Build and release failed:[/red] {exc}")
        raise typer.Exit(code=1) from exc


def main() -> None:
    app()


if __name__ == "__main__":
    main()
