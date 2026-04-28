"""
Universal Project Configuration Framework
========================================

Provides flexible configuration management for any type of project.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ProjectType(Enum):
    """
    Types of projects supported by the framework.
    """

    WEB_SERVER = "web_server"
    CLI_TOOL = "cli_tool"
    API_SERVER = "api_server"
    MICROSERVICE = "microservice"
    MCP_SERVER = "mcp_server"
    WORKER = "worker"
    SCHEDULER = "scheduler"
    CUSTOM = "custom"


@dataclass
class ProjectConfig:
    """Universal configuration for any project type.

    This class provides a flexible configuration system that can be extended and
    customized for any project implementation.
    """

    # Basic project information
    name: str
    project_type: ProjectType
    version: str = "1.0.0"
    description: str = ""

    # Server configuration (for server-type projects)
    host: str = "localhost"
    port: int | None = None
    domain: str | None = None

    # Command configuration (for CLI/worker projects)
    command: str | None = None
    working_directory: Path | None = None
    environment: dict[str, str] = field(default_factory=dict)

    # Infrastructure configuration
    tunnel_enabled: bool = True
    health_check_path: str = "/health"
    startup_timeout: int = 30
    shutdown_timeout: int = 10

    # Development configuration
    dev_mode: bool = False
    verbose: bool = False
    debug: bool = False

    # Dependencies and services
    dependencies: list[str] = field(default_factory=list)
    services: list[str] = field(default_factory=list)

    # CLI configuration
    cli_commands: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Custom configuration
    custom_config: dict[str, Any] = field(default_factory=dict)

    # Validation and setup
    validators: list[Callable[[], bool]] = field(default_factory=list)
    setup_hooks: list[Callable[[], None]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.
        """
        return {
            "name": self.name,
            "project_type": self.project_type.value,
            "version": self.version,
            "description": self.description,
            "host": self.host,
            "port": self.port,
            "domain": self.domain,
            "command": self.command,
            "working_directory": str(self.working_directory) if self.working_directory else None,
            "environment": self.environment,
            "tunnel_enabled": self.tunnel_enabled,
            "health_check_path": self.health_check_path,
            "startup_timeout": self.startup_timeout,
            "shutdown_timeout": self.shutdown_timeout,
            "dev_mode": self.dev_mode,
            "verbose": self.verbose,
            "debug": self.debug,
            "dependencies": self.dependencies,
            "services": self.services,
            "cli_commands": self.cli_commands,
            "custom_config": self.custom_config,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectConfig":
        """
        Create configuration from dictionary.
        """
        # Handle working_directory conversion
        if data.get("working_directory"):
            data["working_directory"] = Path(data["working_directory"])

        # Handle project_type conversion
        if "project_type" in data and isinstance(data["project_type"], str):
            data["project_type"] = ProjectType(data["project_type"])

        return cls(**data)


class ProjectConfigBuilder:
    """Builder pattern for creating project configurations.

    Provides a fluent interface for building complex project configurations.
    """

    def __init__(self, name: str, project_type: ProjectType = ProjectType.CUSTOM):
        self._config = ProjectConfig(name=name, project_type=project_type)

    def version(self, version: str) -> "ProjectConfigBuilder":
        """
        Set the project version.
        """
        self._config.version = version
        return self

    def description(self, description: str) -> "ProjectConfigBuilder":
        """
        Set the project description.
        """
        self._config.description = description
        return self

    def server(self, host: str = "localhost", port: int = 8000) -> "ProjectConfigBuilder":
        """
        Configure server settings.
        """
        self._config.host = host
        self._config.port = port
        return self

    def domain(self, domain: str) -> "ProjectConfigBuilder":
        """
        Set the domain for tunneling.
        """
        self._config.domain = domain
        return self

    def command(self, command: str) -> "ProjectConfigBuilder":
        """
        Set the command to run.
        """
        self._config.command = command
        return self

    def working_directory(self, path: str | Path) -> "ProjectConfigBuilder":
        """
        Set the working directory.
        """
        self._config.working_directory = Path(path)
        return self

    def environment(self, **env_vars) -> "ProjectConfigBuilder":
        """
        Add environment variables.
        """
        self._config.environment.update(env_vars)
        return self

    def tunnel(self, enabled: bool = True) -> "ProjectConfigBuilder":
        """
        Enable or disable tunnel.
        """
        self._config.tunnel_enabled = enabled
        return self

    def health_check(self, path: str = "/health") -> "ProjectConfigBuilder":
        """
        Set health check path.
        """
        self._config.health_check_path = path
        return self

    def timeouts(self, startup: int = 30, shutdown: int = 10) -> "ProjectConfigBuilder":
        """
        Set startup and shutdown timeouts.
        """
        self._config.startup_timeout = startup
        self._config.shutdown_timeout = shutdown
        return self

    def dev_mode(self, enabled: bool = True) -> "ProjectConfigBuilder":
        """
        Enable development mode.
        """
        self._config.dev_mode = enabled
        return self

    def verbose(self, enabled: bool = True) -> "ProjectConfigBuilder":
        """
        Enable verbose logging.
        """
        self._config.verbose = enabled
        return self

    def debug(self, enabled: bool = True) -> "ProjectConfigBuilder":
        """
        Enable debug mode.
        """
        self._config.debug = enabled
        return self

    def dependencies(self, *deps: str) -> "ProjectConfigBuilder":
        """
        Add dependencies.
        """
        self._config.dependencies.extend(deps)
        return self

    def services(self, *services: str) -> "ProjectConfigBuilder":
        """
        Add services.
        """
        self._config.services.extend(services)
        return self

    def cli_command(
        self, name: str, description: str, handler: Callable, **kwargs,
    ) -> "ProjectConfigBuilder":
        """
        Add a CLI command.
        """
        self._config.cli_commands[name] = {"description": description, "handler": handler, **kwargs}
        return self

    def validator(self, validator: Callable[[], bool]) -> "ProjectConfigBuilder":
        """
        Add a validation function.
        """
        self._config.validators.append(validator)
        return self

    def setup_hook(self, hook: Callable[[], None]) -> "ProjectConfigBuilder":
        """
        Add a setup hook.
        """
        self._config.setup_hooks.append(hook)
        return self

    def custom(self, key: str, value: Any) -> "ProjectConfigBuilder":
        """
        Add custom configuration.
        """
        self._config.custom_config[key] = value
        return self

    def build(self) -> ProjectConfig:
        """
        Build the final configuration.
        """
        return self._config


# Predefined configurations for common project types
def web_server_config(name: str, port: int = 8000, **kwargs) -> ProjectConfig:
    """
    Create configuration for a web server project.
    """
    return (
        ProjectConfigBuilder(name, ProjectType.WEB_SERVER)
        .server(port=port)
        .health_check("/health")
        .timeouts(30, 10)
        .build()
    )


def cli_tool_config(name: str, command: str, **kwargs) -> ProjectConfig:
    """
    Create configuration for a CLI tool project.
    """
    return ProjectConfigBuilder(name, ProjectType.CLI_TOOL).command(command).timeouts(10, 5).build()


def api_server_config(name: str, port: int = 8000, **kwargs) -> ProjectConfig:
    """
    Create configuration for an API server project.
    """
    return (
        ProjectConfigBuilder(name, ProjectType.API_SERVER)
        .server(port=port)
        .health_check("/api/health")
        .timeouts(45, 15)
        .build()
    )


def microservice_config(name: str, port: int = 8000, **kwargs) -> ProjectConfig:
    """
    Create configuration for a microservice project.
    """
    return (
        ProjectConfigBuilder(name, ProjectType.MICROSERVICE)
        .server(port=port)
        .health_check("/health")
        .timeouts(60, 20)
        .build()
    )


def mcp_server_config(name: str, port: int = 8000, **kwargs) -> ProjectConfig:
    """
    Create configuration for an MCP server project.
    """
    return (
        ProjectConfigBuilder(name, ProjectType.MCP_SERVER)
        .server(port=port)
        .health_check("/health")
        .timeouts(30, 10)
        .custom("mcp_protocol", True)
        .build()
    )
