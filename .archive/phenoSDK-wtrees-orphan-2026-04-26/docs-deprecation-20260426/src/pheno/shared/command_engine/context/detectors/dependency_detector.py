"""
Detect project dependencies and dev dependencies.
"""

from __future__ import annotations

import json
import logging
import tomllib
from typing import TYPE_CHECKING

from ..types import ProjectType

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def detect_dependencies(
    project_path: Path, project_type: ProjectType,
) -> tuple[list[str], list[str]]:
    """
    Return a tuple of (dependencies, dev_dependencies).
    """
    dependencies: list[str] = []
    dev_dependencies: list[str] = []

    if project_type == ProjectType.PYTHON:
        req_file = project_path / "requirements.txt"
        if req_file.exists():
            try:
                with req_file.open("r") as handle:
                    dependencies = [
                        line.strip() for line in handle if line.strip() and not line.startswith("#")
                    ]
            except Exception as exc:
                logger.warning("Failed to load requirements.txt: %s", exc)

        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            try:
                with pyproject_path.open("rb") as handle:
                    config = tomllib.load(handle)

                project_cfg = config.get("project", {})
                dependencies.extend(project_cfg.get("dependencies", []))
                optional = project_cfg.get("optional-dependencies", {})
                dev_dependencies.extend(optional.get("dev", []))
            except Exception as exc:
                logger.warning("Failed to parse pyproject.toml: %s", exc)

    elif project_type == ProjectType.NODE:
        package_json_path = project_path / "package.json"
        if package_json_path.exists():
            try:
                with package_json_path.open("r") as handle:
                    config = json.load(handle)

                dependencies = list(config.get("dependencies", {}).keys())
                dev_dependencies = list(config.get("devDependencies", {}).keys())
            except Exception as exc:
                logger.warning("Failed to parse package.json: %s", exc)

    return dependencies, dev_dependencies


__all__ = ["detect_dependencies"]
