"""Unit tests for configuration manager.

Test Cases:
- TC-1.4.1: Set Configuration Value
- TC-1.4.2: Configuration Hierarchy
- TC-1.4.3: Invalid Configuration Value
- TC-1.4.4: Project-Specific Config
- TC-1.4.5: Config Schema Validation
"""

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tracertm.config.manager import ConfigManager
from tracertm.config.schema import Config


@pytest.fixture
def temp_config_dir(tmp_path: Path) -> Path:
    """Create temporary config directory."""
    config_dir = tmp_path / "tracertm_config"
    config_dir.mkdir()
    return config_dir


@pytest.fixture
def config_manager(temp_config_dir: Path) -> ConfigManager:
    """Create config manager with temp directory."""
    return ConfigManager(config_dir=temp_config_dir)


class TestConfigManager:
    """Test suite for ConfigManager."""

    # TC-1.4.1: Set Configuration Value
    @pytest.mark.unit
    def test_set_configuration_value(self, config_manager: ConfigManager) -> None:
        """TC-1.4.1: Set Configuration Value.

        Given: Project initialized
        When: User runs `rtm config set default_view FEATURE`
        Then: Config value persisted to config.yaml
        And: `rtm config show` displays updated value
        """
        # Arrange: Initialize config
        config_manager.init(database_url="postgresql://localhost/test")

        # Act: Set configuration value
        config_manager.set("default_view", "CODE")

        # Assert: Value persisted
        loaded_config = config_manager.load()
        assert loaded_config.default_view == "CODE"

        # Assert: Config file contains correct value
        config_path = config_manager.config_path
        assert config_path.exists()

        import yaml

        with Path(config_path).open(encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
        assert config_data["default_view"] == "CODE"

    # TC-1.4.2: Configuration Hierarchy
    @pytest.mark.unit
    def test_configuration_hierarchy(self, config_manager: ConfigManager, monkeypatch: Any) -> None:
        """TC-1.4.2: Configuration Hierarchy.

        Given: Config values at multiple levels (CLI flag, env var, project config, global config)
        When: Config loaded
        Then: CLI flags override env vars override project config override global config
        """
        # Arrange: Set global config
        config_manager.init(database_url="postgresql://localhost/test")
        config_manager.set("default_view", "FEATURE")
        config_manager.set("output_format", "table")

        # Arrange: Set project config
        project_id = "test-project"
        config_manager.set("default_view", "CODE", project_id=project_id)

        # Arrange: Set environment variable (higher precedence)
        monkeypatch.setenv("TRACERTM_OUTPUT_FORMAT", "json")

        # Act: Load config with project
        config = config_manager.load(project_id=project_id)

        # Assert: Correct precedence
        assert config.default_view == "CODE"  # Project config overrides global
        assert config.output_format == "json"  # Env var overrides project config
        assert config.database_url == "postgresql://localhost/test"  # From global config

    # TC-1.4.3: Invalid Configuration Value
    @pytest.mark.unit
    def test_invalid_configuration_value(self, config_manager: ConfigManager) -> None:
        """TC-1.4.3: Invalid Configuration Value.

        Given: User sets invalid config value
        When: `rtm config set output_format invalid_format`
        Then: Validation error displayed
        And: Suggests valid values (table, json, yaml)
        """
        # Arrange: Initialize config
        config_manager.init(database_url="postgresql://localhost/test")

        # Act & Assert: Invalid value raises ValidationError
        with pytest.raises(ValidationError) as exc_info:
            config_manager.set("output_format", "invalid_format")

        # Assert: Error message mentions valid values
        error_message = str(exc_info.value)
        assert "output_format" in error_message
        # Pydantic will show allowed values in error

    # TC-1.4.4: Project-Specific Config
    @pytest.mark.unit
    def test_project_specific_config(self, config_manager: ConfigManager) -> None:
        """TC-1.4.4: Project-Specific Config.

        Given: Global config has default_view=FEATURE
        When: Project config sets default_view=CODE
        Then: Project config overrides global config
        """
        # Arrange: Set global config
        config_manager.init(database_url="postgresql://localhost/test")
        config_manager.set("default_view", "FEATURE")

        # Arrange: Set project-specific config
        project_id = "my-project"
        config_manager.set("default_view", "CODE", project_id=project_id)

        # Act: Load global config
        global_config = config_manager.load()

        # Act: Load project config
        project_config = config_manager.load(project_id=project_id)

        # Assert: Global config unchanged
        assert global_config.default_view == "FEATURE"

        # Assert: Project config overrides
        assert project_config.default_view == "CODE"

    # TC-1.4.5: Config Schema Validation
    @pytest.mark.unit
    def test_config_schema_validation(self) -> None:
        """TC-1.4.5: Config Schema Validation.

        Given: Config file with invalid schema
        When: Config loaded
        Then: Pydantic validation error raised
        And: Clear error message with field name
        """
        # Test 1: Invalid database URL
        with pytest.raises(ValidationError) as exc_info:
            Config(database_url="invalid://url")
        assert "database_url" in str(exc_info.value)
        assert "postgresql://" in str(exc_info.value)

        # Test 2: Invalid view type
        with pytest.raises(ValidationError) as exc_info:
            Config(default_view="INVALID_VIEW")
        assert "default_view" in str(exc_info.value)

        # Test 3: Invalid output format
        with pytest.raises(ValidationError) as exc_info:
            Config(output_format="invalid")
        assert "output_format" in str(exc_info.value)

        # Test 4: Invalid max_agents (out of range)
        with pytest.raises(ValidationError) as exc_info:
            Config(max_agents=0)  # Must be >= 1
        assert "max_agents" in str(exc_info.value)

        # Test 5: Valid config passes
        valid_config = Config(
            database_url="postgresql://localhost/test",
            default_view="FEATURE",
            output_format="json",
            max_agents=100,
        )
        assert valid_config.database_url == "postgresql://localhost/test"
        assert valid_config.default_view == "FEATURE"
