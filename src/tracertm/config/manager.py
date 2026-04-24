"""Configuration manager for TraceRTM.

Handles configuration hierarchy:
1. CLI flags (highest precedence)
2. Environment variables (TRACERTM_*)
3. Project config
4. Global config (lowest precedence)
"""

import os
from pathlib import Path
from typing import Any, cast

import yaml

from tracertm.config.schema import Config


class ConfigManager:
    """Manages TraceRTM configuration with hierarchical precedence.

    Configuration locations:
    - Global: ~/.tracertm/config.yaml
    - Repo project: <repo>/.tracertm/project.yaml
    - User project: ~/.tracertm/projects/<project_id>/config.yaml
    """

    def __init__(self, config_dir: Path | None = None) -> None:
        """Initialize config manager.

        Args:
            config_dir: Override default config directory (for testing)
        """
        self.config_dir = self._resolve_config_dir(config_dir)
        self.config_path = self.config_dir / "config.yaml"
        self.projects_dir = self.config_dir / "projects"

    def _resolve_config_dir(self, config_dir: Path | None) -> Path:
        """Resolve the config directory.

        Precedence:
        1) Explicit config_dir argument (tests/overrides)
        2) TRACERTM_CONFIG_DIR env var
        3) ~/.tracertm (preferred)
        4) Legacy ~/.config/tracertm (fallback if it exists and preferred dir does not)
        """
        if config_dir:
            return Path(config_dir)

        env_dir = os.getenv("TRACERTM_CONFIG_DIR")
        if env_dir:
            return Path(env_dir)

        preferred = Path.home() / ".tracertm"
        fallback = Path.home() / ".config" / "tracertm"

        if preferred.exists():
            return preferred
        if fallback.exists() and not preferred.exists():
            return fallback

        return preferred

    def init(self, database_url: str) -> Config:
        """Initialize TraceRTM configuration.

        Args:
            database_url: PostgreSQL database URL

        Returns:
            Created configuration

        Raises:
            ValueError: If database_url is invalid
        """
        # Create config directory
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.projects_dir.mkdir(parents=True, exist_ok=True)

        # Create config with all required fields
        config = Config.model_validate({
            "database_url": database_url,
            "current_project_id": None,
            "current_project_name": None,
            "default_view": "FEATURE",
            "output_format": "table",
            "max_agents": 4,
            "log_level": "INFO",
        })

        # Save to file
        self._save_config(config, self.config_path)

        return config

    def load(self, project_id: str | None = None) -> Config:
        """Load configuration with hierarchy.

        Args:
            project_id: Optional project ID for project-specific config

        Returns:
            Merged configuration

        Raises:
            FileNotFoundError: If config file doesn't exist
        """
        # Start with defaults
        config_data: dict[str, Any] = {}

        # Load global config
        if self.config_path.exists():
            with self.config_path.open() as f:
                global_config = yaml.safe_load(f) or {}
                config_data.update(global_config)
        else:
            msg = f"Configuration not found. Run 'rtm config init' first.\nExpected location: {self.config_path}"
            raise FileNotFoundError(
                msg,
            )

        # Load repo-level project config (if present)
        repo_project = self._load_repo_project_config()
        if repo_project:
            config_data.update(repo_project)

        # Load user project config (if specified)
        if project_id:
            project_config_path = self.projects_dir / project_id / "config.yaml"
            if project_config_path.exists():
                with project_config_path.open() as f:
                    project_config = yaml.safe_load(f) or {}
                    config_data.update(project_config)

        # Override with environment variables
        env_overrides = self._load_from_env()
        config_data.update(env_overrides)

        # Create and validate config
        return Config.model_validate(config_data)

    def set(self, key: str, value: object, project_id: str | None = None) -> None:
        """Set a configuration value.

        Args:
            key: Configuration key
            value: Configuration value
            project_id: Optional project ID for project-specific config

        Raises:
            ValueError: If key is invalid or value fails validation
        """
        # Determine config file
        if project_id:
            config_path = self.projects_dir / project_id / "config.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            config_path = self.config_path

        # Load existing config
        if config_path.exists():
            with config_path.open() as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}

        # Update value
        config_data[key] = value

        # Validate only known Config fields (allow extra fields in file)
        # Get field names from Config model
        config_fields = set(Config.model_fields.keys())
        known_fields = {k: v for k, v in config_data.items() if k in config_fields}

        # Only validate known fields
        if known_fields:
            Config.model_validate(known_fields)

        # Convert Path objects to strings before saving
        config_data = self._convert_paths_to_strings(config_data)

        # Save (including extra fields)
        with config_path.open("w") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

    def get(self, key: str, project_id: str | None = None) -> Any:
        """Get a configuration value.

        Args:
            key: Configuration key
            project_id: Optional project ID for project-specific config

        Returns:
            Configuration value or None if not found
        """
        # Check environment variables first (highest precedence)
        if key == "database_url":
            # Check both TRACERTM_DATABASE_URL and DATABASE_URL
            db_url = os.getenv("TRACERTM_DATABASE_URL") or os.getenv("DATABASE_URL")
            if db_url:
                return db_url

        # User project config (highest file-based precedence)
        if project_id:
            project_config_path = self.projects_dir / project_id / "config.yaml"
            if project_config_path.exists():
                with project_config_path.open() as f:
                    config_data = yaml.safe_load(f) or {}
                if key in config_data:
                    return config_data.get(key)

        # Repo project config (shared)
        repo_project = self._load_repo_project_config()
        if repo_project and key in repo_project:
            return repo_project.get(key)

        # Global config (lowest precedence)
        if not self.config_path.exists():
            return None

        with self.config_path.open() as f:
            config_data = yaml.safe_load(f) or {}

        return config_data.get(key)

    def get_config(self, project_id: str | None = None) -> dict[str, Any]:
        """Return the resolved configuration as a dictionary.

        This is used by tests and callers that expect a simple mapping.

        This method is intentionally tolerant of missing on-disk config files;
        it will fall back to an empty dictionary rather than raising.
        """
        try:
            loaded = self.load(project_id=project_id)
            if hasattr(loaded, "model_dump"):
                return loaded.model_dump()
            return dict(loaded)
        except Exception:
            # Return whatever values we can read without failing the caller
            keys = [
                "database_url",
                "current_project_id",
                "current_project_name",
                "default_view",
                "output_format",
                "max_agents",
                "log_level",
            ]
            return {key: self.get(key, project_id=project_id) for key in keys}

    def _save_config(self, config: Config, path: Path) -> None:
        """Save config to YAML file."""
        config_dict = config.model_dump()
        # Convert Path objects to strings for YAML serialization
        config_dict = self._convert_paths_to_strings(config_dict)
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(config_dict, f, default_flow_style=False)

    def _convert_paths_to_strings(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively convert Path objects to strings in a dictionary."""
        result: dict[str, Any] = {}
        for key, value in data.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = self._convert_paths_to_strings(value)
            elif isinstance(value, list):
                result[key] = [str(item) if isinstance(item, Path) else item for item in value]
            else:
                result[key] = value
        return result

    def _load_from_env(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        env_config: dict[str, Any] = {}

        # Map environment variables to config keys
        env_mapping = {
            "TRACERTM_DATABASE_URL": "database_url",
            "DATABASE_URL": "database_url",  # Also check standard DATABASE_URL
            "TRACERTM_CURRENT_PROJECT_ID": "current_project_id",
            "TRACERTM_DEFAULT_VIEW": "default_view",
            "TRACERTM_OUTPUT_FORMAT": "output_format",
            "TRACERTM_MAX_AGENTS": "max_agents",
            "TRACERTM_LOG_LEVEL": "log_level",
        }

        for env_var, config_key in env_mapping.items():
            raw_value = os.getenv(env_var)
            if raw_value is not None:
                # Convert types
                converted: str | int = int(raw_value) if config_key == "max_agents" else raw_value
                env_config[config_key] = converted
                # If we found database_url from DATABASE_URL, don't override with TRACERTM_DATABASE_URL
                if config_key == "database_url" and env_var == "DATABASE_URL":
                    break

        return env_config

    def _find_repo_project_path(self) -> Path | None:
        """Find the nearest repo-level .tracertm/project.yaml from CWD."""
        try:
            current = Path.cwd().resolve()
        except Exception:
            return None

        for base in [current, *current.parents]:
            candidate = base / ".tracertm" / "project.yaml"
            if candidate.exists():
                return candidate
        return None

    def _load_repo_project_config(self) -> dict[str, Any]:
        """Load repo-level project config if available."""
        path = self._find_repo_project_path()
        if not path:
            return {}
        try:
            with path.open() as f:
                data = yaml.safe_load(f) or {}
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def set_repo_project_value(self, key: str, value: object) -> Path:
        """Set a value in the repo-level .tracertm/project.yaml.

        Returns:
            The path written to.
        """
        base = self._find_repo_project_path()
        if base is None:
            base = Path.cwd() / ".tracertm" / "project.yaml"
            base.parent.mkdir(parents=True, exist_ok=True)

        if base.exists():
            with base.open() as f:
                data = yaml.safe_load(f) or {}
        else:
            data = {}

        if value is None:
            data.pop(key, None)
        else:
            data[key] = value

        data = self._convert_paths_to_strings(data)

        with base.open("w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)

        return base
