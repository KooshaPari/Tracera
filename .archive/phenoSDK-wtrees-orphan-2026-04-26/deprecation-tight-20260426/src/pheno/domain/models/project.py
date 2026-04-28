"""Project registry data model.

Canonical ProjectRegistry class used across all pheno-sdk components.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ProjectInfo:
    """
    Information about a registered project.
    """

    name: str
    """
    Project name.
    """

    config: dict[str, Any]
    """
    Project configuration.
    """

    processes: dict[str, Any] = field(default_factory=dict)
    """
    Project processes.
    """

    resources: dict[str, Any] = field(default_factory=dict)
    """
    Project resources.
    """

    start_time: datetime = field(default_factory=datetime.now)
    """
    Project registration time.
    """


class ProjectRegistry:
    """
    Registry for managing multiple pheno-sdk projects.
    """

    def __init__(self):
        self.projects: dict[str, ProjectInfo] = {}

    def register_project(self, name: str, config: dict[str, Any]) -> None:
        """
        Register a project with its configuration.
        """
        self.projects[name] = ProjectInfo(name=name, config=config)

    def unregister_project(self, name: str) -> None:
        """
        Unregister a project.
        """
        if name in self.projects:
            del self.projects[name]

    def list_projects(self) -> list[str]:
        """
        List all registered projects.
        """
        return list(self.projects.keys())

    def get_project(self, name: str) -> ProjectInfo | None:
        """
        Get project information.
        """
        return self.projects.get(name)

    def add_process(self, project: str, process_info: Any) -> None:
        """
        Add a process to a project.
        """
        if project in self.projects:
            self.projects[project].processes[process_info.name] = process_info

    def remove_process(self, project: str, process_name: str) -> None:
        """
        Remove a process from a project.
        """
        if project in self.projects:
            self.projects[project].processes.pop(process_name, None)

    def add_resource(self, project: str, resource_info: Any) -> None:
        """
        Add a resource to a project.
        """
        if project in self.projects:
            self.projects[project].resources[resource_info.name] = resource_info

    def remove_resource(self, project: str, resource_name: str) -> None:
        """
        Remove a resource from a project.
        """
        if project in self.projects:
            self.projects[project].resources.pop(resource_name, None)
