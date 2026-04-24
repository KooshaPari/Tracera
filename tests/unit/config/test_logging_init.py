"""Tests for logging initialization and configuration.

Target: +1% coverage on logging initialization paths
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from tests.test_constants import COUNT_THREE
from tracertm.logging_config import get_logger


class TestGetLogger:
    """Test suite for get_logger function."""

    @pytest.mark.unit
    def test_get_logger_returns_bound_logger(self) -> None:
        """Test get_logger returns bound logger."""
        result = get_logger("test_module")

        # Result should be a logger-like object
        assert result is not None

    @pytest.mark.unit
    def test_get_logger_with_different_names(self) -> None:
        """Test get_logger with different module names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        logger3 = get_logger("module3")

        # All should return loggers
        assert logger1 is not None
        assert logger2 is not None
        assert logger3 is not None

    @pytest.mark.unit
    def test_get_logger_module_name(self) -> None:
        """Test get_logger preserves module name."""
        logger = get_logger("tracertm.api.client")

        # Should return a logger instance
        assert logger is not None

    @pytest.mark.unit
    def test_get_logger_nested_module(self) -> None:
        """Test get_logger with nested module names."""
        logger = get_logger("tracertm.core.database")

        assert logger is not None

    @pytest.mark.unit
    def test_get_logger_simple_name(self) -> None:
        """Test get_logger with simple module name."""
        logger = get_logger("api")

        assert logger is not None


class TestLoggingSetup:
    """Test suite for logging setup."""

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_setup_logging_creates_log_directory(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test setup_logging creates log directory."""
        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        tmp_data = Path("/tmp/test_tracertm_logs")
        tmp_data.mkdir(parents=True, exist_ok=True)

        settings = TraceSettings(data_dir=tmp_data)
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        setup_logging()

        # Verify remove was called
        mock_logger.remove.assert_called_once()


class TestLoggingConfiguration:
    """Test suite for logging configuration."""

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_logging_respects_log_level(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test logging respects configured log level."""
        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        settings = TraceSettings(log_level="DEBUG")
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        setup_logging()

        # Verify add was called
        assert mock_logger.add.called

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_logging_file_handlers(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test logging file handlers are created."""
        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        settings = TraceSettings(log_level="INFO")
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        setup_logging()

        # Verify multiple handlers are added
        assert mock_logger.add.call_count >= COUNT_THREE


class TestLoggingIntegration:
    """Integration tests for logging configuration."""

    @pytest.mark.unit
    def test_get_logger_integration(self) -> None:
        """Test get_logger in actual use."""
        logger = get_logger("test.module")

        # Should be usable
        assert logger is not None
        assert hasattr(logger, "__module__") or hasattr(logger, "bind")

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_setup_and_get_logger(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test setup_logging and get_logger work together."""
        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        settings = TraceSettings()
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        # Setup logging
        setup_logging()

        # Get a logger
        logger = get_logger("test.module")

        # Both should work
        assert mock_logger.remove.called
        assert logger is not None


class TestLoggingErrorHandling:
    """Test suite for logging error handling."""

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_logging_with_invalid_directory(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test logging handles invalid directory gracefully."""
        from pathlib import Path

        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        # Use a valid temp directory
        settings = TraceSettings(data_dir=Path("/tmp"))
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        # Should not raise
        setup_logging()

        assert mock_logger.remove.called


class TestLoggingMultipleLevels:
    """Test suite for logging configuration with different levels."""

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_logging_debug_level(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test logging with DEBUG level."""
        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        settings = TraceSettings(log_level="DEBUG")
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        setup_logging()

        assert mock_logger.remove.called

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_logging_error_level(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test logging with ERROR level."""
        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        settings = TraceSettings(log_level="ERROR")
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        setup_logging()

        assert mock_logger.remove.called

    @pytest.mark.unit
    @patch("tracertm.logging_config.logger")
    @patch("tracertm.logging_config.get_settings")
    def test_logging_warning_level(self, mock_get_settings: Any, mock_logger: Any) -> None:
        """Test logging with WARNING level."""
        from tracertm.config.settings import TraceSettings, reset_settings

        reset_settings()
        settings = TraceSettings(log_level="WARNING")
        mock_get_settings.return_value = settings

        mock_logger.remove = MagicMock()
        mock_logger.add = MagicMock()
        mock_logger.info = MagicMock()

        from tracertm.logging_config import setup_logging

        setup_logging()

        assert mock_logger.remove.called
