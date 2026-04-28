"""
Compatibility imports for detector helpers.
"""

from __future__ import annotations

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

__all__ = [
    "detect_build_command",
    "detect_dependencies",
    "detect_environment",
    "detect_project_type",
    "detect_start_command",
    "detect_test_command",
    "detect_tools",
    "load_project_config",
]
