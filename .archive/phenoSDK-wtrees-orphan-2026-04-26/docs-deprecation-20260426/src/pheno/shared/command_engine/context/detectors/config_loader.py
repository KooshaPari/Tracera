"""
Load project configuration files.
"""

from __future__ import annotations

import json
import logging
import tomllib
from typing import TYPE_CHECKING, Any

from ..types import ProjectType

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def load_project_config(project_path: Path, project_type: ProjectType) -> dict[str, Any]:
    """
    Load configuration data associated with the project.
    """
    config: dict[str, Any] = {}

    try:
        if project_type == ProjectType.PYTHON:
            pyproject_path = project_path / "pyproject.toml"
            if pyproject_path.exists():
                with pyproject_path.open("rb") as handle:
                    config = tomllib.load(handle)
            elif (project_path / "setup.py").exists():
                config = {"setup": "detected"}

        elif project_type == ProjectType.NODE:
            package_json_path = project_path / "package.json"
            if package_json_path.exists():
                with package_json_path.open("r") as handle:
                    config = json.load(handle)

        elif project_type == ProjectType.RUST:
            cargo_toml_path = project_path / "Cargo.toml"
            if cargo_toml_path.exists():
                with cargo_toml_path.open("rb") as handle:
                    config = tomllib.load(handle)

        elif project_type == ProjectType.GO:
            if (project_path / "go.mod").exists():
                config = {"go_module": "detected"}

    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning("Failed to load config for %s: %s", project_type.value, exc)

    return config


__all__ = ["load_project_config"]
