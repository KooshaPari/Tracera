"""Legacy configuration helpers built on top of :mod:`pheno.config` primitives.

This module preserves the public surface that older PyDevKit and MCP tooling
expect, while delegating the heavy lifting to the consolidated configuration
package.  By funnelling all behaviour through :mod:`pheno.config`, we avoid the
prior duplication of environment parsing, YAML loading, and configuration
dataclasses spread across multiple kits.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Self, TypeVar

from pheno.config import (
    Config,
    ConfigManager,
    collect_env,
    config_manager,
    get_env_bool,
    load_env_cascade,
    parse_dotenv,
)
from pheno.config import get_config as _core_get_config
from pheno.config.core import DatabaseConfig as CoreDatabaseConfig

T = TypeVar("T")


def get_env(
    key: str,
    default: str | None = None,
    *,
    required: bool = False,
    cast: type | None = None,
) -> Any:
    """
    Retrieve an environment variable with optional casting and validation.
    """

    value = os.environ.get(key, default)

    if value is None:
        if required:
            raise ValueError(f"Required environment variable {key} not set")
        return None

    if cast is None:
        return value

    if cast is bool:
        return value.strip().lower() in {"true", "1", "yes", "on"}

    try:
        return cast(value)
    except (TypeError, ValueError) as exc:  # pragma: no cover - descriptive branch
        raise ValueError(f"Failed to cast {key}={value!r} to {cast.__name__}") from exc


def get_env_config(prefix: str = "") -> dict[str, str]:
    """
    Return a mapping of environment variables filtered by ``prefix``.
    """

    if not prefix:
        return dict(os.environ)

    prefix_upper = prefix.upper()
    return {k: v for k, v in os.environ.items() if k.startswith(prefix_upper)}


def load_env_file(path: str | Path, *, override: bool = False) -> dict[str, str]:
    """
    Parse a ``.env`` file and optionally apply the values to ``os.environ``.
    """

    env_map = parse_dotenv(path)
    if override:
        os.environ.update(env_map)
    else:
        for key, value in env_map.items():
            os.environ.setdefault(key, value)
    return env_map


def load_yaml(path: str | Path) -> dict[str, Any]:
    """
    Load structured configuration from YAML, relying on :class:`Config`.
    """

    config = Config.from_file(path)
    data = config.model_dump()
    if not isinstance(data, Mapping):
        raise ValueError(f"Expected mapping in {path}, received {type(data).__name__}")
    return dict(data)


def save_yaml(data: Mapping[str, Any], path: str | Path) -> None:
    """
    Persist a mapping to disk as YAML.
    """

    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - dependency issue
        raise RuntimeError("PyYAML is required to save YAML configurations") from exc

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(dict(data), handle, default_flow_style=False, sort_keys=False)


@dataclass
class ConfigBase:
    """
    Lightweight dataclass base with YAML round-tripping helpers.
    """

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """
        Construct a configuration instance from a plain mapping.
        """

        valid_fields = {field.name for field in fields(cls)}
        filtered = {key: value for key, value in data.items() if key in valid_fields}
        return cls(**filtered)  # type: ignore[arg-type]

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the configuration dataclass into a serialisable mapping.
        """

        result: dict[str, Any] = {}
        for field in fields(self):
            value = getattr(self, field.name)
            if isinstance(value, ConfigBase):
                result[field.name] = value.to_dict()
            elif isinstance(value, list):
                result[field.name] = [
                    v.to_dict() if isinstance(v, ConfigBase) else v for v in value
                ]
            elif isinstance(value, dict):
                result[field.name] = {
                    key: item.to_dict() if isinstance(item, ConfigBase) else item
                    for key, item in value.items()
                }
            else:
                result[field.name] = value
        return result

    @classmethod
    def from_yaml(cls, path: str | Path) -> Self:
        """
        Create a configuration instance from a YAML file.
        """

        return cls.from_dict(load_yaml(path))

    def to_yaml(self, path: str | Path) -> None:
        """
        Write the configuration to a YAML file.
        """

        save_yaml(self.to_dict(), path)

    def validate(self) -> None:  # pragma: no cover - hook for subclasses
        """
        Hook for subclasses that require custom validation logic.
        """


DatabaseConfig = CoreDatabaseConfig


@dataclass
class ServerConfig(ConfigBase):
    """
    Convenience schema for describing server runtime settings.
    """

    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    reload: bool = False
    log_level: str = "info"


@dataclass
class AuthConfig(ConfigBase):
    """
    Simple authentication configuration container.
    """

    enabled: bool = True
    provider: str = "authkit"
    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = ""


@dataclass
class EnvLoader:
    """
    Aggregate environment variables from project roots and explicit files.
    """

    root_dirs: tuple[Path, ...] = ()
    files: tuple[Path, ...] = ()
    override: bool = False

    def load(self) -> dict[str, str]:
        """
        Return merged environment values without mutating ``os.environ``.
        """

        roots = [Path(root) for root in self.root_dirs]
        explicit = [Path(path) for path in self.files]
        return load_env_cascade(root_dirs=roots, env_files=explicit)

    def apply(self) -> dict[str, str]:
        """
        Load values and apply them to the current process environment.
        """

        values = self.load()
        if self.override:
            os.environ.update(values)
        else:
            for key, value in values.items():
                os.environ.setdefault(key, value)
        return values


def get_config() -> dict[str, str]:
    """
    Return auxiliary configuration hints expected by legacy consumers.
    """

    return _core_get_config()


__all__ = [
    "AuthConfig",
    "Config",
    "ConfigBase",
    "ConfigManager",
    "DatabaseConfig",
    "EnvLoader",
    "ServerConfig",
    "collect_env",
    "config_manager",
    "get_config",
    "get_env",
    "get_env_bool",
    "get_env_config",
    "load_env_cascade",
    "load_env_file",
    "load_yaml",
    "parse_dotenv",
    "save_yaml",
]
