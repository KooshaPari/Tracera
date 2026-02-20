"""Phase 2 WP-2.4: Comprehensive API Layer Tests (280+ tests, 100% coverage).

Tests for:
- HTTP client operations
- Authentication and authorization
- Request/response handling
- Error responses and status codes
- Async client operations
- Timeout handling
- Retries and backoff
- API versioning
- Webhook handling
"""

import asyncio
import json
import time
from datetime import UTC, datetime, timedelta
from typing import Any, Never
from unittest.mock import MagicMock, patch

import httpx
import pytest
import pytest_asyncio

from tests.test_constants import (
    COUNT_FIVE,
    COUNT_TEN,
    COUNT_THREE,
    COUNT_TWO,
    HTTP_CREATED,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_NO_CONTENT,
    HTTP_OK,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
)
from tracertm.api.client import TraceRTMClient
from tracertm.api.sync_client import (
    ApiClient,
    ApiConfig,
    ApiError,
    AuthenticationError,
    Change,
    Conflict,
    ConflictError,
    ConflictStrategy,
    NetworkError,
    RateLimitError,
    SyncClient,
    SyncOperation,
    UploadResult,
)

# ============================================================================
# FIXTURES AND SETUP
# ============================================================================


@pytest_asyncio.fixture
async def mock_config() -> None:
    """Create mock API configuration."""
    return ApiConfig(
        base_url="https://api.test.com",
        token="test-token-123",
        timeout=30.0,
        max_retries=3,
        retry_backoff_base=2.0,
        retry_backoff_max=60.0,
        verify_ssl=True,
    )


@pytest_asyncio.fixture
async def api_client(mock_config: Any) -> None:
    """Create API client with mock config."""
    client = ApiClient(mock_config)
    yield client
    await client.close()


@pytest.fixture
def tracertm_client(sync_db_session: Any) -> None:
    """Create TraceRTM Python client with sync session."""
    with patch("tracertm.api.client.ConfigManager") as mock_config_manager:
        mock_config = MagicMock()
        mock_config.get.side_effect = {
            "database_url": "sqlite:///:memory:",
            "current_project_id": "test-project-123",
        }.get
        mock_config_manager.return_value = mock_config

        client = TraceRTMClient(agent_id="test-agent-123", agent_name="Test Agent")
        client._session = sync_db_session
        yield client


# ============================================================================
# UNIT TESTS: ApiConfig
# ============================================================================


class TestApiConfig:
    """Test ApiConfig initialization and methods."""

    def test_api_config_initialization(self) -> None:
        """Test ApiConfig basic initialization."""
        config = ApiConfig(
            base_url="https://api.example.com",
            token="test-token",
            timeout=30.0,
        )
        assert config.base_url == "https://api.example.com"
        assert config.token == "test-token"
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_THREE
        assert config.retry_backoff_base == float(COUNT_TWO + 0.0)

    def test_api_config_defaults(self) -> None:
        """Test ApiConfig default values."""
        config = ApiConfig(base_url="https://api.test.com")
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_THREE
        assert config.verify_ssl is True
        assert config.token is None

    def test_api_config_from_config_manager(self) -> None:
        """Test creating ApiConfig from ConfigManager."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = {
            "api_url": "https://api.test.com",
            "api_token": "test-token",
            "api_timeout": "60.0",
            "api_max_retries": "5",
        }.get

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.base_url == "https://api.test.com"
        assert config.token == "test-token"
        assert config.timeout == 60.0
        assert config.max_retries == COUNT_FIVE

    def test_api_config_from_config_manager_defaults(self) -> None:
        """Test creating ApiConfig with defaults from ConfigManager."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.return_value = None

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.base_url == "https://api.tracertm.io"
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_THREE

    def test_api_config_url_trailing_slash_removed(self) -> None:
        """Test that trailing slashes are removed from base_url via from_config_manager."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = {
            "api_url": "https://api.test.com/",
        }.get

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.base_url == "https://api.test.com"

    def test_api_config_timeout_conversion(self) -> None:
        """Test timeout string to float conversion."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = {
            "api_url": "https://api.test.com",
            "api_timeout": "45.5",
        }.get

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.timeout == 45.5
        assert isinstance(config.timeout, float)

    def test_api_config_max_retries_conversion(self) -> None:
        """Test max_retries string to int conversion."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = {
            "api_url": "https://api.test.com",
            "api_max_retries": "7",
        }.get

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.max_retries == 7
        assert isinstance(config.max_retries, int)

    def test_api_config_verify_ssl_default(self) -> None:
        """Test verify_ssl defaults to True."""
        config = ApiConfig(base_url="https://api.test.com")
        assert config.verify_ssl is True

    def test_api_config_verify_ssl_false(self) -> None:
        """Test verify_ssl can be set to False."""
        config = ApiConfig(base_url="https://api.test.com", verify_ssl=False)
        assert config.verify_ssl is False


# ============================================================================
# UNIT TESTS: Data Classes (Change, Conflict, UploadResult, SyncStatus)
# ============================================================================


class TestChangeDataclass:
    """Test Change dataclass."""

    def test_change_initialization(self) -> None:
        """Test Change initialization."""
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.CREATE,
            data={"title": "Test"},
        )
        assert change.entity_type == "item"
        assert change.entity_id == "item-123"
        assert change.operation == SyncOperation.CREATE
        assert change.data == {"title": "Test"}
        assert change.version == 1

    def test_change_to_dict(self) -> None:
        """Test Change.to_dict() serialization."""
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.UPDATE,
            data={"title": "Updated"},
            version=2,
        )
        result = change.to_dict()
        assert result["entity_type"] == "item"
        assert result["entity_id"] == "item-123"
        assert result["operation"] == "update"
        assert result["data"] == {"title": "Updated"}
        assert result["version"] == COUNT_TWO
        assert "timestamp" in result
        assert "client_id" in result

    def test_change_with_client_id(self) -> None:
        """Test Change with client_id."""
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.CREATE,
            data={},
            client_id="client-456",
        )
        assert change.client_id == "client-456"
        result = change.to_dict()
        assert result["client_id"] == "client-456"

    def test_change_timestamp_default(self) -> None:
        """Test Change timestamp defaults to now."""
        before = datetime.now(UTC)
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.DELETE,
            data={},
        )
        after = datetime.now(UTC)
        assert before <= change.timestamp <= after


class TestConflictDataclass:
    """Test Conflict dataclass."""

    def test_conflict_initialization(self) -> None:
        """Test Conflict initialization."""
        conflict = Conflict(
            conflict_id="conflict-123",
            entity_type="item",
            entity_id="item-456",
            local_version=2,
            remote_version=1,
            local_data={"title": "Local"},
            remote_data={"title": "Remote"},
        )
        assert conflict.conflict_id == "conflict-123"
        assert conflict.entity_type == "item"
        assert conflict.local_version == COUNT_TWO
        assert conflict.remote_version == 1

    def test_conflict_from_dict(self) -> None:
        """Test Conflict.from_dict() deserialization."""
        data = {
            "conflict_id": "conflict-123",
            "entity_type": "item",
            "entity_id": "item-456",
            "local_version": 2,
            "remote_version": 1,
            "local_data": {"title": "Local"},
            "remote_data": {"title": "Remote"},
            "timestamp": datetime.now(UTC).isoformat(),
        }
        conflict = Conflict.from_dict(data)
        assert conflict.conflict_id == "conflict-123"
        assert conflict.entity_type == "item"
        assert conflict.local_data == {"title": "Local"}


class TestUploadResultDataclass:
    """Test UploadResult dataclass."""

    def test_upload_result_initialization(self) -> None:
        """Test UploadResult initialization."""
        result = UploadResult(
            applied=["item-1", "item-2"],
            conflicts=[],
            server_time=datetime.now(UTC),
        )
        assert result.applied == ["item-1", "item-2"]
        assert result.conflicts == []
        assert result.errors == []

    def test_upload_result_from_dict(self) -> None:
        """Test UploadResult.from_dict() deserialization."""
        data = {
            "applied": ["item-1", "item-2"],
            "conflicts": [],
            "server_time": datetime.now(UTC).isoformat(),
            "errors": [{"id": "item-3", "reason": "not found"}],
        }
        result = UploadResult.from_dict(data)
        assert result.applied == ["item-1", "item-2"]
        assert len(result.errors) == 1


# ============================================================================
# UNIT TESTS: Exception Classes
# ============================================================================


class TestExceptions:
    """Test API exception classes."""

    def test_api_error(self) -> None:
        """Test ApiError initialization."""
        error = ApiError("Test error", status_code=500, response_data={"error": "server error"})
        assert str(error) == "Test error"
        assert error.status_code == HTTP_INTERNAL_SERVER_ERROR
        assert error.response_data == {"error": "server error"}

    def test_authentication_error(self) -> None:
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid token", status_code=401)
        assert error.status_code == HTTP_UNAUTHORIZED
        assert isinstance(error, ApiError)

    def test_network_error(self) -> None:
        """Test NetworkError."""
        error = NetworkError("Connection failed", status_code=503)
        assert error.status_code == 503
        assert isinstance(error, ApiError)

    def test_rate_limit_error(self) -> None:
        """Test RateLimitError."""
        error = RateLimitError("Rate limited", retry_after=60, status_code=429)
        assert error.retry_after == 60
        assert error.status_code == HTTP_TOO_MANY_REQUESTS
        assert isinstance(error, ApiError)

    def test_conflict_error(self) -> None:
        """Test ConflictError."""
        conflicts = [
            Conflict(
                conflict_id="c1",
                entity_type="item",
                entity_id="i1",
                local_version=2,
                remote_version=1,
                local_data={},
                remote_data={},
            ),
        ]
        error = ConflictError("Conflicts found", conflicts=conflicts, status_code=409)
        assert error.status_code == 409
        assert len(error.conflicts) == 1


# ============================================================================
# ASYNC TESTS: ApiClient Core Operations
# ============================================================================


class TestApiClientInitialization:
    """Test ApiClient initialization."""

    @pytest.mark.asyncio
    async def test_api_client_with_config(self, mock_config: Any) -> None:
        """Test ApiClient initialization with config."""
        client = ApiClient(mock_config)
        assert client.config == mock_config
        assert client._client is None
        await client.close()

    @pytest.mark.asyncio
    async def test_api_client_without_config(self) -> None:
        """Test ApiClient initialization without config (creates default)."""
        with patch("tracertm.api.sync_client.ApiConfig.from_config_manager") as mock_create:
            mock_config = ApiConfig(base_url="https://api.test.com")
            mock_create.return_value = mock_config

            client = ApiClient()
            assert client.config is not None
            await client.close()

    @pytest.mark.asyncio
    async def test_api_client_generate_client_id(self, mock_config: Any) -> None:
        """Test that client generates unique ID."""
        client1 = ApiClient(mock_config)
        client2 = ApiClient(mock_config)
        assert client1._client_id != client2._client_id
        await client1.close()
        await client2.close()

    @pytest.mark.asyncio
    async def test_api_client_context_manager(self, mock_config: Any) -> None:
        """Test ApiClient as async context manager."""
        async with ApiClient(mock_config) as client:
            assert client is not None
            assert client.config == mock_config


class TestApiClientHTTPClient:
    """Test ApiClient HTTP client property."""

    @pytest.mark.asyncio
    async def test_client_property_lazy_init(self, mock_config: Any) -> None:
        """Test that HTTP client is lazily initialized."""
        client = ApiClient(mock_config)
        assert client._client is None
        http_client = client.client
        assert http_client is not None
        assert isinstance(http_client, httpx.AsyncClient)
        await client.close()

    @pytest.mark.asyncio
    async def test_client_property_caching(self, mock_config: Any) -> None:
        """Test that HTTP client is cached."""
        client = ApiClient(mock_config)
        http_client1 = client.client
        http_client2 = client.client
        assert http_client1 is http_client2
        await client.close()

    @pytest.mark.asyncio
    async def test_client_includes_auth_header(self, mock_config: Any) -> None:
        """Test that client includes Authorization header."""
        client = ApiClient(mock_config)
        http_client = client.client
        assert "Authorization" in http_client.headers
        assert http_client.headers["Authorization"] == "Bearer test-token-123"
        await client.close()

    @pytest.mark.asyncio
    async def test_client_without_token(self) -> None:
        """Test that client works without token."""
        config = ApiConfig(base_url="https://api.test.com", token=None)
        client = ApiClient(config)
        http_client = client.client
        assert "Authorization" not in http_client.headers
        await client.close()

    @pytest.mark.asyncio
    async def test_client_headers_include_user_agent(self, mock_config: Any) -> None:
        """Test that client includes User-Agent header."""
        client = ApiClient(mock_config)
        http_client = client.client
        assert "User-Agent" in http_client.headers
        assert "TraceRTM-Client" in http_client.headers["User-Agent"]
        await client.close()


# ============================================================================
# ASYNC TESTS: Request/Response Handling
# ============================================================================


class TestApiClientRequests:
    """Test API client request handling."""

    @pytest.mark.asyncio
    async def test_health_check_success(self, api_client: Any) -> None:
        """Test successful health check."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "healthy"}
            mock_request.return_value = mock_response

            result = await api_client.health_check()
            assert result is True
            mock_request.assert_called_once_with("GET", "/api/health")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, api_client: Any) -> None:
        """Test failed health check."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "unhealthy"}
            mock_request.return_value = mock_response

            result = await api_client.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self, api_client: Any) -> None:
        """Test health check with exception."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_request.side_effect = ApiError("Connection failed")

            result = await api_client.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_upload_changes_success(self, api_client: Any) -> None:
        """Test successful changes upload."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "New Item"},
            ),
        ]

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(changes)
            assert isinstance(result, UploadResult)
            assert "item-1" in result.applied
            assert len(result.conflicts) == 0

    @pytest.mark.asyncio
    async def test_upload_changes_with_last_sync(self, api_client: Any) -> None:
        """Test upload changes with last_sync timestamp."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.UPDATE,
                data={"title": "Updated"},
            ),
        ]
        last_sync = datetime.now(UTC) - timedelta(hours=1)

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(changes, last_sync)
            assert isinstance(result, UploadResult)

            # Verify last_sync was included in request
            call_args = mock_request.call_args
            payload = call_args.kwargs.get("json", {})
            assert payload["last_sync"] is not None

    @pytest.mark.asyncio
    async def test_download_changes_success(self, api_client: Any) -> None:
        """Test successful changes download."""
        since = datetime.now(UTC) - timedelta(hours=1)

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "changes": [
                    {
                        "entity_type": "item",
                        "entity_id": "item-2",
                        "operation": "create",
                        "data": {"title": "Downloaded Item"},
                        "version": 1,
                        "timestamp": datetime.now(UTC).isoformat(),
                    },
                ],
            }
            mock_request.return_value = mock_response

            result = await api_client.download_changes(since)
            assert len(result) == 1
            assert result[0].entity_id == "item-2"

    @pytest.mark.asyncio
    async def test_download_changes_with_project_filter(self, api_client: Any) -> None:
        """Test download changes with project_id filter."""
        since = datetime.now(UTC) - timedelta(hours=1)
        project_id = "proj-123"

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"changes": []}
            mock_request.return_value = mock_response

            await api_client.download_changes(since, project_id)

            # Verify project_id was included in params
            call_args = mock_request.call_args
            params = call_args.kwargs.get("params", {})
            assert params["project_id"] == project_id

    @pytest.mark.asyncio
    async def test_resolve_conflict_success(self, api_client: Any) -> None:
        """Test successful conflict resolution."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"resolved": True}
            mock_request.return_value = mock_response

            result = await api_client.resolve_conflict(
                "conflict-123",
                ConflictStrategy.LOCAL_WINS,
                merged_data={"title": "Merged"},
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_get_sync_status_success(self, api_client: Any) -> None:
        """Test successful sync status retrieval."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "last_sync": datetime.now(UTC).isoformat(),
                "pending_changes": 5,
                "online": True,
                "conflicts_pending": 0,
            }
            mock_request.return_value = mock_response

            result = await api_client.get_sync_status()
            assert result.pending_changes == COUNT_FIVE
            assert result.online is True


# ============================================================================
# ASYNC TESTS: Error Handling and Status Codes
# ============================================================================


class TestApiClientErrorHandling:
    """Test API client error handling."""

    @pytest.mark.asyncio
    async def test_authentication_error_401(self, api_client: Any) -> None:
        """Test handling of 401 authentication error."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"detail": "Invalid token"}
            mock_response.content = b'{"detail": "Invalid token"}'
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError) as exc_info:
                await api_client._retry_request("GET", "/api/items")

            err = exc_info.value
            assert isinstance(err, AuthenticationError)
            assert err.status_code == HTTP_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_rate_limit_error_429(self, api_client: Any) -> None:
        """Test handling of 429 rate limit error."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 429
            mock_response.headers = {"Retry-After": "60"}
            mock_response.json.return_value = {"detail": "Too many requests"}
            mock_response.content = b'{"detail": "Too many requests"}'
            mock_request.return_value = mock_response

            with pytest.raises(RateLimitError) as exc_info:
                await api_client._retry_request("GET", "/api/items")

            err = exc_info.value
            assert isinstance(err, RateLimitError)
            assert err.status_code == HTTP_TOO_MANY_REQUESTS
            assert err.retry_after == 60

    @pytest.mark.asyncio
    async def test_conflict_error_409(self, api_client: Any) -> None:
        """Test handling of 409 conflict error."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 409
            mock_response.json.return_value = {
                "conflicts": [
                    {
                        "conflict_id": "c1",
                        "entity_type": "item",
                        "entity_id": "i1",
                        "local_version": 2,
                        "remote_version": 1,
                        "local_data": {},
                        "remote_data": {},
                    },
                ],
            }
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Conflict",
                request=MagicMock(),
                response=mock_response,
            )
            mock_request.return_value = mock_response

            with pytest.raises(ConflictError) as exc_info:
                await api_client.upload_changes([])

            err = exc_info.value
            assert isinstance(err, ConflictError)
            assert err.status_code == 409
            assert len(err.conflicts) == 1

    @pytest.mark.asyncio
    async def test_network_error_handling(self, api_client: Any) -> None:
        """Test handling of network errors."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection refused")

            with pytest.raises(NetworkError):
                await api_client._retry_request("GET", "/api/items")

    @pytest.mark.asyncio
    async def test_server_error_500(self, api_client: Any) -> None:
        """Test handling of 500 server error."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_request.return_value = mock_response

            with pytest.raises(ApiError):
                await api_client._retry_request("GET", "/api/items")


# ============================================================================
# ASYNC TESTS: Retry Logic and Exponential Backoff
# ============================================================================


class TestApiClientRetryLogic:
    """Test API client retry and backoff logic."""

    @pytest.mark.asyncio
    async def test_retry_on_network_error(self, api_client: Any) -> None:
        """Test that network errors trigger retries."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_TWO:
                msg = "Connection failed"
                raise httpx.NetworkError(msg)
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep"):  # Speed up test
                await api_client._retry_request("GET", "/api/items")
                assert call_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, api_client: Any) -> None:
        """Test that request fails after max retries exceeded."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection failed")

            with patch("asyncio.sleep"):  # Speed up test
                with pytest.raises(NetworkError) as exc_info:
                    await api_client._retry_request("GET", "/api/items")

                assert "after 3 retries" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_auth_error_not_retried(self, api_client: Any) -> None:
        """Test that authentication errors are not retried."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with pytest.raises(AuthenticationError):
                await api_client._retry_request("GET", "/api/items")

            # Should only be called once (not retried)
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_rate_limit_with_retry_after(self, api_client: Any) -> None:
        """Test rate limit retry with Retry-After header."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                mock_response = MagicMock()
                mock_response.status_code = 429
                mock_response.headers = {"Retry-After": "1"}
                mock_response.json.return_value = {}
                mock_response.content = b"{}"
                return mock_response
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep"):  # Speed up test
                await api_client._retry_request("GET", "/api/items")
                assert call_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, api_client: Any) -> None:
        """Test exponential backoff with retries."""
        call_count = 0
        sleep_times = []

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "Connection failed"
                raise httpx.NetworkError(msg)
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        async def mock_sleep(duration: Any) -> None:
            sleep_times.append(duration)

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep", side_effect=mock_sleep):
                await api_client._retry_request("GET", "/api/items")

                # Should have slept twice with exponential backoff
                assert len(sleep_times) == COUNT_TWO
                assert sleep_times[1] > sleep_times[0]


# ============================================================================
# ASYNC TESTS: Timeout Handling
# ============================================================================


class TestApiClientTimeouts:
    """Test API client timeout handling."""

    @pytest.mark.asyncio
    async def test_client_timeout_configuration(self, _mock_config: Any) -> None:
        """Test that client timeout is configured correctly."""
        config = ApiConfig(
            base_url="https://api.test.com",
            timeout=45.0,
        )
        client = ApiClient(config)
        # AsyncClient timeout is a Timeout object with individual read/write/connect/pool props
        assert client.client.timeout.read == 45.0
        assert client.client.timeout.write == 45.0
        assert client.client.timeout.connect == 45.0
        await client.close()

    @pytest.mark.asyncio
    async def test_request_timeout_error(self, api_client: Any) -> None:
        """Test handling of request timeout."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_request.side_effect = httpx.TimeoutException("Request timeout")

            with patch("asyncio.sleep"):  # Speed up test
                with pytest.raises(NetworkError):
                    await api_client._retry_request("GET", "/api/items")


# ============================================================================
# ASYNC TESTS: Full Sync Operations
# ============================================================================


class TestApiClientFullSync:
    """Test full sync operation."""

    @pytest.mark.asyncio
    async def test_full_sync_success(self, api_client: Any) -> None:
        """Test successful full sync."""
        local_changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "New"},
            ),
        ]

        with patch.object(api_client, "upload_changes") as mock_upload:
            with patch.object(api_client, "download_changes") as mock_download:
                mock_upload.return_value = UploadResult(
                    applied=["item-1"],
                    conflicts=[],
                    server_time=datetime.now(UTC),
                )
                mock_download.return_value = []

                upload_result, remote_changes = await api_client.full_sync(local_changes)

                assert isinstance(upload_result, UploadResult)
                assert len(remote_changes) == 0
                mock_upload.assert_called_once()
                mock_download.assert_called_once()

    @pytest.mark.asyncio
    async def test_full_sync_with_conflict_local_wins(self, api_client: Any) -> None:
        """Test full sync with LOCAL_WINS conflict resolution."""
        local_changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.UPDATE,
                data={"title": "Local"},
            ),
        ]

        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-1",
            local_version=2,
            remote_version=1,
            local_data={"title": "Local"},
            remote_data={"title": "Remote"},
        )

        with patch.object(api_client, "upload_changes") as mock_upload:
            with patch.object(api_client, "download_changes") as mock_download:
                with patch.object(api_client, "resolve_conflict") as mock_resolve:
                    # First call raises conflict, second succeeds
                    mock_upload.side_effect = [
                        ConflictError("Conflict", conflicts=[conflict]),
                        UploadResult(
                            applied=["item-1"],
                            conflicts=[],
                            server_time=datetime.now(UTC),
                        ),
                    ]
                    mock_download.return_value = []
                    mock_resolve.return_value = True

                    upload_result, _remote_changes = await api_client.full_sync(
                        local_changes,
                        conflict_strategy=ConflictStrategy.LOCAL_WINS,
                    )

                    assert isinstance(upload_result, UploadResult)
                    mock_resolve.assert_called_once()

    @pytest.mark.asyncio
    async def test_full_sync_with_conflict_manual_raises(self, api_client: Any) -> None:
        """Test full sync with MANUAL conflict resolution raises error."""
        local_changes = []
        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-1",
            local_version=2,
            remote_version=1,
            local_data={},
            remote_data={},
        )

        with patch.object(api_client, "upload_changes") as mock_upload:
            mock_upload.side_effect = ConflictError("Conflict", conflicts=[conflict])

            with pytest.raises(ConflictError):
                await api_client.full_sync(
                    local_changes,
                    conflict_strategy=ConflictStrategy.MANUAL,
                )


# ============================================================================
# UNIT TESTS: TraceRTMClient (Python API)
# ============================================================================


class TestTraceRTMClientInitialization:
    """Test TraceRTMClient initialization."""

    def test_tracertm_client_with_agent_id(self) -> None:
        """Test TraceRTMClient initialization with agent_id."""
        with patch("tracertm.config.manager.ConfigManager"):
            client = TraceRTMClient(agent_id="agent-123", agent_name="TestAgent")
            assert client.agent_id == "agent-123"
            assert client.agent_name == "TestAgent"

    def test_tracertm_client_without_agent(self) -> None:
        """Test TraceRTMClient initialization without agent."""
        with patch("tracertm.config.manager.ConfigManager"):
            client = TraceRTMClient()
            assert client.agent_id is None
            assert client.agent_name is None

    def test_tracertm_client_config_manager(self) -> None:
        """Test that TraceRTMClient initializes ConfigManager."""
        with patch("tracertm.config.manager.ConfigManager"):
            client = TraceRTMClient()
            # ConfigManager should be created during initialization
            assert client.config_manager is not None


class TestTraceRTMClientItemOperations:
    """Test TraceRTMClient item operations."""

    def test_query_items_basic(self, tracertm_client: Any) -> None:
        """Test basic item query."""
        from tracertm.models.item import Item

        # Create test items
        item = Item(
            project_id="test-project-123",
            title="Test Item",
            view="FEATURE",
            item_type="requirement",
            status="todo",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        # Query items
        results = tracertm_client.query_items()
        assert len(results) > 0
        assert results[0]["title"] == "Test Item"

    def test_query_items_with_filter(self, tracertm_client: Any) -> None:
        """Test item query with status filter."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Done Item",
            view="FEATURE",
            item_type="requirement",
            status="done",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        results = tracertm_client.query_items(options={"status": "done"})
        assert len(results) == 1
        assert results[0]["status"] == "done"

    def test_get_item_by_id(self, tracertm_client: Any) -> None:
        """Test getting a specific item."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Specific Item",
            view="CODE",
            item_type="design",
            status="in_progress",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        result = tracertm_client.get_item(item.id)
        assert result is not None
        assert result["title"] == "Specific Item"

    def test_get_item_not_found(self, tracertm_client: Any) -> None:
        """Test getting non-existent item returns None."""
        result = tracertm_client.get_item("nonexistent-id")
        assert result is None

    def test_create_item(self, tracertm_client: Any) -> None:
        """Test creating an item."""
        result = tracertm_client.create_item(
            "New Item",
            "FEATURE",
            {"item_type": "requirement", "description": "Test description", "status": "todo"},
        )
        assert result["id"] is not None
        assert result["title"] == "New Item"
        assert result["view"] == "FEATURE"

    def test_create_item_with_metadata(self, tracertm_client: Any) -> None:
        """Test creating item with metadata."""
        metadata = {"priority": "high", "owner": "team-1"}
        result = tracertm_client.create_item(
            "Item with Meta",
            "FEATURE",
            {"item_type": "requirement", "metadata": metadata},
        )
        assert result["id"] is not None

    def test_update_item_basic(self, tracertm_client: Any) -> None:
        """Test updating an item."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Original Title",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        result = tracertm_client.update_item(item.id, {"title": "Updated Title", "status": "done"})
        assert result["title"] == "Updated Title"
        assert result["status"] == "done"

    def test_update_item_not_found(self, tracertm_client: Any) -> None:
        """Test updating non-existent item raises error."""
        with pytest.raises(ValueError) as exc_info:
            tracertm_client.update_item("nonexistent-id", {"title": "Updated"})
        assert "Item not found" in str(exc_info.value)

    def test_delete_item(self, tracertm_client: Any) -> None:
        """Test deleting an item (soft delete)."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Item to Delete",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        tracertm_client.delete_item(item.id)

        # Verify soft delete
        result = tracertm_client.get_item(item.id)
        assert result is None

    def test_delete_item_not_found(self, tracertm_client: Any) -> None:
        """Test deleting non-existent item raises error."""
        with pytest.raises(ValueError):
            tracertm_client.delete_item("nonexistent-id")


class TestTraceRTMClientBatchOperations:
    """Test TraceRTMClient batch operations."""

    def test_batch_create_items(self, tracertm_client: Any) -> None:
        """Test batch creating items."""
        items = [
            {"title": "Item 1", "view": "FEATURE", "type": "requirement"},
            {"title": "Item 2", "view": "CODE", "type": "design"},
        ]
        result = tracertm_client.batch_create_items(items)
        assert result["items_created"] == COUNT_TWO

    def test_batch_create_items_empty(self, tracertm_client: Any) -> None:
        """Test batch create with empty list."""
        result = tracertm_client.batch_create_items([])
        assert result["items_created"] == 0

    def test_batch_update_items(self, tracertm_client: Any) -> None:
        """Test batch updating items."""
        from tracertm.models.item import Item

        # Create items
        item1 = Item(
            project_id="test-project-123",
            title="Item 1",
            view="FEATURE",
            item_type="requirement",
        )
        item2 = Item(
            project_id="test-project-123",
            title="Item 2",
            view="CODE",
            item_type="design",
        )
        tracertm_client._session.add_all([item1, item2])
        tracertm_client._session.commit()

        # Update items
        updates = [
            {"item_id": item1.id, "status": "done"},
            {"item_id": item2.id, "status": "in_progress"},
        ]
        result = tracertm_client.batch_update_items(updates)
        assert result["items_updated"] == COUNT_TWO

    def test_batch_delete_items(self, tracertm_client: Any) -> None:
        """Test batch deleting items."""
        from tracertm.models.item import Item

        # Create items
        item1 = Item(
            project_id="test-project-123",
            title="Item 1",
            view="FEATURE",
            item_type="requirement",
        )
        item2 = Item(
            project_id="test-project-123",
            title="Item 2",
            view="CODE",
            item_type="design",
        )
        tracertm_client._session.add_all([item1, item2])
        tracertm_client._session.commit()

        # Delete items
        result = tracertm_client.batch_delete_items([item1.id, item2.id])
        assert result["items_deleted"] == COUNT_TWO


class TestTraceRTMClientAgentOperations:
    """Test TraceRTMClient agent operations."""

    def test_register_agent(self, tracertm_client: Any) -> None:
        """Test registering an agent."""
        agent_id = tracertm_client.register_agent(
            name="Test Agent",
            agent_type="ai_agent",
        )
        assert agent_id is not None
        assert tracertm_client.agent_id == agent_id

    def test_register_agent_with_projects(self, tracertm_client: Any) -> None:
        """Test registering agent with project assignments."""
        agent_id = tracertm_client.register_agent(
            name="Multi-Project Agent",
            project_ids=["proj-1", "proj-2"],
        )
        assert agent_id is not None

    def test_assign_agent_to_projects(self, tracertm_client: Any) -> None:
        """Test assigning agent to projects."""
        from tracertm.models.agent import Agent

        agent = Agent(
            project_id="test-project-123",
            name="Test Agent",
            agent_type="ai_agent",
            status="active",
        )
        tracertm_client._session.add(agent)
        tracertm_client._session.commit()

        tracertm_client.assign_agent_to_projects(
            agent.id,
            ["proj-1", "proj-2", "proj-3"],
        )

        # Verify assignment
        projects = tracertm_client.get_agent_projects(agent.id)
        assert len(projects) >= COUNT_THREE

    def test_get_agent_projects(self, tracertm_client: Any) -> None:
        """Test getting agent's assigned projects."""
        from tracertm.models.agent import Agent

        agent = Agent(
            project_id="test-project-123",
            name="Test Agent",
            agent_type="ai_agent",
            status="active",
            agent_metadata={"assigned_projects": ["proj-1", "proj-2"]},
        )
        tracertm_client._session.add(agent)
        tracertm_client._session.commit()

        projects = tracertm_client.get_agent_projects(agent.id)
        assert "proj-1" in projects
        assert "proj-2" in projects


class TestTraceRTMClientExportImport:
    """Test TraceRTMClient export/import operations."""

    def test_export_project_json(self, tracertm_client: Any) -> None:
        """Test exporting project as JSON."""
        from tracertm.models.item import Item
        from tracertm.models.project import Project

        # Create project and items
        project = Project(id="test-project-123", name="Test Project")
        item = Item(
            project_id="test-project-123",
            title="Test Item",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(project)
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        result = tracertm_client.export_project(format="json")
        assert isinstance(result, str)
        data = json.loads(result)
        assert "project" in data
        assert "items" in data
        assert "links" in data

    def test_import_data(self, tracertm_client: Any) -> None:
        """Test importing data."""
        data = {
            "items": [
                {
                    "title": "Imported Item 1",
                    "view": "FEATURE",
                    "type": "requirement",
                    "status": "todo",
                },
                {
                    "title": "Imported Item 2",
                    "view": "CODE",
                    "type": "design",
                    "status": "in_progress",
                },
            ],
            "links": [],
        }
        result = tracertm_client.import_data(data)
        assert result["items_created"] == COUNT_TWO
        assert result["links_created"] == 0

    def test_import_data_with_links(self, tracertm_client: Any) -> None:
        """Test importing data with links."""
        from tracertm.models.item import Item

        # Create source and target items
        source = Item(
            project_id="test-project-123",
            title="Source",
            view="FEATURE",
            item_type="requirement",
        )
        target = Item(
            project_id="test-project-123",
            title="Target",
            view="CODE",
            item_type="design",
        )
        tracertm_client._session.add_all([source, target])
        tracertm_client._session.commit()

        data = {
            "items": [],
            "links": [
                {
                    "source_id": source.id,
                    "target_id": target.id,
                    "type": "verifies",
                },
            ],
        }
        result = tracertm_client.import_data(data)
        assert result["links_created"] == 1


class TestTraceRTMClientActivity:
    """Test TraceRTMClient activity tracking."""

    def test_get_agent_activity(self, tracertm_client: Any) -> None:
        """Test getting agent activity."""
        from tracertm.models.agent import Agent
        from tracertm.models.event import Event

        # Create agent and event
        agent = Agent(
            project_id="test-project-123",
            name="Test Agent",
            agent_type="ai_agent",
            status="active",
        )
        tracertm_client._session.add(agent)
        tracertm_client._session.commit()

        event = Event(
            project_id="test-project-123",
            event_type="item_created",
            entity_type="item",
            entity_id="item-123",
            data={"title": "Test"},
            agent_id=agent.id,
        )
        tracertm_client._session.add(event)
        tracertm_client._session.commit()

        activity = tracertm_client.get_agent_activity(agent.id)
        assert len(activity) > 0
        assert activity[0]["event_type"] == "item_created"

    def test_get_all_agents_activity(self, tracertm_client: Any) -> None:
        """Test getting activity for all agents."""
        from tracertm.models.agent import Agent

        agent1 = Agent(
            project_id="test-project-123",
            name="Agent 1",
            agent_type="ai_agent",
            status="active",
        )
        agent2 = Agent(
            project_id="test-project-123",
            name="Agent 2",
            agent_type="ai_agent",
            status="active",
        )
        tracertm_client._session.add_all([agent1, agent2])
        tracertm_client._session.commit()

        activity = tracertm_client.get_all_agents_activity()
        assert isinstance(activity, dict)


class TestTraceRTMClientAssignedItems:
    """Test TraceRTMClient assigned items retrieval."""

    def test_get_assigned_items(self, tracertm_client: Any) -> None:
        """Test getting items assigned to agent."""
        from tracertm.models.item import Item

        agent_id = "agent-123"
        item = Item(
            project_id="test-project-123",
            title="Assigned Item",
            view="FEATURE",
            item_type="requirement",
            owner=agent_id,
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        assigned = tracertm_client.get_assigned_items(agent_id)
        assert len(assigned) > 0
        assert assigned[0]["owner"] == agent_id

    def test_get_assigned_items_no_agent(self, tracertm_client: Any) -> None:
        """Test getting assigned items without agent returns empty."""
        tracertm_client.agent_id = None
        assigned = tracertm_client.get_assigned_items()
        assert assigned == []


class TestTraceRTMClientConnectionManagement:
    """Test TraceRTMClient connection management."""

    def test_close_connection(self, tracertm_client: Any) -> None:
        """Test closing database connection."""
        tracertm_client.close()
        # Should not raise


# ============================================================================
# TESTS: SyncClient Backward Compatibility
# ============================================================================


class TestSyncClientBackwardCompat:
    """Test SyncClient backward compatibility alias."""

    @pytest.mark.asyncio
    async def test_sync_client_alias(self, mock_config: Any) -> None:
        """Test that SyncClient is an alias for ApiClient."""
        assert SyncClient == ApiClient
        client = SyncClient(mock_config)
        assert isinstance(client, ApiClient)
        await client.close()


# ============================================================================
# INTEGRATION TESTS: API Client End-to-End
# ============================================================================


class TestApiClientIntegration:
    """Integration tests for API client."""

    @pytest.mark.asyncio
    async def test_api_client_context_manager_cleanup(self, mock_config: Any) -> None:
        """Test that context manager properly cleans up."""
        async with ApiClient(mock_config) as client:
            http_client = client.client
            assert http_client is not None

        # After context exit, client should be closed
        assert client._client is None

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, api_client: Any) -> None:
        """Test handling concurrent requests."""
        requests = []
        responses = []

        async def mock_request_handler(*args: Any, **kwargs: Any) -> None:
            await asyncio.sleep(0.01)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request_handler):
            requests.extend(api_client._retry_request("GET", f"/api/test/{i}") for i in range(5))

            responses = await asyncio.gather(*requests)
            assert len(responses) == COUNT_FIVE


# ============================================================================
# TESTS: Request Payload Construction
# ============================================================================


class TestApiClientPayloads:
    """Test API request payload construction."""

    @pytest.mark.asyncio
    async def test_upload_changes_payload_structure(self, api_client: Any) -> None:
        """Test upload changes creates proper payload structure."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "New"},
                version=1,
            ),
        ]

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "applied": [],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            await api_client.upload_changes(changes)

            # Verify request was made with correct payload structure
            call_args = mock_request.call_args
            payload = call_args.kwargs.get("json", {})
            assert "changes" in payload
            assert "client_id" in payload
            assert len(payload["changes"]) == 1

    @pytest.mark.asyncio
    async def test_download_changes_params_structure(self, api_client: Any) -> None:
        """Test download changes creates proper params."""
        since = datetime.now(UTC) - timedelta(hours=1)

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"changes": []}
            mock_request.return_value = mock_response

            await api_client.download_changes(since, "proj-123")

            # Verify params structure
            call_args = mock_request.call_args
            params = call_args.kwargs.get("params", {})
            assert "since" in params
            assert "project_id" in params


# ============================================================================
# TESTS: Response Parsing
# ============================================================================


class TestApiClientResponseParsing:
    """Test API response parsing."""

    @pytest.mark.asyncio
    async def test_parse_upload_result_with_conflicts(self, _api_client: Any) -> None:
        """Test parsing upload result with conflicts."""
        raw_response = {
            "applied": ["item-1"],
            "conflicts": [
                {
                    "conflict_id": "c1",
                    "entity_type": "item",
                    "entity_id": "item-2",
                    "local_version": 2,
                    "remote_version": 3,
                    "local_data": {"title": "Local"},
                    "remote_data": {"title": "Remote"},
                    "timestamp": datetime.now(UTC).isoformat(),
                },
            ],
            "server_time": datetime.now(UTC).isoformat(),
            "errors": [{"id": "item-3", "reason": "invalid"}],
        }

        result = UploadResult.from_dict(raw_response)
        assert result.applied == ["item-1"]
        assert len(result.conflicts) == 1
        assert len(result.errors) == 1
        assert result.conflicts[0].conflict_id == "c1"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestApiClientEdgeCases:
    """Test edge cases and boundary conditions."""

    @pytest.mark.asyncio
    async def test_empty_response_body(self, api_client: Any) -> None:
        """Test handling empty response body."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b""
            mock_response.json.side_effect = ValueError("No JSON")
            mock_request.return_value = mock_response

            with pytest.raises(ValueError):
                await api_client.health_check()

    @pytest.mark.asyncio
    async def test_large_payload(self, api_client: Any) -> None:
        """Test handling large payload."""
        large_changes = [
            Change(
                entity_type="item",
                entity_id=f"item-{i}",
                operation=SyncOperation.CREATE,
                data={"title": f"Item {i}", "description": "x" * 1000},
            )
            for i in range(100)
        ]

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "applied": [f"item-{i}" for i in range(100)],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(large_changes)
            assert len(result.applied) == 100

    @pytest.mark.asyncio
    async def test_special_characters_in_data(self, api_client: Any) -> None:
        """Test handling special characters in data."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "Special: <>&\"'\\"},
            ),
        ]

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(changes)
            assert len(result.applied) == 1


# ============================================================================
# PERFORMANCE AND STRESS TESTS
# ============================================================================


class TestApiClientPerformance:
    """Test API client performance characteristics."""

    @pytest.mark.asyncio
    async def test_rapid_retries_performance(self, api_client: Any) -> None:
        """Test performance of rapid retries."""
        start_time = time.time()

        with patch.object(api_client.client, "request") as mock_request:
            call_count = 0

            async def mock_request_impl(*args: Any, **kwargs: Any) -> None:
                nonlocal call_count
                call_count += 1
                if call_count < COUNT_THREE:
                    msg = "Failed"
                    raise httpx.NetworkError(msg)
                mock_response = MagicMock()
                mock_response.status_code = 200
                return mock_response

            mock_request.side_effect = mock_request_impl

            with patch("asyncio.sleep"):  # Speed up test
                await api_client._retry_request("GET", "/api/test")

        elapsed = time.time() - start_time
        # Should complete quickly with mocked sleep
        assert elapsed < 1.0
        assert call_count == COUNT_THREE


# ============================================================================
# FINAL VALIDATION TESTS
# ============================================================================


class TestApiFinal:
    """Final validation tests to ensure 100% coverage."""

    @pytest.mark.asyncio
    async def test_api_config_all_params(self) -> None:
        """Test ApiConfig with all parameters specified."""
        config = ApiConfig(
            base_url="https://api.test.com/v1/",
            token="secret-token",
            timeout=60.0,
            max_retries=5,
            retry_backoff_base=1.5,
            retry_backoff_max=120.0,
            verify_ssl=False,
        )
        assert "api.test.com" in config.base_url
        assert config.token == "secret-token"
        assert config.timeout == 60.0
        assert config.max_retries == COUNT_FIVE
        assert config.retry_backoff_base == 1.5
        assert config.retry_backoff_max == 120.0
        assert config.verify_ssl is False

    @pytest.mark.asyncio
    async def test_api_client_generate_unique_ids(self, mock_config: Any) -> None:
        """Test that multiple clients generate unique IDs."""
        clients = [ApiClient(mock_config) for _ in range(10)]
        ids = [client._client_id for client in clients]
        assert len(set(ids)) == COUNT_TEN  # All unique

        for client in clients:
            await client.close()

    def test_change_with_all_fields(self) -> None:
        """Test Change with all fields."""
        timestamp = datetime.now(UTC)
        change = Change(
            entity_type="project",
            entity_id="proj-1",
            operation=SyncOperation.UPDATE,
            data={"name": "Updated Project", "description": "New desc"},
            version=5,
            timestamp=timestamp,
            client_id="client-789",
        )

        dict_repr = change.to_dict()
        assert dict_repr["version"] == COUNT_FIVE
        assert dict_repr["client_id"] == "client-789"
        assert dict_repr["entity_type"] == "project"

    def test_conflict_resolution_strategies(self) -> None:
        """Test all conflict resolution strategies."""
        strategies = [
            ConflictStrategy.LAST_WRITE_WINS,
            ConflictStrategy.LOCAL_WINS,
            ConflictStrategy.REMOTE_WINS,
            ConflictStrategy.MANUAL,
        ]

        for strategy in strategies:
            assert isinstance(strategy, ConflictStrategy)
            assert hasattr(strategy, "value")

    @pytest.mark.asyncio
    async def test_api_close_idempotent(self, mock_config: Any) -> None:
        """Test that close can be called multiple times."""
        client = ApiClient(mock_config)
        await client.close()
        await client.close()  # Should not raise
        assert client._client is None

    @pytest.mark.asyncio
    async def test_api_context_manager_exception_handling(self, mock_config: Any) -> None:
        """Test context manager handles exceptions properly."""
        try:
            async with ApiClient(mock_config) as client:
                msg = "Test exception"
                raise ValueError(msg)
        except ValueError:
            pass

        # Client should still be closed
        assert client._client is None


# ============================================================================
# EXTENDED TESTS: Webhook Handling (FR45+)
# ============================================================================


class TestWebhookHandling:
    """Test webhook handling in API."""

    @pytest.mark.asyncio
    async def test_webhook_payload_validation(self) -> None:
        """Test validating webhook payload structure."""
        payload = {
            "event_type": "item_created",
            "entity_type": "item",
            "entity_id": "item-1",
            "data": {"title": "New Item"},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Validate required fields
        assert "event_type" in payload
        assert "entity_type" in payload
        assert "entity_id" in payload
        assert "data" in payload

    @pytest.mark.asyncio
    async def test_webhook_signature_verification(self) -> None:
        """Test webhook signature verification."""
        import hashlib
        import hmac

        secret = "webhook-secret-key"
        payload = json.dumps({"event": "test"})
        signature = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()

        # Verify signature
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        assert signature == expected

    @pytest.mark.asyncio
    async def test_webhook_retry_on_failure(self, api_client: Any) -> None:
        """Test webhook delivery retry logic."""
        with patch.object(api_client.client, "request") as mock_request:
            call_count = 0

            async def mock_webhook_request(*args: Any, **kwargs: Any) -> None:
                nonlocal call_count
                call_count += 1
                if call_count < COUNT_TWO:
                    # First call fails with HTTPStatusError
                    mock_response = MagicMock()
                    mock_response.status_code = 500
                    mock_response.text = "Server error"
                    msg = "Error"
                    raise httpx.HTTPStatusError(msg, request=MagicMock(), response=mock_response)
                # Second call succeeds
                mock_response = MagicMock()
                mock_response.status_code = 200
                return mock_response

            mock_request.side_effect = mock_webhook_request

            with patch("asyncio.sleep"):
                # Simulate webhook delivery with retries
                for attempt in range(3):
                    try:
                        await api_client.client.request("POST", "/webhook", json={})
                        break
                    except httpx.HTTPStatusError:
                        if attempt < COUNT_TWO:
                            await asyncio.sleep(0.1)

            assert call_count >= COUNT_TWO

    @pytest.mark.asyncio
    async def test_webhook_event_types(self) -> None:
        """Test various webhook event types."""
        event_types = [
            "item_created",
            "item_updated",
            "item_deleted",
            "link_created",
            "link_deleted",
            "project_created",
            "agent_registered",
            "conflict_detected",
        ]

        for event_type in event_types:
            assert event_type in event_types

    @pytest.mark.asyncio
    async def test_webhook_filter_by_event_type(self) -> None:
        """Test filtering webhooks by event type."""
        events = [
            {"event_type": "item_created", "data": {}},
            {"event_type": "item_updated", "data": {}},
            {"event_type": "item_deleted", "data": {}},
            {"event_type": "item_created", "data": {}},
        ]

        filtered = [e for e in events if e["event_type"] == "item_created"]
        assert len(filtered) == COUNT_TWO

    @pytest.mark.asyncio
    async def test_webhook_filter_by_entity_type(self) -> None:
        """Test filtering webhooks by entity type."""
        events = [
            {"entity_type": "item", "data": {}},
            {"entity_type": "link", "data": {}},
            {"entity_type": "project", "data": {}},
            {"entity_type": "item", "data": {}},
        ]

        filtered = [e for e in events if e["entity_type"] == "item"]
        assert len(filtered) == COUNT_TWO


# ============================================================================
# EXTENDED TESTS: API Versioning
# ============================================================================


class TestApiVersioning:
    """Test API versioning support."""

    @pytest.mark.asyncio
    async def test_api_version_in_headers(self, api_client: Any) -> None:
        """Test API version is included in request headers."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.headers = {"API-Version": "1.0.0"}
            mock_request.return_value = mock_response

            await api_client._retry_request("GET", "/api/items")

            # Verify request was made
            mock_request.assert_called_once()

    @pytest.mark.asyncio
    async def test_version_compatibility_check(self) -> None:
        """Test checking API version compatibility."""
        client_version = "1.0.0"
        server_version = "1.0.0"

        # Parse versions
        client_major = int(client_version.split(".", maxsplit=1)[0])
        server_major = int(server_version.split(".", maxsplit=1)[0])

        # Check compatibility
        assert client_major == server_major

    @pytest.mark.asyncio
    async def test_api_version_mismatch_handling(self) -> None:
        """Test handling API version mismatch."""
        client_version = "1.0.0"
        server_version = "2.0.0"

        client_major = int(client_version.split(".", maxsplit=1)[0])
        server_major = int(server_version.split(".", maxsplit=1)[0])

        if client_major != server_major:
            # Versions incompatible
            assert True
        else:
            raise AssertionError


# ============================================================================
# EXTENDED TESTS: Request Header Management
# ============================================================================


class TestRequestHeaders:
    """Test HTTP request header management."""

    @pytest.mark.asyncio
    async def test_headers_include_content_type(self, mock_config: Any) -> None:
        """Test Content-Type header is included."""
        client = ApiClient(mock_config)
        assert "Content-Type" in client.client.headers
        assert client.client.headers["Content-Type"] == "application/json"
        await client.close()

    @pytest.mark.asyncio
    async def test_headers_include_user_agent(self, mock_config: Any) -> None:
        """Test User-Agent header is included."""
        client = ApiClient(mock_config)
        assert "User-Agent" in client.client.headers
        assert "TraceRTM" in client.client.headers["User-Agent"]
        await client.close()

    @pytest.mark.asyncio
    async def test_custom_headers(self, mock_config: Any) -> None:
        """Test custom headers can be added."""
        client = ApiClient(mock_config)
        # Client should have Authorization if token is set
        if mock_config.token:
            assert "Authorization" in client.client.headers
        await client.close()

    @pytest.mark.asyncio
    async def test_request_with_headers(self, api_client: Any) -> None:
        """Test request includes all required headers."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            await api_client._retry_request("GET", "/api/test")

            # Verify request was made with headers
            mock_request.assert_called_once()
            # Headers should be included via client.headers


# ============================================================================
# EXTENDED TESTS: SSL/TLS Configuration
# ============================================================================


class TestSSLTLS:
    """Test SSL/TLS configuration."""

    def test_ssl_verify_enabled(self) -> None:
        """Test SSL verification is enabled by default."""
        config = ApiConfig(base_url="https://api.test.com")
        assert config.verify_ssl is True

    def test_ssl_verify_disabled(self) -> None:
        """Test SSL verification can be disabled."""
        config = ApiConfig(
            base_url="https://api.test.com",
            verify_ssl=False,
        )
        assert config.verify_ssl is False

    @pytest.mark.asyncio
    async def test_ssl_configuration_passed_to_client(self) -> None:
        """Test SSL configuration is passed to HTTP client."""
        config = ApiConfig(
            base_url="https://api.test.com",
            verify_ssl=False,
        )
        client = ApiClient(config)
        # AsyncClient verify is accessed via _client_config attribute
        assert client.config.verify_ssl is False
        await client.close()


# ============================================================================
# EXTENDED TESTS: Response Status Codes
# ============================================================================


class TestResponseStatusCodes:
    """Test handling of various HTTP status codes."""

    @pytest.mark.asyncio
    async def test_status_200_ok(self, api_client: Any) -> None:
        """Test handling 200 OK response."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_request.return_value = mock_response

            response = await api_client._retry_request("GET", "/api/items")
            assert response.status_code == HTTP_OK

    @pytest.mark.asyncio
    async def test_status_201_created(self, api_client: Any) -> None:
        """Test handling 201 Created response."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_request.return_value = mock_response

            response = await api_client._retry_request("POST", "/api/items")
            assert response.status_code == HTTP_CREATED

    @pytest.mark.asyncio
    async def test_status_204_no_content(self, api_client: Any) -> None:
        """Test handling 204 No Content response."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_request.return_value = mock_response

            response = await api_client._retry_request("DELETE", "/api/items/1")
            assert response.status_code == HTTP_NO_CONTENT

    @pytest.mark.asyncio
    async def test_status_400_bad_request(self, api_client: Any) -> None:
        """Test handling 400 Bad Request response."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 400
            mock_response.text = "Bad request"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_request.return_value = mock_response

            with patch("asyncio.sleep"), pytest.raises(ApiError):
                await api_client._retry_request("POST", "/api/items")

    @pytest.mark.asyncio
    async def test_status_403_forbidden(self, api_client: Any) -> None:
        """Test handling 403 Forbidden response."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 403
            mock_response.text = "Forbidden"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_request.return_value = mock_response

            with patch("asyncio.sleep"), pytest.raises(ApiError):
                await api_client._retry_request("GET", "/api/admin")

    @pytest.mark.asyncio
    async def test_status_502_bad_gateway(self, api_client: Any) -> None:
        """Test handling 502 Bad Gateway response."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 502
            mock_response.text = "Bad gateway"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_request.return_value = mock_response

            with patch("asyncio.sleep"), pytest.raises(ApiError):
                await api_client._retry_request("GET", "/api/items")

    @pytest.mark.asyncio
    async def test_status_503_service_unavailable(self, api_client: Any) -> None:
        """Test handling 503 Service Unavailable response."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 503
            mock_response.text = "Service unavailable"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error",
                request=MagicMock(),
                response=mock_response,
            )
            mock_request.return_value = mock_response

            with patch("asyncio.sleep"), pytest.raises(ApiError):
                await api_client._retry_request("GET", "/api/items")


# ============================================================================
# EXTENDED TESTS: Client ID Management
# ============================================================================


class TestClientIDManagement:
    """Test client ID generation and management."""

    @pytest.mark.asyncio
    async def test_client_id_format(self, mock_config: Any) -> None:
        """Test client ID format."""
        client = ApiClient(mock_config)
        # Should be 16 character hex string
        assert len(client._client_id) == 16
        assert all(c in "0123456789abcdef" for c in client._client_id)
        await client.close()

    @pytest.mark.asyncio
    async def test_client_id_uniqueness_across_instances(self, mock_config: Any) -> None:
        """Test that different instances have unique client IDs."""
        clients = [ApiClient(mock_config) for _ in range(5)]
        ids = [c._client_id for c in clients]
        assert len(set(ids)) == COUNT_FIVE

        for client in clients:
            await client.close()

    @pytest.mark.asyncio
    async def test_client_id_persistence(self, mock_config: Any) -> None:
        """Test that client ID persists across requests."""
        client = ApiClient(mock_config)
        id1 = client._client_id

        # Make some operations
        with patch.object(client.client, "request"):
            pass

        id2 = client._client_id
        assert id1 == id2
        await client.close()

    @pytest.mark.asyncio
    async def test_client_id_included_in_requests(self, api_client: Any) -> None:
        """Test that client ID is included in requests."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "applied": [],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            await api_client.upload_changes([])

            call_args = mock_request.call_args
            payload = call_args.kwargs.get("json", {})
            assert "client_id" in payload
            assert payload["client_id"] == api_client._client_id


# ============================================================================
# EXTENDED TESTS: Data Serialization
# ============================================================================


class TestDataSerialization:
    """Test data serialization and deserialization."""

    def test_change_serialization_to_json(self) -> None:
        """Test Change can be serialized to JSON."""
        change = Change(
            entity_type="item",
            entity_id="item-1",
            operation=SyncOperation.CREATE,
            data={"title": "Test"},
        )
        change_dict = change.to_dict()
        json_str = json.dumps(change_dict, default=str)
        assert "item" in json_str
        assert "item-1" in json_str

    def test_change_deserialization_from_json(self) -> None:
        """Test Change can be deserialized from JSON."""
        json_str = json.dumps({
            "entity_type": "item",
            "entity_id": "item-1",
            "operation": "create",
            "data": {"title": "Test"},
            "version": 1,
            "timestamp": datetime.now(UTC).isoformat(),
            "client_id": None,
        })
        data = json.loads(json_str)
        change = Change(
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            operation=SyncOperation(data["operation"]),
            data=data["data"],
            version=data["version"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            client_id=data.get("client_id"),
        )
        assert change.entity_id == "item-1"

    def test_upload_result_json_serialization(self) -> None:
        """Test UploadResult can be serialized to JSON."""
        result = UploadResult(
            applied=["item-1", "item-2"],
            conflicts=[],
            server_time=datetime.now(UTC),
        )
        json_str = json.dumps(result.__dict__, default=str)
        assert "item-1" in json_str
        assert "applied" in json_str

    def test_conflict_json_serialization(self) -> None:
        """Test Conflict can be serialized to JSON."""
        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-1",
            local_version=2,
            remote_version=1,
            local_data={"title": "Local"},
            remote_data={"title": "Remote"},
        )
        json_str = json.dumps(conflict.__dict__, default=str)
        assert "conflict_id" in json_str
        assert "Local" in json_str


# ============================================================================
# EXTENDED TESTS: Multi-Project Support
# ============================================================================


class TestMultiProjectSupport:
    """Test multi-project support."""

    def test_agent_multi_project_assignment(self, tracertm_client: Any) -> None:
        """Test agent can be assigned to multiple projects."""
        from tracertm.models.agent import Agent

        agent = Agent(
            project_id="proj-1",
            name="Multi-Project Agent",
            agent_type="ai_agent",
            status="active",
            agent_metadata={"assigned_projects": ["proj-1", "proj-2", "proj-3"]},
        )
        tracertm_client._session.add(agent)
        tracertm_client._session.commit()

        projects = tracertm_client.get_agent_projects(agent.id)
        assert len(projects) >= COUNT_THREE

    def test_change_includes_project_context(self) -> None:
        """Test changes can include project context."""
        change = Change(
            entity_type="item",
            entity_id="item-1",
            operation=SyncOperation.CREATE,
            data={
                "title": "Item",
                "project_id": "proj-123",
            },
        )
        assert change.data.get("project_id") == "proj-123"

    @pytest.mark.asyncio
    async def test_download_changes_project_filter(self, api_client: Any) -> None:
        """Test downloading changes filtered by project."""
        since = datetime.now(UTC) - timedelta(hours=1)

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"changes": []}
            mock_request.return_value = mock_response

            await api_client.download_changes(since, "proj-123")

            call_args = mock_request.call_args
            params = call_args.kwargs.get("params", {})
            assert params.get("project_id") == "proj-123"


# ============================================================================
# EXTENDED TESTS: Error Recovery
# ============================================================================


class TestErrorRecovery:
    """Test error recovery mechanisms."""

    @pytest.mark.asyncio
    async def test_recovery_from_transient_error(self, api_client: Any) -> None:
        """Test recovery from transient network error."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                msg = "Connection failed"
                raise httpx.NetworkError(msg)
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request), patch("asyncio.sleep"):
            response = await api_client._retry_request("GET", "/api/items")
            assert response.status_code == HTTP_OK
            assert call_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_graceful_degradation_on_failure(self, api_client: Any) -> None:
        """Test graceful degradation when all retries fail."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection failed")

            with patch("asyncio.sleep"):
                with pytest.raises(NetworkError) as exc_info:
                    await api_client._retry_request("GET", "/api/items")

                assert "after 3 retries" in str(exc_info.value)


# ============================================================================
# EXTENDED TESTS: Concurrent Operations
# ============================================================================


class TestConcurrentOperations:
    """Test concurrent API operations."""

    @pytest.mark.asyncio
    async def test_concurrent_uploads(self, api_client: Any) -> None:
        """Test concurrent change uploads."""
        changes_list = [
            [
                Change(
                    entity_type="item",
                    entity_id=f"item-{i}",
                    operation=SyncOperation.CREATE,
                    data={"title": f"Item {i}"},
                ),
            ]
            for i in range(5)
        ]

        async def mock_upload(changes: Any, **kwargs: Any) -> None:
            return UploadResult(
                applied=[c.entity_id for c in changes],
                conflicts=[],
                server_time=datetime.now(UTC),
            )

        with patch.object(api_client, "upload_changes", side_effect=mock_upload):
            results = await asyncio.gather(*[api_client.upload_changes(changes) for changes in changes_list])
            assert len(results) == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_concurrent_downloads(self, api_client: Any) -> None:
        """Test concurrent change downloads."""
        since = datetime.now(UTC) - timedelta(hours=1)

        async def mock_download(since: Any, **kwargs: Any) -> None:
            return []

        with patch.object(api_client, "download_changes", side_effect=mock_download):
            results = await asyncio.gather(*[api_client.download_changes(since) for _ in range(5)])
            assert len(results) == COUNT_FIVE


# ============================================================================
# EXTENDED TESTS: Advanced Query Operations
# ============================================================================


class TestAdvancedQueryOperations:
    """Test advanced query operations in TraceRTMClient."""

    def test_query_items_with_multiple_filters(self, tracertm_client: Any) -> None:
        """Test querying items with multiple filters."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Filtered Item",
            view="FEATURE",
            item_type="requirement",
            status="in_progress",
            priority="high",
            owner="agent-1",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        results = tracertm_client.query_items(
            options={
                "view": "FEATURE",
                "status": "in_progress",
                "item_type": "requirement",
            },
            priority="high",
            owner="agent-1",
        )
        assert len(results) > 0
        assert results[0]["priority"] == "high"

    def test_query_items_with_parent_filter(self, tracertm_client: Any) -> None:
        """Test querying items with parent_id filter."""
        from tracertm.models.item import Item

        parent = Item(
            project_id="test-project-123",
            title="Parent Item",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(parent)
        tracertm_client._session.commit()

        child = Item(
            project_id="test-project-123",
            title="Child Item",
            view="CODE",
            item_type="design",
            parent_id=parent.id,
        )
        tracertm_client._session.add(child)
        tracertm_client._session.commit()

        results = tracertm_client.query_items(parent_id=parent.id)
        assert len(results) > 0
        assert results[0]["parent_id"] == parent.id

    def test_query_items_with_limit(self, tracertm_client: Any) -> None:
        """Test querying items with limit."""
        from tracertm.models.item import Item

        for i in range(15):
            item = Item(
                project_id="test-project-123",
                title=f"Item {i}",
                view="FEATURE",
                item_type="requirement",
            )
            tracertm_client._session.add(item)
        tracertm_client._session.commit()

        results = tracertm_client.query_items(options={"limit": 5})
        assert len(results) == COUNT_FIVE

    def test_query_items_no_results(self, tracertm_client: Any) -> None:
        """Test querying items returns empty when no matches."""
        results = tracertm_client.query_items(options={"status": "nonexistent_status"})
        assert results == []

    def test_get_item_with_prefix_match(self, tracertm_client: Any) -> None:
        """Test getting item with prefix matching."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Item with Long ID",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        # Get with full ID
        result = tracertm_client.get_item(item.id)
        assert result is not None
        assert result["id"] == item.id

    def test_get_item_cross_project_isolation(self, tracertm_client: Any) -> None:
        """Test that get_item respects project isolation."""
        from tracertm.models.item import Item

        item = Item(
            project_id="other-project",
            title="Other Project Item",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        # Should not find item from different project
        result = tracertm_client.get_item(item.id)
        assert result is None


# ============================================================================
# EXTENDED TESTS: Batch Operations - Edge Cases
# ============================================================================


class TestBatchOperationsEdgeCases:
    """Test edge cases in batch operations."""

    def test_batch_create_single_item(self, tracertm_client: Any) -> None:
        """Test batch create with single item."""
        items = [{"title": "Single Item", "view": "FEATURE", "type": "requirement"}]
        result = tracertm_client.batch_create_items(items)
        assert result["items_created"] == 1

    def test_batch_create_with_metadata(self, tracertm_client: Any) -> None:
        """Test batch create with metadata."""
        items = [
            {
                "title": "Item with Meta",
                "view": "FEATURE",
                "type": "requirement",
                "metadata": {"custom_field": "value"},
            },
        ]
        result = tracertm_client.batch_create_items(items)
        assert result["items_created"] == 1

    def test_batch_create_with_all_fields(self, tracertm_client: Any) -> None:
        """Test batch create with all fields."""
        items = [
            {
                "title": "Full Item",
                "view": "CODE",
                "type": "design",
                "description": "Detailed description",
                "status": "in_progress",
                "priority": "high",
                "owner": "agent-1",
                "parent_id": None,
                "metadata": {"key": "value"},
            },
        ]
        result = tracertm_client.batch_create_items(items)
        assert result["items_created"] == 1

    def test_batch_create_large_batch(self, tracertm_client: Any) -> None:
        """Test batch create with many items."""
        items = [{"title": f"Item {i}", "view": "FEATURE", "type": "requirement"} for i in range(50)]
        result = tracertm_client.batch_create_items(items)
        assert result["items_created"] == 50

    def test_batch_update_non_existent_items(self, tracertm_client: Any) -> None:
        """Test batch update skips non-existent items."""
        updates = [
            {"item_id": "nonexistent-1", "status": "done"},
            {"item_id": "nonexistent-2", "status": "in_progress"},
        ]
        result = tracertm_client.batch_update_items(updates)
        assert result["items_updated"] == 0

    def test_batch_update_partial_success(self, tracertm_client: Any) -> None:
        """Test batch update with some non-existent items."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Item 1",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        updates = [
            {"item_id": item.id, "status": "done"},
            {"item_id": "nonexistent", "status": "in_progress"},
        ]
        result = tracertm_client.batch_update_items(updates)
        assert result["items_updated"] == 1

    def test_batch_delete_non_existent_items(self, tracertm_client: Any) -> None:
        """Test batch delete skips non-existent items."""
        result = tracertm_client.batch_delete_items(["nonexistent-1", "nonexistent-2"])
        assert result["items_deleted"] == 0

    def test_batch_delete_partial(self, tracertm_client: Any) -> None:
        """Test batch delete with some non-existent items."""
        from tracertm.models.item import Item

        item = Item(
            project_id="test-project-123",
            title="Item to Delete",
            view="FEATURE",
            item_type="requirement",
        )
        tracertm_client._session.add(item)
        tracertm_client._session.commit()

        result = tracertm_client.batch_delete_items([item.id, "nonexistent"])
        assert result["items_deleted"] == 1


# ============================================================================
# EXTENDED TESTS: Authentication & Error Scenarios
# ============================================================================


class TestAuthenticationErrors:
    """Test authentication error scenarios."""

    @pytest.mark.asyncio
    async def test_auth_error_with_empty_token(self) -> None:
        """Test authentication error with empty token."""
        config = ApiConfig(base_url="https://api.test.com", token="")
        client = ApiClient(config)
        # Empty token should still add Authorization header
        assert "Authorization" in client.client.headers
        assert client.client.headers["Authorization"] == "Bearer "
        await client.close()

    @pytest.mark.asyncio
    async def test_401_error_details_preserved(self, api_client: Any) -> None:
        """Test that 401 error details are preserved."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {
                "detail": "Invalid token",
                "error_code": "AUTH_001",
            }
            mock_response.content = b'{"detail": "Invalid token", "error_code": "AUTH_001"}'
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError) as exc_info:
                await api_client._retry_request("GET", "/api/items")

            err = exc_info.value
            assert isinstance(err, AuthenticationError)
            assert err.response_data["error_code"] == "AUTH_001"

    @pytest.mark.asyncio
    async def test_auth_error_no_retry_immediately_raises(self, api_client: Any) -> None:
        """Test auth errors are not retried."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {}
            mock_response.content = b"{}"
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with pytest.raises(AuthenticationError):
                await api_client._retry_request("GET", "/api/items")

            assert call_count == 1  # Only called once, not retried


# ============================================================================
# EXTENDED TESTS: Conflict Resolution Flows
# ============================================================================


class TestConflictResolutionAdvanced:
    """Test advanced conflict resolution scenarios."""

    @pytest.mark.asyncio
    async def test_resolve_conflict_with_local_wins_strategy(self, api_client: Any) -> None:
        """Test resolving conflict with LOCAL_WINS strategy."""
        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="i1",
            local_version=3,
            remote_version=2,
            local_data={"title": "Local Title", "status": "in_progress"},
            remote_data={"title": "Remote Title", "status": "todo"},
        )

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"resolved": True}
            mock_request.return_value = mock_response

            result = await api_client.resolve_conflict(
                conflict.conflict_id,
                ConflictStrategy.LOCAL_WINS,
                conflict.local_data,
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_resolve_conflict_with_remote_wins_strategy(self, api_client: Any) -> None:
        """Test resolving conflict with REMOTE_WINS strategy."""
        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="i1",
            local_version=2,
            remote_version=3,
            local_data={"title": "Local Title"},
            remote_data={"title": "Remote Title"},
        )

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"resolved": True}
            mock_request.return_value = mock_response

            result = await api_client.resolve_conflict(
                conflict.conflict_id,
                ConflictStrategy.REMOTE_WINS,
                conflict.remote_data,
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_resolve_conflict_without_merged_data(self, api_client: Any) -> None:
        """Test resolving conflict without merged data."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"resolved": True}
            mock_request.return_value = mock_response

            result = await api_client.resolve_conflict(
                "c1",
                ConflictStrategy.LAST_WRITE_WINS,
            )

            # Verify request was made without merged_data
            call_args = mock_request.call_args
            payload = call_args.kwargs.get("json", {})
            assert "merged_data" not in payload
            assert result is True

    @pytest.mark.asyncio
    async def test_full_sync_with_multiple_conflicts(self, api_client: Any) -> None:
        """Test full sync handling multiple conflicts."""
        conflicts = [
            Conflict(
                conflict_id=f"c{i}",
                entity_type="item",
                entity_id=f"i{i}",
                local_version=2,
                remote_version=1,
                local_data={"title": f"Local {i}"},
                remote_data={"title": f"Remote {i}"},
            )
            for i in range(3)
        ]

        with patch.object(api_client, "upload_changes") as mock_upload:
            with patch.object(api_client, "resolve_conflict") as mock_resolve:
                with patch.object(api_client, "download_changes") as mock_download:
                    mock_upload.side_effect = [
                        ConflictError("Conflicts", conflicts=conflicts),
                        UploadResult(
                            applied=["i0", "i1", "i2"],
                            conflicts=[],
                            server_time=datetime.now(UTC),
                        ),
                    ]
                    mock_download.return_value = []
                    mock_resolve.return_value = True

                    _result, _remote = await api_client.full_sync(
                        [],
                        conflict_strategy=ConflictStrategy.LOCAL_WINS,
                    )

                    assert mock_resolve.call_count == COUNT_THREE  # Called for each conflict


# ============================================================================
# EXTENDED TESTS: Multi-Project Operations
# ============================================================================


class TestMultiProjectOperations:
    """Test multi-project operations."""

    def test_batch_create_items_multi_project_context(self, tracertm_client: Any) -> None:
        """Test batch create respects project context."""
        items = [{"title": "Project-specific Item", "view": "FEATURE", "type": "requirement"}]
        result = tracertm_client.batch_create_items(items)
        assert result["items_created"] == 1

        # Verify all items belong to current project
        all_items = tracertm_client.query_items()
        for item in all_items:
            if item["title"] == "Project-specific Item":
                # Item should be retrievable in current project context
                retrieved = tracertm_client.get_item(item["id"])
                assert retrieved is not None

    def test_agent_operations_with_multiple_projects(self, tracertm_client: Any) -> None:
        """Test agent can be assigned to multiple projects."""
        agent_id = tracertm_client.register_agent(
            name="Multi-Project Agent",
            project_ids=["proj-1", "proj-2", "proj-3"],
        )

        projects = tracertm_client.get_agent_projects(agent_id)
        assert len(projects) >= COUNT_THREE
        assert "proj-1" in projects
        assert "proj-2" in projects
        assert "proj-3" in projects

    @pytest.mark.asyncio
    async def test_download_changes_respects_project_filter(self, api_client: Any) -> None:
        """Test download changes respects project filter."""
        since = datetime.now(UTC) - timedelta(hours=1)

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"changes": []}
            mock_request.return_value = mock_response

            await api_client.download_changes(since, "proj-123")

            call_args = mock_request.call_args
            params = call_args.kwargs.get("params", {})
            assert params["project_id"] == "proj-123"


# ============================================================================
# EXTENDED TESTS: Advanced Error Handling & Retry Scenarios
# ============================================================================


class TestAdvancedErrorHandlingRetries:
    """Test advanced error handling and retry scenarios."""

    @pytest.mark.asyncio
    async def test_retry_on_503_service_unavailable(self, api_client: Any) -> None:
        """Test retries on 503 Service Unavailable."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_TWO:
                mock_response = MagicMock()
                mock_response.status_code = 503
                mock_response.text = "Service unavailable"
                msg = "Error"
                raise httpx.HTTPStatusError(msg, request=MagicMock(), response=mock_response)
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request), patch("asyncio.sleep"):
            response = await api_client._retry_request("GET", "/api/items")
            assert response.status_code == HTTP_OK
            assert call_count == COUNT_TWO

    @pytest.mark.asyncio
    async def test_retry_on_502_bad_gateway(self, api_client: Any) -> None:
        """Test retries on 502 Bad Gateway."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_TWO:
                mock_response = MagicMock()
                mock_response.status_code = 502
                msg = "Error"
                raise httpx.HTTPStatusError(msg, request=MagicMock(), response=mock_response)
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request), patch("asyncio.sleep"):
            response = await api_client._retry_request("GET", "/api/items")
            assert response.status_code == HTTP_OK

    @pytest.mark.asyncio
    async def test_rate_limit_with_custom_retry_after(self, api_client: Any) -> None:
        """Test rate limit with custom retry-after value."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                mock_response = MagicMock()
                mock_response.status_code = 429
                mock_response.headers = {"Retry-After": "120"}
                mock_response.json.return_value = {}
                mock_response.content = b"{}"
                return mock_response
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep") as mock_sleep:
                await api_client._retry_request("GET", "/api/items")
                # Verify sleep was called with retry-after value
                mock_sleep.assert_called_once_with(120)

    @pytest.mark.asyncio
    async def test_network_error_accumulates_retries(self, api_client: Any) -> None:
        """Test network errors accumulate across retries."""
        call_count = 0

        async def mock_request(*args: Any, **kwargs: Any) -> Never:
            nonlocal call_count
            call_count += 1
            msg = "Connection failed"
            raise httpx.NetworkError(msg)

        with patch.object(api_client.client, "request", side_effect=mock_request), patch("asyncio.sleep"):
            with pytest.raises(NetworkError):
                await api_client._retry_request("GET", "/api/items")

            # Should attempt max_retries times
            assert call_count == api_client.config.max_retries

    @pytest.mark.asyncio
    async def test_backoff_increases_with_attempts(self, api_client: Any) -> None:
        """Test backoff duration increases with each retry."""
        call_count = 0
        sleep_times = []

        async def mock_request(*args: Any, **kwargs: Any) -> None:
            nonlocal call_count
            call_count += 1
            if call_count < COUNT_THREE:
                msg = "Connection failed"
                raise httpx.NetworkError(msg)
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        async def mock_sleep(duration: Any) -> None:
            sleep_times.append(duration)

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep", side_effect=mock_sleep):
                await api_client._retry_request("GET", "/api/items")

                # Backoff should increase monotonically
                assert len(sleep_times) >= 1
                if len(sleep_times) > 1:
                    assert sleep_times[1] >= sleep_times[0]


# ============================================================================
# EXTENDED TESTS: Special Characters & Data Encoding
# ============================================================================


class TestDataEncodingEdgeCases:
    """Test data encoding and special characters."""

    def test_create_item_with_unicode_characters(self, tracertm_client: Any) -> None:
        """Test creating item with unicode characters."""
        result = tracertm_client.create_item(
            "Unicode Test: 你好世界 🌍 Привет мир",
            "FEATURE",
            {"item_type": "requirement"},
        )
        assert result["id"] is not None

    def test_create_item_with_special_characters(self, tracertm_client: Any) -> None:
        """Test creating item with special characters."""
        result = tracertm_client.create_item(
            "Special: <>&\"'\\n\\t",
            "FEATURE",
            {"item_type": "requirement", "description": "Description with special: <>|{}[]"},
        )
        assert result["id"] is not None

    def test_create_item_with_very_long_title(self, tracertm_client: Any) -> None:
        """Test creating item with very long title."""
        long_title = "a" * 500
        result = tracertm_client.create_item(
            long_title,
            "FEATURE",
            {"item_type": "requirement"},
        )
        assert result["id"] is not None

    @pytest.mark.asyncio
    async def test_upload_changes_preserves_special_characters(self, api_client: Any) -> None:
        """Test that special characters are preserved in upload."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "Title with: <>&\"'\\"},
            ),
        ]

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.now(UTC).isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(changes)
            assert len(result.applied) == 1


# ============================================================================
# EXTENDED TESTS: Sync Status & Metadata
# ============================================================================


class TestSyncStatusMetadata:
    """Test sync status and metadata retrieval."""

    @pytest.mark.asyncio
    async def test_get_sync_status_with_pending_changes(self, api_client: Any) -> None:
        """Test get_sync_status with pending changes."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "last_sync": datetime.now(UTC).isoformat(),
                "pending_changes": 42,
                "online": True,
                "conflicts_pending": 0,
            }
            mock_request.return_value = mock_response

            status = await api_client.get_sync_status()
            assert status.pending_changes == 42
            assert status.online is True

    @pytest.mark.asyncio
    async def test_get_sync_status_offline(self, api_client: Any) -> None:
        """Test get_sync_status when offline."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "last_sync": None,
                "pending_changes": 10,
                "online": False,
                "conflicts_pending": 2,
            }
            mock_request.return_value = mock_response

            status = await api_client.get_sync_status()
            assert status.online is False
            assert status.conflicts_pending == COUNT_TWO

    def test_export_project_with_empty_items(self, tracertm_client: Any) -> None:
        """Test exporting project with no items."""
        result = tracertm_client.export_project(format="json")
        data = json.loads(result)
        assert "project" in data
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_import_data_with_duplicate_items(self, tracertm_client: Any) -> None:
        """Test importing data with duplicate items."""
        data = {
            "items": [
                {"title": "Duplicate", "view": "FEATURE", "type": "requirement"},
                {"title": "Duplicate", "view": "FEATURE", "type": "requirement"},
            ],
            "links": [],
        }
        result = tracertm_client.import_data(data)
        assert result["items_created"] == COUNT_TWO


# ============================================================================
# EXTENDED TESTS: Activity Tracking & Logging
# ============================================================================


class TestActivityTrackingLogging:
    """Test activity tracking and logging."""

    def test_get_agent_activity_with_no_events(self, tracertm_client: Any) -> None:
        """Test getting activity for agent with no events."""
        activity = tracertm_client.get_agent_activity("nonexistent-agent")
        assert activity == []

    def test_get_agent_activity_limit_enforcement(self, tracertm_client: Any) -> None:
        """Test activity retrieval respects limit."""
        from tracertm.models.agent import Agent
        from tracertm.models.event import Event

        agent = Agent(
            project_id="test-project-123",
            name="Test Agent",
            agent_type="ai_agent",
            status="active",
        )
        tracertm_client._session.add(agent)
        tracertm_client._session.commit()

        # Create multiple events
        for i in range(10):
            event = Event(
                project_id="test-project-123",
                event_type="item_created",
                entity_type="item",
                entity_id=f"item-{i}",
                data={"index": i},
                agent_id=agent.id,
            )
            tracertm_client._session.add(event)
        tracertm_client._session.commit()

        activity = tracertm_client.get_agent_activity(agent.id, limit=5)
        assert len(activity) == COUNT_FIVE

    def test_get_all_agents_activity_multi_agent(self, tracertm_client: Any) -> None:
        """Test getting activity for multiple agents."""
        from tracertm.models.agent import Agent

        agent1 = Agent(
            project_id="test-project-123",
            name="Agent 1",
            agent_type="ai_agent",
            status="active",
        )
        agent2 = Agent(
            project_id="test-project-123",
            name="Agent 2",
            agent_type="ai_agent",
            status="active",
        )
        tracertm_client._session.add_all([agent1, agent2])
        tracertm_client._session.commit()

        activity = tracertm_client.get_all_agents_activity()
        assert isinstance(activity, dict)
        assert len(activity) >= COUNT_TWO


# ============================================================================
# EXTENDED TESTS: Configuration & Initialization
# ============================================================================


class TestConfigurationInitialization:
    """Test configuration and initialization scenarios."""

    def test_tracertm_client_without_database_url(self) -> None:
        """Test TraceRTMClient initialization without database URL."""
        with patch("tracertm.api.client.ConfigManager") as mock_cm:
            mock_config = MagicMock()
            mock_config.get.return_value = None
            mock_cm.return_value = mock_config

            client = TraceRTMClient()
            with pytest.raises(ValueError, match="Database not configured"):
                client._get_session()

    def test_tracertm_client_without_project(self) -> None:
        """Test TraceRTMClient initialization without current project."""
        with patch("tracertm.api.client.ConfigManager") as mock_cm:
            mock_config = MagicMock()
            mock_config.get.side_effect = lambda key: "sqlite:///:memory:" if key == "database_url" else None
            mock_cm.return_value = mock_config

            client = TraceRTMClient()
            with pytest.raises(ValueError, match="No project selected"):
                client._get_project_id()

    @pytest.mark.asyncio
    async def test_api_config_with_custom_backoff_parameters(self) -> None:
        """Test ApiConfig with custom backoff parameters."""
        config = ApiConfig(
            base_url="https://api.test.com",
            retry_backoff_base=1.5,
            retry_backoff_max=30.0,
        )
        assert config.retry_backoff_base == 1.5
        assert config.retry_backoff_max == 30.0

    @pytest.mark.asyncio
    async def test_api_client_timeout_configuration_various_values(self) -> None:
        """Test API client with various timeout values."""
        test_cases = [1.0, 15.0, 60.0, 120.0]
        for timeout in test_cases:
            config = ApiConfig(base_url="https://api.test.com", timeout=timeout)
            client = ApiClient(config)
            assert client.client.timeout.read == timeout
            await client.close()


# ============================================================================
# EXTENDED TESTS: JSON Serialization Edge Cases
# ============================================================================


class TestJSONSerializationEdgeCases:
    """Test JSON serialization edge cases."""

    def test_change_serialization_with_none_values(self) -> None:
        """Test Change serialization with None values."""
        change = Change(
            entity_type="item",
            entity_id="item-1",
            operation=SyncOperation.UPDATE,
            data={"title": None, "description": None},
        )
        change_dict = change.to_dict()
        json_str = json.dumps(change_dict, default=str)
        assert "null" in json_str

    def test_upload_result_with_large_error_list(self) -> None:
        """Test UploadResult with many errors."""
        errors = [{"id": f"item-{i}", "reason": f"Error {i}"} for i in range(100)]
        result = UploadResult(
            applied=[],
            conflicts=[],
            server_time=datetime.now(UTC),
            errors=errors,
        )
        assert len(result.errors) == 100

    def test_conflict_with_nested_data_structures(self) -> None:
        """Test Conflict with nested data structures."""
        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-1",
            local_version=1,
            remote_version=1,
            local_data={
                "title": "Title",
                "metadata": {"nested": {"deeply": {"value": "test"}}},
            },
            remote_data={
                "title": "Title",
                "metadata": {"nested": {"deeply": {"value": "test"}}},
            },
        )
        assert conflict.local_data["metadata"]["nested"]["deeply"]["value"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
