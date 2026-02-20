"""Unit tests for TraceRTM sync API client."""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

from tests.test_constants import COUNT_FIVE, COUNT_TEN, COUNT_THREE, COUNT_TWO, HTTP_UNAUTHORIZED
from tracertm.api import (
    ApiClient,
    ApiConfig,
    ApiError,
    AuthenticationError,
    Change,
    Conflict,
    ConflictError,
    NetworkError,
    SyncOperation,
    SyncStatus,
    UploadResult,
)

# Configure pytest-asyncio


@pytest.fixture
def api_config() -> ApiConfig:
    """Create test API configuration."""
    return ApiConfig(
        base_url="https://test.api.com",
        token="test-token",
        timeout=5.0,
        max_retries=3,
    )


@pytest.fixture
def api_client(api_config: ApiConfig) -> ApiClient:
    """Create test API client."""
    return ApiClient(api_config)


@pytest.fixture
def sample_changes() -> list[Change]:
    """Create sample changes for testing."""
    return [
        Change(
            entity_type="item",
            entity_id="item-001",
            operation=SyncOperation.CREATE,
            data={"title": "Test Item", "status": "todo"},
            version=1,
        ),
        Change(
            entity_type="item",
            entity_id="item-002",
            operation=SyncOperation.UPDATE,
            data={"title": "Updated Item", "status": "in_progress"},
            version=2,
        ),
    ]


class TestApiConfig:
    """Tests for ApiConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = ApiConfig(base_url="https://api.example.com")

        assert config.base_url == "https://api.example.com"
        assert config.token is None
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_THREE
        assert config.verify_ssl is True

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = ApiConfig(
            base_url="http://localhost:8000",
            token="test-token",
            timeout=10.0,
            max_retries=5,
            verify_ssl=False,
        )

        assert config.base_url == "http://localhost:8000"
        assert config.token == "test-token"
        assert config.timeout == float(COUNT_TEN + 0.0)
        assert config.max_retries == COUNT_FIVE
        assert config.verify_ssl is False

    @patch("tracertm.api.sync_client.ConfigManager")
    def test_from_config_manager(self, mock_config_manager: Mock) -> None:
        """Test creating ApiConfig from ConfigManager."""
        mock_manager = Mock()
        mock_manager.get.side_effect = lambda key, default=None: {
            "api_url": "https://custom.api.com",
            "api_token": "custom-token",
            "api_timeout": "15.0",
            "api_max_retries": "5",
        }.get(key, default)

        mock_config_manager.return_value = mock_manager

        config = ApiConfig.from_config_manager()

        assert config.base_url == "https://custom.api.com"
        assert config.token == "custom-token"
        assert config.timeout == 15.0
        assert config.max_retries == COUNT_FIVE


class TestChange:
    """Tests for Change data class."""

    def test_change_creation(self) -> None:
        """Test creating a Change object."""
        change = Change(
            entity_type="item",
            entity_id="item-001",
            operation=SyncOperation.CREATE,
            data={"title": "Test"},
            version=1,
        )

        assert change.entity_type == "item"
        assert change.entity_id == "item-001"
        assert change.operation == SyncOperation.CREATE
        assert change.data == {"title": "Test"}
        assert change.version == 1

    def test_change_to_dict(self) -> None:
        """Test converting Change to dictionary."""
        timestamp = datetime.now(UTC)
        change = Change(
            entity_type="item",
            entity_id="item-001",
            operation=SyncOperation.UPDATE,
            data={"title": "Test"},
            version=2,
            timestamp=timestamp,
            client_id="client-123",
        )

        result = change.to_dict()

        assert result["entity_type"] == "item"
        assert result["entity_id"] == "item-001"
        assert result["operation"] == "update"
        assert result["data"] == {"title": "Test"}
        assert result["version"] == COUNT_TWO
        assert result["timestamp"] == timestamp.isoformat()
        assert result["client_id"] == "client-123"


class TestConflict:
    """Tests for Conflict data class."""

    def test_conflict_from_dict(self) -> None:
        """Test creating Conflict from dictionary."""
        data = {
            "conflict_id": "conflict-001",
            "entity_type": "item",
            "entity_id": "item-001",
            "local_version": 5,
            "remote_version": 6,
            "local_data": {"title": "Local"},
            "remote_data": {"title": "Remote"},
            "timestamp": "2024-01-01T12:00:00",
        }

        conflict = Conflict.from_dict(data)

        assert conflict.conflict_id == "conflict-001"
        assert conflict.entity_type == "item"
        assert conflict.entity_id == "item-001"
        assert conflict.local_version == COUNT_FIVE
        assert conflict.remote_version == 6
        assert conflict.local_data == {"title": "Local"}
        assert conflict.remote_data == {"title": "Remote"}


class TestUploadResult:
    """Tests for UploadResult data class."""

    def test_upload_result_from_dict(self) -> None:
        """Test creating UploadResult from dictionary."""
        data = {
            "applied": ["item-001", "item-002"],
            "conflicts": [
                {
                    "conflict_id": "conflict-001",
                    "entity_type": "item",
                    "entity_id": "item-003",
                    "local_version": 5,
                    "remote_version": 6,
                    "local_data": {},
                    "remote_data": {},
                },
            ],
            "server_time": "2024-01-01T12:00:00",
            "errors": [{"entity_id": "item-004", "error": "Invalid data"}],
        }

        result = UploadResult.from_dict(data)

        assert result.applied == ["item-001", "item-002"]
        assert len(result.conflicts) == 1
        assert result.conflicts[0].conflict_id == "conflict-001"
        assert len(result.errors) == 1


class TestSyncStatus:
    """Tests for SyncStatus data class."""

    def test_sync_status_from_dict(self) -> None:
        """Test creating SyncStatus from dictionary."""
        data = {
            "last_sync": "2024-01-01T12:00:00",
            "pending_changes": 5,
            "online": True,
            "server_time": "2024-01-01T12:30:00",
            "conflicts_pending": 2,
        }

        status = SyncStatus.from_dict(data)

        assert status.last_sync == datetime.fromisoformat("2024-01-01T12:00:00")
        assert status.pending_changes == COUNT_FIVE
        assert status.online is True
        assert status.server_time == datetime.fromisoformat("2024-01-01T12:30:00")
        assert status.conflicts_pending == COUNT_TWO


class TestApiClient:
    """Tests for ApiClient."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, api_client: ApiClient) -> None:
        """Test API client initialization."""
        assert api_client.config.base_url == "https://test.api.com"
        assert api_client.config.token == "test-token"
        assert api_client._client_id is not None

    @pytest.mark.asyncio
    async def test_client_property_creates_httpx_client(self, api_client: ApiClient) -> None:
        """Test that client property creates httpx client."""
        client = api_client.client

        assert isinstance(client, httpx.AsyncClient)
        assert client.base_url == "https://test.api.com"
        assert "Authorization" in client.headers
        assert client.headers["Authorization"] == "Bearer test-token"

    @pytest.mark.asyncio
    async def test_context_manager(self, api_config: ApiConfig) -> None:
        """Test async context manager."""
        async with ApiClient(api_config) as client:
            # Access client property to trigger lazy initialization
            _ = client.client
            assert client._client is not None

        # Client should be closed after context exit
        assert client._client is None

    @pytest.mark.asyncio
    async def test_health_check_success(self, api_client: ApiClient) -> None:
        """Test successful health check."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}

        with patch.object(api_client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await api_client.health_check()

            assert result is True
            mock_request.assert_called_once_with("GET", "/api/health")

    @pytest.mark.asyncio
    async def test_health_check_failure(self, api_client: ApiClient) -> None:
        """Test health check failure."""
        with patch.object(api_client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = NetworkError("Connection failed")

            result = await api_client.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_upload_changes_success(self, api_client: ApiClient, sample_changes: list[Change]) -> None:
        """Test successful upload of changes."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "applied": ["item-001", "item-002"],
            "conflicts": [],
            "server_time": "2024-01-01T12:00:00",
            "errors": [],
        }

        with patch.object(api_client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await api_client.upload_changes(sample_changes)

            assert isinstance(result, UploadResult)
            assert len(result.applied) == COUNT_TWO
            assert len(result.conflicts) == 0

    @pytest.mark.asyncio
    async def test_upload_changes_with_conflict(self, api_client: ApiClient, sample_changes: list[Change]) -> None:
        """Test upload with conflict detection."""
        mock_response = Mock(status_code=409)
        mock_response.json.return_value = {
            "conflicts": [
                {
                    "conflict_id": "conflict-001",
                    "entity_type": "item",
                    "entity_id": "item-001",
                    "local_version": 1,
                    "remote_version": 2,
                    "local_data": {},
                    "remote_data": {},
                },
            ],
        }

        error = httpx.HTTPStatusError("Conflict", request=Mock(), response=mock_response)

        with patch.object(api_client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = error

            with pytest.raises(ConflictError) as exc_info:
                await api_client.upload_changes(sample_changes)

            assert len(exc_info.value.conflicts) == 1
            assert exc_info.value.conflicts[0].conflict_id == "conflict-001"

    @pytest.mark.asyncio
    async def test_download_changes_success(self, api_client: ApiClient) -> None:
        """Test successful download of changes."""
        since = datetime.now(UTC) - timedelta(hours=1)

        mock_response = Mock()
        mock_response.json.return_value = {
            "changes": [
                {
                    "entity_type": "item",
                    "entity_id": "item-001",
                    "operation": "create",
                    "data": {"title": "Remote Item"},
                    "version": 1,
                    "timestamp": since.isoformat(),
                },
            ],
        }

        with patch.object(api_client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            changes = await api_client.download_changes(since)

            assert len(changes) == 1
            assert changes[0].entity_id == "item-001"
            assert changes[0].operation == SyncOperation.CREATE

    @pytest.mark.asyncio
    async def test_resolve_conflict_success(self, api_client: ApiClient) -> None:
        """Test successful conflict resolution."""
        from tracertm.api import ConflictStrategy

        mock_response = Mock()
        mock_response.json.return_value = {"resolved": True}

        with patch.object(api_client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await api_client.resolve_conflict(
                "conflict-001",
                ConflictStrategy.LOCAL_WINS,
                {"title": "Local Version"},
            )

            assert result is True

    @pytest.mark.asyncio
    async def test_get_sync_status_success(self, api_client: ApiClient) -> None:
        """Test getting sync status."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "last_sync": "2024-01-01T12:00:00",
            "pending_changes": 10,
            "online": True,
            "server_time": "2024-01-01T13:00:00",
            "conflicts_pending": 0,
        }

        with patch.object(api_client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            status = await api_client.get_sync_status()

            assert isinstance(status, SyncStatus)
            assert status.pending_changes == COUNT_TEN
            assert status.online is True
            assert status.conflicts_pending == 0

    @pytest.mark.asyncio
    async def test_retry_on_network_error(self, api_client: ApiClient) -> None:
        """Test retry logic on network errors."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}

        with patch.object(api_client.client, "request", new_callable=AsyncMock) as mock_request:
            # Fail twice, then succeed
            mock_request.side_effect = [
                httpx.NetworkError("Connection failed"),
                httpx.NetworkError("Connection failed"),
                mock_response,
            ]

            result = await api_client._retry_request("GET", "/api/health")

            assert result == mock_response
            assert mock_request.call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_retry_exhausted(self, api_client: ApiClient) -> None:
        """Test behavior when all retries are exhausted."""
        with patch.object(api_client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.NetworkError("Connection failed")

            with pytest.raises(NetworkError) as exc_info:
                await api_client._retry_request("GET", "/api/health")

            assert "after 3 retries" in str(exc_info.value)
            assert mock_request.call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_authentication_error_no_retry(self, api_client: ApiClient) -> None:
        """Test that authentication errors are not retried."""
        mock_response = Mock(status_code=401, content=b'{"error": "Unauthorized"}')
        mock_response.json.return_value = {"error": "Unauthorized"}

        with patch.object(api_client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError) as exc_info:
                await api_client._retry_request("GET", "/api/test")

            assert exc_info.value.status_code == HTTP_UNAUTHORIZED
            # Should only attempt once, no retries for auth errors
            assert mock_request.call_count == 1

    @pytest.mark.asyncio
    async def test_rate_limit_error(self, api_client: ApiClient) -> None:
        """Test handling of rate limit errors with mocked sleep to avoid timeout."""
        mock_response = Mock(status_code=429)
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": "Rate limited"}
        mock_response.content = b'{"error": "Rate limited"}'

        # Access client property first to initialize the httpx client
        client = api_client.client

        # Mock asyncio.sleep to avoid actual delays during retry
        with (
            patch("tracertm.api.sync_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep,
            patch.object(client, "request", new_callable=AsyncMock) as mock_request,
        ):
            # Always return 429 response - will retry 3 times then give up
            # Since RateLimitError continues (doesn't set last_error),
            # after exhausting retries it raises ApiError
            mock_request.return_value = mock_response

            # After max retries with persistent rate limiting, raises ApiError
            with pytest.raises(ApiError):
                await api_client._retry_request("GET", "/api/test")

            # Should have attempted the request max_retries times
            assert mock_request.call_count == api_client.config.max_retries

            # Verify sleep was called (but didn't actually wait due to mock)
            assert mock_sleep.called, "asyncio.sleep should have been called during retry backoff"


class TestFullSync:
    """Tests for full bidirectional sync."""

    @pytest.mark.asyncio
    async def test_full_sync_success(self, api_client: ApiClient, sample_changes: list[Change]) -> None:
        """Test successful full sync."""
        from tracertm.api import ConflictStrategy

        upload_response = {
            "applied": ["item-001", "item-002"],
            "conflicts": [],
            "server_time": "2024-01-01T12:00:00",
            "errors": [],
        }

        remote_changes_payload = [
            Change(
                entity_type="item",
                entity_id="item-003",
                operation=SyncOperation.UPDATE,
                data={"title": "Remote Update"},
                version=2,
            ),
        ]

        with (
            patch.object(api_client, "upload_changes", new_callable=AsyncMock) as mock_upload,
            patch.object(api_client, "download_changes", new_callable=AsyncMock) as mock_download,
        ):
            mock_upload.return_value = UploadResult.from_dict(upload_response)
            mock_download.return_value = remote_changes_payload

            upload_result, remote_changes = await api_client.full_sync(
                local_changes=sample_changes,
                conflict_strategy=ConflictStrategy.LAST_WRITE_WINS,
            )

            assert len(upload_result.applied) == COUNT_TWO
            assert len(remote_changes) == 1
            assert remote_changes[0].entity_id == "item-003"
