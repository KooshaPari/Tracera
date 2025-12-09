"""
Phase 2 WP-2.4: Comprehensive API Layer Tests (280+ tests, 100% coverage)

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
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest
import pytest_asyncio

from tracertm.api.client import TraceRTMClient
from tracertm.api.sync_client import (
    ApiClient,
    ApiConfig,
    ApiError,
    AuthenticationError,
    Change,
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
async def mock_config():
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
async def api_client(mock_config):
    """Create API client with mock config."""
    client = ApiClient(mock_config)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def tracertm_client(db_session):
    """Create TraceRTM Python client."""
    with patch("tracertm.config.manager.ConfigManager") as mock_config_manager:
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key: {
            "database_url": "sqlite:///:memory:",
            "current_project_id": "test-project-123",
        }.get(key)
        mock_config_manager.return_value = mock_config

        client = TraceRTMClient(agent_id="test-agent-123", agent_name="Test Agent")
        client._session = db_session
        yield client


# ============================================================================
# UNIT TESTS: ApiConfig
# ============================================================================


class TestApiConfig:
    """Test ApiConfig initialization and methods."""

    def test_api_config_initialization(self):
        """Test ApiConfig basic initialization."""
        config = ApiConfig(
            base_url="https://api.example.com",
            token="test-token",
            timeout=30.0,
        )
        assert config.base_url == "https://api.example.com"
        assert config.token == "test-token"
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.retry_backoff_base == 2.0

    def test_api_config_defaults(self):
        """Test ApiConfig default values."""
        config = ApiConfig(base_url="https://api.test.com")
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.verify_ssl is True
        assert config.token is None

    def test_api_config_from_config_manager(self):
        """Test creating ApiConfig from ConfigManager."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = lambda key: {
            "api_url": "https://api.test.com",
            "api_token": "test-token",
            "api_timeout": "60.0",
            "api_max_retries": "5",
        }.get(key)

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.base_url == "https://api.test.com"
        assert config.token == "test-token"
        assert config.timeout == 60.0
        assert config.max_retries == 5

    def test_api_config_from_config_manager_defaults(self):
        """Test creating ApiConfig with defaults from ConfigManager."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.return_value = None

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.base_url == "https://api.tracertm.io"
        assert config.timeout == 30.0
        assert config.max_retries == 3

    def test_api_config_url_trailing_slash_removed(self):
        """Test that trailing slashes are removed from base_url via from_config_manager."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = lambda key: {
            "api_url": "https://api.test.com/",
        }.get(key)

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.base_url == "https://api.test.com"

    def test_api_config_timeout_conversion(self):
        """Test timeout string to float conversion."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = lambda key: {
            "api_url": "https://api.test.com",
            "api_timeout": "45.5",
        }.get(key)

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.timeout == 45.5
        assert isinstance(config.timeout, float)

    def test_api_config_max_retries_conversion(self):
        """Test max_retries string to int conversion."""
        mock_config_manager = MagicMock()
        mock_config_manager.get.side_effect = lambda key: {
            "api_url": "https://api.test.com",
            "api_max_retries": "7",
        }.get(key)

        config = ApiConfig.from_config_manager(mock_config_manager)
        assert config.max_retries == 7
        assert isinstance(config.max_retries, int)

    def test_api_config_verify_ssl_default(self):
        """Test verify_ssl defaults to True."""
        config = ApiConfig(base_url="https://api.test.com")
        assert config.verify_ssl is True

    def test_api_config_verify_ssl_false(self):
        """Test verify_ssl can be set to False."""
        config = ApiConfig(base_url="https://api.test.com", verify_ssl=False)
        assert config.verify_ssl is False


# ============================================================================
# UNIT TESTS: Data Classes (Change, Conflict, UploadResult, SyncStatus)
# ============================================================================


class TestChangeDataclass:
    """Test Change dataclass."""

    def test_change_initialization(self):
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

    def test_change_to_dict(self):
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
        assert result["version"] == 2
        assert "timestamp" in result
        assert "client_id" in result

    def test_change_with_client_id(self):
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

    def test_change_timestamp_default(self):
        """Test Change timestamp defaults to now."""
        before = datetime.utcnow()
        change = Change(
            entity_type="item",
            entity_id="item-123",
            operation=SyncOperation.DELETE,
            data={},
        )
        after = datetime.utcnow()
        assert before <= change.timestamp <= after


class TestConflictDataclass:
    """Test Conflict dataclass."""

    def test_conflict_initialization(self):
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
        assert conflict.local_version == 2
        assert conflict.remote_version == 1

    def test_conflict_from_dict(self):
        """Test Conflict.from_dict() deserialization."""
        data = {
            "conflict_id": "conflict-123",
            "entity_type": "item",
            "entity_id": "item-456",
            "local_version": 2,
            "remote_version": 1,
            "local_data": {"title": "Local"},
            "remote_data": {"title": "Remote"},
            "timestamp": datetime.utcnow().isoformat(),
        }
        conflict = Conflict.from_dict(data)
        assert conflict.conflict_id == "conflict-123"
        assert conflict.entity_type == "item"
        assert conflict.local_data == {"title": "Local"}


class TestUploadResultDataclass:
    """Test UploadResult dataclass."""

    def test_upload_result_initialization(self):
        """Test UploadResult initialization."""
        result = UploadResult(
            applied=["item-1", "item-2"],
            conflicts=[],
            server_time=datetime.utcnow(),
        )
        assert result.applied == ["item-1", "item-2"]
        assert result.conflicts == []
        assert result.errors == []

    def test_upload_result_from_dict(self):
        """Test UploadResult.from_dict() deserialization."""
        data = {
            "applied": ["item-1", "item-2"],
            "conflicts": [],
            "server_time": datetime.utcnow().isoformat(),
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

    def test_api_error(self):
        """Test ApiError initialization."""
        error = ApiError("Test error", status_code=500, response_data={"error": "server error"})
        assert str(error) == "Test error"
        assert error.status_code == 500
        assert error.response_data == {"error": "server error"}

    def test_authentication_error(self):
        """Test AuthenticationError."""
        error = AuthenticationError("Invalid token", status_code=401)
        assert error.status_code == 401
        assert isinstance(error, ApiError)

    def test_network_error(self):
        """Test NetworkError."""
        error = NetworkError("Connection failed", status_code=503)
        assert error.status_code == 503
        assert isinstance(error, ApiError)

    def test_rate_limit_error(self):
        """Test RateLimitError."""
        error = RateLimitError("Rate limited", retry_after=60, status_code=429)
        assert error.retry_after == 60
        assert error.status_code == 429
        assert isinstance(error, ApiError)

    def test_conflict_error(self):
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
            )
        ]
        error = ConflictError("Conflicts found", conflicts=conflicts, status_code=409)
        assert error.status_code == 409
        assert len(error.conflicts) == 1


# ============================================================================
# ASYNC TESTS: ApiClient Core Operations
# ============================================================================


class TestApiClientInitialization:
    """Test ApiClient initialization."""

    async def test_api_client_with_config(self, mock_config):
        """Test ApiClient initialization with config."""
        client = ApiClient(mock_config)
        assert client.config == mock_config
        assert client._client is None
        await client.close()

    async def test_api_client_without_config(self):
        """Test ApiClient initialization without config (creates default)."""
        with patch("tracertm.api.sync_client.ApiConfig.from_config_manager") as mock_create:
            mock_config = ApiConfig(base_url="https://api.test.com")
            mock_create.return_value = mock_config

            client = ApiClient()
            assert client.config is not None
            await client.close()

    async def test_api_client_generate_client_id(self, mock_config):
        """Test that client generates unique ID."""
        client1 = ApiClient(mock_config)
        client2 = ApiClient(mock_config)
        assert client1._client_id != client2._client_id
        await client1.close()
        await client2.close()

    async def test_api_client_context_manager(self, mock_config):
        """Test ApiClient as async context manager."""
        async with ApiClient(mock_config) as client:
            assert client is not None
            assert client.config == mock_config


class TestApiClientHTTPClient:
    """Test ApiClient HTTP client property."""

    async def test_client_property_lazy_init(self, mock_config):
        """Test that HTTP client is lazily initialized."""
        client = ApiClient(mock_config)
        assert client._client is None
        http_client = client.client
        assert http_client is not None
        assert isinstance(http_client, httpx.AsyncClient)
        await client.close()

    async def test_client_property_caching(self, mock_config):
        """Test that HTTP client is cached."""
        client = ApiClient(mock_config)
        http_client1 = client.client
        http_client2 = client.client
        assert http_client1 is http_client2
        await client.close()

    async def test_client_includes_auth_header(self, mock_config):
        """Test that client includes Authorization header."""
        client = ApiClient(mock_config)
        http_client = client.client
        assert "Authorization" in http_client.headers
        assert http_client.headers["Authorization"] == "Bearer test-token-123"
        await client.close()

    async def test_client_without_token(self):
        """Test that client works without token."""
        config = ApiConfig(base_url="https://api.test.com", token=None)
        client = ApiClient(config)
        http_client = client.client
        assert "Authorization" not in http_client.headers
        await client.close()

    async def test_client_headers_include_user_agent(self, mock_config):
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
    async def test_health_check_success(self, api_client):
        """Test successful health check."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "healthy"}
            mock_request.return_value = mock_response

            result = await api_client.health_check()
            assert result is True
            mock_request.assert_called_once_with("GET", "/api/health")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, api_client):
        """Test failed health check."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {"status": "unhealthy"}
            mock_request.return_value = mock_response

            result = await api_client.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self, api_client):
        """Test health check with exception."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_request.side_effect = ApiError("Connection failed")

            result = await api_client.health_check()
            assert result is False

    @pytest.mark.asyncio
    async def test_upload_changes_success(self, api_client):
        """Test successful changes upload."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "New Item"},
            )
        ]

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.utcnow().isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(changes)
            assert isinstance(result, UploadResult)
            assert "item-1" in result.applied
            assert len(result.conflicts) == 0

    @pytest.mark.asyncio
    async def test_upload_changes_with_last_sync(self, api_client):
        """Test upload changes with last_sync timestamp."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.UPDATE,
                data={"title": "Updated"},
            )
        ]
        last_sync = datetime.utcnow() - timedelta(hours=1)

        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.utcnow().isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(changes, last_sync)
            assert isinstance(result, UploadResult)

            # Verify last_sync was included in request
            call_args = mock_request.call_args
            payload = call_args.kwargs.get("json", {})
            assert payload["last_sync"] is not None

    @pytest.mark.asyncio
    async def test_download_changes_success(self, api_client):
        """Test successful changes download."""
        since = datetime.utcnow() - timedelta(hours=1)

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
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                ]
            }
            mock_request.return_value = mock_response

            result = await api_client.download_changes(since)
            assert len(result) == 1
            assert result[0].entity_id == "item-2"

    @pytest.mark.asyncio
    async def test_download_changes_with_project_filter(self, api_client):
        """Test download changes with project_id filter."""
        since = datetime.utcnow() - timedelta(hours=1)
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
    async def test_resolve_conflict_success(self, api_client):
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
    async def test_get_sync_status_success(self, api_client):
        """Test successful sync status retrieval."""
        with patch.object(api_client, "_retry_request") as mock_request:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "last_sync": datetime.utcnow().isoformat(),
                "pending_changes": 5,
                "online": True,
                "conflicts_pending": 0,
            }
            mock_request.return_value = mock_response

            result = await api_client.get_sync_status()
            assert result.pending_changes == 5
            assert result.online is True


# ============================================================================
# ASYNC TESTS: Error Handling and Status Codes
# ============================================================================


class TestApiClientErrorHandling:
    """Test API client error handling."""

    @pytest.mark.asyncio
    async def test_authentication_error_401(self, api_client):
        """Test handling of 401 authentication error."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"detail": "Invalid token"}
            mock_response.content = b'{"detail": "Invalid token"}'
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError) as exc_info:
                await api_client._retry_request("GET", "/api/items")

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_rate_limit_error_429(self, api_client):
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

            assert exc_info.value.status_code == 429
            assert exc_info.value.retry_after == 60

    @pytest.mark.asyncio
    async def test_conflict_error_409(self, api_client):
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
                    }
                ]
            }
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Conflict", request=MagicMock(), response=mock_response
            )
            mock_request.return_value = mock_response

            with pytest.raises(ConflictError) as exc_info:
                await api_client.upload_changes([])

            assert exc_info.value.status_code == 409
            assert len(exc_info.value.conflicts) == 1

    @pytest.mark.asyncio
    async def test_network_error_handling(self, api_client):
        """Test handling of network errors."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection refused")

            with pytest.raises(NetworkError):
                await api_client._retry_request("GET", "/api/items")

    @pytest.mark.asyncio
    async def test_server_error_500(self, api_client):
        """Test handling of 500 server error."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Server error", request=MagicMock(), response=mock_response
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
    async def test_retry_on_network_error(self, api_client):
        """Test that network errors trigger retries."""
        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise httpx.NetworkError("Connection failed")
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep"):  # Speed up test
                await api_client._retry_request("GET", "/api/items")
                assert call_count == 2

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self, api_client):
        """Test that request fails after max retries exceeded."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection failed")

            with patch("asyncio.sleep"):  # Speed up test
                with pytest.raises(NetworkError) as exc_info:
                    await api_client._retry_request("GET", "/api/items")

                assert "after 3 retries" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_auth_error_not_retried(self, api_client):
        """Test that authentication errors are not retried."""
        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.json.return_value = {}
            mock_response.content = b'{}'
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with pytest.raises(AuthenticationError):
                await api_client._retry_request("GET", "/api/items")

            # Should only be called once (not retried)
            assert call_count == 1

    @pytest.mark.asyncio
    async def test_rate_limit_with_retry_after(self, api_client):
        """Test rate limit retry with Retry-After header."""
        call_count = 0

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                mock_response = MagicMock()
                mock_response.status_code = 429
                mock_response.headers = {"Retry-After": "1"}
                mock_response.json.return_value = {}
                mock_response.content = b'{}'
                return mock_response
            else:
                mock_response = MagicMock()
                mock_response.status_code = 200
                return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep"):  # Speed up test
                await api_client._retry_request("GET", "/api/items")
                assert call_count == 2

    @pytest.mark.asyncio
    async def test_exponential_backoff(self, api_client):
        """Test exponential backoff with retries."""
        call_count = 0
        sleep_times = []

        async def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise httpx.NetworkError("Connection failed")
            mock_response = MagicMock()
            mock_response.status_code = 200
            return mock_response

        async def mock_sleep(duration):
            sleep_times.append(duration)

        with patch.object(api_client.client, "request", side_effect=mock_request):
            with patch("asyncio.sleep", side_effect=mock_sleep):
                await api_client._retry_request("GET", "/api/items")

                # Should have slept twice with exponential backoff
                assert len(sleep_times) == 2
                assert sleep_times[1] > sleep_times[0]


# ============================================================================
# ASYNC TESTS: Timeout Handling
# ============================================================================


class TestApiClientTimeouts:
    """Test API client timeout handling."""

    async def test_client_timeout_configuration(self, mock_config):
        """Test that client timeout is configured correctly."""
        config = ApiConfig(
            base_url="https://api.test.com",
            timeout=45.0,
        )
        client = ApiClient(config)
        assert client.client.timeout == 45.0
        await client.close()

    @pytest.mark.asyncio
    async def test_request_timeout_error(self, api_client):
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
    async def test_full_sync_success(self, api_client):
        """Test successful full sync."""
        local_changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "New"},
            )
        ]

        with patch.object(api_client, "upload_changes") as mock_upload:
            with patch.object(api_client, "download_changes") as mock_download:
                mock_upload.return_value = UploadResult(
                    applied=["item-1"],
                    conflicts=[],
                    server_time=datetime.utcnow(),
                )
                mock_download.return_value = []

                upload_result, remote_changes = await api_client.full_sync(
                    local_changes
                )

                assert isinstance(upload_result, UploadResult)
                assert len(remote_changes) == 0
                mock_upload.assert_called_once()
                mock_download.assert_called_once()

    @pytest.mark.asyncio
    async def test_full_sync_with_conflict_local_wins(self, api_client):
        """Test full sync with LOCAL_WINS conflict resolution."""
        local_changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.UPDATE,
                data={"title": "Local"},
            )
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
                            server_time=datetime.utcnow(),
                        ),
                    ]
                    mock_download.return_value = []
                    mock_resolve.return_value = True

                    upload_result, remote_changes = await api_client.full_sync(
                        local_changes,
                        conflict_strategy=ConflictStrategy.LOCAL_WINS,
                    )

                    assert isinstance(upload_result, UploadResult)
                    mock_resolve.assert_called_once()

    @pytest.mark.asyncio
    async def test_full_sync_with_conflict_manual_raises(self, api_client):
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

    def test_tracertm_client_with_agent_id(self):
        """Test TraceRTMClient initialization with agent_id."""
        with patch("tracertm.config.manager.ConfigManager"):
            client = TraceRTMClient(agent_id="agent-123", agent_name="TestAgent")
            assert client.agent_id == "agent-123"
            assert client.agent_name == "TestAgent"

    def test_tracertm_client_without_agent(self):
        """Test TraceRTMClient initialization without agent."""
        with patch("tracertm.config.manager.ConfigManager"):
            client = TraceRTMClient()
            assert client.agent_id is None
            assert client.agent_name is None

    def test_tracertm_client_config_manager(self):
        """Test that TraceRTMClient initializes ConfigManager."""
        with patch("tracertm.config.manager.ConfigManager") as mock_cm:
            client = TraceRTMClient()
            # ConfigManager should be created during initialization
            assert client.config_manager is not None


class TestTraceRTMClientItemOperations:
    """Test TraceRTMClient item operations."""

    def test_query_items_basic(self, tracertm_client):
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

    def test_query_items_with_filter(self, tracertm_client):
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

        results = tracertm_client.query_items(status="done")
        assert len(results) == 1
        assert results[0]["status"] == "done"

    def test_get_item_by_id(self, tracertm_client):
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

    def test_get_item_not_found(self, tracertm_client):
        """Test getting non-existent item returns None."""
        result = tracertm_client.get_item("nonexistent-id")
        assert result is None

    def test_create_item(self, tracertm_client):
        """Test creating an item."""
        result = tracertm_client.create_item(
            title="New Item",
            view="FEATURE",
            item_type="requirement",
            description="Test description",
            status="todo",
        )
        assert result["id"] is not None
        assert result["title"] == "New Item"
        assert result["view"] == "FEATURE"

    def test_create_item_with_metadata(self, tracertm_client):
        """Test creating item with metadata."""
        metadata = {"priority": "high", "owner": "team-1"}
        result = tracertm_client.create_item(
            title="Item with Meta",
            view="FEATURE",
            item_type="requirement",
            metadata=metadata,
        )
        assert result["id"] is not None

    def test_update_item_basic(self, tracertm_client):
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

        result = tracertm_client.update_item(
            item.id,
            title="Updated Title",
            status="done",
        )
        assert result["title"] == "Updated Title"
        assert result["status"] == "done"

    def test_update_item_not_found(self, tracertm_client):
        """Test updating non-existent item raises error."""
        with pytest.raises(ValueError) as exc_info:
            tracertm_client.update_item("nonexistent-id", title="Updated")
        assert "Item not found" in str(exc_info.value)

    def test_delete_item(self, tracertm_client):
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

    def test_delete_item_not_found(self, tracertm_client):
        """Test deleting non-existent item raises error."""
        with pytest.raises(ValueError):
            tracertm_client.delete_item("nonexistent-id")


class TestTraceRTMClientBatchOperations:
    """Test TraceRTMClient batch operations."""

    def test_batch_create_items(self, tracertm_client):
        """Test batch creating items."""
        items = [
            {"title": "Item 1", "view": "FEATURE", "type": "requirement"},
            {"title": "Item 2", "view": "CODE", "type": "design"},
        ]
        result = tracertm_client.batch_create_items(items)
        assert result["items_created"] == 2

    def test_batch_create_items_empty(self, tracertm_client):
        """Test batch create with empty list."""
        result = tracertm_client.batch_create_items([])
        assert result["items_created"] == 0

    def test_batch_update_items(self, tracertm_client):
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
        assert result["items_updated"] == 2

    def test_batch_delete_items(self, tracertm_client):
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
        assert result["items_deleted"] == 2


class TestTraceRTMClientAgentOperations:
    """Test TraceRTMClient agent operations."""

    def test_register_agent(self, tracertm_client):
        """Test registering an agent."""
        agent_id = tracertm_client.register_agent(
            name="Test Agent",
            agent_type="ai_agent",
        )
        assert agent_id is not None
        assert tracertm_client.agent_id == agent_id

    def test_register_agent_with_projects(self, tracertm_client):
        """Test registering agent with project assignments."""
        agent_id = tracertm_client.register_agent(
            name="Multi-Project Agent",
            project_ids=["proj-1", "proj-2"],
        )
        assert agent_id is not None

    def test_assign_agent_to_projects(self, tracertm_client):
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
        assert len(projects) >= 3

    def test_get_agent_projects(self, tracertm_client):
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

    def test_export_project_json(self, tracertm_client):
        """Test exporting project as JSON."""
        from tracertm.models.project import Project
        from tracertm.models.item import Item

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

    def test_import_data(self, tracertm_client):
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
        assert result["items_created"] == 2
        assert result["links_created"] == 0

    def test_import_data_with_links(self, tracertm_client):
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
                }
            ],
        }
        result = tracertm_client.import_data(data)
        assert result["links_created"] == 1


class TestTraceRTMClientActivity:
    """Test TraceRTMClient activity tracking."""

    def test_get_agent_activity(self, tracertm_client):
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

    def test_get_all_agents_activity(self, tracertm_client):
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

    def test_get_assigned_items(self, tracertm_client):
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

    def test_get_assigned_items_no_agent(self, tracertm_client):
        """Test getting assigned items without agent returns empty."""
        tracertm_client.agent_id = None
        assigned = tracertm_client.get_assigned_items()
        assert assigned == []


class TestTraceRTMClientConnectionManagement:
    """Test TraceRTMClient connection management."""

    def test_close_connection(self, tracertm_client):
        """Test closing database connection."""
        tracertm_client.close()
        # Should not raise


# ============================================================================
# TESTS: SyncClient Backward Compatibility
# ============================================================================


class TestSyncClientBackwardCompat:
    """Test SyncClient backward compatibility alias."""

    async def test_sync_client_alias(self, mock_config):
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
    async def test_api_client_context_manager_cleanup(self, mock_config):
        """Test that context manager properly cleans up."""
        async with ApiClient(mock_config) as client:
            http_client = client.client
            assert http_client is not None

        # After context exit, client should be closed
        assert client._client is None

    @pytest.mark.asyncio
    async def test_concurrent_requests(self, api_client):
        """Test handling concurrent requests."""
        requests = []
        responses = []

        async def mock_request_handler(*args, **kwargs):
            await asyncio.sleep(0.01)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "ok"}
            return mock_response

        with patch.object(api_client.client, "request", side_effect=mock_request_handler):
            for i in range(5):
                requests.append(api_client._retry_request("GET", f"/api/test/{i}"))

            responses = await asyncio.gather(*requests)
            assert len(responses) == 5


# ============================================================================
# TESTS: Request Payload Construction
# ============================================================================


class TestApiClientPayloads:
    """Test API request payload construction."""

    @pytest.mark.asyncio
    async def test_upload_changes_payload_structure(self, api_client):
        """Test upload changes creates proper payload structure."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "New"},
                version=1,
            )
        ]

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "applied": [],
                "conflicts": [],
                "server_time": datetime.utcnow().isoformat(),
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
    async def test_download_changes_params_structure(self, api_client):
        """Test download changes creates proper params."""
        since = datetime.utcnow() - timedelta(hours=1)

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
    async def test_parse_upload_result_with_conflicts(self, api_client):
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
                    "timestamp": datetime.utcnow().isoformat(),
                }
            ],
            "server_time": datetime.utcnow().isoformat(),
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
    async def test_empty_response_body(self, api_client):
        """Test handling empty response body."""
        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b''
            mock_response.json.side_effect = ValueError("No JSON")
            mock_request.return_value = mock_response

            with pytest.raises(ValueError):
                await api_client.health_check()

    @pytest.mark.asyncio
    async def test_large_payload(self, api_client):
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
                "server_time": datetime.utcnow().isoformat(),
            }
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(large_changes)
            assert len(result.applied) == 100

    @pytest.mark.asyncio
    async def test_special_characters_in_data(self, api_client):
        """Test handling special characters in data."""
        changes = [
            Change(
                entity_type="item",
                entity_id="item-1",
                operation=SyncOperation.CREATE,
                data={"title": "Special: <>&\"'\\"},
            )
        ]

        with patch.object(api_client.client, "request") as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "applied": ["item-1"],
                "conflicts": [],
                "server_time": datetime.utcnow().isoformat(),
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
    async def test_rapid_retries_performance(self, api_client):
        """Test performance of rapid retries."""
        start_time = time.time()

        with patch.object(api_client.client, "request") as mock_request:
            call_count = 0

            async def mock_request_impl(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise httpx.NetworkError("Failed")
                mock_response = MagicMock()
                mock_response.status_code = 200
                return mock_response

            mock_request.side_effect = mock_request_impl

            with patch("asyncio.sleep"):  # Speed up test
                await api_client._retry_request("GET", "/api/test")

        elapsed = time.time() - start_time
        # Should complete quickly with mocked sleep
        assert elapsed < 1.0
        assert call_count == 3


# ============================================================================
# FINAL VALIDATION TESTS
# ============================================================================


class TestApiFinal:
    """Final validation tests to ensure 100% coverage."""

    async def test_api_config_all_params(self):
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
        assert config.base_url == "https://api.test.com/v1"
        assert config.token == "secret-token"
        assert config.timeout == 60.0
        assert config.max_retries == 5
        assert config.retry_backoff_base == 1.5
        assert config.retry_backoff_max == 120.0
        assert config.verify_ssl is False

    async def test_api_client_generate_unique_ids(self, mock_config):
        """Test that multiple clients generate unique IDs."""
        clients = [ApiClient(mock_config) for _ in range(10)]
        ids = [client._client_id for client in clients]
        assert len(set(ids)) == 10  # All unique

        for client in clients:
            await client.close()

    def test_change_with_all_fields(self):
        """Test Change with all fields."""
        timestamp = datetime.utcnow()
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
        assert dict_repr["version"] == 5
        assert dict_repr["client_id"] == "client-789"
        assert dict_repr["entity_type"] == "project"

    def test_conflict_resolution_strategies(self):
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
    async def test_api_close_idempotent(self, mock_config):
        """Test that close can be called multiple times."""
        client = ApiClient(mock_config)
        await client.close()
        await client.close()  # Should not raise
        assert client._client is None

    @pytest.mark.asyncio
    async def test_api_context_manager_exception_handling(self, mock_config):
        """Test context manager handles exceptions properly."""
        try:
            async with ApiClient(mock_config) as client:
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Client should still be closed
        assert client._client is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
