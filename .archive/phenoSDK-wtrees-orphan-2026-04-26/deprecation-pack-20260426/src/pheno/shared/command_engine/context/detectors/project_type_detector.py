"""
Detect the project type based on repository structure.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import ProjectType

if TYPE_CHECKING:
    from pathlib import Path


def detect_project_type(project_path: Path) -> ProjectType:
    """
    Return the most likely project type for the provided path.
    """
    if any(
        (project_path / name).exists()
        for name in ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"]
    ):
        return ProjectType.PYTHON

    if (project_path / "package.json").exists():
        return ProjectType.NODE

    if (project_path / "Cargo.toml").exists():
        return ProjectType.RUST

    if any((project_path / name).exists() for name in ["go.mod", "go.sum", "main.go"]):
        return ProjectType.GO

    if any(
        (project_path / name).exists() for name in ["pom.xml", "build.gradle", "build.gradle.kts"]
    ):
        return ProjectType.JAVA

    if (project_path / "Dockerfile").exists():
        return ProjectType.DOCKER

    return ProjectType.UNKNOWN


__all__ = ["detect_project_type"]
