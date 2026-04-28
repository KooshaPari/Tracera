"""
Dataclasses representing project context.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .types import ProjectType

logger = logging.getLogger(__name__)


@dataclass
class ProjectContext:
    """
    Context information required to execute commands for a project.
    """

    project_type: ProjectType
    project_path: Path
    project_name: str

    config: dict[str, Any]
    environment: dict[str, str]
    dependencies: list[str]
    dev_dependencies: list[str]
    tools: list[str]

    build_command: str | None = None
    test_command: str | None = None
    start_command: str | None = None

    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def detect(cls, project_path: Path | None = None) -> ProjectContext:
        """
        Detect project context from disk.
        """
        if project_path is None:
            project_path = Path.cwd()

        from .builder import build_project_context

        return build_project_context(project_path, cls)

    def get_command_for_stage(self, stage: str) -> str | None:
        """
        Return the command associated with a named stage.
        """
        return {
            "build": self.build_command,
            "test": self.test_command,
            "start": self.start_command,
        }.get(stage)

    def to_dict(self) -> dict[str, Any]:
        """
        Serialize the project context to a dictionary.
        """
        return {
            "project_type": self.project_type.value,
            "project_path": str(self.project_path),
            "project_name": self.project_name,
            "config": self.config,
            "environment": self.environment,
            "dependencies": self.dependencies,
            "dev_dependencies": self.dev_dependencies,
            "tools": self.tools,
            "build_command": self.build_command,
            "test_command": self.test_command,
            "start_command": self.start_command,
            "metadata": self.metadata,
        }


__all__ = ["ProjectContext"]
