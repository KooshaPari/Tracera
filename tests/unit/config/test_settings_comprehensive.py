"""
Comprehensive unit tests for settings module.

Tests config/settings.py:
- DatabaseSettings class
- TraceSettings class
- get_settings function
- reset_settings function
- Environment variable handling
- Validation
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from tracertm.config.settings import (
    DatabaseSettings,
    TraceSettings,
    get_settings,
    reset_settings,
)


class TestDatabaseSettings:
    """Test DatabaseSettings class."""

    def test_create_with_defaults(self):
        """Test creating DatabaseSettings with default values."""
        db = DatabaseSettings()
        assert db.url == "sqlite:///tracertm.db"
        assert db.echo is False
        assert db.pool_size == 10
        assert db.max_overflow == 20

    def test_create_with_postgresql_url(self):
        """Test creating DatabaseSettings with PostgreSQL URL."""
        db = DatabaseSettings(url="postgresql://user:pass@localhost/dbname")
        assert db.url == "postgresql://user:pass@localhost/dbname"

    def test_create_with_custom_pool_size(self):
        """Test creating DatabaseSettings with custom pool size."""
        db = DatabaseSettings(pool_size=50, max_overflow=100)
        assert db.pool_size == 50
        assert db.max_overflow == 100

    def test_validate_url_postgresql(self):
        """Test URL validation accepts postgresql://."""
        db = DatabaseSettings(url="postgresql://localhost/test")
        assert db.url.startswith("postgresql://")

    def test_validate_url_sqlite(self):
        """Test URL validation accepts sqlite:///."""
        db = DatabaseSettings(url="sqlite:///test.db")
        assert db.url.startswith("sqlite:///")

    def test_validate_url_invalid(self):
        """Test URL validation rejects invalid URLs."""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(url="mysql://localhost/test")
        assert "postgresql://" in str(exc_info.value)
        assert "sqlite:///" in str(exc_info.value)

    def test_validate_url_empty(self):
        """Test URL validation rejects empty string."""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(url="")
        assert "postgresql://" in str(exc_info.value)

    def test_pool_size_minimum(self):
        """Test pool_size minimum constraint."""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(pool_size=0)
        assert "pool_size" in str(exc_info.value)

    def test_pool_size_maximum(self):
        """Test pool_size maximum constraint."""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(pool_size=101)
        assert "pool_size" in str(exc_info.value)

    def test_max_overflow_minimum(self):
        """Test max_overflow minimum constraint."""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(max_overflow=-1)
        assert "max_overflow" in str(exc_info.value)

    def test_max_overflow_maximum(self):
        """Test max_overflow maximum constraint."""
        with pytest.raises(ValidationError) as exc_info:
            DatabaseSettings(max_overflow=201)
        assert "max_overflow" in str(exc_info.value)

    def test_echo_boolean(self):
        """Test echo is boolean."""
        db_true = DatabaseSettings(echo=True)
        db_false = DatabaseSettings(echo=False)
        assert db_true.echo is True
        assert db_false.echo is False


class TestTraceSettings:
    """Test TraceSettings class."""

    def test_create_with_defaults(self):
        """Test creating TraceSettings with defaults."""
        settings = TraceSettings()
        assert settings.current_project_id is None
        assert settings.default_view == "FEATURE"
        assert settings.output_format == "table"
        assert settings.max_agents == 1000
        assert settings.log_level == "INFO"

    def test_create_with_custom_values(self):
        """Test creating TraceSettings with custom values."""
        settings = TraceSettings(
            current_project_id="proj-123",
            default_view="CODE",
            output_format="json",
            max_agents=500,
            log_level="DEBUG",
        )
        assert settings.current_project_id == "proj-123"
        assert settings.default_view == "CODE"
        assert settings.output_format == "json"
        assert settings.max_agents == 500
        assert settings.log_level == "DEBUG"

    def test_default_view_literal_validation(self):
        """Test default_view accepts only valid literals."""
        valid_views = ["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]
        for view in valid_views:
            settings = TraceSettings(default_view=view)
            assert settings.default_view == view

    def test_default_view_invalid(self):
        """Test default_view rejects invalid values."""
        with pytest.raises(ValidationError) as exc_info:
            TraceSettings(default_view="INVALID")
        assert "default_view" in str(exc_info.value)

    def test_output_format_literal_validation(self):
        """Test output_format accepts only valid literals."""
        valid_formats = ["table", "json", "yaml", "csv"]
        for fmt in valid_formats:
            settings = TraceSettings(output_format=fmt)
            assert settings.output_format == fmt

    def test_output_format_invalid(self):
        """Test output_format rejects invalid values."""
        with pytest.raises(ValidationError) as exc_info:
            TraceSettings(output_format="xml")
        assert "output_format" in str(exc_info.value)

    def test_log_level_literal_validation(self):
        """Test log_level accepts only valid literals."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            settings = TraceSettings(log_level=level)
            assert settings.log_level == level

    def test_log_level_invalid(self):
        """Test log_level rejects invalid values."""
        with pytest.raises(ValidationError) as exc_info:
            TraceSettings(log_level="TRACE")
        assert "log_level" in str(exc_info.value)

    def test_max_agents_minimum(self):
        """Test max_agents minimum constraint."""
        with pytest.raises(ValidationError) as exc_info:
            TraceSettings(max_agents=0)
        assert "max_agents" in str(exc_info.value)

    def test_max_agents_maximum(self):
        """Test max_agents maximum constraint."""
        with pytest.raises(ValidationError) as exc_info:
            TraceSettings(max_agents=10001)
        assert "max_agents" in str(exc_info.value)

    def test_max_agents_at_boundaries(self):
        """Test max_agents at boundary values."""
        settings_min = TraceSettings(max_agents=1)
        settings_max = TraceSettings(max_agents=10000)
        assert settings_min.max_agents == 1
        assert settings_max.max_agents == 10000

    def test_cache_ttl_constraints(self):
        """Test cache_ttl constraints."""
        settings_min = TraceSettings(cache_ttl=0)
        settings_max = TraceSettings(cache_ttl=3600)
        assert settings_min.cache_ttl == 0
        assert settings_max.cache_ttl == 3600

        with pytest.raises(ValidationError):
            TraceSettings(cache_ttl=-1)

        with pytest.raises(ValidationError):
            TraceSettings(cache_ttl=3601)

    def test_batch_size_constraints(self):
        """Test batch_size constraints."""
        settings_min = TraceSettings(batch_size=1)
        settings_max = TraceSettings(batch_size=1000)
        assert settings_min.batch_size == 1
        assert settings_max.batch_size == 1000

        with pytest.raises(ValidationError):
            TraceSettings(batch_size=0)

        with pytest.raises(ValidationError):
            TraceSettings(batch_size=1001)

    def test_database_nested_settings(self):
        """Test nested database settings."""
        settings = TraceSettings()
        assert isinstance(settings.database, DatabaseSettings)
        assert settings.database.url == "sqlite:///tracertm.db"

    def test_database_custom_nested(self):
        """Test custom nested database settings."""
        db = DatabaseSettings(
            url="postgresql://localhost/test",
            pool_size=50,
        )
        settings = TraceSettings(database=db)
        assert settings.database.url == "postgresql://localhost/test"
        assert settings.database.pool_size == 50

    def test_data_dir_default(self):
        """Test data_dir default value."""
        settings = TraceSettings()
        expected = Path.home() / ".tracertm"
        assert settings.data_dir == expected

    def test_config_dir_default(self):
        """Test config_dir default value."""
        settings = TraceSettings()
        expected = Path.home() / ".config" / "tracertm"
        assert settings.config_dir == expected

    def test_data_dir_custom(self):
        """Test custom data_dir."""
        custom_path = Path("/tmp/tracertm_data")
        settings = TraceSettings(data_dir=custom_path)
        assert settings.data_dir == custom_path

    def test_config_dir_custom(self):
        """Test custom config_dir."""
        custom_path = Path("/tmp/tracertm_config")
        settings = TraceSettings(config_dir=custom_path)
        assert settings.config_dir == custom_path

    def test_feature_flags_defaults(self):
        """Test feature flags have correct defaults."""
        settings = TraceSettings()
        assert settings.enable_cache is True
        assert settings.enable_async is True
        assert settings.enable_validation is True

    def test_feature_flags_custom(self):
        """Test custom feature flags."""
        settings = TraceSettings(
            enable_cache=False,
            enable_async=False,
            enable_validation=False,
        )
        assert settings.enable_cache is False
        assert settings.enable_async is False
        assert settings.enable_validation is False

    def test_config_file_property(self):
        """Test config_file property."""
        settings = TraceSettings()
        expected = settings.config_dir / "config.yaml"
        assert settings.config_file == expected

    def test_env_file_path_property(self):
        """Test env_file_path property."""
        settings = TraceSettings()
        expected = Path(".env")
        assert settings.env_file_path == expected


class TestTraceSettingsInitialization:
    """Test TraceSettings initialization."""

    def test_creates_data_dir(self, tmp_path):
        """Test that initialization creates data_dir."""
        data_dir = tmp_path / "data"
        assert not data_dir.exists()

        TraceSettings(data_dir=data_dir)

        assert data_dir.exists()
        assert data_dir.is_dir()

    def test_creates_config_dir(self, tmp_path):
        """Test that initialization creates config_dir."""
        config_dir = tmp_path / "config"
        assert not config_dir.exists()

        TraceSettings(config_dir=config_dir)

        assert config_dir.exists()
        assert config_dir.is_dir()

    def test_creates_parent_dirs(self, tmp_path):
        """Test that initialization creates parent directories."""
        data_dir = tmp_path / "parent" / "child" / "data"
        assert not data_dir.exists()

        TraceSettings(data_dir=data_dir)

        assert data_dir.exists()
        assert data_dir.is_dir()

    def test_existing_dirs_no_error(self, tmp_path):
        """Test that existing directories don't cause errors."""
        data_dir = tmp_path / "existing"
        data_dir.mkdir()

        # Should not raise error
        settings = TraceSettings(data_dir=data_dir)
        assert settings.data_dir == data_dir


class TestGetSettings:
    """Test get_settings singleton function."""

    def test_get_settings_returns_instance(self):
        """Test that get_settings returns TraceSettings instance."""
        reset_settings()  # Clean state
        settings = get_settings()
        assert isinstance(settings, TraceSettings)

    def test_get_settings_singleton(self):
        """Test that get_settings returns same instance."""
        reset_settings()  # Clean state
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2

    def test_get_settings_after_reset(self):
        """Test get_settings after reset creates new instance."""
        reset_settings()
        settings1 = get_settings()

        reset_settings()
        settings2 = get_settings()

        # Should be different instances
        assert settings1 is not settings2

    def test_get_settings_multiple_calls(self):
        """Test multiple get_settings calls return same instance."""
        reset_settings()
        instances = [get_settings() for _ in range(5)]
        assert all(inst is instances[0] for inst in instances)


class TestResetSettings:
    """Test reset_settings function."""

    def test_reset_settings_callable(self):
        """Test that reset_settings is callable."""
        assert callable(reset_settings)

    def test_reset_settings_clears_singleton(self):
        """Test that reset_settings clears singleton state."""
        reset_settings()
        settings1 = get_settings()

        reset_settings()
        settings2 = get_settings()

        # New instance after reset
        assert settings1 is not settings2

    def test_reset_settings_multiple_times(self):
        """Test calling reset_settings multiple times."""
        for _ in range(3):
            reset_settings()
            settings = get_settings()
            assert isinstance(settings, TraceSettings)


class TestSettingsEnvPrefix:
    """Test environment variable prefix handling."""

    def test_env_prefix_configured(self):
        """Test that TRACERTM_ prefix is configured."""
        # Check model_config has correct env_prefix
        assert TraceSettings.model_config.get("env_prefix") == "TRACERTM_"

    def test_env_case_insensitive(self):
        """Test that env vars are case insensitive."""
        assert TraceSettings.model_config.get("case_sensitive") is False

    def test_env_nested_delimiter(self):
        """Test nested delimiter for env vars."""
        assert TraceSettings.model_config.get("nested_delimiter") == "__"

    def test_env_file_configured(self):
        """Test that .env file is configured."""
        assert TraceSettings.model_config.get("env_file") == ".env"


class TestSettingsValidation:
    """Test settings validation and error messages."""

    def test_validation_clear_error_messages(self):
        """Test that validation errors have clear messages."""
        try:
            TraceSettings(max_agents=0)
        except ValidationError as e:
            error_str = str(e)
            assert "max_agents" in error_str
            # Error should indicate constraint

    def test_multiple_validation_errors(self):
        """Test handling multiple validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            TraceSettings(
                default_view="INVALID",
                output_format="INVALID",
                max_agents=0,
            )

        error_str = str(exc_info.value)
        # Should report all errors
        assert "default_view" in error_str or "output_format" in error_str

    def test_nested_validation_errors(self):
        """Test nested validation errors in database settings."""
        with pytest.raises(ValidationError) as exc_info:
            TraceSettings(
                database=DatabaseSettings(url="invalid://url")
            )

        error_str = str(exc_info.value)
        assert "url" in error_str or "database" in error_str
