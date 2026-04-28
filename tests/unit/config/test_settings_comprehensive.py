"""Comprehensive tests for TraceRTM settings and configuration.

Target: +2% coverage on configuration paths (40 test cases)
"""

from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from tests.test_constants import COUNT_TEN, HTTP_INTERNAL_SERVER_ERROR, HTTP_OK
from tracertm.config.settings import (
    DatabaseSettings,
    TraceSettings,
    get_settings,
    reset_settings,
)


class TestDatabaseSettings:
    """Test suite for DatabaseSettings configuration."""

    @pytest.mark.unit
    def test_database_settings_defaults(self) -> None:
        """Test default database settings."""
        settings = DatabaseSettings()
        assert settings.url == "sqlite:///tracertm.db"
        assert settings.echo is False
        assert settings.pool_size == COUNT_TEN
        assert settings.max_overflow == 20

    @pytest.mark.unit
    def test_database_settings_custom_values(self) -> None:
        """Test custom database settings."""
        settings = DatabaseSettings(
            url="postgresql://localhost/test",
            echo=True,
            pool_size=20,
            max_overflow=30,
        )
        assert settings.url == "postgresql://localhost/test"
        assert settings.echo is True
        assert settings.pool_size == 20
        assert settings.max_overflow == 30

    @pytest.mark.unit
    def test_database_settings_pool_size_constraints(self) -> None:
        """Test pool size validation (1-100)."""
        db = DatabaseSettings(pool_size=1)
        assert db.pool_size == 1

        db = DatabaseSettings(pool_size=100)
        assert db.pool_size == 100

        with pytest.raises(ValidationError):
            DatabaseSettings(pool_size=0)

        with pytest.raises(ValidationError):
            DatabaseSettings(pool_size=101)

    @pytest.mark.unit
    def test_database_settings_max_overflow_constraints(self) -> None:
        """Test max overflow validation (0-200)."""
        db = DatabaseSettings(max_overflow=0)
        assert db.max_overflow == 0

        db = DatabaseSettings(max_overflow=200)
        assert db.max_overflow == HTTP_OK

        with pytest.raises(ValidationError):
            DatabaseSettings(max_overflow=-1)

        with pytest.raises(ValidationError):
            DatabaseSettings(max_overflow=201)

    @pytest.mark.unit
    def test_database_url_validation_postgresql(self) -> None:
        """Test PostgreSQL URL validation."""
        db = DatabaseSettings(url="postgresql://user:pass@localhost:5432/db")
        assert db.url == "postgresql://user:pass@localhost:5432/db"

    @pytest.mark.unit
    def test_database_url_validation_sqlite(self) -> None:
        """Test SQLite URL validation."""
        db = DatabaseSettings(url="sqlite:///path/to/db.sqlite")
        assert db.url == "sqlite:///path/to/db.sqlite"

    @pytest.mark.unit
    def test_database_url_validation_invalid(self) -> None:
        """Test invalid database URL rejection."""
        invalid_urls = [
            "mysql://localhost/db",
            "mongodb://localhost/db",
            "http://localhost:5432/db",
        ]

        for invalid_url in invalid_urls:
            with pytest.raises(ValidationError):
                DatabaseSettings(url=invalid_url)


class TestTraceSettingsDefaults:
    """Test suite for TraceSettings default values."""

    @pytest.mark.unit
    def test_settings_all_defaults(self) -> None:
        """Test default settings values."""
        reset_settings()
        settings = TraceSettings()

        assert settings.current_project_id is None
        assert settings.current_project_name is None
        assert settings.default_view == "FEATURE"
        assert settings.output_format == "table"
        assert settings.max_agents == 1000
        assert settings.cache_ttl == 300
        assert settings.batch_size == 100
        assert settings.log_level == "INFO"
        assert settings.enable_cache is True
        assert settings.enable_async is True
        assert settings.enable_validation is True

    @pytest.mark.unit
    def test_settings_custom_override(self) -> None:
        """Test custom settings initialization."""
        reset_settings()
        settings = TraceSettings(
            current_project_id="proj-123",
            current_project_name="My Project",
            default_view="CODE",
            output_format="json",
            max_agents=500,
            cache_ttl=600,
            batch_size=50,
            log_level="DEBUG",
        )

        assert settings.current_project_id == "proj-123"
        assert settings.current_project_name == "My Project"
        assert settings.default_view == "CODE"
        assert settings.output_format == "json"
        assert settings.max_agents == HTTP_INTERNAL_SERVER_ERROR


class TestTraceSettingsValidation:
    """Test suite for TraceSettings validation."""

    @pytest.mark.unit
    def test_max_agents_constraints(self) -> None:
        """Test max_agents validation (1-10000)."""
        TraceSettings(max_agents=1)
        TraceSettings(max_agents=10000)

        with pytest.raises(ValidationError):
            TraceSettings(max_agents=0)

        with pytest.raises(ValidationError):
            TraceSettings(max_agents=10001)

    @pytest.mark.unit
    def test_cache_ttl_constraints(self) -> None:
        """Test cache_ttl validation (0-3600)."""
        TraceSettings(cache_ttl=0)
        TraceSettings(cache_ttl=3600)

        with pytest.raises(ValidationError):
            TraceSettings(cache_ttl=-1)

        with pytest.raises(ValidationError):
            TraceSettings(cache_ttl=3601)

    @pytest.mark.unit
    def test_batch_size_constraints(self) -> None:
        """Test batch_size validation (1-1000)."""
        TraceSettings(batch_size=1)
        TraceSettings(batch_size=1000)

        with pytest.raises(ValidationError):
            TraceSettings(batch_size=0)

        with pytest.raises(ValidationError):
            TraceSettings(batch_size=1001)

    @pytest.mark.unit
    def test_log_level_values(self) -> None:
        """Test valid log levels."""
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            settings = TraceSettings(log_level=level)
            assert settings.log_level == level

        with pytest.raises(ValidationError):
            TraceSettings(log_level="INVALID")

    @pytest.mark.unit
    def test_output_format_values(self) -> None:
        """Test valid output formats."""
        for fmt in ["table", "json", "yaml", "csv"]:
            settings = TraceSettings(output_format=fmt)
            assert settings.output_format == fmt

        with pytest.raises(ValidationError):
            TraceSettings(output_format="invalid")

    @pytest.mark.unit
    def test_view_type_values(self) -> None:
        """Test valid view types."""
        views = [
            "FEATURE",
            "CODE",
            "WIREFRAME",
            "API",
            "TEST",
            "DATABASE",
            "ROADMAP",
            "PROGRESS",
        ]
        for view in views:
            settings = TraceSettings(default_view=view)
            assert settings.default_view == view

        with pytest.raises(ValidationError):
            TraceSettings(default_view="INVALID_VIEW")


class TestTraceSettingsDirectories:
    """Test suite for directory handling in TraceSettings."""

    @pytest.mark.unit
    def test_directory_creation(self, tmp_path: Any) -> None:
        """Test that settings creates required directories."""
        data_dir = tmp_path / "data"
        config_dir = tmp_path / "config"

        assert not data_dir.exists()
        assert not config_dir.exists()

        reset_settings()
        TraceSettings(data_dir=data_dir, config_dir=config_dir)

        assert data_dir.exists()
        assert config_dir.exists()

    @pytest.mark.unit
    def test_custom_paths(self, tmp_path: Any) -> None:
        """Test custom path configuration."""
        reset_settings()
        custom_data = tmp_path / "custom_data"
        custom_config = tmp_path / "custom_config"

        settings = TraceSettings(data_dir=custom_data, config_dir=custom_config)

        assert settings.data_dir == custom_data
        assert settings.config_dir == custom_config

    @pytest.mark.unit
    def test_nested_path_creation(self, tmp_path: Any) -> None:
        """Test nested path creation."""
        reset_settings()
        nested_path = tmp_path / "a" / "b" / "c"

        assert not nested_path.exists()

        TraceSettings(data_dir=nested_path)

        assert nested_path.exists()


class TestTraceSettingsProperties:
    """Test suite for TraceSettings properties."""

    @pytest.mark.unit
    def test_config_file_path(self, tmp_path: Any) -> None:
        """Test config file path property."""
        reset_settings()
        config_dir = tmp_path / "config"
        settings = TraceSettings(config_dir=config_dir)

        assert settings.config_file == config_dir / "config.yaml"

    @pytest.mark.unit
    def test_env_file_path(self) -> None:
        """Test env file path property."""
        reset_settings()
        settings = TraceSettings()
        assert settings.env_file_path == Path(".env")

    @pytest.mark.unit
    def test_database_settings_access(self) -> None:
        """Test accessing nested database settings."""
        reset_settings()
        db_settings = DatabaseSettings(url="postgresql://localhost/test", pool_size=20)
        settings = TraceSettings(database=db_settings)

        assert settings.database.url == "postgresql://localhost/test"
        assert settings.database.pool_size == 20


class TestSettingsSingleton:
    """Test suite for settings singleton pattern."""

    @pytest.mark.unit
    def test_get_settings_singleton(self) -> None:
        """Test get_settings returns singleton instance."""
        reset_settings()

        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    @pytest.mark.unit
    def test_get_settings_creates_instance(self) -> None:
        """Test get_settings creates instance on first call."""
        reset_settings()

        assert not hasattr(get_settings, "_instance")

        settings = get_settings()

        assert hasattr(get_settings, "_instance")
        assert isinstance(settings, TraceSettings)

    @pytest.mark.unit
    def test_reset_settings_clears_singleton(self) -> None:
        """Test reset_settings clears singleton."""
        reset_settings()

        settings1 = get_settings()
        assert hasattr(get_settings, "_instance")

        reset_settings()
        assert not hasattr(get_settings, "_instance")

        settings2 = get_settings()
        assert settings1 is not settings2


class TestSettingsEnvironmentVariables:
    """Test suite for environment variable handling."""

    @pytest.mark.unit
    def test_env_prefix_tracertm(self, monkeypatch: Any) -> None:
        """Test TRACERTM_ environment variable prefix."""
        reset_settings()
        monkeypatch.setenv("TRACERTM_LOG_LEVEL", "DEBUG")

        settings = TraceSettings()
        assert settings.log_level == "DEBUG"

    @pytest.mark.unit
    def test_env_case_insensitive(self, monkeypatch: Any) -> None:
        """Test environment variables are case insensitive."""
        reset_settings()
        monkeypatch.setenv("tracertm_log_level", "WARNING")

        settings = TraceSettings()
        assert settings.log_level == "WARNING"

    @pytest.mark.unit
    def test_multiple_env_variables(self, monkeypatch: Any) -> None:
        """Test multiple environment variable overrides."""
        reset_settings()
        monkeypatch.setenv("TRACERTM_LOG_LEVEL", "ERROR")
        monkeypatch.setenv("TRACERTM_DEFAULT_VIEW", "CODE")
        monkeypatch.setenv("TRACERTM_OUTPUT_FORMAT", "json")

        settings = TraceSettings()
        assert settings.log_level == "ERROR"
        assert settings.default_view == "CODE"
        assert settings.output_format == "json"

    @pytest.mark.unit
    def test_env_number_conversion(self, monkeypatch: Any) -> None:
        """Test environment variable number conversion."""
        reset_settings()
        monkeypatch.setenv("TRACERTM_MAX_AGENTS", "500")
        monkeypatch.setenv("TRACERTM_CACHE_TTL", "600")
        monkeypatch.setenv("TRACERTM_BATCH_SIZE", "75")

        settings = TraceSettings()
        assert settings.max_agents == HTTP_INTERNAL_SERVER_ERROR
        assert settings.cache_ttl == 600
        assert settings.batch_size == 75

    @pytest.mark.unit
    def test_env_boolean_conversion(self, monkeypatch: Any) -> None:
        """Test environment variable boolean conversion."""
        reset_settings()
        monkeypatch.setenv("TRACERTM_ENABLE_CACHE", "false")
        monkeypatch.setenv("TRACERTM_ENABLE_ASYNC", "0")

        settings = TraceSettings()
        assert settings.enable_cache is False
        assert settings.enable_async is False


class TestSettingsLogging:
    """Test suite for logging configuration settings."""

    @pytest.mark.unit
    def test_custom_log_format(self) -> None:
        """Test custom log format setting."""
        reset_settings()
        custom_format = "%(asctime)s - %(message)s"
        settings = TraceSettings(log_format=custom_format)

        assert settings.log_format == custom_format

    @pytest.mark.unit
    def test_default_log_format(self) -> None:
        """Test default log format."""
        reset_settings()
        settings = TraceSettings()

        expected_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        assert settings.log_format == expected_format

    @pytest.mark.unit
    def test_all_log_levels(self) -> None:
        """Test all valid log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            reset_settings()
            settings = TraceSettings(log_level=level)
            assert settings.log_level == level


class TestSettingsFeatureFlags:
    """Test suite for feature flag settings."""

    @pytest.mark.unit
    def test_enable_cache_flag(self) -> None:
        """Test cache feature flag."""
        reset_settings()
        s1 = TraceSettings(enable_cache=True)
        assert s1.enable_cache is True

        reset_settings()
        s2 = TraceSettings(enable_cache=False)
        assert s2.enable_cache is False

    @pytest.mark.unit
    def test_enable_async_flag(self) -> None:
        """Test async feature flag."""
        reset_settings()
        s1 = TraceSettings(enable_async=True)
        assert s1.enable_async is True

        reset_settings()
        s2 = TraceSettings(enable_async=False)
        assert s2.enable_async is False

    @pytest.mark.unit
    def test_enable_validation_flag(self) -> None:
        """Test validation feature flag."""
        reset_settings()
        s1 = TraceSettings(enable_validation=True)
        assert s1.enable_validation is True

        reset_settings()
        s2 = TraceSettings(enable_validation=False)
        assert s2.enable_validation is False

    @pytest.mark.unit
    def test_all_features_enabled(self) -> None:
        """Test all features enabled simultaneously."""
        reset_settings()
        settings = TraceSettings(enable_cache=True, enable_async=True, enable_validation=True)

        assert settings.enable_cache is True
        assert settings.enable_async is True
        assert settings.enable_validation is True

    @pytest.mark.unit
    def test_all_features_disabled(self) -> None:
        """Test all features disabled simultaneously."""
        reset_settings()
        settings = TraceSettings(enable_cache=False, enable_async=False, enable_validation=False)

        assert settings.enable_cache is False
        assert settings.enable_async is False
        assert settings.enable_validation is False
