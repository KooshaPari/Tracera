"""
Detect commonly used project automation commands.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from ..types import ProjectType

if TYPE_CHECKING:
    from pathlib import Path


def detect_build_command(project_path: Path, project_type: ProjectType) -> str | None:
    """
    Infer the build command for a project.
    """
    if project_type == ProjectType.PYTHON:
        if (project_path / "poetry.lock").exists():
            return "poetry build"
        if (project_path / "pyproject.toml").exists():
            return "python -m build"
        if (project_path / "setup.py").exists():
            return "python setup.py sdist bdist_wheel"

    if project_type == ProjectType.NODE:
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with package_json_path.open("r") as handle:
                    config = json.load(handle)
                scripts = config.get("scripts", {})
                if "build" in scripts:
                    return "npm run build"
                if "yarn" in project_path.glob("*lock*"):
                    return "yarn build"
            except Exception:  # pragma: no cover - non-critical
                pass

    if project_type == ProjectType.RUST:
        return "cargo build"
    if project_type == ProjectType.GO:
        return "go build"
    return None


def detect_test_command(project_path: Path, project_type: ProjectType) -> str | None:
    """
    Infer the test command for a project.
    """
    if project_type == ProjectType.PYTHON:
        if (project_path / "pytest.ini").exists() or "pytest" in str(project_path.glob("*.py")):
            return "pytest"
        if (project_path / "poetry.lock").exists():
            return "poetry run pytest"
        return "python -m pytest"

    if project_type == ProjectType.NODE:
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with package_json_path.open("r") as handle:
                    config = json.load(handle)
                scripts = config.get("scripts", {})
                if "test" in scripts:
                    return "npm run test"
            except Exception:
                pass

    if project_type == ProjectType.RUST:
        return "cargo test"
    if project_type == ProjectType.GO:
        return "go test ./..."
    return None


def detect_start_command(project_path: Path, project_type: ProjectType) -> str | None:
    """
    Infer the start command for a project.
    """
    if project_type == ProjectType.PYTHON:
        for main_file in ["main.py", "app.py", "run.py"]:
            if (project_path / main_file).exists():
                return f"python {main_file}"
        if (project_path / "main.py").exists():
            return "uvicorn main:app --reload"

    if project_type == ProjectType.NODE:
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with package_json_path.open("r") as handle:
                    config = json.load(handle)
                scripts = config.get("scripts", {})
                if "start" in scripts:
                    return "npm start"
                if "dev" in scripts:
                    return "npm run dev"
            except Exception:
                pass

    if project_type == ProjectType.RUST:
        return "cargo run"
    if project_type == ProjectType.GO:
        return "go run ."
    return None


__all__ = [
    "detect_build_command",
    "detect_start_command",
    "detect_test_command",
]
