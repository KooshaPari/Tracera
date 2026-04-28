"""
Project context assembly routines.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

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

if TYPE_CHECKING:  # pragma: no cover
    from pathlib import Path

    from .models import ProjectContext


def build_project_context(
    project_path: Path,
    context_cls: type[ProjectContext],
) -> ProjectContext:
    """
    Construct a project context instance for the given path.
    """
    project_path = project_path.resolve()
    project_type = detect_project_type(project_path)
    project_name = project_path.name

    config = load_project_config(project_path, project_type)
    environment = detect_environment(project_path, project_type)
    dependencies, dev_dependencies = detect_dependencies(project_path, project_type)
    tools = detect_tools(project_path, project_type)
    build_command = detect_build_command(project_path, project_type)
    test_command = detect_test_command(project_path, project_type)
    start_command = detect_start_command(project_path, project_type)

    return context_cls(
        project_type=project_type,
        project_path=project_path,
        project_name=project_name,
        config=config,
        environment=environment,
        dependencies=dependencies,
        dev_dependencies=dev_dependencies,
        tools=tools,
        build_command=build_command,
        test_command=test_command,
        start_command=start_command,
    )


__all__ = ["build_project_context"]
