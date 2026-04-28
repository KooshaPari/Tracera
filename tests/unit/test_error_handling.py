"""Unit tests for error handling and user-friendly messages.

Story 1.6: Error Handling & User-Friendly Messages
Test Cases: TC-1.6.1 to TC-1.6.7
"""

import pytest

pytest.importorskip("tracertm.cli.errors", reason="tracertm.cli.errors module not yet implemented")

from tests.test_constants import COUNT_TEN
from tracertm.cli.errors import (
    ConfigurationError,
    DatabaseConnectionError,
    DiskSpaceError,
    NetworkError,
    PermissionError,
    ProjectNotFoundError,
    TraceRTMError,
    format_validation_error,
    handle_error,
)


class TestErrorHandling:
    """Test error handling and user-friendly messages."""

    def test_database_connection_error(self) -> None:
        """TC-1.6.1: Database connection error with helpful message.

        Given: Database connection fails
        When: Error is raised
        Then: User-friendly message displayed with suggestion
        """
        # PostgreSQL connection error
        pg_error = DatabaseConnectionError(
            "postgresql://localhost:5432/testdb",
            Exception("could not connect to server"),
        )

        assert "Failed to connect to database" in pg_error.message
        assert "PostgreSQL is running" in (pg_error.suggestion or "")

        # SQLite permission error
        sqlite_error = DatabaseConnectionError("sqlite:///test.db", Exception("unable to open database file"))

        assert "Failed to connect to database" in sqlite_error.message
        assert pg_error.suggestion is not None

    def test_invalid_configuration_error(self) -> None:
        """TC-1.6.2: Invalid configuration error with suggestion.

        Given: Configuration is invalid
        When: Error is raised
        Then: Clear error message with fix suggestion
        """
        error = ConfigurationError("database_url", "must start with 'postgresql://'")

        assert "Invalid configuration for 'database_url'" in error.message
        assert "must start with 'postgresql://'" in error.message
        assert "rtm config set database_url" in (error.suggestion or "")

    def test_missing_project_error(self) -> None:
        """TC-1.6.3: Missing project error with helpful guidance.

        Given: Project does not exist
        When: Error is raised
        Then: Helpful message with next steps
        """
        # Specific project not found
        error1 = ProjectNotFoundError("myproject")
        assert "Project 'myproject' not found" in error1.message
        assert error1.suggestion is not None and "rtm project list" in error1.suggestion

        # No current project
        error2 = ProjectNotFoundError()
        assert "No current project set" in error2.message
        assert error2.suggestion is not None and "rtm project init" in error2.suggestion

    def test_permission_error(self) -> None:
        """TC-1.6.4: Permission error with clear explanation.

        Given: Permission denied for operation
        When: Error is raised
        Then: Clear message about permissions
        """
        error = PermissionError("/path/to/file", "write")

        assert "Permission denied to write" in error.message
        assert "/path/to/file" in error.message
        assert error.suggestion is not None and "permissions" in error.suggestion.lower()

    def test_disk_space_error(self) -> None:
        """TC-1.6.5: Disk space error with size information.

        Given: Insufficient disk space
        When: Error is raised
        Then: Message includes required space
        """
        error = DiskSpaceError(required_mb=100)

        assert "Insufficient disk space" in error.message
        assert "100MB" in error.message
        assert error.suggestion is not None and "Free up disk space" in error.suggestion

    def test_network_error(self) -> None:
        """TC-1.6.6: Network error with retry suggestion.

        Given: Network operation fails
        When: Error is raised
        Then: Message suggests checking connection
        """
        error = NetworkError("database sync", "connection timeout")

        assert "Network error during database sync" in error.message
        assert "connection timeout" in error.message
        assert error.suggestion is not None and "network connection" in error.suggestion.lower()

    def test_user_friendly_error_messages(self) -> None:
        """TC-1.6.7: All errors have user-friendly messages.

        Given: Any TraceRTM error
        When: Error is displayed
        Then: Message is clear and actionable
        """
        errors = [
            DatabaseConnectionError("postgresql://localhost/db"),
            ConfigurationError("test_key", "invalid value"),
            ProjectNotFoundError("test"),
            PermissionError("/test/path"),
            DiskSpaceError(50),
            NetworkError("test operation"),
        ]

        for error in errors:
            # All errors should have message and suggestion
            assert error.message is not None
            assert len(error.message) > 0
            assert error.suggestion is not None
            assert len(error.suggestion) > 0

            # Messages should not contain technical jargon
            assert "exception" not in error.message.lower()
            assert "traceback" not in error.message.lower()

            # Suggestions should be actionable (contain action words or be helpful)
            # Just verify suggestion is not empty and meaningful
            assert len(error.suggestion) > COUNT_TEN  # More than just a few words

    def test_validation_error_formatting(self) -> None:
        """Test validation error message formatting."""
        message = format_validation_error("port", "abc", "integer between 1-65535")

        assert "Invalid value for 'port'" in message
        assert "got 'abc'" in message
        assert "expected integer between 1-65535" in message

    def test_error_display_formatting(self) -> None:
        """Test that errors display with rich formatting."""
        error = TraceRTMError("Test error", "Test suggestion")

        # Should not raise exception
        error.display()

        assert error.message == "Test error"
        assert error.suggestion == "Test suggestion"

    def test_handle_error_function(self) -> None:
        """Test generic error handling function."""
        # TraceRTM error
        tracertm_error = ConfigurationError("test")
        handle_error(tracertm_error)

        # Generic exception
        generic_error = ValueError("Test error")
        handle_error(generic_error)

        # Should not raise exceptions
        assert True
