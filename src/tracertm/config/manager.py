"""
Configuration manager for TraceRTM.

Handles configuration hierarchy:
1. CLI flags (highest precedence)
2. Environment variables (TRACERTM_*)
3. Project config
4. Global config (lowest precedence)
"""

import os
from pathlib import Path
from typing import Any

import yaml

from tracertm.config.schema import Config


class ConfigManager:
    """
    Manages TraceRTM configuration with hierarchical precedence.

    Configuration locations:
    - Global: ~/.tracertm/config.yaml
    - Project: ~/.tracertm/projects/<project_id>/config.yaml
    """

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize config manager.

        Args:
            config_dir: Override default config directory (for testing)
        """
        self.config_dir = self._resolve_config_dir(config_dir)
        self.config_path = self.config_dir / "config.yaml"
        self.projects_dir = self.config_dir / "projects"

    def _resolve_config_dir(self, config_dir: Path | None) -> Path:
        """
        Resolve the config directory.

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
        legacy = Path.home() / ".config" / "tracertm"

        if preferred.exists():
            return preferred
        if legacy.exists() and not preferred.exists():
            return legacy

        return preferred

    def init(self, database_url: str) -> Config:
        """
        Initialize TraceRTM configuration.

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
        config = Config(
            database_url=database_url,
            current_project_id=None,
            current_project_name=None,
            default_view="FEATURE",
            output_format="table",
            max_agents=4,
            log_level="INFO",
        )

        # Save to file
        self._save_config(config, self.config_path)

        return config

    def load(self, project_id: str | None = None) -> Config:
        """
        Load configuration with hierarchy.

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
            with open(self.config_path) as f:
                global_config = yaml.safe_load(f) or {}
                config_data.update(global_config)
        else:
            raise FileNotFoundError(
                f"Configuration not found. Run 'rtm config init' first.\n"
                f"Expected location: {self.config_path}"
            )

        # Load project config (if specified)
        if project_id:
            project_config_path = self.projects_dir / project_id / "config.yaml"
            if project_config_path.exists():
                with open(project_config_path) as f:
                    project_config = yaml.safe_load(f) or {}
                    config_data.update(project_config)

        # Override with environment variables
        env_overrides = self._load_from_env()
        config_data.update(env_overrides)

        # Create and validate config
        return Config(**config_data)

    def set(self, key: str, value: Any, project_id: str | None = None) -> None:
        """
        Set a configuration value.

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
            with open(config_path) as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}

        # Update value
        config_data[key] = value

        # Validate by creating Config instance
        Config(**config_data)

        # Convert Path objects to strings before saving
        config_data = self._convert_paths_to_strings(config_data)

        # Save
        with open(config_path, "w") as f:
            yaml.safe_dump(config_data, f, default_flow_style=False)

    def get(self, key: str, project_id: str | None = None) -> Any | None:
        """
        Get a configuration value.

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
        
        # Determine config file
        config_path = self.projects_dir / project_id / "config.yaml" if project_id else self.config_path

        # Load config
        if not config_path.exists():
            return None

        with open(config_path) as f:
            config_data = yaml.safe_load(f) or {}

        return config_data.get(key)

    def get_config(self, project_id: str | None = None) -> dict[str, Any]:
        """
        Return the resolved configuration as a dictionary for tests and callers
        that expect a simple mapping.

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
        with open(path, "w") as f:
            yaml.safe_dump(config_dict, f, default_flow_style=False)
    
    def _convert_paths_to_strings(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively convert Path objects to strings in a dictionary."""
        result = {}
        for key, value in data.items():
            if isinstance(value, Path):
                result[key] = str(value)
            elif isinstance(value, dict):
                result[key] = self._convert_paths_to_strings(value)
            elif isinstance(value, list):
                result[key] = [
                    str(item) if isinstance(item, Path) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def _load_from_env(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}

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
            value = os.getenv(env_var)
            if value is not None:
                # Convert types
                if config_key == "max_agents":
                    value = int(value)
                env_config[config_key] = value
                # If we found database_url from DATABASE_URL, don't override with TRACERTM_DATABASE_URL
                if config_key == "database_url" and env_var == "DATABASE_URL":
                    break

        return env_config
