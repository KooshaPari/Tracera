"""
Detect environment variables required by the project.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from ..types import ProjectType

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def detect_environment(project_path: Path, project_type: ProjectType) -> dict[str, str]:
    """
    Return environment variables gleaned from the project configuration.
    """
    env: dict[str, str] = {}

    env_file = project_path / ".env"
    if env_file.exists():
        try:
            with env_file.open("r") as handle:
                for line in handle:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        env[key] = value
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Failed to load .env file: %s", exc)

    if project_type == ProjectType.PYTHON:
        env.setdefault("PYTHONPATH", str(project_path))
        env.setdefault("PYTHONUNBUFFERED", "1")
    elif project_type == ProjectType.NODE:
        env.setdefault("NODE_ENV", "development")

    return env


__all__ = ["detect_environment"]
