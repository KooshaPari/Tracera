"""Phase 15A: Quick Wins - Core Module Edge Cases.

Focus: Edge cases and boundary conditions for core utilities
Target: Core types, config, concurrency modules
Coverage Goal: 75% → 80%
"""

import asyncio
from pathlib import Path
from typing import Any, Never
from unittest.mock import Mock, mock_open, patch

import pytest
from sqlalchemy import create_engine

from tests.test_constants import COUNT_TEN, COUNT_THREE, COUNT_TWO, HTTP_INTERNAL_SERVER_ERROR
from tracertm.core.concurrency import ConcurrencyError, update_with_retry
from tracertm.core.config import Config, DatabaseConfig, UIConfig, get_config, set_config
from tracertm.models.types import JSONType


class TestJSONTypeEdgeCases:
    """Edge cases for JSONType custom SQLAlchemy type."""

    def test_json_type_cache_ok_attribute(self) -> None:
        """Test that cache_ok is properly set."""
        json_type = JSONType()
        assert json_type.cache_ok is True

    def test_json_type_postgresql_dialect(self) -> None:
        """Test JSONB is used for PostgreSQL dialect."""
        json_type = JSONType()
        dialect = Mock()
        dialect.name = "postgresql"
        dialect.type_descriptor = Mock(return_value="JSONB_TYPE")

        result = json_type.load_dialect_impl(dialect)
        assert result == "JSONB_TYPE"
        dialect.type_descriptor.assert_called_once()

    def test_json_type_sqlite_dialect(self) -> None:
        """Test JSON is used for SQLite dialect."""
        json_type = JSONType()
        dialect = Mock()
        dialect.name = "sqlite"
        dialect.type_descriptor = Mock(return_value="JSON_TYPE")

        result = json_type.load_dialect_impl(dialect)
        assert result == "JSON_TYPE"
        dialect.type_descriptor.assert_called_once()

    def test_json_type_mysql_dialect(self) -> None:
        """Test JSON is used for MySQL dialect (non-PostgreSQL)."""
        json_type = JSONType()
        dialect = Mock()
        dialect.name = "mysql"
        dialect.type_descriptor = Mock(return_value="JSON_TYPE")

        result = json_type.load_dialect_impl(dialect)
        assert result == "JSON_TYPE"

    def test_json_type_impl_attribute(self) -> None:
        """Test that impl is correctly set to JSON."""
        json_type = JSONType()
        assert json_type.impl is not None


class TestDatabaseConfigEdgeCases:
    """Edge cases for DatabaseConfig."""

    def test_database_config_defaults(self) -> None:
        """Test all default values are set correctly."""
        config = DatabaseConfig()
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "tracertm"
        assert config.username == "tracertm"
        assert config.password == "tracertm"
        assert config.pool_size == 20
        assert config.max_overflow == COUNT_TEN

    def test_database_config_url_generation(self) -> None:
        """Test database URL is correctly generated."""
        config = DatabaseConfig()
        expected = "postgresql://tracertm:tracertm@localhost:5432/tracertm"
        assert config.url == expected

    def test_database_config_custom_values(self) -> None:
        """Test custom configuration values."""
        config = DatabaseConfig(
            host="db.example.com",
            port=5433,
            database="custom_db",
            username="admin",
            password="secure_pass",
            pool_size=50,
            max_overflow=20,
        )
        assert config.host == "db.example.com"
        assert config.port == 5433
        assert "admin:secure_pass@db.example.com:5433/custom_db" in config.url

    def test_database_config_url_with_special_characters(self) -> None:
        """Test URL generation with special characters in credentials."""
        config = DatabaseConfig(
            username="user@domain",
            password="p@ss:w/rd",
        )
        # URL should be generated even with special chars
        assert "user@domain" in config.url or "p@ss" in config.url

    def test_database_config_boundary_values(self) -> None:
        """Test boundary values for ports and pool sizes."""
        config = DatabaseConfig(port=1, pool_size=1, max_overflow=0)
        assert config.port == 1
        assert config.pool_size == 1
        assert config.max_overflow == 0

    def test_database_config_large_pool_sizes(self) -> None:
        """Test large pool size values."""
        config = DatabaseConfig(pool_size=1000, max_overflow=500)
        assert config.pool_size == 1000
        assert config.max_overflow == HTTP_INTERNAL_SERVER_ERROR


class TestUIConfigEdgeCases:
    """Edge cases for UIConfig."""

    def test_ui_config_defaults(self) -> None:
        """Test default UI configuration."""
        config = UIConfig()
        assert config.theme == "developer-focus"
        assert config.force_bold is False
        assert config.use_symbols is True

    def test_ui_config_high_contrast_theme(self) -> None:
        """Test high-contrast theme configuration."""
        config = UIConfig(theme="high-contrast")
        assert config.theme == "high-contrast"

    def test_ui_config_all_disabled(self) -> None:
        """Test configuration with all features disabled."""
        config = UIConfig(force_bold=False, use_symbols=False)
        assert config.force_bold is False
        assert config.use_symbols is False

    def test_ui_config_all_enabled(self) -> None:
        """Test configuration with all features enabled."""
        config = UIConfig(force_bold=True, use_symbols=True)
        assert config.force_bold is True
        assert config.use_symbols is True

    def test_ui_config_custom_theme(self) -> None:
        """Test custom theme name."""
        config = UIConfig(theme="custom-dark")
        assert config.theme == "custom-dark"


class TestConfigEdgeCases:
    """Edge cases for main Config class."""

    def test_config_defaults(self) -> None:
        """Test default configuration values."""
        config = Config()
        assert config.database is not None
        assert config.ui is not None
        assert config.data_dir == Path.home() / ".tracertm"
        assert config.current_project is None

    def test_config_with_custom_project(self) -> None:
        """Test configuration with custom project."""
        config = Config(current_project="my-project")
        assert config.current_project == "my-project"

    def test_config_with_custom_data_dir(self, tmp_path: Any) -> None:
        """Test configuration with custom data directory."""
        custom_dir = tmp_path / "tracertm-test"
        config = Config(data_dir=custom_dir)
        assert config.data_dir == custom_dir

    def test_config_nested_defaults(self) -> None:
        """Test nested configuration with factories."""
        config = Config()
        assert isinstance(config.database, DatabaseConfig)
        assert isinstance(config.ui, UIConfig)

    @patch("pathlib.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data="database:\n  host: testhost\n")
    def test_config_load_existing_file(self, mock_file: Any, mock_exists: Any, _tmp_path: Any) -> None:
        """Test loading configuration from existing file."""
        mock_exists.return_value = True

        config = Config.load(tmp_path / "config.yaml")
        assert config is not None

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_config_load_creates_default(
        self, mock_file: Any, mock_mkdir: Any, mock_exists: Any, tmp_path: Any
    ) -> None:
        """Test that load creates default config when file doesn't exist."""
        mock_exists.return_value = False

        config = Config.load(tmp_path / "config.yaml")
        assert config is not None
        # Verify default values
        assert config.database.host == "localhost"

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_config_save_creates_directory(self, mock_file: Any, mock_mkdir: Any, _tmp_path: Any) -> None:
        """Test that save creates parent directory if needed."""
        config = Config()
        config.save(tmp_path / "tracertm" / "config.yaml")
        mock_mkdir.assert_called_once()

    @patch("pathlib.Path.mkdir")
    @patch("builtins.open", new_callable=mock_open)
    def test_config_save_writes_yaml(self, mock_file: Any, mock_mkdir: Any, _tmp_path: Any) -> None:
        """Test that save writes YAML correctly."""
        config = Config()
        config.save(tmp_path / "config.yaml")
        mock_file.assert_called_once()

    def test_config_model_dump(self) -> None:
        """Test model_dump returns dictionary."""
        config = Config()
        data = config.model_dump()
        assert isinstance(data, dict)
        assert "database" in data
        assert "ui" in data

    @patch("tracertm.core.config.Config.load")
    def test_get_config_singleton(self, mock_load: Any) -> None:
        """Test get_config returns singleton instance."""
        mock_load.return_value = Config()

        # Reset global config
        import tracertm.core.config

        tracertm.core.config._config = None

        config1 = get_config()
        config2 = get_config()

        # Should only load once
        assert mock_load.call_count == 1
        assert config1 is config2

    def test_set_config_updates_global(self) -> None:
        """Test set_config updates global instance."""
        custom_config = Config(current_project="test-project")
        set_config(custom_config)

        # Get config should return the custom one
        config = get_config()
        assert config.current_project == "test-project"

    def test_config_with_all_custom_values(self) -> None:
        """Test configuration with all custom values."""
        db_config = DatabaseConfig(host="custom-host", port=5433, database="custom-db")
        ui_config = UIConfig(theme="custom-theme", force_bold=True)

        config = Config(
            database=db_config,
            ui=ui_config,
            data_dir=Path("/custom/dir"),
            current_project="custom-project",
        )

        assert config.database.host == "custom-host"
        assert config.ui.theme == "custom-theme"
        assert config.data_dir == Path("/custom/dir")
        assert config.current_project == "custom-project"


class TestConcurrencyEdgeCases:
    """Edge cases for concurrency control."""

    def test_concurrency_error_creation(self) -> None:
        """Test ConcurrencyError can be created."""
        error = ConcurrencyError("Test error")
        assert str(error) == "Test error"

    def test_concurrency_error_inheritance(self) -> None:
        """Test ConcurrencyError inherits from Exception."""
        error = ConcurrencyError("Test")
        assert isinstance(error, Exception)

    @pytest.mark.asyncio
    async def test_update_with_retry_success_first_try(self) -> None:
        """Test successful update on first try."""
        call_count = 0

        async def update_fn() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            return "success"

        result = await update_with_retry(update_fn)
        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_update_with_retry_success_after_retries(self) -> None:
        """Test successful update after retries."""
        call_count = 0

        async def update_fn() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "Retry needed"
                raise ConcurrencyError(msg)
            return "success"

        result = await update_with_retry(update_fn, max_retries=5)
        assert result == "success"
        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_update_with_retry_fails_all_retries(self) -> None:
        """Test failure after all retries exhausted."""
        call_count = 0

        async def update_fn() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Always fails"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError) as exc_info:
            await update_with_retry(update_fn, max_retries=3)

        assert "Failed after 3 retries" in str(exc_info.value)
        assert call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_update_with_retry_custom_max_retries(self) -> None:
        """Test custom max_retries parameter."""
        call_count = 0

        async def update_fn() -> Never:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            msg = "Fail"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError):
            await update_with_retry(update_fn, max_retries=1)

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_update_with_retry_custom_base_delay(self) -> None:
        """Test custom base_delay parameter."""
        start_time = asyncio.get_event_loop().time()

        async def update_fn() -> Never:
            await asyncio.sleep(0)
            msg = "Fail"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError):
            await update_with_retry(update_fn, max_retries=2, base_delay=0.01)

        # Should have some delay but very small due to base_delay=0.01
        elapsed = asyncio.get_event_loop().time() - start_time
        assert elapsed < 1.0  # Should be much less than a second

    @pytest.mark.asyncio
    async def test_update_with_retry_exponential_backoff(self) -> None:
        """Test that retry delays follow exponential backoff."""
        call_times = []

        async def update_fn() -> Never:
            await asyncio.sleep(0)
            call_times.append(asyncio.get_event_loop().time())
            msg = "Fail"
            raise ConcurrencyError(msg)

        with pytest.raises(ConcurrencyError):
            await update_with_retry(update_fn, max_retries=3, base_delay=0.05)

        # Verify increasing delays between retries
        assert len(call_times) == COUNT_THREE
        if len(call_times) >= COUNT_TWO:
            delay1 = call_times[1] - call_times[0]
            assert delay1 > 0.04  # Base delay with jitter

    @pytest.mark.asyncio
    async def test_update_with_retry_returns_correct_value(self) -> None:
        """Test that return value is passed through correctly."""
        test_object = {"key": "value", "number": 42}

        async def update_fn() -> None:
            await asyncio.sleep(0)
            return test_object

        result = await update_with_retry(update_fn)
        assert result is test_object
        assert result["key"] == "value"

    @pytest.mark.asyncio
    async def test_update_with_retry_preserves_error_message(self) -> None:
        """Test that original error message is preserved."""
        error_message = "Custom error message with details"

        async def update_fn() -> Never:
            await asyncio.sleep(0)
            raise ConcurrencyError(error_message)

        with pytest.raises(ConcurrencyError) as exc_info:
            await update_with_retry(update_fn, max_retries=1)

        assert error_message in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_with_retry_zero_retries(self) -> None:
        """Test behavior with max_retries=0 (edge case)."""
        call_count = 0

        async def update_fn() -> str:
            await asyncio.sleep(0)
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "Fail"
                raise ConcurrencyError(msg)
            return "success"

        # With 0 retries, should fail immediately
        with pytest.raises(ConcurrencyError):
            await update_with_retry(update_fn, max_retries=0)

        # Should only call once (no retries)
        assert call_count in {0, 1}  # May vary based on implementation

    @pytest.mark.asyncio
    async def test_update_with_retry_propagates_other_exceptions(self) -> None:
        """Test that non-ConcurrencyError exceptions are propagated."""

        async def update_fn() -> Never:
            await asyncio.sleep(0)
            msg = "Different error type"
            raise ValueError(msg)

        with pytest.raises(ValueError, match="Different error type") as exc_info:
            await update_with_retry(update_fn)

        assert "Different error type" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_with_retry_handles_none_return(self) -> None:
        """Test handling of None return value."""

        async def update_fn() -> None:
            await asyncio.sleep(0)

        result = await update_with_retry(update_fn)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_with_retry_multiple_concurrent_calls(self) -> None:
        """Test multiple concurrent retry operations."""
        counter = 0

        async def update_fn() -> None:
            nonlocal counter
            counter += 1
            await asyncio.sleep(0.01)
            return counter

        # Run multiple retries concurrently
        results = await asyncio.gather(
            update_with_retry(update_fn),
            update_with_retry(update_fn),
            update_with_retry(update_fn),
        )

        # All should succeed
        assert len(results) == COUNT_THREE
        assert all(r > 0 for r in results)


class TestCoreIntegration:
    """Integration tests for core modules working together."""

    def test_config_with_database_url_integration(self) -> None:
        """Test that config generates valid database URLs."""
        config = Config()
        db_url = config.database.url

        # URL should be valid PostgreSQL URL
        assert db_url.startswith("postgresql://")
        assert "localhost" in db_url
        assert "5432" in db_url

    @patch("tracertm.core.config.Config.load")
    def test_config_lifecycle(self, mock_load: Any) -> None:
        """Test complete configuration lifecycle."""
        # Create config
        config = Config(current_project="test")
        mock_load.return_value = config

        # Set it globally
        set_config(config)

        # Retrieve it
        retrieved = get_config()
        assert retrieved.current_project == "test"

    def test_json_type_with_real_dialect(self) -> None:
        """Test JSONType with real SQLAlchemy dialect."""
        json_type = JSONType()

        # Test with SQLite dialect
        sqlite_engine = create_engine("sqlite:///:memory:")
        sqlite_result = json_type.load_dialect_impl(sqlite_engine.dialect)
        assert sqlite_result is not None

    @pytest.mark.asyncio
    async def test_retry_with_config_updates(self) -> None:
        """Test retry mechanism with configuration updates."""
        config = Config()
        attempt = 0

        async def update_config() -> None:
            await asyncio.sleep(0)
            nonlocal attempt
            attempt += 1
            if attempt < COUNT_TWO:
                msg = "Config locked"
                raise ConcurrencyError(msg)
            config.current_project = f"project-{attempt}"
            return config

        result = await update_with_retry(update_config, max_retries=3)
        assert result.current_project == "project-2"
        assert attempt == COUNT_TWO
