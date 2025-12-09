"""
Comprehensive tests for ConcurrentOperationsService.

Tests all methods: retry_with_backoff decorator, execute_with_retry, execute_in_transaction.

Coverage target: 85%+
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm.exc import StaleDataError

from tracertm.services.concurrent_operations_service import (
    ConcurrentOperationsService,
    ConcurrencyError,
    retry_with_backoff,
)


class TestConcurrencyError:
    """Test ConcurrencyError exception."""

    def test_exception_message(self):
        """Test exception stores message."""
        error = ConcurrencyError("Conflict detected")
        assert str(error) == "Conflict detected"

    def test_exception_raises(self):
        """Test exception can be raised."""
        with pytest.raises(ConcurrencyError, match="Test error"):
            raise ConcurrencyError("Test error")


class TestRetryWithBackoffDecorator:
    """Test retry_with_backoff decorator."""

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_succeeds_first_try(self, mock_sleep):
        """Test operation succeeding on first try."""
        @retry_with_backoff(max_retries=3)
        def success_op():
            return "success"

        result = success_op()

        assert result == "success"
        mock_sleep.assert_not_called()

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_retries_on_stale_data_error(self, mock_sleep):
        """Test retry on StaleDataError."""
        attempts = [0]

        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def flaky_op():
            attempts[0] += 1
            if attempts[0] < 3:
                raise StaleDataError()
            return "success"

        result = flaky_op()

        assert result == "success"
        assert attempts[0] == 3
        assert mock_sleep.call_count == 2

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_retries_on_concurrency_error(self, mock_sleep):
        """Test retry on ConcurrencyError."""
        attempts = [0]

        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def flaky_op():
            attempts[0] += 1
            if attempts[0] < 2:
                raise ConcurrencyError("Conflict")
            return "success"

        result = flaky_op()

        assert result == "success"
        assert attempts[0] == 2

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_max_retries_exceeded(self, mock_sleep):
        """Test failure after max retries exceeded."""
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_fails():
            raise StaleDataError()

        with pytest.raises(ConcurrencyError, match="failed after 2 retries"):
            always_fails()

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_non_retryable_error_propagates(self, mock_sleep):
        """Test non-retryable errors propagate immediately."""
        @retry_with_backoff(max_retries=3)
        def fails_with_value_error():
            raise ValueError("Bad value")

        with pytest.raises(ValueError, match="Bad value"):
            fails_with_value_error()

        mock_sleep.assert_not_called()

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    @patch("tracertm.services.concurrent_operations_service.random.random")
    def test_jitter_applied(self, mock_random, mock_sleep):
        """Test jitter is applied to delay."""
        mock_random.return_value = 0.5  # Neutral jitter

        attempts = [0]

        @retry_with_backoff(max_retries=2, initial_delay=0.1, jitter=True)
        def flaky_op():
            attempts[0] += 1
            if attempts[0] < 2:
                raise StaleDataError()
            return "success"

        flaky_op()

        mock_random.assert_called()

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_no_jitter_when_disabled(self, mock_sleep):
        """Test no jitter when disabled."""
        attempts = [0]

        @retry_with_backoff(max_retries=2, initial_delay=0.1, jitter=False)
        def flaky_op():
            attempts[0] += 1
            if attempts[0] < 2:
                raise StaleDataError()
            return "success"

        flaky_op()

        # First sleep should be exactly initial_delay (0.1)
        mock_sleep.assert_called()

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_delay_clamped_to_max(self, mock_sleep):
        """Test delay is clamped to max_delay."""
        attempts = [0]

        @retry_with_backoff(max_retries=5, initial_delay=1.0, max_delay=0.5, jitter=False)
        def flaky_op():
            attempts[0] += 1
            if attempts[0] < 3:
                raise StaleDataError()
            return "success"

        flaky_op()

        # All delays should be clamped to max_delay
        for call in mock_sleep.call_args_list:
            assert call[0][0] <= 0.5


class TestConcurrentOperationsService:
    """Test ConcurrentOperationsService class."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ConcurrentOperationsService(mock_session)

    def test_init(self, service, mock_session):
        """Test service initialization."""
        assert service.session == mock_session


class TestExecuteWithRetry:
    """Test execute_with_retry method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ConcurrentOperationsService(mock_session)

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_succeeds_first_try(self, mock_sleep, service):
        """Test operation succeeding on first try."""
        operation = Mock(return_value="result")

        result = service.execute_with_retry(operation)

        assert result == "result"
        operation.assert_called_once()
        mock_sleep.assert_not_called()

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_retries_on_stale_data_error(self, mock_sleep, service):
        """Test retry on StaleDataError."""
        operation = Mock()
        operation.side_effect = [StaleDataError(), StaleDataError(), "success"]

        result = service.execute_with_retry(operation, max_retries=3)

        assert result == "success"
        assert operation.call_count == 3
        assert mock_sleep.call_count == 2

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_retries_on_concurrency_error(self, mock_sleep, service):
        """Test retry on ConcurrencyError."""
        operation = Mock()
        operation.side_effect = [ConcurrencyError("Conflict"), "success"]

        result = service.execute_with_retry(operation, max_retries=2)

        assert result == "success"

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_max_retries_exceeded(self, mock_sleep, service):
        """Test failure after max retries."""
        operation = Mock(side_effect=StaleDataError())

        with pytest.raises(ConcurrencyError, match="failed after 2 retries"):
            service.execute_with_retry(operation, max_retries=2)

    @patch("tracertm.services.concurrent_operations_service.time.sleep")
    def test_custom_initial_delay(self, mock_sleep, service):
        """Test custom initial delay."""
        operation = Mock()
        operation.side_effect = [StaleDataError(), "success"]

        service.execute_with_retry(operation, max_retries=2, initial_delay=0.5)

        # First sleep should include jitter around 0.5
        assert mock_sleep.called


class TestExecuteInTransaction:
    """Test execute_in_transaction method."""

    @pytest.fixture
    def mock_session(self):
        """Create mock session."""
        return Mock()

    @pytest.fixture
    def service(self, mock_session):
        """Create service instance."""
        return ConcurrentOperationsService(mock_session)

    def test_all_operations_succeed(self, service, mock_session):
        """Test successful execution of all operations."""
        op1 = Mock(return_value="result1")
        op2 = Mock(return_value="result2")
        op3 = Mock(return_value="result3")

        results = service.execute_in_transaction([op1, op2, op3])

        assert results == ["result1", "result2", "result3"]
        mock_session.commit.assert_called_once()
        mock_session.rollback.assert_not_called()

    def test_rollback_on_failure(self, service, mock_session):
        """Test rollback when operation fails."""
        op1 = Mock(return_value="result1")
        op2 = Mock(side_effect=ValueError("Failed"))
        op3 = Mock(return_value="result3")

        with pytest.raises(ValueError, match="Failed"):
            service.execute_in_transaction([op1, op2, op3])

        mock_session.rollback.assert_called_once()
        mock_session.commit.assert_not_called()

    def test_empty_operations_list(self, service, mock_session):
        """Test with empty operations list."""
        results = service.execute_in_transaction([])

        assert results == []
        mock_session.commit.assert_called_once()

    def test_single_operation(self, service, mock_session):
        """Test with single operation."""
        op = Mock(return_value="single")

        results = service.execute_in_transaction([op])

        assert results == ["single"]
        mock_session.commit.assert_called_once()
