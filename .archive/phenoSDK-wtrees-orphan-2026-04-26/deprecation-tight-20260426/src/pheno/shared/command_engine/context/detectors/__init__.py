"""
Submodules providing project detection helpers.
"""

from .command_detector import (
    detect_build_command,
    detect_start_command,
    detect_test_command,
)
from .config_loader import load_project_config
from .dependency_detector import detect_dependencies
from .environment_detector import detect_environment
from .project_type_detector import detect_project_type
from .tool_detector import detect_tools

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
