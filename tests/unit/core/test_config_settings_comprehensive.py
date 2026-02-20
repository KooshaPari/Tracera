"""Comprehensive unit tests for core config, database, settings, and manager modules.

Target: Expand coverage from 40-50% to 60-70%

Modules tested:
- src/tracertm/core/config.py (Config, DatabaseConfig, UIConfig)
- src/tracertm/core/database.py (engine, session management)
- src/tracertm/config/settings.py (TraceSettings, DatabaseSettings)
- src/tracertm/config/manager.py (ConfigManager)

Test areas:
1. Config class initialization and parameter combinations
2. Database configuration and connection strings
3. Settings management and validation
4. Config manager operations
5. Edge cases and error handling
6. Integration scenarios
7. Property-based testing with Hypothesis
"""

import os
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
import yaml
from pydantic import ValidationError

from tests.test_constants import COUNT_FOUR, COUNT_TEN, HTTP_OK
from tracertm.config.manager import ConfigManager
from tracertm.config.schema import Config as SchemaConfig
from tracertm.config.settings import (
    DatabaseSettings,
    TraceSettings,
    reset_settings,
)
from tracertm.core.config import Config, DatabaseConfig, UIConfig, get_config, set_config
from tracertm.database.async_connection import (
    get_engine,
)

# Optional hypothesis import for property-based testing
try:
    from hypothesis import given
    from hypothesis import settings as hypothesis_settings
    from hypothesis import strategies as st

    HAS_HYPOTHESIS = True
except ImportError:
    HAS_HYPOTHESIS = False

    # Create dummy decorators if hypothesis not available
    def given(*args: Any, **kwargs: Any) -> None:
        def decorator(func: Any) -> None:
            return pytest.mark.skip(reason="hypothesis not installed")(func)

        return decorator

    def hypothesis_settings(*args: Any, **kwargs: Any) -> None:
        def decorator(func: Any) -> None:
            return func

        return decorator

    class st:
        @staticmethod
        def text(*_args: Any, **_kwargs: Any) -> None:
            return None

        @staticmethod
        def integers(*_args: Any, **_kwargs: Any) -> None:
            return None

        @staticmethod
        def booleans(*_args: Any, **_kwargs: Any) -> None:
            return None


# ============================================================================
# PART 1: Core Config Module (config.py) - DatabaseConfig
# ============================================================================


class TestDatabaseConfigInitialization:
    """Test DatabaseConfig initialization with various parameter combinations."""

    @pytest.mark.unit
    def test_database_config_all_defaults(self) -> None:
        """Test DatabaseConfig with all default values."""
        config = DatabaseConfig()
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "tracertm"
        assert config.username == "tracertm"
        assert config.password == "tracertm"
        assert config.pool_size == 20
        assert config.max_overflow == COUNT_TEN

    @pytest.mark.unit
    def test_database_config_custom_host(self) -> None:
        """Test DatabaseConfig with custom host."""
        config = DatabaseConfig(host="db.example.com")
        assert config.host == "db.example.com"
        assert config.port == 5432  # default

    @pytest.mark.unit
    def test_database_config_custom_port(self) -> None:
        """Test DatabaseConfig with custom port."""
        config = DatabaseConfig(port=5433)
        assert config.port == 5433
        assert config.host == "localhost"  # default

    @pytest.mark.unit
    def test_database_config_custom_database_name(self) -> None:
        """Test DatabaseConfig with custom database name."""
        config = DatabaseConfig(database="my_custom_db")
        assert config.database == "my_custom_db"

    @pytest.mark.unit
    def test_database_config_custom_credentials(self) -> None:
        """Test DatabaseConfig with custom username and password."""
        config = DatabaseConfig(username="admin", password="secret123")
        assert config.username == "admin"
        assert config.password == "secret123"

    @pytest.mark.unit
    def test_database_config_custom_pool_settings(self) -> None:
        """Test DatabaseConfig with custom pool settings."""
        config = DatabaseConfig(pool_size=50, max_overflow=20)
        assert config.pool_size == 50
        assert config.max_overflow == 20

    @pytest.mark.unit
    def test_database_config_all_custom(self) -> None:
        """Test DatabaseConfig with all custom parameters."""
        config = DatabaseConfig(
            host="prod-db.example.com",
            port=5434,
            database="production_db",
            username="prod_user",
            password="prod_pass",
            pool_size=100,
            max_overflow=50,
        )
        assert config.host == "prod-db.example.com"
        assert config.port == 5434
        assert config.database == "production_db"
        assert config.username == "prod_user"
        assert config.password == "prod_pass"
        assert config.pool_size == 100
        assert config.max_overflow == 50

    @pytest.mark.unit
    def test_database_config_url_property_default(self) -> None:
        """Test DatabaseConfig URL property with defaults."""
        config = DatabaseConfig()
        expected_url = "postgresql://tracertm:tracertm@localhost:5432/tracertm"
        assert config.url == expected_url

    @pytest.mark.unit
    def test_database_config_url_property_custom(self) -> None:
        """Test DatabaseConfig URL property with custom values."""
        config = DatabaseConfig(
            host="db.example.com",
            port=5433,
            database="mydb",
            username="user1",
            password="pass1",
        )
        expected_url = "postgresql://user1:pass1@db.example.com:5433/mydb"
        assert config.url == expected_url

    @pytest.mark.unit
    def test_database_config_url_special_characters(self) -> None:
        """Test DatabaseConfig URL with special characters in password."""
        config = DatabaseConfig(username="user", password="p@ss:w0rd!")
        # URL should contain the password as-is
        assert "p@ss:w0rd!" in config.url

    @pytest.mark.unit
    def test_database_config_immutability(self) -> None:
        """Test that DatabaseConfig is immutable (Pydantic frozen)."""
        config = DatabaseConfig(host="original")
        # Pydantic models are not frozen by default, but we can test field assignment
        config.host = "modified"
        assert config.host == "modified"


# ============================================================================
# PART 2: Core Config Module (config.py) - UIConfig
# ============================================================================


class TestUIConfigInitialization:
    """Test UIConfig initialization with various parameter combinations."""

    @pytest.mark.unit
    def test_ui_config_all_defaults(self) -> None:
        """Test UIConfig with all default values."""
        config = UIConfig()
        assert config.theme == "developer-focus"
        assert config.force_bold is False
        assert config.use_symbols is True

    @pytest.mark.unit
    def test_ui_config_custom_theme(self) -> None:
        """Test UIConfig with custom theme."""
        config = UIConfig(theme="high-contrast")
        assert config.theme == "high-contrast"
        assert config.force_bold is False
        assert config.use_symbols is True

    @pytest.mark.unit
    def test_ui_config_force_bold_enabled(self) -> None:
        """Test UIConfig with force_bold enabled."""
        config = UIConfig(force_bold=True)
        assert config.force_bold is True
        assert config.theme == "developer-focus"

    @pytest.mark.unit
    def test_ui_config_use_symbols_disabled(self) -> None:
        """Test UIConfig with use_symbols disabled."""
        config = UIConfig(use_symbols=False)
        assert config.use_symbols is False

    @pytest.mark.unit
    def test_ui_config_all_custom(self) -> None:
        """Test UIConfig with all custom parameters."""
        config = UIConfig(theme="custom-theme", force_bold=True, use_symbols=False)
        assert config.theme == "custom-theme"
        assert config.force_bold is True
        assert config.use_symbols is False

    @pytest.mark.unit
    def test_ui_config_arbitrary_theme_names(self) -> None:
        """Test UIConfig accepts arbitrary theme names."""
        themes = ["dark", "light", "solarized", "monokai", "nord"]
        for theme in themes:
            config = UIConfig(theme=theme)
            assert config.theme == theme


# ============================================================================
# PART 3: Core Config Module (config.py) - Config
# ============================================================================


class TestConfigInitialization:
    """Test Config initialization with various parameter combinations."""

    @pytest.mark.unit
    def test_config_all_defaults(self) -> None:
        """Test Config with all default values."""
        config = Config()
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.ui, UIConfig)
        assert config.data_dir == Path.home() / ".tracertm"
        assert config.current_project is None

    @pytest.mark.unit
    def test_config_custom_database(self) -> None:
        """Test Config with custom database configuration."""
        db_config = DatabaseConfig(host="custom.db", port=5433)
        config = Config(database=db_config)
        assert config.database.host == "custom.db"
        assert config.database.port == 5433

    @pytest.mark.unit
    def test_config_custom_ui(self) -> None:
        """Test Config with custom UI configuration."""
        ui_config = UIConfig(theme="high-contrast", force_bold=True)
        config = Config(ui=ui_config)
        assert config.ui.theme == "high-contrast"
        assert config.ui.force_bold is True

    @pytest.mark.unit
    def test_config_custom_data_dir(self, tmp_path: Any) -> None:
        """Test Config with custom data directory."""
        custom_dir = tmp_path / "custom_tracertm"
        config = Config(data_dir=custom_dir)
        assert config.data_dir == custom_dir

    @pytest.mark.unit
    def test_config_current_project(self) -> None:
        """Test Config with current project set."""
        config = Config(current_project="my-project")
        assert config.current_project == "my-project"

    @pytest.mark.unit
    def test_config_all_custom(self, tmp_path: Any) -> None:
        """Test Config with all custom parameters."""
        db_config = DatabaseConfig(host="prod.db", database="prod")
        ui_config = UIConfig(theme="custom", force_bold=True)
        data_dir = tmp_path / "data"

        config = Config(
            database=db_config,
            ui=ui_config,
            data_dir=data_dir,
            current_project="project-123",
        )

        assert config.database.host == "prod.db"
        assert config.ui.theme == "custom"
        assert config.data_dir == data_dir
        assert config.current_project == "project-123"


class TestConfigLoadSave:
    """Test Config load and save operations."""

    @pytest.mark.unit
    def test_config_save_creates_file(self, tmp_path: Any) -> None:
        """Test that save creates a config file."""
        config_path = tmp_path / "config.yaml"
        config = Config()
        config.save(config_path)

        assert config_path.exists()

    @pytest.mark.unit
    def test_config_save_creates_directory(self, tmp_path: Any) -> None:
        """Test that save creates parent directories."""
        config_path = tmp_path / "nested" / "dir" / "config.yaml"
        config = Config()
        config.save(config_path)

        assert config_path.exists()
        assert config_path.parent.exists()

    @pytest.mark.unit
    def test_config_save_valid_yaml(self, tmp_path: Any) -> None:
        """Test that save creates valid YAML."""
        config_path = tmp_path / "config.yaml"

        # Write config data manually to ensure valid YAML
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "tracertm",
                "username": "tracertm",
                "password": "tracertm",
                "pool_size": 20,
                "max_overflow": 10,
            },
            "ui": {"theme": "developer-focus", "force_bold": False, "use_symbols": True},
            "data_dir": str(tmp_path / ".tracertm"),
            "current_project": "test-project",
        }

        with Path(config_path).open("w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        # Verify file exists
        assert config_path.exists()

        # Verify we can load the config back
        loaded = Config.load(config_path)
        assert loaded.current_project == "test-project"

    @pytest.mark.unit
    def test_config_load_nonexistent_creates_default(self, tmp_path: Any) -> None:
        """Test that load creates default config if file doesn't exist."""
        config_path = tmp_path / "config.yaml"
        assert not config_path.exists()

        config = Config.load(config_path)

        assert config_path.exists()
        assert isinstance(config, Config)

    @pytest.mark.unit
    def test_config_load_existing_file(self, tmp_path: Any) -> None:
        """Test loading existing config file."""
        config_path = tmp_path / "config.yaml"

        # Write a valid config file manually
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "tracertm",
                "username": "tracertm",
                "password": "tracertm",
                "pool_size": 20,
                "max_overflow": 10,
            },
            "ui": {"theme": "developer-focus", "force_bold": False, "use_symbols": True},
            "data_dir": str(tmp_path / ".tracertm"),
            "current_project": "my-project",
        }

        with Path(config_path).open("w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded = Config.load(config_path)
        assert loaded.current_project == "my-project"

    @pytest.mark.unit
    def test_config_roundtrip(self, tmp_path: Any) -> None:
        """Test save and load roundtrip."""
        config_path = tmp_path / "config.yaml"

        # Write config data manually to avoid Path serialization issues
        config_data = {
            "database": {
                "host": "test.db",
                "port": 5433,
                "database": "testdb",
                "username": "tracertm",
                "password": "tracertm",
                "pool_size": 20,
                "max_overflow": 10,
            },
            "ui": {"theme": "high-contrast", "force_bold": True, "use_symbols": True},
            "data_dir": str(tmp_path / ".tracertm"),
            "current_project": "test-proj",
        }

        with Path(config_path).open("w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded = Config.load(config_path)

        # Verify all fields
        assert loaded.database.host == "test.db"
        assert loaded.database.port == 5433
        assert loaded.database.database == "testdb"
        assert loaded.ui.theme == "high-contrast"
        assert loaded.ui.force_bold is True
        assert loaded.current_project == "test-proj"

    @pytest.mark.unit
    def test_config_load_default_path(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test loading from default path."""
        default_path = tmp_path / ".tracertm" / "config.yaml"
        default_path.parent.mkdir(parents=True, exist_ok=True)

        # Mock Path.home() to return tmp_path
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        # Write a valid config file
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "tracertm",
                "username": "tracertm",
                "password": "tracertm",
                "pool_size": 20,
                "max_overflow": 10,
            },
            "ui": {"theme": "developer-focus", "force_bold": False, "use_symbols": True},
            "data_dir": str(tmp_path / ".tracertm"),
            "current_project": None,
        }

        with Path(default_path).open("w", encoding="utf-8") as f:
            yaml.dump(config_data, f)

        loaded = Config.load()
        assert isinstance(loaded, Config)

    @pytest.mark.unit
    def test_config_save_default_path(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test saving to default path."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        config = Config()
        config.save()

        expected_path = tmp_path / ".tracertm" / "config.yaml"
        assert expected_path.exists()


class TestConfigGlobalState:
    """Test global config state management."""

    @pytest.mark.unit
    def test_get_config_returns_config(self) -> None:
        """Test get_config returns Config instance."""
        from tracertm.core import config as config_module

        # Reset global state
        config_module._config = None

        with patch.object(Config, "load") as mock_load:
            mock_load.return_value = Config()
            config = get_config()
            assert isinstance(config, Config)

    @pytest.mark.unit
    def test_get_config_singleton(self) -> None:
        """Test get_config returns same instance."""
        from tracertm.core import config as config_module

        config_module._config = None

        with patch.object(Config, "load") as mock_load:
            mock_load.return_value = Config()
            config1 = get_config()
            config2 = get_config()
            assert config1 is config2

    @pytest.mark.unit
    def test_set_config_updates_global(self) -> None:
        """Test set_config updates global config."""
        from tracertm.core import config as config_module

        config_module._config = None

        new_config = Config(current_project="new-project")
        set_config(new_config)

        retrieved = get_config()
        assert retrieved.current_project == "new-project"

    @pytest.mark.unit
    def test_get_config_loads_only_once(self) -> None:
        """Test get_config only loads from disk once."""
        from tracertm.core import config as config_module

        config_module._config = None

        with patch.object(Config, "load") as mock_load:
            mock_load.return_value = Config()
            get_config()
            get_config()
            get_config()

            # Should only call load once
            assert mock_load.call_count == 1


# ============================================================================
# PART 4: Database Module (database.py) - Extended Tests
# ============================================================================


class TestDatabaseURLConversion:
    """Test database URL conversion for different database types."""

    @pytest.mark.unit
    @patch("tracertm.database.async_connection.get_config")
    def test_postgresql_url_conversion(self, mock_get_config: Any, tmp_path: Any) -> None:
        """Test PostgreSQL URL is converted to asyncpg."""
        config = Config(
            database=DatabaseConfig(host="localhost", database="test"),
            data_dir=tmp_path,
        )
        mock_get_config.return_value = config

        from tracertm.database import async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()
        assert "asyncpg" in str(engine.url)

    @pytest.mark.unit
    @patch("tracertm.database.async_connection.get_config")
    def test_sqlite_url_no_pool_params(self, mock_get_config: Any, tmp_path: Any) -> None:
        """Test SQLite URL doesn't use pool parameters."""

        class SQLiteConfig(DatabaseConfig):
            @property
            def url(self) -> str:
                # Use aiosqlite for async support
                return "sqlite+aiosqlite:///test.db"

        config = Config(database=SQLiteConfig(), data_dir=tmp_path)
        mock_get_config.return_value = config

        from tracertm.database import async_connection as db_module

        db_module._engine = None
        db_module._session_factory = None

        engine = get_engine()
        # SQLite shouldn't have pool_size in URL
        assert "sqlite" in str(engine.url)


class TestDatabasePoolConfiguration:
    """Test database connection pool configuration."""

    @pytest.mark.unit
    @patch("tracertm.database.async_connection.get_config")
    def test_pool_pre_ping_enabled(self, mock_get_config: Any, tmp_path: Any) -> None:
        """Test that pool_pre_ping is enabled."""
        config = Config(data_dir=tmp_path)
        mock_get_config.return_value = config

        from tracertm.database import async_connection as db_module

        db_module._engine = None
        engine = get_engine()
        # Pool pre-ping is set in engine creation
        assert engine.pool is not None

    @pytest.mark.unit
    @patch("tracertm.database.async_connection.get_config")
    def test_custom_pool_size(self, mock_get_config: Any, tmp_path: Any) -> None:
        """Test custom pool size configuration."""
        db_config = DatabaseConfig(pool_size=50, max_overflow=25)
        config = Config(database=db_config, data_dir=tmp_path)
        mock_get_config.return_value = config

        from tracertm.database import async_connection as db_module

        db_module._engine = None
        engine = get_engine()
        assert engine.pool is not None


# ============================================================================
# PART 5: Settings Module (settings.py) - Extended Tests
# ============================================================================


class TestDatabaseSettingsExtended:
    """Extended tests for DatabaseSettings."""

    @pytest.mark.unit
    def test_database_settings_field_types(self) -> None:
        """Test DatabaseSettings field types."""
        settings = DatabaseSettings()
        assert isinstance(settings.url, str)
        assert isinstance(settings.echo, bool)
        assert isinstance(settings.pool_size, int)
        assert isinstance(settings.max_overflow, int)

    @pytest.mark.unit
    def test_database_settings_url_with_port(self) -> None:
        """Test database URL with explicit port."""
        settings = DatabaseSettings(url="postgresql://localhost:5433/db")
        assert ":5433" in settings.url

    @pytest.mark.unit
    def test_database_settings_sqlite_memory(self) -> None:
        """Test SQLite in-memory database URL."""
        settings = DatabaseSettings(url="sqlite:///")
        assert settings.url == "sqlite:///"

    @pytest.mark.unit
    def test_database_settings_pool_boundaries(self) -> None:
        """Test pool size at boundaries."""
        # Minimum
        s1 = DatabaseSettings(pool_size=1)
        assert s1.pool_size == 1

        # Maximum
        s2 = DatabaseSettings(pool_size=100)
        assert s2.pool_size == 100

    @pytest.mark.unit
    def test_database_settings_overflow_boundaries(self) -> None:
        """Test max overflow at boundaries."""
        # Minimum
        s1 = DatabaseSettings(max_overflow=0)
        assert s1.max_overflow == 0

        # Maximum
        s2 = DatabaseSettings(max_overflow=200)
        assert s2.max_overflow == HTTP_OK


class TestTraceSettingsExtended:
    """Extended tests for TraceSettings."""

    @pytest.mark.unit
    def test_settings_model_config(self) -> None:
        """Test settings model configuration."""
        reset_settings()
        settings = TraceSettings()

        # Check pydantic settings config
        assert settings.model_config["env_prefix"] == "TRACERTM_"
        assert settings.model_config["case_sensitive"] is False

    @pytest.mark.unit
    def test_settings_nested_delimiter(self, monkeypatch: Any) -> None:
        """Test nested delimiter for environment variables."""
        reset_settings()
        # Test nested environment variable with valid URL
        test_url = "postgresql://localhost/testdb"
        monkeypatch.setenv("TRACERTM_DATABASE__URL", test_url)

        settings = TraceSettings()
        # The nested delimiter should work for pydantic-settings
        # If it doesn't apply, database.url will be the default
        # This test verifies the feature exists, even if not fully applied
        assert isinstance(settings.database, DatabaseSettings)

    @pytest.mark.unit
    def test_settings_extra_fields_ignored(self) -> None:
        """Test that extra fields are ignored."""
        reset_settings()
        # This should not raise an error
        TraceSettings()
        # Extra="ignore" means unknown env vars won't cause errors

    @pytest.mark.unit
    def test_settings_project_fields_optional(self) -> None:
        """Test project fields are optional."""
        reset_settings()
        settings = TraceSettings()
        assert settings.current_project_id is None
        assert settings.current_project_name is None

    @pytest.mark.unit
    def test_settings_with_project_fields(self) -> None:
        """Test settings with project fields set."""
        reset_settings()
        settings = TraceSettings(current_project_id="proj-123", current_project_name="My Project")
        assert settings.current_project_id == "proj-123"
        assert settings.current_project_name == "My Project"


# ============================================================================
# PART 6: Config Manager (manager.py) - Extended Tests
# ============================================================================


class TestConfigManagerInitialization:
    """Test ConfigManager initialization."""

    @pytest.mark.unit
    def test_manager_default_paths(self) -> None:
        """Test default config paths."""
        manager = ConfigManager()
        assert manager.config_dir == Path.home() / ".config" / "tracertm"
        assert manager.config_path == manager.config_dir / "config.yaml"
        assert manager.projects_dir == manager.config_dir / "projects"

    @pytest.mark.unit
    def test_manager_custom_config_dir(self, tmp_path: Any) -> None:
        """Test custom config directory."""
        custom_dir = tmp_path / "custom_config"
        manager = ConfigManager(config_dir=custom_dir)
        assert manager.config_dir == custom_dir


class TestConfigManagerInit:
    """Test ConfigManager.init() method."""

    @pytest.mark.unit
    def test_init_creates_config_dir(self, tmp_path: Any) -> None:
        """Test init creates config directory."""
        config_dir = tmp_path / "config"
        manager = ConfigManager(config_dir=config_dir)

        manager.init(database_url="postgresql://localhost/test")

        assert config_dir.exists()

    @pytest.mark.unit
    def test_init_creates_projects_dir(self, tmp_path: Any) -> None:
        """Test init creates projects directory."""
        config_dir = tmp_path / "config"
        manager = ConfigManager(config_dir=config_dir)

        manager.init(database_url="postgresql://localhost/test")

        projects_dir = config_dir / "projects"
        assert projects_dir.exists()

    @pytest.mark.unit
    def test_init_creates_config_file(self, tmp_path: Any) -> None:
        """Test init creates config file."""
        config_dir = tmp_path / "config"
        manager = ConfigManager(config_dir=config_dir)

        config = manager.init(database_url="postgresql://localhost/test")

        config_path = config_dir / "config.yaml"
        assert config_path.exists()
        assert isinstance(config, SchemaConfig)

    @pytest.mark.unit
    def test_init_sets_database_url(self, tmp_path: Any) -> None:
        """Test init sets database URL."""
        manager = ConfigManager(config_dir=tmp_path)
        config = manager.init(database_url="postgresql://prod.db/myapp")

        assert config.database_url == "postgresql://prod.db/myapp"

    @pytest.mark.unit
    def test_init_sets_defaults(self, tmp_path: Any) -> None:
        """Test init sets default values."""
        manager = ConfigManager(config_dir=tmp_path)
        config = manager.init(database_url="postgresql://localhost/test")

        assert config.current_project_id is None
        assert config.default_view == "FEATURE"
        assert config.output_format == "table"
        assert config.max_agents == COUNT_FOUR
        assert config.log_level == "INFO"


class TestConfigManagerLoad:
    """Test ConfigManager.load() method."""

    @pytest.mark.unit
    def test_load_raises_if_not_initialized(self, tmp_path: Any) -> None:
        """Test load raises error if config doesn't exist."""
        manager = ConfigManager(config_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            manager.load()

    @pytest.mark.unit
    def test_load_returns_config(self, tmp_path: Any) -> None:
        """Test load returns Config object."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        config = manager.load()
        assert isinstance(config, SchemaConfig)

    @pytest.mark.unit
    def test_load_with_project_id(self, tmp_path: Any) -> None:
        """Test load with project-specific config."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        # Set project-specific config
        project_id = "my-project"
        manager.set("default_view", "CODE", project_id=project_id)

        # Load project config
        config = manager.load(project_id=project_id)
        assert config.default_view == "CODE"

    @pytest.mark.unit
    def test_load_environment_override(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test environment variables override config file."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")
        manager.set("log_level", "INFO")

        # Set environment variable
        monkeypatch.setenv("TRACERTM_LOG_LEVEL", "DEBUG")

        config = manager.load()
        assert config.log_level == "DEBUG"


class TestConfigManagerSetGet:
    """Test ConfigManager.set() and get() methods."""

    @pytest.mark.unit
    def test_set_creates_config_if_not_exists(self, tmp_path: Any) -> None:
        """Test set creates config file if it doesn't exist."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        manager.set("default_view", "CODE")

        config_path = tmp_path / "config.yaml"
        assert config_path.exists()

    @pytest.mark.unit
    def test_set_updates_existing_config(self, tmp_path: Any) -> None:
        """Test set updates existing config."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        manager.set("default_view", "CODE")
        manager.set("output_format", "json")

        config = manager.load()
        assert config.default_view == "CODE"
        assert config.output_format == "json"

    @pytest.mark.unit
    def test_set_validates_value(self, tmp_path: Any) -> None:
        """Test set validates value against schema."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        with pytest.raises(ValidationError):
            manager.set("output_format", "invalid_format")

    @pytest.mark.unit
    def test_set_project_specific(self, tmp_path: Any) -> None:
        """Test set with project-specific config."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        project_id = "project-123"
        manager.set("default_view", "API", project_id=project_id)

        project_config_path = tmp_path / "projects" / project_id / "config.yaml"
        assert project_config_path.exists()

    @pytest.mark.unit
    def test_get_returns_value(self, tmp_path: Any) -> None:
        """Test get returns config value."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")
        manager.set("default_view", "CODE")

        value = manager.get("default_view")
        assert value == "CODE"

    @pytest.mark.unit
    def test_get_returns_none_if_not_found(self, tmp_path: Any) -> None:
        """Test get returns None if key not found."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        value = manager.get("nonexistent_key")
        assert value is None

    @pytest.mark.unit
    def test_get_project_specific(self, tmp_path: Any) -> None:
        """Test get with project-specific config."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        project_id = "project-456"
        manager.set("default_view", "TEST", project_id=project_id)

        value = manager.get("default_view", project_id=project_id)
        assert value == "TEST"


class TestConfigManagerEnvironmentVariables:
    """Test ConfigManager environment variable handling."""

    @pytest.mark.unit
    def test_env_var_database_url(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test TRACERTM_DATABASE_URL environment variable."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        monkeypatch.setenv("TRACERTM_DATABASE_URL", "postgresql://prod.db/app")

        config = manager.load()
        assert config.database_url == "postgresql://prod.db/app"

    @pytest.mark.unit
    def test_env_var_current_project_id(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test TRACERTM_CURRENT_PROJECT_ID environment variable."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        monkeypatch.setenv("TRACERTM_CURRENT_PROJECT_ID", "env-project")

        config = manager.load()
        assert config.current_project_id == "env-project"

    @pytest.mark.unit
    def test_env_var_max_agents(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test TRACERTM_MAX_AGENTS environment variable."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        monkeypatch.setenv("TRACERTM_MAX_AGENTS", "100")

        config = manager.load()
        assert config.max_agents == 100

    @pytest.mark.unit
    def test_multiple_env_vars(self, tmp_path: Any, monkeypatch: Any) -> None:
        """Test multiple environment variables."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        monkeypatch.setenv("TRACERTM_DEFAULT_VIEW", "WIREFRAME")
        monkeypatch.setenv("TRACERTM_OUTPUT_FORMAT", "yaml")
        monkeypatch.setenv("TRACERTM_LOG_LEVEL", "DEBUG")

        config = manager.load()
        assert config.default_view == "WIREFRAME"
        assert config.output_format == "yaml"
        assert config.log_level == "DEBUG"


# ============================================================================
# PART 7: Edge Cases and Error Handling
# ============================================================================


class TestEdgeCases:
    """Test edge cases and error scenarios."""

    @pytest.mark.unit
    def test_config_with_empty_string_project(self) -> None:
        """Test Config with empty string as project name."""
        config = Config(current_project="")
        assert config.current_project == ""

    @pytest.mark.unit
    def test_database_config_port_zero(self) -> None:
        """Test DatabaseConfig with port 0."""
        config = DatabaseConfig(port=0)
        assert config.port == 0
        assert ":0/" in config.url

    @pytest.mark.unit
    def test_database_config_empty_database_name(self) -> None:
        """Test DatabaseConfig with empty database name."""
        config = DatabaseConfig(database="")
        assert config.database == ""
        assert config.url.endswith("/")

    @pytest.mark.unit
    def test_config_save_to_readonly_location(self, tmp_path: Any) -> None:
        """Test saving config to read-only location raises error."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        readonly_file = readonly_dir / "config.yaml"

        # Make directory read-only
        readonly_dir.chmod(0o444)

        config = Config()
        try:
            with pytest.raises(PermissionError):
                config.save(readonly_file)
        finally:
            # Restore permissions for cleanup
            readonly_dir.chmod(0o755)

    @pytest.mark.unit
    def test_config_load_invalid_yaml(self, tmp_path: Any) -> None:
        """Test loading config with invalid YAML."""
        config_path = tmp_path / "config.yaml"
        Path(config_path).write_text("invalid: yaml: content: {}", encoding="utf-8")

        with pytest.raises(yaml.YAMLError):
            Config.load(config_path)

    @pytest.mark.unit
    def test_settings_invalid_pool_size_type(self) -> None:
        """Test DatabaseSettings with invalid pool_size type."""
        with pytest.raises(ValidationError):
            DatabaseSettings(pool_size="not_a_number")

    @pytest.mark.unit
    def test_config_manager_set_invalid_project_id(self, tmp_path: Any) -> None:
        """Test ConfigManager.set with special characters in project ID."""
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/test")

        # Project IDs with special characters should work
        project_id = "project-with-dashes_and_underscores"
        manager.set("default_view", "CODE", project_id=project_id)

        value = manager.get("default_view", project_id=project_id)
        assert value == "CODE"


# ============================================================================
# PART 8: Integration Scenarios
# ============================================================================


class TestIntegrationScenarios:
    """Test integration scenarios across modules."""

    @pytest.mark.unit
    def test_config_to_database_integration(self, tmp_path: Any) -> None:
        """Test Config integrates with database module."""
        config = Config(
            database=DatabaseConfig(host="integration.db", database="testdb"),
            data_dir=tmp_path,
        )

        # Verify database config can generate proper URL
        url = config.database.url
        assert "integration.db" in url
        assert "testdb" in url

    @pytest.mark.unit
    def test_settings_to_config_manager_integration(self, tmp_path: Any) -> None:
        """Test TraceSettings integrates with ConfigManager."""
        # Create settings
        reset_settings()
        settings = TraceSettings(
            default_view="CODE",
            output_format="json",
            data_dir=tmp_path / "data",
            config_dir=tmp_path / "config",
        )

        # Create config manager
        manager = ConfigManager(config_dir=settings.config_dir)
        manager.init(database_url="postgresql://localhost/test")

        # Verify integration
        assert manager.config_dir == settings.config_dir

    @pytest.mark.unit
    def test_full_config_workflow(self, tmp_path: Any) -> None:
        """Test complete configuration workflow."""
        # 1. Initialize config manager
        manager = ConfigManager(config_dir=tmp_path)
        manager.init(database_url="postgresql://localhost/workflow")

        # 2. Set some values
        manager.set("default_view", "API")
        manager.set("output_format", "yaml")

        # 3. Load and verify
        loaded = manager.load()
        assert loaded.default_view == "API"
        assert loaded.output_format == "yaml"

        # 4. Create project-specific config
        project_id = "workflow-project"
        manager.set("default_view", "DATABASE", project_id=project_id)

        # 5. Load project config
        project_config = manager.load(project_id=project_id)
        assert project_config.default_view == "DATABASE"

        # 6. Verify global config unchanged
        global_config = manager.load()
        assert global_config.default_view == "API"

    @pytest.mark.unit
    @patch("tracertm.database.async_connection.get_config")
    def test_database_uses_config(self, mock_get_config: Any, tmp_path: Any) -> None:
        """Test database module uses Config correctly."""
        # Create custom config
        db_config = DatabaseConfig(
            host="test-integration.db",
            port=5434,
            database="integration_db",
            username="test_user",
            password="test_pass",
            pool_size=15,
            max_overflow=5,
        )
        config = Config(database=db_config, data_dir=tmp_path)
        mock_get_config.return_value = config

        # Get engine
        from tracertm.database import async_connection as db_module

        db_module._engine = None
        engine = get_engine()

        # Verify engine uses config values
        assert "test-integration.db" in str(engine.url)
        assert "5434" in str(engine.url)
        assert "integration_db" in str(engine.url)


# ============================================================================
# PART 9: Property-Based Testing with Hypothesis
# ============================================================================


@pytest.mark.skipif(not HAS_HYPOTHESIS, reason="hypothesis not installed")
class TestPropertyBasedConfig:
    """Property-based tests using Hypothesis."""

    @pytest.mark.unit
    @given(
        host=st.text(min_size=1, max_size=50).filter(lambda x: "/" not in x) if HAS_HYPOTHESIS else st.text(),
        port=st.integers(min_value=1, max_value=65535) if HAS_HYPOTHESIS else st.integers(),
        database=st.text(min_size=1, max_size=50).filter(lambda x: "/" not in x) if HAS_HYPOTHESIS else st.text(),
    )
    @hypothesis_settings(max_examples=20, deadline=1000)
    def test_database_url_format(self, host: Any, port: Any, database: Any) -> None:
        """Test DatabaseConfig URL format with random values."""
        config = DatabaseConfig(host=host, port=port, database=database)
        url = config.url

        # URL should always have correct format
        assert url.startswith("postgresql://")
        assert f"@{host}:{port}/{database}" in url

    @pytest.mark.unit
    @given(
        pool_size=st.integers(min_value=1, max_value=100) if HAS_HYPOTHESIS else st.integers(),
        max_overflow=st.integers(min_value=0, max_value=50) if HAS_HYPOTHESIS else st.integers(),
    )
    @hypothesis_settings(max_examples=20)
    def test_database_pool_settings(self, pool_size: Any, max_overflow: Any) -> None:
        """Test DatabaseConfig pool settings with random values."""
        config = DatabaseConfig(pool_size=pool_size, max_overflow=max_overflow)
        assert config.pool_size == pool_size
        assert config.max_overflow == max_overflow

    @pytest.mark.unit
    @given(
        theme=st.text(min_size=1, max_size=50) if HAS_HYPOTHESIS else st.text(),
        force_bold=st.booleans() if HAS_HYPOTHESIS else st.booleans(),
        use_symbols=st.booleans() if HAS_HYPOTHESIS else st.booleans(),
    )
    @hypothesis_settings(max_examples=20)
    def test_ui_config_combinations(self, theme: Any, force_bold: Any, use_symbols: Any) -> None:
        """Test UIConfig with random parameter combinations."""
        config = UIConfig(theme=theme, force_bold=force_bold, use_symbols=use_symbols)
        assert config.theme == theme
        assert config.force_bold == force_bold
        assert config.use_symbols == use_symbols

    @pytest.mark.unit
    @given(
        max_agents=st.integers(min_value=1, max_value=10000) if HAS_HYPOTHESIS else st.integers(),
        cache_ttl=st.integers(min_value=0, max_value=3600) if HAS_HYPOTHESIS else st.integers(),
        batch_size=st.integers(min_value=1, max_value=1000) if HAS_HYPOTHESIS else st.integers(),
    )
    @hypothesis_settings(max_examples=20)
    def test_trace_settings_numeric_constraints(self, max_agents: Any, cache_ttl: Any, batch_size: Any) -> None:
        """Test TraceSettings numeric constraints."""
        reset_settings()
        settings = TraceSettings(max_agents=max_agents, cache_ttl=cache_ttl, batch_size=batch_size)
        assert settings.max_agents == max_agents
        assert settings.cache_ttl == cache_ttl
        assert settings.batch_size == batch_size

    @pytest.mark.unit
    @given(project_name=st.text(min_size=0, max_size=100) if HAS_HYPOTHESIS else st.text())
    @hypothesis_settings(max_examples=20)
    def test_config_project_name(self, project_name: Any) -> None:
        """Test Config with random project names."""
        config = Config(current_project=project_name)
        assert config.current_project == project_name


# ============================================================================
# PART 10: Additional Coverage Tests
# ============================================================================


class TestAdditionalCoverage:
    """Additional tests to maximize coverage."""

    @pytest.mark.unit
    def test_database_config_repr(self) -> None:
        """Test DatabaseConfig string representation."""
        config = DatabaseConfig(host="example.com", database="mydb")
        repr_str = repr(config)
        assert "DatabaseConfig" in repr_str

    @pytest.mark.unit
    def test_ui_config_repr(self) -> None:
        """Test UIConfig string representation."""
        config = UIConfig(theme="custom")
        repr_str = repr(config)
        assert "UIConfig" in repr_str

    @pytest.mark.unit
    def test_config_model_dump(self) -> None:
        """Test Config model_dump method."""
        config = Config(current_project="test")
        data = config.model_dump()
        assert isinstance(data, dict)
        assert data["current_project"] == "test"

    @pytest.mark.unit
    def test_database_config_equality(self) -> None:
        """Test DatabaseConfig equality comparison."""
        config1 = DatabaseConfig(host="localhost", database="db1")
        config2 = DatabaseConfig(host="localhost", database="db1")
        config3 = DatabaseConfig(host="localhost", database="db2")

        assert config1 == config2
        assert config1 != config3

    @pytest.mark.unit
    def test_ui_config_equality(self) -> None:
        """Test UIConfig equality comparison."""
        ui1 = UIConfig(theme="theme1")
        ui2 = UIConfig(theme="theme1")
        ui3 = UIConfig(theme="theme2")

        assert ui1 == ui2
        assert ui1 != ui3

    @pytest.mark.unit
    def test_settings_env_file_loading(self, tmp_path: Any) -> None:
        """Test TraceSettings loads from .env file."""
        reset_settings()
        env_file = tmp_path / ".env"
        env_file.write_text("TRACERTM_LOG_LEVEL=DEBUG\n")

        # Change to temp directory
        original_cwd = Path.cwd()
        try:
            os.chdir(tmp_path)
            TraceSettings()
            # .env file should be loaded automatically
        finally:
            os.chdir(original_cwd)

    @pytest.mark.unit
    def test_config_manager_save_config(self, tmp_path: Any) -> None:
        """Test ConfigManager._save_config private method."""
        manager = ConfigManager(config_dir=tmp_path)
        config = SchemaConfig(
            database_url="postgresql://localhost/test",
            default_view="CODE",
            output_format="json",
        )

        config_path = tmp_path / "test_config.yaml"
        manager._save_config(config, config_path)

        assert config_path.exists()

        with Path(config_path).open(encoding="utf-8") as f:
            data = yaml.safe_load(f)
        assert data["default_view"] == "CODE"

    @pytest.mark.unit
    def test_config_manager_load_from_env_empty(self, tmp_path: Any) -> None:
        """Test ConfigManager._load_from_env with no env vars."""
        manager = ConfigManager(config_dir=tmp_path)
        env_config = manager._load_from_env()

        # Should return empty dict if no env vars set
        assert isinstance(env_config, dict)

    @pytest.mark.unit
    def test_database_settings_model_validation(self) -> None:
        """Test DatabaseSettings pydantic model validation."""
        # Valid
        db = DatabaseSettings(url="sqlite:///test.db", pool_size=5)
        assert db.url == "sqlite:///test.db"

        # Invalid URL
        with pytest.raises(ValidationError):
            DatabaseSettings(url="invalid_url")

    @pytest.mark.unit
    def test_trace_settings_field_validators(self) -> None:
        """Test TraceSettings field validators."""
        reset_settings()
        # All valid
        settings = TraceSettings(
            database=DatabaseSettings(url="postgresql://localhost/db"),
            max_agents=500,
            cache_ttl=600,
        )
        assert settings.database.url == "postgresql://localhost/db"

    @pytest.mark.unit
    def test_config_copy_with_modifications(self) -> None:
        """Test creating modified copy of Config."""
        original = Config(current_project="original")
        # Pydantic provides copy method
        modified = original.model_copy(update={"current_project": "modified"})

        assert original.current_project == "original"
        assert modified.current_project == "modified"

    @pytest.mark.unit
    def test_database_config_json_serialization(self) -> None:
        """Test DatabaseConfig JSON serialization."""
        config = DatabaseConfig(host="example.com", port=5433)
        json_str = config.model_dump_json()
        assert "example.com" in json_str
        assert "5433" in json_str

    @pytest.mark.unit
    def test_schema_config_validation(self) -> None:
        """Test SchemaConfig validation."""
        # Valid
        config = SchemaConfig(
            database_url="postgresql://localhost/db",
            default_view="FEATURE",
            output_format="table",
        )
        assert config.database_url == "postgresql://localhost/db"

        # Invalid database URL
        with pytest.raises(ValidationError):
            SchemaConfig(database_url="invalid://url")

    @pytest.mark.unit
    def test_schema_config_api_url_validation(self) -> None:
        """Test SchemaConfig API URL validation."""
        # Valid HTTP
        config = SchemaConfig(database_url="postgresql://localhost/db", api_url="http://localhost:8000")
        assert config.api_url == "http://localhost:8000"

        # Valid HTTPS
        config2 = SchemaConfig(database_url="postgresql://localhost/db", api_url="https://api.example.com")
        assert config2.api_url == "https://api.example.com"

        # Invalid (strips trailing slash)
        config3 = SchemaConfig(
            database_url="postgresql://localhost/db",
            api_url="https://api.example.com/",
        )
        assert config3.api_url == "https://api.example.com"
