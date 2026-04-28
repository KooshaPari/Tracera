"""
Project context detection utilities for the command engine.
"""

from .detectors import (
    detect_build_command,
    detect_dependencies,
    detect_environment,
    detect_project_type,
    detect_start_command,
    detect_test_command,
    detect_tools,
    load_project_config,
)
from .models import ProjectContext
from .types import ProjectType

__all__ = [
    "ProjectContext",
    "ProjectType",
    "detect_build_command",
    "detect_dependencies",
    "detect_environment",
    "detect_project_type",
    "detect_start_command",
    "detect_test_command",
    "detect_tools",
    "load_project_config",
]
