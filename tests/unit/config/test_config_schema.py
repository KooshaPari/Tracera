"""Comprehensive tests for config schema validation.

Target: +1% coverage on schema validation paths
"""

import pytest
from pydantic import ValidationError

from tests.test_constants import COUNT_TEN, COUNT_THREE, HTTP_INTERNAL_SERVER_ERROR
from tracertm.config.schema import Config


class TestConfigSchemaDefaults:
    """Test suite for Config schema defaults."""

    @pytest.mark.unit
    def test_config_defaults(self) -> None:
        """Test Config default values."""
        config = Config()

        assert config.database_url is None
        assert config.current_project_id is None
        assert config.current_project_name is None
        assert config.default_view == "FEATURE"
        assert config.output_format == "table"
        assert config.max_agents == 1000
        assert config.log_level == "INFO"
        assert config.aliases == {}
        assert config.api_url == "https://api.tracertm.io"
        assert config.api_token is None
        assert config.api_timeout == 30.0
        assert config.api_max_retries == COUNT_THREE
        assert config.sync_enabled is True
        assert config.sync_interval_seconds == 300
        assert config.sync_conflict_strategy == "last_write_wins"

    @pytest.mark.unit
    def test_config_with_values(self) -> None:
        """Test Config initialization with values."""
        config = Config(
            database_url="postgresql://localhost/test",
            current_project_id="proj-123",
            current_project_name="Test Project",
            default_view="CODE",
            output_format="json",
            max_agents=500,
        )

        assert config.database_url == "postgresql://localhost/test"
        assert config.current_project_id == "proj-123"
        assert config.current_project_name == "Test Project"
        assert config.default_view == "CODE"
        assert config.output_format == "json"
        assert config.max_agents == HTTP_INTERNAL_SERVER_ERROR


class TestConfigDatabaseUrlValidation:
    """Test suite for database URL validation."""

    @pytest.mark.unit
    def test_database_url_none(self) -> None:
        """Test database_url can be None."""
        config = Config(database_url=None)
        assert config.database_url is None

    @pytest.mark.unit
    def test_database_url_postgresql(self) -> None:
        """Test valid PostgreSQL URL."""
        config = Config(database_url="postgresql://user:pass@localhost/db")
        assert config.database_url == "postgresql://user:pass@localhost/db"

    @pytest.mark.unit
    def test_database_url_sqlite(self) -> None:
        """Test valid SQLite URL."""
        config = Config(database_url="sqlite:///test.db")
        assert config.database_url == "sqlite:///test.db"

    @pytest.mark.unit
    def test_database_url_invalid_mysql(self) -> None:
        """Test invalid MySQL URL."""
        with pytest.raises(ValidationError):
            Config(database_url="mysql://localhost/db")

    @pytest.mark.unit
    def test_database_url_invalid_mongodb(self) -> None:
        """Test invalid MongoDB URL."""
        with pytest.raises(ValidationError):
            Config(database_url="mongodb://localhost/db")

    @pytest.mark.unit
    def test_database_url_invalid_http(self) -> None:
        """Test invalid HTTP URL."""
        with pytest.raises(ValidationError):
            Config(database_url="http://localhost:5432/db")


class TestConfigViewTypeValidation:
    """Test suite for view type validation."""

    @pytest.mark.unit
    def test_all_valid_view_types(self) -> None:
        """Test all valid view types."""
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
            config = Config(default_view=view)
            assert config.default_view == view

    @pytest.mark.unit
    def test_invalid_view_type(self) -> None:
        """Test invalid view type."""
        with pytest.raises(ValidationError):
            Config(default_view="INVALID")


class TestConfigOutputFormatValidation:
    """Test suite for output format validation."""

    @pytest.mark.unit
    def test_all_valid_formats(self) -> None:
        """Test all valid output formats."""
        formats = ["table", "json", "yaml", "csv"]
        for fmt in formats:
            config = Config(output_format=fmt)
            assert config.output_format == fmt

    @pytest.mark.unit
    def test_invalid_format(self) -> None:
        """Test invalid output format."""
        with pytest.raises(ValidationError):
            Config(output_format="xml")


class TestConfigLogLevelValidation:
    """Test suite for log level validation."""

    @pytest.mark.unit
    def test_all_valid_log_levels(self) -> None:
        """Test all valid log levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
        for level in levels:
            config = Config(log_level=level)
            assert config.log_level == level

    @pytest.mark.unit
    def test_invalid_log_level(self) -> None:
        """Test invalid log level."""
        with pytest.raises(ValidationError):
            Config(log_level="TRACE")


class TestConfigMaxAgentsValidation:
    """Test suite for max_agents validation."""

    @pytest.mark.unit
    def test_max_agents_valid(self) -> None:
        """Test valid max_agents values."""
        config = Config(max_agents=1)
        assert config.max_agents == 1

        config = Config(max_agents=10000)
        assert config.max_agents == 10000

        config = Config(max_agents=5000)
        assert config.max_agents == 5000

    @pytest.mark.unit
    def test_max_agents_invalid_below_min(self) -> None:
        """Test max_agents below minimum."""
        with pytest.raises(ValidationError):
            Config(max_agents=0)

    @pytest.mark.unit
    def test_max_agents_invalid_above_max(self) -> None:
        """Test max_agents above maximum."""
        with pytest.raises(ValidationError):
            Config(max_agents=10001)


class TestConfigApiValidation:
    """Test suite for API configuration validation."""

    @pytest.mark.unit
    def test_api_url_https(self) -> None:
        """Test HTTPS API URL."""
        config = Config(api_url="https://api.example.com")
        assert config.api_url == "https://api.example.com"

    @pytest.mark.unit
    def test_api_url_http(self) -> None:
        """Test HTTP API URL."""
        config = Config(api_url="http://localhost:8000")
        assert config.api_url == "http://localhost:8000"

    @pytest.mark.unit
    def test_api_url_trailing_slash_removed(self) -> None:
        """Test trailing slash removed from API URL."""
        config = Config(api_url="https://api.example.com/")
        assert config.api_url == "https://api.example.com"

    @pytest.mark.unit
    def test_api_url_invalid(self) -> None:
        """Test invalid API URL."""
        with pytest.raises(ValidationError):
            Config(api_url="ftp://example.com")

    @pytest.mark.unit
    def test_api_url_no_protocol(self) -> None:
        """Test API URL without protocol."""
        with pytest.raises(ValidationError):
            Config(api_url="example.com")


class TestConfigApiTimeoutValidation:
    """Test suite for API timeout validation."""

    @pytest.mark.unit
    def test_api_timeout_valid(self) -> None:
        """Test valid API timeout values."""
        config = Config(api_timeout=1.0)
        assert config.api_timeout == 1.0

        config = Config(api_timeout=300.0)
        assert config.api_timeout == 300.0

    @pytest.mark.unit
    def test_api_timeout_invalid_below_min(self) -> None:
        """Test API timeout below minimum."""
        with pytest.raises(ValidationError):
            Config(api_timeout=0.5)

    @pytest.mark.unit
    def test_api_timeout_invalid_above_max(self) -> None:
        """Test API timeout above maximum."""
        with pytest.raises(ValidationError):
            Config(api_timeout=300.1)


class TestConfigApiRetriesValidation:
    """Test suite for API retries validation."""

    @pytest.mark.unit
    def test_api_max_retries_valid(self) -> None:
        """Test valid max retries values."""
        config = Config(api_max_retries=1)
        assert config.api_max_retries == 1

        config = Config(api_max_retries=10)
        assert config.api_max_retries == COUNT_TEN

    @pytest.mark.unit
    def test_api_max_retries_invalid_below_min(self) -> None:
        """Test max retries below minimum."""
        with pytest.raises(ValidationError):
            Config(api_max_retries=0)

    @pytest.mark.unit
    def test_api_max_retries_invalid_above_max(self) -> None:
        """Test max retries above maximum."""
        with pytest.raises(ValidationError):
            Config(api_max_retries=11)


class TestConfigSyncIntervalValidation:
    """Test suite for sync interval validation."""

    @pytest.mark.unit
    def test_sync_interval_valid(self) -> None:
        """Test valid sync interval values."""
        config = Config(sync_interval_seconds=10)
        assert config.sync_interval_seconds == COUNT_TEN

        config = Config(sync_interval_seconds=60)
        assert config.sync_interval_seconds == 60

    @pytest.mark.unit
    def test_sync_interval_invalid_below_min(self) -> None:
        """Test sync interval below minimum."""
        with pytest.raises(ValidationError):
            Config(sync_interval_seconds=9)


class TestConfigSyncConflictStrategy:
    """Test suite for sync conflict strategy validation."""

    @pytest.mark.unit
    def test_sync_conflict_strategies(self) -> None:
        """Test all valid sync conflict strategies."""
        strategies = [
            "last_write_wins",
            "local_wins",
            "remote_wins",
            "manual",
        ]
        for strategy in strategies:
            config = Config(sync_conflict_strategy=strategy)
            assert config.sync_conflict_strategy == strategy

    @pytest.mark.unit
    def test_invalid_sync_conflict_strategy(self) -> None:
        """Test invalid sync conflict strategy."""
        with pytest.raises(ValidationError):
            Config(sync_conflict_strategy="invalid_strategy")


class TestConfigAliases:
    """Test suite for aliases configuration."""

    @pytest.mark.unit
    def test_aliases_default_empty(self) -> None:
        """Test default aliases is empty."""
        config = Config()
        assert config.aliases == {}

    @pytest.mark.unit
    def test_aliases_custom(self) -> None:
        """Test custom aliases."""
        aliases = {"ll": "list", "cr": "create"}
        config = Config(aliases=aliases)
        assert config.aliases == aliases

    @pytest.mark.unit
    def test_aliases_single(self) -> None:
        """Test single alias."""
        config = Config(aliases={"ls": "list"})
        assert config.aliases == {"ls": "list"}


class TestConfigProjectSettings:
    """Test suite for project-specific settings."""

    @pytest.mark.unit
    def test_current_project_id(self) -> None:
        """Test current_project_id."""
        config = Config(current_project_id="my-project")
        assert config.current_project_id == "my-project"

    @pytest.mark.unit
    def test_current_project_name(self) -> None:
        """Test current_project_name."""
        config = Config(current_project_name="My Project")
        assert config.current_project_name == "My Project"

    @pytest.mark.unit
    def test_both_project_settings(self) -> None:
        """Test both project settings together."""
        config = Config(current_project_id="proj-123", current_project_name="Test Project")
        assert config.current_project_id == "proj-123"
        assert config.current_project_name == "Test Project"


class TestConfigIntegration:
    """Integration tests for config schema."""

    @pytest.mark.unit
    def test_full_config(self) -> None:
        """Test full config with all settings."""
        config = Config(
            database_url="postgresql://localhost/tracertm",
            current_project_id="proj-1",
            current_project_name="Project 1",
            default_view="CODE",
            output_format="json",
            max_agents=2000,
            log_level="DEBUG",
            api_url="https://api.tracertm.io",
            api_timeout=60.0,
            api_max_retries=5,
            sync_enabled=True,
            sync_interval_seconds=300,
            sync_conflict_strategy="local_wins",
            aliases={"ll": "list"},
        )

        assert config.database_url == "postgresql://localhost/tracertm"
        assert config.current_project_id == "proj-1"
        assert config.default_view == "CODE"
        assert config.output_format == "json"
        assert config.max_agents == 2000
        assert config.log_level == "DEBUG"

    @pytest.mark.unit
    def test_config_minimal(self) -> None:
        """Test minimal config."""
        config = Config()
        # All fields have defaults
        assert config is not None

    @pytest.mark.unit
    def test_config_forbid_extra_fields(self) -> None:
        """Test config forbids extra fields."""
        with pytest.raises(ValidationError):
            Config(unknown_field="value")
