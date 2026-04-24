"""Comprehensive tests for schema validation and Pydantic models.

This module provides 50+ tests for:
- Pydantic model validation (all fields)
- Type coercion and transformation
- Error messages for validation failures
- Edge cases (None, empty, very large values)
- Custom validators and constraints
- Property-based testing with Hypothesis
"""

from typing import Any

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from tests.test_constants import COUNT_TEN, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR
from tracertm.config.schema import Config


class TestConfigTypeCoercion:
    """Test suite for type coercion in Config model."""

    @pytest.mark.unit
    def test_max_agents_string_to_int_coercion(self) -> None:
        """Test that max_agents coerces string to int."""
        config = Config(max_agents="500")
        assert config.max_agents == HTTP_INTERNAL_SERVER_ERROR
        assert isinstance(config.max_agents, int)

    @pytest.mark.unit
    def test_api_timeout_int_to_float_coercion(self) -> None:
        """Test that api_timeout coerces int to float."""
        config = Config(api_timeout=30)
        assert config.api_timeout == 30.0
        assert isinstance(config.api_timeout, float)

    @pytest.mark.unit
    def test_sync_enabled_string_to_bool_coercion(self) -> None:
        """Test that sync_enabled coerces string to bool."""
        config = Config(sync_enabled="True")
        assert config.sync_enabled is True
        assert isinstance(config.sync_enabled, bool)

    @pytest.mark.unit
    def test_sync_enabled_int_to_bool_coercion(self) -> None:
        """Test that sync_enabled coerces int to bool."""
        config = Config(sync_enabled=1)
        assert config.sync_enabled is True
        config = Config(sync_enabled=0)
        assert config.sync_enabled is False

    @pytest.mark.unit
    def test_sync_interval_string_to_int_coercion(self) -> None:
        """Test that sync_interval_seconds coerces string to int."""
        config = Config(sync_interval_seconds="300")
        assert config.sync_interval_seconds == 300
        assert isinstance(config.sync_interval_seconds, int)


class TestConfigValidationErrors:
    """Test suite for validation error messages."""

    @pytest.mark.unit
    def test_invalid_view_type_error_message(self) -> None:
        """Test error message for invalid view type."""
        with pytest.raises(ValidationError) as exc_info:
            Config(default_view="INVALID_VIEW")

        error = exc_info.value
        assert "default_view" in str(error)
        assert "INVALID_VIEW" in str(error)

    @pytest.mark.unit
    def test_invalid_output_format_error_message(self) -> None:
        """Test error message for invalid output format."""
        with pytest.raises(ValidationError) as exc_info:
            Config(output_format="xml")

        error = exc_info.value
        assert "output_format" in str(error)

    @pytest.mark.unit
    def test_invalid_log_level_error_message(self) -> None:
        """Test error message for invalid log level."""
        with pytest.raises(ValidationError) as exc_info:
            Config(log_level="TRACE")

        error = exc_info.value
        assert "log_level" in str(error)

    @pytest.mark.unit
    def test_max_agents_below_min_error_message(self) -> None:
        """Test error message for max_agents below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            Config(max_agents=0)

        error = exc_info.value
        assert "max_agents" in str(error)
        assert "greater than or equal to 1" in str(error).lower()

    @pytest.mark.unit
    def test_max_agents_above_max_error_message(self) -> None:
        """Test error message for max_agents above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            Config(max_agents=10001)

        error = exc_info.value
        assert "max_agents" in str(error)
        assert "less than or equal to 10000" in str(error).lower()

    @pytest.mark.unit
    def test_api_timeout_below_min_error_message(self) -> None:
        """Test error message for api_timeout below minimum."""
        with pytest.raises(ValidationError) as exc_info:
            Config(api_timeout=0.5)

        error = exc_info.value
        assert "api_timeout" in str(error)
        assert "greater than or equal to 1" in str(error).lower()

    @pytest.mark.unit
    def test_api_timeout_above_max_error_message(self) -> None:
        """Test error message for api_timeout above maximum."""
        with pytest.raises(ValidationError) as exc_info:
            Config(api_timeout=301.0)

        error = exc_info.value
        assert "api_timeout" in str(error)
        assert "less than or equal to 300" in str(error).lower()

    @pytest.mark.unit
    def test_invalid_database_url_error_message(self) -> None:
        """Test error message for invalid database URL."""
        with pytest.raises(ValidationError) as exc_info:
            Config(database_url="mysql://localhost/db")

        error = exc_info.value
        assert "database_url" in str(error)
        assert "postgresql://" in str(error) or "sqlite:///" in str(error)

    @pytest.mark.unit
    def test_invalid_api_url_error_message(self) -> None:
        """Test error message for invalid API URL."""
        with pytest.raises(ValidationError) as exc_info:
            Config(api_url="ftp://example.com")

        error = exc_info.value
        assert "api_url" in str(error)
        assert "http://" in str(error) or "https://" in str(error)

    @pytest.mark.unit
    def test_extra_field_error_message(self) -> None:
        """Test error message for extra fields."""
        with pytest.raises(ValidationError) as exc_info:
            Config(unknown_field="value")

        error = exc_info.value
        assert "unknown_field" in str(error) or "extra" in str(error).lower()


class TestConfigEdgeCases:
    """Test suite for edge cases in Config model."""

    @pytest.mark.unit
    def test_none_optional_fields(self) -> None:
        """Test None values for optional fields."""
        config = Config(
            database_url=None,
            current_project_id=None,
            current_project_name=None,
            api_token=None,
        )
        assert config.database_url is None
        assert config.current_project_id is None
        assert config.current_project_name is None
        assert config.api_token is None

    @pytest.mark.unit
    def test_empty_string_fields(self) -> None:
        """Test empty string values."""
        config = Config(
            current_project_id="",
            current_project_name="",
            api_token="",
        )
        assert config.current_project_id == ""
        assert config.current_project_name == ""
        assert config.api_token == ""

    @pytest.mark.unit
    def test_whitespace_string_fields(self) -> None:
        """Test whitespace-only string values."""
        config = Config(
            current_project_id="   ",
            current_project_name="\t\n",
        )
        assert config.current_project_id == "   "
        assert config.current_project_name == "\t\n"

    @pytest.mark.unit
    def test_very_long_strings(self) -> None:
        """Test very long string values."""
        long_string = "a" * 10000
        config = Config(
            current_project_id=long_string,
            current_project_name=long_string,
            api_token=long_string,
        )
        assert len(config.current_project_id) == 10000
        assert len(config.current_project_name) == 10000
        assert len(config.api_token) == 10000

    @pytest.mark.unit
    def test_unicode_strings(self) -> None:
        """Test unicode string values."""
        config = Config(
            current_project_id="测试项目-🚀",
            current_project_name="Прøject Ñamé 🎯",
        )
        assert config.current_project_id == "测试项目-🚀"
        assert config.current_project_name == "Прøject Ñamé 🎯"

    @pytest.mark.unit
    def test_special_characters_in_strings(self) -> None:
        """Test special characters in string values."""
        config = Config(
            current_project_id="proj-123_456.789",
            current_project_name="Project: Test (v1.0) [Beta]",
        )
        assert config.current_project_id == "proj-123_456.789"
        assert config.current_project_name == "Project: Test (v1.0) [Beta]"

    @pytest.mark.unit
    def test_max_agents_boundary_values(self) -> None:
        """Test max_agents at boundary values."""
        # Minimum
        config = Config(max_agents=1)
        assert config.max_agents == 1

        # Maximum
        config = Config(max_agents=10000)
        assert config.max_agents == 10000

    @pytest.mark.unit
    def test_api_timeout_boundary_values(self) -> None:
        """Test api_timeout at boundary values."""
        # Minimum
        config = Config(api_timeout=1.0)
        assert config.api_timeout == 1.0

        # Maximum
        config = Config(api_timeout=300.0)
        assert config.api_timeout == 300.0

    @pytest.mark.unit
    def test_api_max_retries_boundary_values(self) -> None:
        """Test api_max_retries at boundary values."""
        # Minimum
        config = Config(api_max_retries=1)
        assert config.api_max_retries == 1

        # Maximum
        config = Config(api_max_retries=10)
        assert config.api_max_retries == COUNT_TEN

    @pytest.mark.unit
    def test_sync_interval_boundary_values(self) -> None:
        """Test sync_interval_seconds at boundary values."""
        # Minimum
        config = Config(sync_interval_seconds=10)
        assert config.sync_interval_seconds == COUNT_TEN

        # Very large value
        config = Config(sync_interval_seconds=86400)  # 24 hours
        assert config.sync_interval_seconds == 86400

    @pytest.mark.unit
    def test_empty_aliases_dict(self) -> None:
        """Test empty aliases dictionary."""
        config = Config(aliases={})
        assert config.aliases == {}

    @pytest.mark.unit
    def test_large_aliases_dict(self) -> None:
        """Test large aliases dictionary."""
        aliases = {f"alias{i}": f"command{i}" for i in range(1000)}
        config = Config(aliases=aliases)
        assert len(config.aliases) == 1000
        assert config.aliases["alias500"] == "command500"


class TestConfigCustomValidators:
    """Test suite for custom validators."""

    @pytest.mark.unit
    def test_database_url_validator_postgresql(self) -> None:
        """Test database_url validator with PostgreSQL URL."""
        config = Config(database_url="postgresql://user:pass@localhost:5432/db")
        assert config.database_url == "postgresql://user:pass@localhost:5432/db"

    @pytest.mark.unit
    def test_database_url_validator_sqlite(self) -> None:
        """Test database_url validator with SQLite URL."""
        config = Config(database_url="sqlite:///path/to/db.sqlite")
        assert config.database_url == "sqlite:///path/to/db.sqlite"

    @pytest.mark.unit
    def test_database_url_validator_rejects_mysql(self) -> None:
        """Test database_url validator rejects MySQL."""
        with pytest.raises(ValidationError) as exc_info:
            Config(database_url="mysql://localhost/db")
        assert "postgresql://" in str(exc_info.value) or "sqlite:///" in str(exc_info.value)

    @pytest.mark.unit
    def test_database_url_validator_rejects_mongodb(self) -> None:
        """Test database_url validator rejects MongoDB."""
        with pytest.raises(ValidationError) as exc_info:
            Config(database_url="mongodb://localhost/db")
        assert "postgresql://" in str(exc_info.value) or "sqlite:///" in str(exc_info.value)

    @pytest.mark.unit
    def test_database_url_validator_allows_none(self) -> None:
        """Test database_url validator allows None."""
        config = Config(database_url=None)
        assert config.database_url is None

    @pytest.mark.unit
    def test_api_url_validator_https(self) -> None:
        """Test api_url validator with HTTPS."""
        config = Config(api_url="https://api.example.com")
        assert config.api_url == "https://api.example.com"

    @pytest.mark.unit
    def test_api_url_validator_http(self) -> None:
        """Test api_url validator with HTTP."""
        config = Config(api_url="http://localhost:8000")
        assert config.api_url == "http://localhost:8000"

    @pytest.mark.unit
    def test_api_url_validator_strips_trailing_slash(self) -> None:
        """Test api_url validator strips trailing slash."""
        config = Config(api_url="https://api.example.com/")
        assert config.api_url == "https://api.example.com"

    @pytest.mark.unit
    def test_api_url_validator_strips_multiple_trailing_slashes(self) -> None:
        """Test api_url validator strips multiple trailing slashes."""
        config = Config(api_url="https://api.example.com///")
        assert config.api_url == "https://api.example.com"

    @pytest.mark.unit
    def test_api_url_validator_rejects_ftp(self) -> None:
        """Test api_url validator rejects FTP."""
        with pytest.raises(ValidationError) as exc_info:
            Config(api_url="ftp://example.com")
        assert "http://" in str(exc_info.value) or "https://" in str(exc_info.value)

    @pytest.mark.unit
    def test_api_url_validator_rejects_no_protocol(self) -> None:
        """Test api_url validator rejects URL without protocol."""
        with pytest.raises(ValidationError) as exc_info:
            Config(api_url="api.example.com")
        assert "http://" in str(exc_info.value) or "https://" in str(exc_info.value)


class TestConfigValidateAssignment:
    """Test suite for validate_assignment behavior."""

    @pytest.mark.unit
    def test_validate_assignment_enabled(self) -> None:
        """Test that validate_assignment is enabled."""
        config = Config()

        # Validation should occur on assignment
        with pytest.raises(ValidationError):
            config.max_agents = 0

    @pytest.mark.unit
    def test_validate_assignment_max_agents(self) -> None:
        """Test validate_assignment for max_agents."""
        config = Config()

        # Valid assignment
        config.max_agents = 500
        assert config.max_agents == HTTP_INTERNAL_SERVER_ERROR

        # Invalid assignment
        with pytest.raises(ValidationError):
            config.max_agents = 10001

    @pytest.mark.unit
    def test_validate_assignment_default_view(self) -> None:
        """Test validate_assignment for default_view."""
        config = Config()

        # Valid assignment
        config.default_view = "CODE"
        assert config.default_view == "CODE"

        # Invalid assignment
        with pytest.raises(ValidationError):
            config.default_view = "INVALID"

    @pytest.mark.unit
    def test_validate_assignment_database_url(self) -> None:
        """Test validate_assignment for database_url."""
        config = Config()

        # Valid assignment
        config.database_url = "postgresql://localhost/db"
        assert config.database_url == "postgresql://localhost/db"

        # Invalid assignment
        with pytest.raises(ValidationError):
            config.database_url = "mysql://localhost/db"

    @pytest.mark.unit
    def test_validate_assignment_api_url(self) -> None:
        """Test validate_assignment for api_url."""
        config = Config()

        # Valid assignment
        config.api_url = "https://new-api.example.com/"
        assert config.api_url == "https://new-api.example.com"

        # Invalid assignment
        with pytest.raises(ValidationError):
            config.api_url = "ftp://example.com"


class TestConfigPropertyBasedHypothesis:
    """Property-based tests using Hypothesis."""

    @pytest.mark.unit
    @pytest.mark.property
    @given(max_agents=st.integers(min_value=1, max_value=10000))
    def test_max_agents_valid_range(self, max_agents: Any) -> None:
        """Test max_agents accepts all valid values."""
        config = Config(max_agents=max_agents)
        assert 1 <= config.max_agents <= 10000

    @pytest.mark.unit
    @pytest.mark.property
    @given(max_agents=st.integers(max_value=0))
    def test_max_agents_rejects_below_min(self, max_agents: Any) -> None:
        """Test max_agents rejects values below minimum."""
        with pytest.raises(ValidationError):
            Config(max_agents=max_agents)

    @pytest.mark.unit
    @pytest.mark.property
    @given(max_agents=st.integers(min_value=10001))
    def test_max_agents_rejects_above_max(self, max_agents: Any) -> None:
        """Test max_agents rejects values above maximum."""
        with pytest.raises(ValidationError):
            Config(max_agents=max_agents)

    @pytest.mark.unit
    @pytest.mark.property
    @given(api_timeout=st.floats(min_value=1.0, max_value=300.0, allow_nan=False, allow_infinity=False))
    def test_api_timeout_valid_range(self, api_timeout: Any) -> None:
        """Test api_timeout accepts all valid values."""
        config = Config(api_timeout=api_timeout)
        assert 1.0 <= config.api_timeout <= 300.0

    @pytest.mark.unit
    @pytest.mark.property
    @given(api_max_retries=st.integers(min_value=1, max_value=10))
    def test_api_max_retries_valid_range(self, api_max_retries: Any) -> None:
        """Test api_max_retries accepts all valid values."""
        config = Config(api_max_retries=api_max_retries)
        assert 1 <= config.api_max_retries <= COUNT_TEN

    @pytest.mark.unit
    @pytest.mark.property
    @given(sync_interval=st.integers(min_value=10, max_value=86400))
    def test_sync_interval_valid_range(self, sync_interval: Any) -> None:
        """Test sync_interval_seconds accepts all valid values."""
        config = Config(sync_interval_seconds=sync_interval)
        assert config.sync_interval_seconds >= COUNT_TEN

    @pytest.mark.unit
    @pytest.mark.property
    @given(project_id=st.text(min_size=1, max_size=100))
    def test_current_project_id_accepts_text(self, project_id: Any) -> None:
        """Test current_project_id accepts any text."""
        config = Config(current_project_id=project_id)
        assert config.current_project_id == project_id

    @pytest.mark.unit
    @pytest.mark.property
    @given(project_name=st.text(min_size=1, max_size=200))
    def test_current_project_name_accepts_text(self, project_name: Any) -> None:
        """Test current_project_name accepts any text."""
        config = Config(current_project_name=project_name)
        assert config.current_project_name == project_name

    @pytest.mark.unit
    @pytest.mark.property
    @given(
        aliases=st.dictionaries(
            keys=st.text(min_size=1, max_size=50),
            values=st.text(min_size=1, max_size=100),
            max_size=50,
        ),
    )
    def test_aliases_accepts_any_dict(self, aliases: Any) -> None:
        """Test aliases accepts any dictionary."""
        config = Config(aliases=aliases)
        assert config.aliases == aliases

    @pytest.mark.unit
    @pytest.mark.property
    @given(
        view_type=st.sampled_from(["FEATURE", "CODE", "WIREFRAME", "API", "TEST", "DATABASE", "ROADMAP", "PROGRESS"]),
    )
    def test_default_view_accepts_valid_types(self, view_type: Any) -> None:
        """Test default_view accepts all valid view types."""
        config = Config(default_view=view_type)
        assert config.default_view == view_type

    @pytest.mark.unit
    @pytest.mark.property
    @given(output_format=st.sampled_from(["table", "json", "yaml", "csv"]))
    def test_output_format_accepts_valid_formats(self, output_format: Any) -> None:
        """Test output_format accepts all valid formats."""
        config = Config(output_format=output_format)
        assert config.output_format == output_format

    @pytest.mark.unit
    @pytest.mark.property
    @given(log_level=st.sampled_from(["DEBUG", "INFO", "WARNING", "ERROR"]))
    def test_log_level_accepts_valid_levels(self, log_level: Any) -> None:
        """Test log_level accepts all valid levels."""
        config = Config(log_level=log_level)
        assert config.log_level == log_level

    @pytest.mark.unit
    @pytest.mark.property
    @given(strategy=st.sampled_from(["last_write_wins", "local_wins", "remote_wins", "manual"]))
    def test_sync_conflict_strategy_accepts_valid_strategies(self, strategy: Any) -> None:
        """Test sync_conflict_strategy accepts all valid strategies."""
        config = Config(sync_conflict_strategy=strategy)
        assert config.sync_conflict_strategy == strategy


class TestConfigComplexScenarios:
    """Test suite for complex validation scenarios."""

    @pytest.mark.unit
    def test_multiple_validation_errors(self) -> None:
        """Test that multiple validation errors are reported."""
        with pytest.raises(ValidationError) as exc_info:
            Config(
                max_agents=0,
                api_timeout=0.5,
                default_view="INVALID",
            )

        error = exc_info.value
        errors_dict = error.errors()
        assert len(errors_dict) >= COUNT_TWO  # At least 2 errors

    @pytest.mark.unit
    def test_config_immutability_extra_forbid(self) -> None:
        """Test that extra fields are forbidden."""
        with pytest.raises(ValidationError):
            Config(extra_field="value")

    @pytest.mark.unit
    def test_database_url_with_special_characters(self) -> None:
        """Test database URL with special characters in password."""
        config = Config(database_url="postgresql://user:p@ss!w0rd@localhost/db")
        assert config.database_url == "postgresql://user:p@ss!w0rd@localhost/db"

    @pytest.mark.unit
    def test_api_url_with_port(self) -> None:
        """Test API URL with port number."""
        config = Config(api_url="https://api.example.com:8443")
        assert config.api_url == "https://api.example.com:8443"

    @pytest.mark.unit
    def test_api_url_with_path(self) -> None:
        """Test API URL with path."""
        config = Config(api_url="https://api.example.com/v1/api/")
        assert config.api_url == "https://api.example.com/v1/api"

    @pytest.mark.unit
    def test_config_serialization_deserialization(self) -> None:
        """Test config can be serialized and deserialized."""
        original = Config(
            database_url="postgresql://localhost/db",
            current_project_id="proj-123",
            max_agents=500,
            default_view="CODE",
        )

        # Serialize to dict
        config_dict = original.model_dump()

        # Deserialize from dict
        restored = Config(**config_dict)

        assert restored.database_url == original.database_url
        assert restored.current_project_id == original.current_project_id
        assert restored.max_agents == original.max_agents
        assert restored.default_view == original.default_view

    @pytest.mark.unit
    def test_config_json_serialization(self) -> None:
        """Test config can be serialized to JSON."""
        config = Config(
            database_url="postgresql://localhost/db",
            max_agents=500,
        )

        json_str = config.model_dump_json()
        assert isinstance(json_str, str)
        assert "postgresql://localhost/db" in json_str
        assert "500" in json_str

    @pytest.mark.unit
    def test_config_update_via_dict(self) -> None:
        """Test config can be updated via dictionary."""
        config = Config()

        # Update via model_dump and create new instance
        updates = {"max_agents": 500, "default_view": "CODE"}
        config_dict = config.model_dump()
        config_dict.update(updates)

        new_config = Config(**config_dict)
        assert new_config.max_agents == HTTP_INTERNAL_SERVER_ERROR
        assert new_config.default_view == "CODE"
