"""
Identify tooling present in the project.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import ProjectType

if TYPE_CHECKING:
    from pathlib import Path


def detect_tools(project_path: Path, project_type: ProjectType) -> list[str]:
    """
    Return a list of development tools detected in the project.
    """
    tools: list[str] = []
    tool_files = {
        "make": "Makefile",
        "docker": "Dockerfile",
        "docker-compose": "docker-compose.yml",
        "git": ".git",
        "pre-commit": ".pre-commit-config.yaml",
        "ruff": "ruff.toml",
        "black": "pyproject.toml",
        "pytest": "pytest.ini",
        "mypy": "mypy.ini",
    }

    for tool, file_name in tool_files.items():
        if (project_path / file_name).exists():
            tools.append(tool)

    if project_type == ProjectType.PYTHON:
        if (project_path / "poetry.lock").exists():
            tools.append("poetry")
        if (project_path / "Pipfile").exists():
            tools.append("pipenv")
    elif project_type == ProjectType.NODE:
        if (project_path / "yarn.lock").exists():
            tools.append("yarn")
        if (project_path / "pnpm-lock.yaml").exists():
            tools.append("pnpm")

    return tools


__all__ = ["detect_tools"]
