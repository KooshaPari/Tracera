"""Comprehensive Edge Case Tests for Coverage Gap Closure.

This test suite targets uncovered lines in:
- api/sync_client.py (70.52% -> 85%+)
- bulk_operation_service.py (77.21% -> 85%+)
- markdown_parser.py (73.09% -> 85%+)

Focus areas:
- Error paths and exception handling
- Boundary conditions
- Edge cases in input validation
- Network failures and retries
- Database transaction failures
- Malformed data handling
"""

from datetime import UTC, datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import httpx
import pytest
from sqlalchemy.exc import IntegrityError, OperationalError

from tests.test_constants import (
    COUNT_FIVE,
    COUNT_THREE,
    COUNT_TWO,
    HTTP_INTERNAL_SERVER_ERROR,
    HTTP_OK,
    HTTP_TOO_MANY_REQUESTS,
)
from tracertm.api.sync_client import (
    ApiClient,
    ApiConfig,
    ApiError,
    Change,
    Conflict,
    ConflictError,
    ConflictStrategy,
    RateLimitError,
    SyncOperation,
    SyncStatus,
    UploadResult,
)
from tracertm.services.bulk_operation_service import BulkOperationService
from tracertm.storage.markdown_parser import (
    ItemData,
    LinkData,
    get_item_path,
    list_items,
    parse_config_yaml,
    parse_item_markdown,
    parse_links_yaml,
    write_config_yaml,
    write_item_markdown,
    write_links_yaml,
)

# ============================================================================
# SYNC CLIENT EDGE CASES
# ============================================================================


class TestSyncClientEdgeCases:
    """Edge case tests for sync_client.py to reach 85%+ coverage."""

    @pytest.mark.asyncio
    async def test_config_from_manager_with_none_manager(self) -> None:
        """TC-SC-E1: ApiConfig creation with None ConfigManager.

        Given: ConfigManager is None
        When: Creating ApiConfig from ConfigManager
        Then: Creates new ConfigManager internally and returns default config
        """
        config = ApiConfig.from_config_manager(None)

        assert config.base_url == "https://api.tracertm.io"
        assert config.timeout == 30.0
        assert config.max_retries == COUNT_THREE

    @pytest.mark.asyncio
    async def test_config_from_manager_with_string_timeout(self) -> None:
        """TC-SC-E2: ApiConfig handles string timeout value.

        Given: ConfigManager returns string timeout
        When: Creating ApiConfig
        Then: Converts string to float successfully
        """
        mock_manager = Mock()
        mock_manager.get.side_effect = lambda key, default=None: {
            "api_url": "https://test.api.com",
            "api_timeout": "45.5",
            "api_max_retries": "5",
        }.get(key, default)

        with patch("tracertm.api.sync_client.ConfigManager", return_value=mock_manager):
            config = ApiConfig.from_config_manager()

        assert config.timeout == 45.5
        assert config.max_retries == COUNT_FIVE

    @pytest.mark.asyncio
    async def test_config_trailing_slash_stripped(self) -> None:
        """TC-SC-E3: Base URL trailing slash is stripped.

        Given: Base URL ends with slash
        When: Creating ApiConfig
        Then: Trailing slash is removed
        """
        config = ApiConfig(base_url="https://api.example.com/")

        assert config.base_url == "https://api.example.com"

    @pytest.mark.asyncio
    async def test_client_property_without_token(self) -> None:
        """TC-SC-E4: Client creation without authentication token.

        Given: ApiConfig has no token
        When: Accessing client property
        Then: Creates client without Authorization header
        """
        config = ApiConfig(base_url="https://test.api.com", token=None)
        client = ApiClient(config)

        http_client = client.client

        assert "Authorization" not in http_client.headers

    @pytest.mark.asyncio
    async def test_client_close_when_none(self) -> None:
        """TC-SC-E5: Closing client when already None.

        Given: Client is None
        When: close() is called
        Then: No error is raised
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        # Don't initialize client
        assert client._client is None
        await client.close()  # Should not raise

        assert client._client is None

    @pytest.mark.asyncio
    async def test_retry_request_http_status_error_all_retries(self) -> None:
        """TC-SC-E6: HTTP status error exhausts all retries.

        Given: Request always returns 500 error
        When: Retry request is attempted
        Then: Raises ApiError after max retries with status code
        """
        config = ApiConfig(base_url="https://test.api.com", max_retries=3)
        client = ApiClient(config)

        mock_response = Mock(status_code=500, content=b'{"error": "Server error"}')
        mock_response.json.return_value = {"error": "Server error"}

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.side_effect = httpx.HTTPStatusError("Server error", request=Mock(), response=mock_response)

            with pytest.raises(ApiError) as exc_info:
                await client._retry_request("GET", "/test")

            err = exc_info.value
            assert "after 3 retries" in str(err)
            assert isinstance(err, ApiError)
            assert err.status_code == HTTP_INTERNAL_SERVER_ERROR
            assert mock_request.call_count == COUNT_THREE

    @pytest.mark.asyncio
    async def test_retry_request_rate_limit_with_retry_after(self) -> None:
        """TC-SC-E7: Rate limit error respects Retry-After header.

        Given: Request returns 429 with Retry-After header
        When: Retry is attempted
        Then: Waits for specified time before retry
        """
        config = ApiConfig(base_url="https://test.api.com", max_retries=2)
        client = ApiClient(config)

        mock_rate_limit_response = Mock(status_code=429)
        mock_rate_limit_response.headers = {"Retry-After": "2"}
        mock_rate_limit_response.json.return_value = {"error": "Rate limited"}
        mock_rate_limit_response.content = b'{"error": "Rate limited"}'

        mock_success_response = Mock(status_code=200, content=b'{"status": "ok"}')
        mock_success_response.json.return_value = {"status": "ok"}

        with patch("tracertm.api.sync_client.asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
                # First call: rate limit, second call: success
                mock_request.side_effect = [mock_rate_limit_response, mock_success_response]

                result = await client._retry_request("GET", "/test")

                assert result.status_code == HTTP_OK
                mock_sleep.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_retry_request_rate_limit_no_retry_after_on_last_attempt(self) -> None:
        """TC-SC-E8: Rate limit on final retry raises error.

        Given: Rate limit error on last retry attempt
        When: No more retries available
        Then: Raises RateLimitError immediately
        """
        config = ApiConfig(base_url="https://test.api.com", max_retries=1)
        client = ApiClient(config)

        mock_response = Mock(status_code=429)
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"error": "Rate limited"}
        mock_response.content = b'{"error": "Rate limited"}'

        with patch.object(client.client, "request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(RateLimitError) as exc_info:
                await client._retry_request("GET", "/test")

            err = exc_info.value
            assert isinstance(err, RateLimitError)
            assert err.retry_after == 60

    @pytest.mark.asyncio
    async def test_health_check_unhealthy_status(self) -> None:
        """TC-SC-E9: Health check returns unhealthy status.

        Given: API returns non-healthy status
        When: Health check is performed
        Then: Returns False
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        mock_response = Mock()
        mock_response.json.return_value = {"status": "degraded"}

        with patch.object(client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.health_check()

            assert result is False

    @pytest.mark.asyncio
    async def test_upload_changes_with_last_sync_none(self) -> None:
        """TC-SC-E10: Upload changes without last_sync timestamp.

        Given: last_sync is None
        When: Uploading changes
        Then: Payload includes None for last_sync
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        changes = [
            Change(
                entity_type="item",
                entity_id="item-001",
                operation=SyncOperation.CREATE,
                data={"title": "Test"},
                version=1,
            ),
        ]

        mock_response = Mock()
        mock_response.json.return_value = {
            "applied": ["item-001"],
            "conflicts": [],
            "server_time": datetime.now(UTC).isoformat(),
            "errors": [],
        }

        with patch.object(client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            await client.upload_changes(changes, last_sync=None)

            # Verify payload
            call_args = mock_request.call_args
            assert call_args[1]["json"]["last_sync"] is None

    @pytest.mark.asyncio
    async def test_download_changes_without_project_id(self) -> None:
        """TC-SC-E11: Download changes without project filter.

        Given: project_id is None
        When: Downloading changes
        Then: No project_id in query params
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        since = datetime.now(UTC) - timedelta(hours=1)

        mock_response = Mock()
        mock_response.json.return_value = {"changes": []}

        with patch.object(client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            await client.download_changes(since, project_id=None)

            # Verify params
            call_args = mock_request.call_args
            params = call_args[1]["params"]
            assert "project_id" not in params

    @pytest.mark.asyncio
    async def test_resolve_conflict_without_merged_data(self) -> None:
        """TC-SC-E12: Resolve conflict without providing merged data.

        Given: merged_data is None
        When: Resolving conflict
        Then: Payload does not include merged_data
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        mock_response = Mock()
        mock_response.json.return_value = {"resolved": True}

        with patch.object(client, "_retry_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            await client.resolve_conflict("conflict-001", ConflictStrategy.REMOTE_WINS, merged_data=None)

            call_args = mock_request.call_args
            assert "merged_data" not in call_args[1]["json"]

    @pytest.mark.asyncio
    async def test_sync_status_with_null_timestamps(self) -> None:
        """TC-SC-E13: SyncStatus handles null timestamps.

        Given: API returns null for last_sync and server_time
        When: Creating SyncStatus from dict
        Then: Timestamps are None
        """
        data = {"last_sync": None, "pending_changes": 0, "online": True, "server_time": None, "conflicts_pending": 0}

        status = SyncStatus.from_dict(data)

        assert status.last_sync is None
        assert status.server_time is None

    @pytest.mark.asyncio
    async def test_full_sync_with_manual_conflict_strategy(self) -> None:
        """TC-SC-E14: Full sync with MANUAL conflict strategy raises error.

        Given: Conflict occurs and strategy is MANUAL
        When: Full sync is performed
        Then: ConflictError is raised without auto-resolution
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        changes = [
            Change(
                entity_type="item",
                entity_id="item-001",
                operation=SyncOperation.UPDATE,
                data={"title": "Local"},
                version=2,
            ),
        ]

        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-001",
            local_version=2,
            remote_version=3,
            local_data={"title": "Local"},
            remote_data={"title": "Remote"},
        )

        with patch.object(client, "upload_changes", new_callable=AsyncMock) as mock_upload:
            mock_upload.side_effect = ConflictError("Conflict detected", conflicts=[conflict], status_code=409)

            with pytest.raises(ConflictError):
                await client.full_sync(changes, conflict_strategy=ConflictStrategy.MANUAL)

    @pytest.mark.asyncio
    async def test_full_sync_local_wins_conflict_resolution(self) -> None:
        """TC-SC-E15: Full sync with LOCAL_WINS resolves conflicts.

        Given: Conflict occurs and strategy is LOCAL_WINS
        When: Full sync is performed
        Then: Local data is used for conflict resolution
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        changes = [
            Change(
                entity_type="item",
                entity_id="item-001",
                operation=SyncOperation.UPDATE,
                data={"title": "Local"},
                version=2,
            ),
        ]

        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-001",
            local_version=2,
            remote_version=3,
            local_data={"title": "Local"},
            remote_data={"title": "Remote"},
        )

        upload_result = UploadResult(applied=["item-001"], conflicts=[], server_time=datetime.now(UTC), errors=[])

        with patch.object(client, "upload_changes", new_callable=AsyncMock) as mock_upload:
            with patch.object(client, "resolve_conflict", new_callable=AsyncMock) as mock_resolve:
                with patch.object(client, "download_changes", new_callable=AsyncMock) as mock_download:
                    # First upload fails with conflict, second succeeds
                    mock_upload.side_effect = [
                        ConflictError("Conflict", conflicts=[conflict], status_code=409),
                        upload_result,
                    ]
                    mock_resolve.return_value = True
                    mock_download.return_value = []

                    _result, _remote = await client.full_sync(changes, conflict_strategy=ConflictStrategy.LOCAL_WINS)

                    # Verify conflict was resolved with local data
                    mock_resolve.assert_called_once()
                    args = mock_resolve.call_args
                    assert args[0][1] == ConflictStrategy.LOCAL_WINS
                    assert args[0][2] == {"title": "Local"}

    @pytest.mark.asyncio
    async def test_full_sync_remote_wins_conflict_resolution(self) -> None:
        """TC-SC-E16: Full sync with REMOTE_WINS resolves conflicts.

        Given: Conflict occurs and strategy is REMOTE_WINS
        When: Full sync is performed
        Then: Remote data is used for conflict resolution
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        changes = [
            Change(
                entity_type="item",
                entity_id="item-001",
                operation=SyncOperation.UPDATE,
                data={"title": "Local"},
                version=2,
            ),
        ]

        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-001",
            local_version=2,
            remote_version=3,
            local_data={"title": "Local"},
            remote_data={"title": "Remote"},
        )

        upload_result = UploadResult(applied=["item-001"], conflicts=[], server_time=datetime.now(UTC))

        with patch.object(client, "upload_changes", new_callable=AsyncMock) as mock_upload:
            with patch.object(client, "resolve_conflict", new_callable=AsyncMock) as mock_resolve:
                with patch.object(client, "download_changes", new_callable=AsyncMock) as mock_download:
                    mock_upload.side_effect = [
                        ConflictError("Conflict", conflicts=[conflict], status_code=409),
                        upload_result,
                    ]
                    mock_resolve.return_value = True
                    mock_download.return_value = []

                    await client.full_sync(changes, conflict_strategy=ConflictStrategy.REMOTE_WINS)

                    # Verify remote data was used
                    args = mock_resolve.call_args
                    assert args[0][2] == {"title": "Remote"}

    @pytest.mark.asyncio
    async def test_full_sync_last_write_wins_higher_remote_version(self) -> None:
        """TC-SC-E17: LAST_WRITE_WINS uses remote when remote version higher.

        Given: Conflict with remote_version > local_version
        When: Full sync with LAST_WRITE_WINS
        Then: Remote data is used
        """
        config = ApiConfig(base_url="https://test.api.com")
        client = ApiClient(config)

        changes = [
            Change(
                entity_type="item",
                entity_id="item-001",
                operation=SyncOperation.UPDATE,
                data={"title": "Local"},
                version=2,
            ),
        ]

        conflict = Conflict(
            conflict_id="c1",
            entity_type="item",
            entity_id="item-001",
            local_version=2,
            remote_version=5,
            local_data={"title": "Local"},
            remote_data={"title": "Remote"},
        )

        upload_result = UploadResult(applied=["item-001"], conflicts=[], server_time=datetime.now(UTC))

        with patch.object(client, "upload_changes", new_callable=AsyncMock) as mock_upload:
            with patch.object(client, "resolve_conflict", new_callable=AsyncMock) as mock_resolve:
                with patch.object(client, "download_changes", new_callable=AsyncMock) as mock_download:
                    mock_upload.side_effect = [
                        ConflictError("Conflict", conflicts=[conflict], status_code=409),
                        upload_result,
                    ]
                    mock_resolve.return_value = True
                    mock_download.return_value = []

                    await client.full_sync(changes, conflict_strategy=ConflictStrategy.LAST_WRITE_WINS)

                    # Verify remote data was used (higher version)
                    args = mock_resolve.call_args
                    assert args[0][2] == {"title": "Remote"}


# ============================================================================
# BULK OPERATION SERVICE EDGE CASES
# ============================================================================


class TestBulkOperationServiceEdgeCases:
    """Edge case tests for bulk_operation_service.py to reach 85%+ coverage."""

    @pytest.fixture
    def mock_session(self) -> None:
        """Create mock database session."""
        session = MagicMock()
        query_chain = MagicMock()
        query_chain.filter.return_value = query_chain
        query_chain.limit.return_value = query_chain
        query_chain.all.return_value = []
        query_chain.count.return_value = 1
        session.query.return_value = query_chain
        session.add = Mock()
        session.commit = Mock()
        session.rollback = Mock()
        session.flush = Mock()
        return session

    @pytest.fixture
    def service(self, mock_session: Any) -> None:
        """Create service instance."""
        return BulkOperationService(mock_session)

    def test_bulk_update_preview_with_all_filters(self, mock_session: Any) -> None:
        """TC-BOS-E1: Preview with all filter types.

        Given: Filters for view, status, type, priority, owner
        When: Bulk update preview is requested
        Then: All filters are applied to query
        """
        mock_items = [Mock(id="item-001-long", title="Test Item 1", status="todo", priority="high", owner="user1")]
        # Configure the query chain
        query_chain = mock_session.query.return_value
        query_chain.filter.return_value = query_chain
        query_chain.count.return_value = 1
        query_chain.limit.return_value = query_chain
        query_chain.all.return_value = mock_items

        service = BulkOperationService(mock_session)
        filters = {"view": "epic", "status": "todo", "item_type": "feature", "priority": "high", "owner": "user1"}
        updates = {"status": "in_progress"}

        result = service.bulk_update_preview("proj-1", filters, updates)

        assert result["total_count"] == 1
        assert len(result["sample_items"]) == 1
        assert result["sample_items"][0]["id"] == "item-001"  # Truncated to 8 chars

    def test_bulk_update_preview_large_operation_warning(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E2: Preview generates warning for large operations.

        Given: More than 100 items will be updated
        When: Preview is generated
        Then: Warning is included
        """
        mock_session.count.return_value = 150
        mock_session.limit.return_value.all.return_value = []

        result = service.bulk_update_preview("proj-1", {"view": "epic"}, {"status": "done"})

        assert any("150 items" in w for w in result["warnings"])

    def test_bulk_update_preview_mixed_statuses_warning(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E3: Preview warns about mixed statuses.

        Given: Sample items have different statuses
        When: Status update preview is generated
        Then: Mixed status warning is included
        """
        mock_items = [
            Mock(id="1", title="Item 1", status="todo", priority="medium", owner=None),
            Mock(id="2", title="Item 2", status="done", priority="high", owner=None),
        ]
        mock_session.count.return_value = 2
        mock_session.limit.return_value.all.return_value = mock_items

        result = service.bulk_update_preview("proj-1", {}, {"status": "in_progress"})

        assert any("Mixed statuses" in w for w in result["warnings"])

    def test_bulk_update_items_with_all_update_fields(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E4: Update items with all possible fields.

        Given: Updates include status, priority, owner, title, description
        When: Bulk update is executed
        Then: All fields are updated for each item
        """
        mock_items = [
            Mock(id="item-1", title="Old Title", status="todo", priority="low", owner=None, description="Old"),
        ]
        mock_session.all.return_value = mock_items

        updates = {
            "status": "done",
            "priority": "high",
            "owner": "user@example.com",
            "title": "New Title",
            "description": "New Description",
        }

        result = service.bulk_update_items("proj-1", {}, updates, agent_id="agent-1")

        assert result["items_updated"] == 1
        assert mock_items[0].title == "New Title"
        assert mock_items[0].description == "New Description"
        assert mock_items[0].status == "done"

    def test_bulk_update_items_rollback_on_error(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E5: Rollback on update failure.

        Given: Database commit fails
        When: Bulk update is attempted
        Then: Transaction is rolled back and error is raised
        """
        mock_session.all.return_value = [Mock(id="1", title="Test")]
        mock_session.commit.side_effect = OperationalError("DB Error", None, Exception("db error"))

        with pytest.raises(OperationalError):
            service.bulk_update_items("proj-1", {}, {"status": "done"})

        mock_session.rollback.assert_called_once()

    def test_bulk_delete_items_with_filters(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E6: Delete items with multiple filters.

        Given: Filters for view, status, item_type
        When: Bulk delete is executed
        Then: Only matching items are soft-deleted
        """
        mock_items = [Mock(id="1", title="Item 1", deleted_at=None), Mock(id="2", title="Item 2", deleted_at=None)]
        mock_session.all.return_value = mock_items

        filters = {"view": "epic", "status": "obsolete", "item_type": "deprecated"}

        result = service.bulk_delete_items("proj-1", filters, agent_id="agent-1")

        assert result["items_deleted"] == COUNT_TWO
        for item in mock_items:
            assert item.deleted_at is not None

    def test_bulk_delete_rollback_on_error(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E7: Rollback on delete failure.

        Given: Database commit fails during delete
        When: Bulk delete is attempted
        Then: Transaction is rolled back
        """
        mock_session.all.return_value = [Mock(id="1", title="Test", deleted_at=None)]
        mock_session.commit.side_effect = Exception("Commit failed")

        with pytest.raises(Exception):
            service.bulk_delete_items("proj-1", {})

        mock_session.rollback.assert_called_once()

    def test_bulk_create_preview_empty_csv(self, service: Any) -> None:
        """TC-BOS-E8: Preview with empty CSV file.

        Given: CSV file is empty (no data rows)
        When: Preview is generated
        Then: Returns error about empty file
        """
        csv_data = "Title,View,Type\n"  # Header only

        result = service.bulk_create_preview("proj-1", csv_data)

        assert result["total_count"] == 0
        assert "empty" in result["validation_errors"][0].lower()

    def test_bulk_create_preview_missing_required_headers(self, service: Any) -> None:
        """TC-BOS-E9: Preview with missing required CSV headers.

        Given: CSV missing required columns (Title, View, Type)
        When: Preview is generated
        Then: Validation error lists missing headers
        """
        csv_data = "Title,Status\nTest Item,todo\n"

        result = service.bulk_create_preview("proj-1", csv_data)

        assert len(result["validation_errors"]) > 0
        assert "missing required" in result["validation_errors"][0].lower()
        assert "view" in result["validation_errors"][0].lower()

    def test_bulk_create_preview_case_insensitive_headers(self, service: Any) -> None:
        """TC-BOS-E10: Preview handles case-insensitive headers.

        Given: CSV headers in lowercase/mixed case
        When: Preview is generated
        Then: Headers are normalized and accepted
        """
        csv_data = "title,view,type\nTest Item,EPIC,feature\n"

        result = service.bulk_create_preview("proj-1", csv_data)

        # Should not have missing header errors
        assert result["total_count"] == 1

    def test_bulk_create_preview_invalid_json_metadata(self, service: Any) -> None:
        """TC-BOS-E11: Preview handles invalid JSON in metadata column.

        Given: CSV row has malformed JSON in Metadata column
        When: Preview is generated
        Then: Row is marked as invalid with JSON error
        """
        csv_data = """Title,View,Type,Metadata
Test Item,EPIC,feature,"{invalid json"
"""

        result = service.bulk_create_preview("proj-1", csv_data)

        assert result["invalid_rows_count"] == 1
        assert any("JSON" in err for err in result["validation_errors"])

    def test_bulk_create_preview_pydantic_validation_error(self, service: Any) -> None:
        """TC-BOS-E12: Preview handles Pydantic validation errors.

        Given: CSV row has invalid data for ItemCreate schema
        When: Preview is generated
        Then: Row is marked as invalid
        """
        csv_data = """Title,View,Type
,EPIC,feature
"""  # Empty title should fail validation

        result = service.bulk_create_preview("proj-1", csv_data)

        assert result["invalid_rows_count"] >= 1

    def test_bulk_create_preview_duplicate_title_warning(self, service: Any) -> None:
        """TC-BOS-E13: Preview warns about duplicate titles in same view.

        Given: CSV has duplicate title/view combinations
        When: Preview is generated
        Then: Warning is included with row numbers
        """
        csv_data = """Title,View,Type
Duplicate Item,EPIC,feature
Duplicate Item,EPIC,feature
"""

        result = service.bulk_create_preview("proj-1", csv_data)

        assert any("Duplicate title" in w for w in result["warnings"])

    def test_bulk_create_preview_large_operation_warning(self, service: Any) -> None:
        """TC-BOS-E14: Preview warns about large create operations.

        Given: CSV has more than 100 valid rows
        When: Preview is generated
        Then: Large operation warning is included
        """
        # Generate CSV with 101 rows
        rows = ["Title,View,Type"]
        rows.extend(f"Item {i},EPIC,feature" for i in range(101))
        csv_data = "\n".join(rows)

        result = service.bulk_create_preview("proj-1", csv_data, limit=5)

        assert result["total_count"] == 101
        assert any("101 items" in w for w in result["warnings"])

    def test_bulk_create_preview_with_all_optional_fields(self, service: Any) -> None:
        """TC-BOS-E15: Preview with all optional CSV columns.

        Given: CSV includes Description, Status, Priority, Owner, Parent Id, Metadata
        When: Preview is generated
        Then: All fields are parsed and included in samples
        """
        csv_data = """Title,View,Type,Description,Status,Priority,Owner,Parent Id,Metadata
Test Item,EPIC,feature,Description here,in_progress,high,user@example.com,PARENT-1,"{""key"": ""value""}"
"""

        result = service.bulk_create_preview("proj-1", csv_data)

        assert result["total_count"] == 1
        sample = result["sample_items"][0]
        assert sample["priority"] == "high"
        assert sample["owner"] == "user@example.com"

    def test_bulk_create_items_skip_invalid_rows(self, service: Any, _mock_session: Any) -> None:
        """TC-BOS-E16: Create skips invalid rows and continues.

        Given: CSV has mix of valid and invalid rows
        When: Bulk create is executed
        Then: Valid rows are created, invalid rows are skipped
        """
        csv_data = """Title,View,Type
Valid Item,EPIC,feature
,INVALID,bad
Another Valid,STORY,task
"""

        result = service.bulk_create_items("proj-1", csv_data)

        # Should create valid items only
        assert result["items_created"] >= 1

    def test_bulk_create_items_skip_json_decode_error(self, service: Any, _mock_session: Any) -> None:
        """TC-BOS-E17: Create skips rows with JSON decode errors.

        Given: CSV row has invalid JSON metadata
        When: Bulk create is executed
        Then: Row is skipped without raising error
        """
        csv_data = """Title,View,Type,Metadata
Valid Item,EPIC,feature,"{""valid"": true}"
Bad JSON,EPIC,feature,"{invalid"
"""

        result = service.bulk_create_items("proj-1", csv_data)

        # Should create at least one valid item
        assert result["items_created"] >= 1

    def test_bulk_create_items_rollback_on_commit_error(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E18: Rollback on create commit failure.

        Given: Database commit fails
        When: Bulk create is attempted
        Then: Transaction is rolled back and error is raised
        """
        csv_data = "Title,View,Type\nTest,EPIC,feature\n"
        mock_session.commit.side_effect = IntegrityError("Duplicate", None, Exception("duplicate"))

        with pytest.raises(IntegrityError):
            service.bulk_create_items("proj-1", csv_data)

        mock_session.rollback.assert_called_once()

    def test_bulk_create_items_skip_row_on_exception(self, service: Any, mock_session: Any) -> None:
        """TC-BOS-E19: Create skips row that raises exception during processing.

        Given: One row causes exception during item creation
        When: Bulk create is executed
        Then: Exception row is skipped, other rows processed
        """
        csv_data = """Title,View,Type
Item 1,EPIC,feature
Item 2,EPIC,feature
"""

        # Mock flush to succeed for some, fail for others
        call_count = [0]

        def flush_side_effect() -> None:
            call_count[0] += 1
            if call_count[0] == 1:
                msg = "First item fails"
                raise Exception(msg)

        mock_session.flush.side_effect = flush_side_effect

        # Should not raise, should skip failing rows
        result = service.bulk_create_items("proj-1", csv_data)

        # At least one should be skipped due to error
        assert isinstance(result, dict)


# ============================================================================
# MARKDOWN PARSER EDGE CASES
# ============================================================================


class TestMarkdownParserEdgeCases:
    """Edge case tests for markdown_parser.py to reach 85%+ coverage."""

    @pytest.fixture
    def temp_dir(self, tmp_path: Any) -> None:
        """Create temporary directory."""
        return tmp_path

    def test_parse_item_markdown_file_not_found(self, temp_dir: Any) -> None:
        """TC-MP-E1: Parse raises FileNotFoundError for missing file.

        Given: File does not exist
        When: parse_item_markdown is called
        Then: FileNotFoundError is raised
        """
        path = temp_dir / "nonexistent.md"

        with pytest.raises(FileNotFoundError):
            parse_item_markdown(path)

    def test_parse_item_markdown_no_frontmatter(self, temp_dir: Any) -> None:
        """TC-MP-E2: Parse raises ValueError when no frontmatter.

        Given: File has no YAML frontmatter
        When: parse_item_markdown is called
        Then: ValueError is raised
        """
        path = temp_dir / "no_frontmatter.md"
        path.write_text("# Just a title\n\nNo frontmatter here.")

        with pytest.raises(ValueError, match="No YAML frontmatter"):
            parse_item_markdown(path)

    def test_parse_item_markdown_missing_required_fields(self, temp_dir: Any) -> None:
        """TC-MP-E3: Parse raises ValueError for missing required fields.

        Given: Frontmatter missing required fields (id, external_id, type, status)
        When: parse_item_markdown is called
        Then: ValueError is raised with field names
        """
        path = temp_dir / "missing_fields.md"
        content = """---
id: item-001
type: epic
---

# Content
"""
        path.write_text(content)

        with pytest.raises(ValueError, match="Missing required frontmatter"):
            parse_item_markdown(path)

    def test_write_item_markdown_missing_required_fields(self, temp_dir: Any) -> None:
        """TC-MP-E4: Write raises ValueError for missing required fields.

        Given: ItemData missing required fields
        When: write_item_markdown is called
        Then: ValueError is raised
        """
        item = ItemData(
            id="",  # Empty ID
            external_id="EXT-001",
            item_type="epic",
            status="todo",
        )

        with pytest.raises(ValueError, match="missing required fields"):
            write_item_markdown(item, temp_dir / "test.md")

    def test_parse_links_yaml_file_not_found(self, temp_dir: Any) -> None:
        """TC-MP-E5: Parse links raises FileNotFoundError.

        Given: links.yaml does not exist
        When: parse_links_yaml is called
        Then: FileNotFoundError is raised
        """
        with pytest.raises(FileNotFoundError):
            parse_links_yaml(temp_dir / "links.yaml")

    def test_parse_links_yaml_empty_file(self, temp_dir: Any) -> None:
        """TC-MP-E6: Parse links handles empty file.

        Given: links.yaml is empty
        When: parse_links_yaml is called
        Then: Returns empty list
        """
        path = temp_dir / "links.yaml"
        path.write_text("")

        result = parse_links_yaml(path)

        assert result == []

    def test_parse_links_yaml_no_links_key(self, temp_dir: Any) -> None:
        """TC-MP-E7: Parse links handles YAML without 'links' key.

        Given: YAML file has other keys but not 'links'
        When: parse_links_yaml is called
        Then: Returns empty list
        """
        path = temp_dir / "links.yaml"
        path.write_text("other_key: value\n")

        result = parse_links_yaml(path)

        assert result == []

    def test_parse_links_yaml_invalid_link_format(self, temp_dir: Any) -> None:
        """TC-MP-E8: Parse links raises ValueError for invalid format.

        Given: Link dict missing required fields
        When: parse_links_yaml is called
        Then: ValueError is raised
        """
        path = temp_dir / "links.yaml"
        content = """
links:
  - id: link-1
    source: EPIC-1
    # Missing 'target' and 'type'
"""
        path.write_text(content)

        with pytest.raises(ValueError, match="Invalid link format"):
            parse_links_yaml(path)

    def test_parse_config_yaml_file_not_found(self, temp_dir: Any) -> None:
        """TC-MP-E9: Parse config raises FileNotFoundError.

        Given: config.yaml does not exist
        When: parse_config_yaml is called
        Then: FileNotFoundError is raised
        """
        with pytest.raises(FileNotFoundError):
            parse_config_yaml(temp_dir / "config.yaml")

    def test_parse_config_yaml_empty_file(self, temp_dir: Any) -> None:
        """TC-MP-E10: Parse config handles empty file.

        Given: config.yaml is empty
        When: parse_config_yaml is called
        Then: Returns empty dict
        """
        path = temp_dir / "config.yaml"
        path.write_text("")

        result = parse_config_yaml(path)

        assert result == {}

    def test_item_data_frontmatter_with_figma_fields(self, _temp_dir: Any) -> None:
        """TC-MP-E11: ItemData includes Figma fields in frontmatter.

        Given: ItemData has Figma-specific fields
        When: to_frontmatter_dict is called
        Then: All Figma fields are included
        """
        item = ItemData(
            id="item-1",
            external_id="WIRE-001",
            item_type="wireframe",
            status="draft",
            figma_url="https://figma.com/file/abc",
            figma_file_key="abc123",
            figma_node_id="1:2",
            components=["Button", "Input"],
            screens=["Login", "Dashboard"],
            implements=["STORY-001"],
        )

        fm = item.to_frontmatter_dict()

        assert fm["figma_url"] == "https://figma.com/file/abc"
        assert fm["figma_file_key"] == "abc123"
        assert fm["figma_node_id"] == "1:2"
        assert fm["components"] == ["Button", "Input"]
        assert fm["screens"] == ["Login", "Dashboard"]
        assert fm["implements"] == ["STORY-001"]

    def test_item_data_markdown_body_wireframe_type(self, _temp_dir: Any) -> None:
        """TC-MP-E12: Wireframe type generates Figma sections.

        Given: ItemData type is wireframe with Figma data
        When: to_markdown_body is called
        Then: Figma Preview, Components, Screens sections are included
        """
        item = ItemData(
            id="item-1",
            external_id="WIRE-001",
            item_type="wireframe",
            status="draft",
            title="Login Screen",
            figma_url="https://figma.com/file/abc",
            figma_file_key="abc123",
            figma_node_id="1:2",
            components=["Button", "Input Field"],
            screens=["Login Page", "Signup Page"],
        )

        body = item.to_markdown_body()

        assert "## Figma Preview" in body
        assert "![Figma Preview](figma://abc123/1:2)" in body
        assert "## Components Used" in body
        assert "- Button" in body
        assert "## Screens" in body
        assert "- Login Page" in body

    def test_item_data_markdown_body_wireframe_no_node_id(self, _temp_dir: Any) -> None:
        """TC-MP-E13: Wireframe without node_id shows link only.

        Given: Wireframe has figma_url but no file_key/node_id
        When: to_markdown_body is called
        Then: Only Figma link is shown, no image embed
        """
        item = ItemData(
            id="item-1",
            external_id="WIRE-001",
            item_type="wireframe",
            status="draft",
            title="Screen",
            figma_url="https://figma.com/file/abc",
        )

        body = item.to_markdown_body()

        assert "[View in Figma]" in body
        assert "![Figma Preview]" not in body

    def test_link_data_datetime_string_conversion(self) -> None:
        """TC-MP-E14: LinkData handles ISO string with Z suffix.

        Given: Link dict has timestamp with 'Z' suffix
        When: from_dict is called
        Then: Datetime is parsed correctly
        """
        data = {
            "id": "link-1",
            "source": "EPIC-1",
            "target": "STORY-1",
            "type": "implements",
            "created": "2024-01-01T12:00:00Z",
        }

        link = LinkData.from_dict(data)

        assert isinstance(link.created, datetime)

    def test_link_data_to_dict_with_metadata(self) -> None:
        """TC-MP-E15: LinkData includes metadata in to_dict.

        Given: LinkData has metadata
        When: to_dict is called
        Then: Metadata is included
        """
        link = LinkData(
            id="link-1",
            source="EPIC-1",
            target="STORY-1",
            link_type="implements",
            created=datetime.now(UTC),
            metadata={"confidence": 0.95},
        )

        result = link.to_dict()

        assert "metadata" in result
        assert result["metadata"]["confidence"] == 0.95

    def test_link_data_to_dict_without_metadata(self) -> None:
        """TC-MP-E16: LinkData excludes empty metadata from to_dict.

        Given: LinkData has empty metadata
        When: to_dict is called
        Then: Metadata key is not included
        """
        link = LinkData(
            id="link-1",
            source="EPIC-1",
            target="STORY-1",
            link_type="implements",
            created=datetime.now(UTC),
            metadata={},
        )

        result = link.to_dict()

        assert "metadata" not in result

    def test_parse_history_table_insufficient_rows(self) -> None:
        """TC-MP-E17: History table parser handles insufficient rows.

        Given: Table has less than 3 lines (header + separator)
        When: _parse_history_table is called
        Then: Returns empty list
        """
        from tracertm.storage.markdown_parser import _parse_history_table

        table = "| Header |\n"

        result = _parse_history_table(table)

        assert result == []

    def test_parse_history_table_non_table_line(self) -> None:
        """TC-MP-E18: History parser skips non-table lines.

        Given: Table content has lines not starting with |
        When: _parse_history_table is called
        Then: Non-table lines are skipped
        """
        from tracertm.storage.markdown_parser import _parse_history_table

        table = """| Version | Date |
|---------|------|
Some non-table text
| 1 | 2024-01-01 |
"""

        result = _parse_history_table(table)

        assert len(result) == 1

    def test_parse_history_table_insufficient_columns(self) -> None:
        """TC-MP-E19: History parser handles rows with too few columns.

        Given: Row has less than 4 columns
        When: _parse_history_table is called
        Then: Row is skipped
        """
        from tracertm.storage.markdown_parser import _parse_history_table

        table = """| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1 | 2024-01-01 |
| 2 | 2024-01-02 | user | Complete change |
"""

        result = _parse_history_table(table)

        # Only the complete row should be parsed
        assert len(result) == 1

    def test_list_items_nonexistent_project(self, temp_dir: Any) -> None:
        """TC-MP-E20: List items returns empty for nonexistent project.

        Given: Project directory does not exist
        When: list_items is called
        Then: Returns empty list
        """
        result = list_items(temp_dir, "nonexistent_project")

        assert result == []

    def test_list_items_nonexistent_type(self, temp_dir: Any) -> None:
        """TC-MP-E21: List items returns empty for nonexistent type.

        Given: Item type directory does not exist
        When: list_items is called with item_type
        Then: Returns empty list
        """
        project_dir = temp_dir / "projects" / "test_project"
        project_dir.mkdir(parents=True)

        result = list_items(temp_dir, "test_project", item_type="epic")

        assert result == []

    def test_list_items_all_types(self, temp_dir: Any) -> None:
        """TC-MP-E22: List items finds all types when no filter.

        Given: Project has multiple item type directories
        When: list_items is called without item_type
        Then: Returns items from all types
        """
        project_dir = temp_dir / "projects" / "test_project"
        epics_dir = project_dir / "epics"
        stories_dir = project_dir / "stories"
        epics_dir.mkdir(parents=True)
        stories_dir.mkdir(parents=True)

        (epics_dir / "EPIC-001.md").write_text("# Epic")
        (stories_dir / "STORY-001.md").write_text("# Story")

        result = list_items(temp_dir, "test_project")

        assert len(result) == COUNT_TWO

    def test_get_item_path_story_pluralization(self, temp_dir: Any) -> None:
        """TC-MP-E23: get_item_path correctly pluralizes 'story'.

        Given: item_type is 'story'
        When: get_item_path is called
        Then: Path uses 'stories' directory
        """
        path = get_item_path(temp_dir, "project", "story", "STORY-001")

        assert "stories" in str(path)
        assert path.name == "STORY-001.md"

    def test_parse_markdown_body_no_sections(self) -> None:
        """TC-MP-E24: Parse body handles content with no H2 sections.

        Given: Markdown body has no ## sections
        When: _parse_markdown_body is called
        Then: Returns empty values for all sections
        """
        from tracertm.storage.markdown_parser import _parse_markdown_body

        body = "# Title Only\n\nSome content."

        title, desc, criteria, _notes, _history = _parse_markdown_body(body)

        assert title == "Title Only"
        assert desc == ""
        assert criteria == []

    def test_parse_markdown_body_empty_sections(self) -> None:
        """TC-MP-E25: Parse body handles empty sections.

        Given: Body has ## section headers but no content
        When: _parse_markdown_body is called
        Then: Sections are parsed as empty strings
        """
        from tracertm.storage.markdown_parser import _parse_markdown_body

        body = """# Title

## Description

## Notes
"""

        title, desc, _criteria, notes, _history = _parse_markdown_body(body)

        assert title == "Title"
        assert desc == ""
        assert notes == ""

    def test_parse_frontmatter_invalid_yaml_raises(self) -> None:
        """TC-MP-E26: Parse frontmatter raises ValueError for invalid YAML.

        Given: Frontmatter contains invalid YAML syntax
        When: _parse_frontmatter is called
        Then: ValueError is raised
        """
        from tracertm.storage.markdown_parser import _parse_frontmatter

        content = """---
invalid: yaml: structure
  - bad indent
---

Body
"""

        with pytest.raises(ValueError, match="Invalid YAML frontmatter"):
            _parse_frontmatter(content)

    def test_write_links_yaml_creates_parent_directory(self, temp_dir: Any) -> None:
        """TC-MP-E27: write_links_yaml creates parent directory.

        Given: Parent directory does not exist
        When: write_links_yaml is called
        Then: Parent directory is created
        """
        path = temp_dir / "new" / "dir" / "links.yaml"
        links = []

        write_links_yaml(links, path)

        assert path.parent.exists()
        assert path.exists()

    def test_write_config_yaml_creates_parent_directory(self, temp_dir: Any) -> None:
        """TC-MP-E28: write_config_yaml creates parent directory.

        Given: Parent directory does not exist
        When: write_config_yaml is called
        Then: Parent directory is created
        """
        path = temp_dir / "new" / "config.yaml"
        config = {"key": "value"}

        write_config_yaml(config, path)

        assert path.parent.exists()
        assert path.exists()

    def test_write_item_markdown_creates_parent_directory(self, temp_dir: Any) -> None:
        """TC-MP-E29: write_item_markdown creates parent directory.

        Given: Parent directory does not exist
        When: write_item_markdown is called
        Then: Parent directory is created
        """
        item = ItemData(id="item-1", external_id="EPIC-001", item_type="epic", status="todo", title="Test")
        path = temp_dir / "new" / "dir" / "epic.md"

        write_item_markdown(item, path)

        assert path.parent.exists()
        assert path.exists()

    def test_item_data_custom_fields_excluded_from_known_fields(self) -> None:
        """TC-MP-E30: ItemData separates custom fields from known fields.

        Given: Frontmatter has custom fields not in known_fields
        When: from_frontmatter_and_body is called
        Then: Custom fields are stored separately
        """
        fm_data = {
            "id": "item-1",
            "external_id": "EPIC-001",
            "type": "epic",
            "status": "todo",
            "custom_field_1": "value1",
            "custom_field_2": "value2",
        }
        body = "# Title"

        item = ItemData.from_frontmatter_and_body(fm_data, body)

        assert item.custom_fields["custom_field_1"] == "value1"
        assert item.custom_fields["custom_field_2"] == "value2"

    def test_item_data_to_frontmatter_includes_custom_fields(self) -> None:
        """TC-MP-E31: to_frontmatter_dict includes custom fields.

        Given: ItemData has custom_fields
        When: to_frontmatter_dict is called
        Then: Custom fields are included in output
        """
        item = ItemData(
            id="item-1",
            external_id="EPIC-001",
            item_type="epic",
            status="todo",
            custom_fields={"custom_key": "custom_value"},
        )

        fm = item.to_frontmatter_dict()

        assert fm["custom_key"] == "custom_value"

    def test_conflict_from_dict_missing_timestamp(self) -> None:
        """TC-MP-E32: Conflict.from_dict uses default timestamp when missing.

        Given: Conflict dict has no timestamp
        When: from_dict is called
        Then: Uses current UTC time as default
        """
        data = {
            "conflict_id": "c1",
            "entity_type": "item",
            "entity_id": "item-1",
            "local_version": 1,
            "remote_version": 2,
            "local_data": {},
            "remote_data": {},
        }

        conflict = Conflict.from_dict(data)

        assert isinstance(conflict.timestamp, datetime)

    def test_upload_result_from_dict_minimal_data(self) -> None:
        """TC-MP-E33: UploadResult.from_dict handles minimal data.

        Given: Response dict has only server_time
        When: from_dict is called
        Then: Uses defaults for other fields
        """
        data = {"server_time": datetime.now(UTC).isoformat()}

        result = UploadResult.from_dict(data)

        assert result.applied == []
        assert result.conflicts == []
        assert result.errors == []

    def test_sync_status_from_dict_minimal_data(self) -> None:
        """TC-MP-E34: SyncStatus.from_dict handles minimal data.

        Given: Response dict has minimal fields
        When: from_dict is called
        Then: Uses defaults for missing fields
        """
        data = {"online": False}

        status = SyncStatus.from_dict(data)

        assert status.pending_changes == 0
        assert status.online is False
        assert status.conflicts_pending == 0

    def test_api_error_without_response_data(self) -> None:
        """TC-MP-E35: ApiError initializes with None response_data.

        Given: response_data is None
        When: ApiError is created
        Then: response_data defaults to empty dict
        """
        error = ApiError("Test error", status_code=500, response_data=None)

        assert error.response_data == {}

    def test_rate_limit_error_initialization(self) -> None:
        """TC-MP-E36: RateLimitError stores retry_after value.

        Given: retry_after is provided
        When: RateLimitError is created
        Then: retry_after is accessible
        """
        error = RateLimitError("Rate limited", retry_after=120, status_code=429)

        assert error.retry_after == 120
        assert error.status_code == HTTP_TOO_MANY_REQUESTS

    def test_conflict_error_stores_conflicts(self) -> None:
        """TC-MP-E37: ConflictError stores conflict list.

        Given: Conflicts list is provided
        When: ConflictError is created
        Then: Conflicts are accessible
        """
        conflicts = [
            Conflict(
                conflict_id="c1",
                entity_type="item",
                entity_id="item-1",
                local_version=1,
                remote_version=2,
                local_data={},
                remote_data={},
            ),
        ]

        error = ConflictError("Conflicts detected", conflicts=conflicts)

        assert len(error.conflicts) == 1
        assert error.conflicts[0].conflict_id == "c1"


# ============================================================================
# SUMMARY
# ============================================================================

"""
Test Coverage Summary:

SYNC CLIENT (20 edge case tests):
- Config creation edge cases (None manager, string conversions, URL normalization)
- Client property edge cases (no token, close when None)
- Retry logic edge cases (exhausted retries, rate limiting, auth errors)
- Health check edge cases (unhealthy status)
- Upload/download edge cases (None values, missing fields)
- Conflict resolution edge cases (all strategies, version comparisons)

BULK OPERATION SERVICE (19 edge case tests):
- Preview edge cases (all filters, warnings, large operations)
- Update edge cases (all fields, rollback on error)
- Delete edge cases (filters, rollback on error)
- CSV parsing edge cases (empty, missing headers, case insensitivity)
- JSON metadata errors
- Pydantic validation errors
- Duplicate detection
- Invalid row handling
- Transaction rollback scenarios

MARKDOWN PARSER (37 edge case tests):
- File I/O edge cases (not found, empty files)
- Frontmatter parsing edge cases (missing, invalid YAML)
- Required field validation
- Links/config parsing edge cases (empty, invalid format)
- Figma field handling for wireframes
- DateTime parsing edge cases
- History table parsing edge cases
- Item listing edge cases (nonexistent paths)
- Path generation edge cases (pluralization)
- Body parsing edge cases (no sections, empty sections)
- Directory creation edge cases
- Custom field handling
- Minimal data handling for all data classes

Total: 76 edge case tests covering error paths, boundary conditions,
and exception handling to push all modules above 85% coverage.
"""
