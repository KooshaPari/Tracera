"""HTTP API client for TraceRTM sync operations.

Handles communication with the backend API for synchronization of local changes.
"""

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Self, cast

import httpx
from loguru import logger

from tracertm.config.manager import ConfigManager
from tracertm.constants import (
    HTTP_CONFLICT,
    HTTP_TOO_MANY_REQUESTS,
    HTTP_UNAUTHORIZED,
    MAX_RETRIES_DEFAULT,
    RETRY_BACKOFF_BASE,
    RETRY_BACKOFF_MAX,
    TIMEOUT_DEFAULT,
)


class SyncOperation(StrEnum):
    """Sync operation types."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class ConflictStrategy(StrEnum):
    """Conflict resolution strategies."""

    LAST_WRITE_WINS = "last_write_wins"
    LOCAL_WINS = "local_wins"
    REMOTE_WINS = "remote_wins"
    MANUAL = "manual"


@dataclass
class ApiConfig:
    """Configuration for API client."""

    base_url: str
    token: str | None = None
    timeout: float = TIMEOUT_DEFAULT
    max_retries: int = MAX_RETRIES_DEFAULT
    retry_backoff_base: float = RETRY_BACKOFF_BASE
    retry_backoff_max: float = RETRY_BACKOFF_MAX
    verify_ssl: bool = True

    @classmethod
    def from_config_manager(cls, config_manager: ConfigManager | None = None) -> "ApiConfig":
        """Create ApiConfig from ConfigManager.

        Args:
            config_manager: Optional ConfigManager instance (creates new if None)

        Returns:
            ApiConfig instance
        """
        if config_manager is None:
            config_manager = ConfigManager()

        # Get API configuration
        api_url = config_manager.get("api_url") or "https://api.tracertm.io"
        token = config_manager.get("api_token")

        # Handle timeout - could be string or numeric
        timeout_value = config_manager.get("api_timeout")
        timeout = float(cast("float | str", timeout_value)) if timeout_value is not None else TIMEOUT_DEFAULT

        # Handle max_retries - could be string or numeric
        retries_value = config_manager.get("api_max_retries")
        max_retries = int(cast("int | str", retries_value)) if retries_value is not None else MAX_RETRIES_DEFAULT

        return cls(
            base_url=cast("str", api_url).rstrip("/"),
            token=cast("str | None", token),
            timeout=timeout,
            max_retries=max_retries,
        )


@dataclass
class Change:
    """Represents a local change to sync."""

    entity_type: str  # project, item, link
    entity_id: str
    operation: SyncOperation
    data: dict[str, Any]
    version: int = 1
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    client_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "operation": self.operation.value,
            "data": self.data,
            "version": self.version,
            "timestamp": self.timestamp.isoformat(),
            "client_id": self.client_id,
        }


@dataclass
class Conflict:
    """Represents a sync conflict."""

    conflict_id: str
    entity_type: str
    entity_id: str
    local_version: int
    remote_version: int
    local_data: dict[str, Any]
    remote_data: dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Conflict":
        """Create Conflict from API response."""
        return cls(
            conflict_id=cast("str", data["conflict_id"]),
            entity_type=cast("str", data["entity_type"]),
            entity_id=cast("str", data["entity_id"]),
            local_version=cast("int", data["local_version"]),
            remote_version=cast("int", data["remote_version"]),
            local_data=cast("dict[str, Any]", data["local_data"]),
            remote_data=cast("dict[str, Any]", data["remote_data"]),
            timestamp=datetime.fromisoformat(cast("str", data.get("timestamp", datetime.now(UTC).isoformat()))),
        )


@dataclass
class UploadResult:
    """Result of uploading changes."""

    applied: list[str]  # Entity IDs successfully applied
    conflicts: list[Conflict]
    server_time: datetime
    errors: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UploadResult":
        """Create UploadResult from API response."""
        conflicts_data = cast("list[dict[str, Any]]", data.get("conflicts", []))
        return cls(
            applied=cast("list[str]", data.get("applied", [])),
            conflicts=[Conflict.from_dict(c) for c in conflicts_data],
            server_time=datetime.fromisoformat(cast("str", data["server_time"])),
            errors=cast("list[dict[str, Any]]", data.get("errors", [])),
        )


@dataclass
class SyncStatus:
    """Sync status information."""

    last_sync: datetime | None
    pending_changes: int
    online: bool
    server_time: datetime | None = None
    conflicts_pending: int = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SyncStatus":
        """Create SyncStatus from API response."""
        last_sync = None
        last_sync_val = data.get("last_sync")
        if last_sync_val:
            last_sync = datetime.fromisoformat(cast("str", last_sync_val))

        server_time = None
        server_time_val = data.get("server_time")
        if server_time_val:
            server_time = datetime.fromisoformat(cast("str", server_time_val))

        return cls(
            last_sync=last_sync,
            pending_changes=cast("int", data.get("pending_changes", 0)),
            online=cast("bool", data.get("online", False)),
            server_time=server_time,
            conflicts_pending=cast("int", data.get("conflicts_pending", 0)),
        )


class ApiError(Exception):
    """Base exception for API errors."""

    def __init__(
        self, message: str, status_code: int | None = None, response_data: dict[str, Any] | None = None
    ) -> None:
        """Initialize API error.

        Args:
            message: Error message
            status_code: Optional HTTP status code
            response_data: Optional response data
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}


class AuthenticationError(ApiError):
    """Authentication failed."""


class NetworkError(ApiError):
    """Network connection error."""


class RateLimitError(ApiError):
    """Rate limit exceeded."""

    def __init__(
        self,
        message: str,
        retry_after: float | None = None,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize rate limit error.

        Args:
            message: Error message
            retry_after: Optional delay in seconds before retrying
            status_code: Optional HTTP status code
            response_data: Optional response data
        """
        super().__init__(message, status_code, response_data)
        self.retry_after = retry_after


class ConflictError(ApiError):
    """Conflict detected during sync."""

    def __init__(
        self,
        message: str,
        conflicts: list[Conflict],
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ) -> None:
        """Initialize conflict error.

        Args:
            message: Error message
            conflicts: List of detected conflicts
            status_code: Optional HTTP status code
            response_data: Optional response data
        """
        super().__init__(message, status_code, response_data)
        self.conflicts = conflicts


class ApiClient:
    """Async HTTP client for TraceRTM backend API.

    Handles authentication, retries, and error handling for sync operations.
    """

    def __init__(self, config: ApiConfig | None = None) -> None:
        """Initialize API client.

        Args:
            config: Optional ApiConfig (creates default if None)
        """
        self.config = config or ApiConfig.from_config_manager()
        self._client: httpx.AsyncClient | None = None
        self._client_id = self._generate_client_id()

    def _generate_client_id(self) -> str:
        """Generate unique client ID for this instance."""
        # Use machine ID + process ID + timestamp for uniqueness
        import os
        import platform

        data = f"{platform.node()}-{os.getpid()}-{datetime.now(UTC).isoformat()}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            headers = {
                "Content-Type": "application/json",
                "User-Agent": f"TraceRTM-Client/{self._client_id}",
            }

            if self.config.token is not None:
                headers["Authorization"] = f"Bearer {self.config.token}"

            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                headers=headers,
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            )

        return self._client

    async def close(self) -> None:
        """Close HTTP client connection."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> Self:
        """Async context manager entry."""
        return self

    async def __aexit__(self, _exc_type: object, _exc_val: object, _exc_tb: object) -> None:
        """Async context manager exit."""
        await self.close()

    async def _retry_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: object,
    ) -> httpx.Response:
        """Execute HTTP request with exponential backoff retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for httpx request

        Returns:
            httpx.Response

        Raises:
            ApiError: On failure after retries
        """
        last_error: Exception | None = None
        delay = 1.0

        for attempt in range(self.config.max_retries):
            try:
                response = await self.client.request(method, endpoint, **kwargs)

                # Check for rate limiting
                if response.status_code == HTTP_TOO_MANY_REQUESTS:
                    retry_after_raw = response.headers.get("Retry-After", "60")
                    try:
                        retry_after = float(retry_after_raw)
                    except Exception:
                        retry_after = 60.0
                    msg = f"Rate limit exceeded. Retry after {retry_after}s"
                    raise RateLimitError(
                        msg,
                        retry_after=retry_after,
                        status_code=429,
                        response_data=response.json() if response.content else {},
                    )

                # Check for auth errors
                if response.status_code == HTTP_UNAUTHORIZED:
                    msg = "Authentication failed. Check API token."
                    raise AuthenticationError(
                        msg,
                        status_code=401,
                        response_data=response.json() if response.content else {},
                    )

                # Raise for other HTTP errors
                response.raise_for_status()

            except httpx.HTTPStatusError as e:
                # Handle 409 Conflict errors specially
                if e.response.status_code == HTTP_CONFLICT:
                    data = e.response.json() if e.response.content else {}
                    conflicts = [Conflict.from_dict(c) for c in data.get("conflicts", [])]
                    msg = "Conflicts detected during request"
                    raise ConflictError(
                        msg,
                        conflicts=conflicts,
                        status_code=409,
                        response_data=data,
                    ) from e
                last_error = e
                logger.warning(
                    "HTTP error on attempt %s/%s: %s - %s",
                    attempt + 1,
                    self.config.max_retries,
                    e.response.status_code,
                    e.response.text,
                )

            except httpx.TimeoutException as e:
                # Wrap timeout exceptions as NetworkError
                last_error = e
                logger.warning("Timeout error on attempt %s/%s: %s", attempt + 1, self.config.max_retries, e)

            except httpx.NetworkError as e:
                last_error = e
                logger.warning("Network error on attempt %s/%s: %s", attempt + 1, self.config.max_retries, e)

            except RateLimitError as e:
                last_error = e
                # For rate limiting, wait the specified time and retry
                if e.retry_after and attempt < self.config.max_retries - 1:
                    logger.info("Rate limited. Waiting %ss before retry...", e.retry_after)
                    await asyncio.sleep(e.retry_after)
                    continue
                # If no more retries or no retry_after, raise immediately
                raise

            except AuthenticationError:
                # Don't retry auth errors
                raise
            else:
                return response

            # Exponential backoff with jitter (not crypto-sensitive)
            if attempt < self.config.max_retries - 1:
                import random

                jitter = random.uniform(0, 0.1 * delay)
                sleep_time = min(delay + jitter, self.config.retry_backoff_max)
                logger.debug("Retrying in %.2fs...", sleep_time)
                await asyncio.sleep(sleep_time)
                delay *= self.config.retry_backoff_base

        # All retries failed
        if isinstance(last_error, (httpx.TimeoutException, httpx.NetworkError)):
            msg = f"Network error after {self.config.max_retries} retries: {last_error}"
            raise NetworkError(msg)
        if isinstance(last_error, httpx.HTTPStatusError):
            msg = f"HTTP error after {self.config.max_retries} retries: {last_error}"
            raise ApiError(
                msg,
                status_code=last_error.response.status_code,
                response_data=last_error.response.json() if last_error.response.content else {},
            )
        msg = f"Request failed after {self.config.max_retries} retries: {last_error}"
        raise ApiError(msg)

    async def health_check(self) -> bool:
        """Check API health.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = await self._retry_request("GET", "/api/health")
            data = response.json()
            status_result: object = data.get("status")
            return bool(status_result == "healthy")
        except (ApiError, AuthenticationError, NetworkError, RateLimitError):
            logger.error("Health check failed: API error")
            return False
        except Exception:
            logger.error("Health check failed: unexpected error")
            return False

    async def upload_changes(
        self,
        changes: list[Change],
        last_sync: datetime | None = None,
    ) -> UploadResult:
        """Upload local changes to server.

        Args:
            changes: List of changes to upload
            last_sync: Optional timestamp of last sync

        Returns:
            UploadResult with applied changes and conflicts

        Raises:
            ConflictError: If conflicts are detected
            ApiError: On upload failure
        """
        payload = {
            "changes": [change.to_dict() for change in changes],
            "client_id": self._client_id,
            "last_sync": last_sync.isoformat() if last_sync else None,
        }

        try:
            response = await self._retry_request("POST", "/api/sync/upload", json=payload)
            data = response.json()
            return UploadResult.from_dict(data)
        except httpx.HTTPStatusError as exc:
            if exc.response is not None and exc.response.status_code == HTTP_CONFLICT:
                response_payload = exc.response.json()
                conflicts_raw: list[object] = response_payload.get("conflicts", [])
                conflicts: list[Conflict] = [
                    Conflict.from_dict(c) if isinstance(c, dict[str, Any]) else c
                    for c in conflicts_raw
                    if isinstance(c, (dict[str, Any], Conflict))
                ]
                msg = "Sync conflicts detected"
                raise ConflictError(msg, conflicts=conflicts) from exc
            raise

    async def download_changes(
        self,
        since: datetime,
        project_id: str | None = None,
    ) -> list[Change]:
        """Download remote changes since timestamp.

        Args:
            since: Download changes after this timestamp
            project_id: Optional project ID filter

        Returns:
            List of remote changes

        Raises:
            ApiError: On download failure
        """
        params: dict[str, Any] = {"since": since.isoformat()}
        if project_id:
            params["project_id"] = project_id

        response = await self._retry_request("GET", "/api/sync/changes", params=params)
        data = response.json()

        return [
            Change(
                entity_type=change_data["entity_type"],
                entity_id=change_data["entity_id"],
                operation=SyncOperation(change_data["operation"]),
                data=change_data["data"],
                version=change_data.get("version", 1),
                timestamp=datetime.fromisoformat(change_data["timestamp"]),
                client_id=change_data.get("client_id"),
            )
            for change_data in data.get("changes", [])
        ]

    async def resolve_conflict(
        self,
        conflict_id: str,
        resolution: ConflictStrategy,
        merged_data: dict[str, Any] | None = None,
    ) -> bool:
        """Resolve a sync conflict.

        Args:
            conflict_id: Conflict ID to resolve
            resolution: Resolution strategy
            merged_data: Optional merged data for manual resolution

        Returns:
            True if resolved successfully

        Raises:
            ApiError: On resolution failure
        """
        resolve_payload: dict[str, Any] = {
            "conflict_id": conflict_id,
            "resolution": resolution.value,
        }

        if merged_data is not None:
            resolve_payload["merged_data"] = merged_data

        response = await self._retry_request("POST", "/api/sync/resolve", json=resolve_payload)
        data = response.json()
        resolved_result: object = data.get("resolved", False)
        return bool(resolved_result)

    async def get_sync_status(self) -> SyncStatus:
        """Get current sync status.

        Returns:
            SyncStatus with sync information

        Raises:
            ApiError: On status fetch failure
        """
        response = await self._retry_request("GET", "/api/sync/status")
        data = response.json()
        return SyncStatus.from_dict(data)

    # Convenience sync methods

    async def full_sync(
        self,
        local_changes: list[Change],
        last_sync: datetime | None = None,
        project_id: str | None = None,
        conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS,
    ) -> tuple[UploadResult, list[Change]]:
        """Perform full bidirectional sync.

        Args:
            local_changes: Local changes to upload
            last_sync: Timestamp of last sync
            project_id: Optional project ID filter
            conflict_strategy: Strategy for auto-resolving conflicts

        Returns:
            Tuple of (upload_result, remote_changes)

        Raises:
            ConflictError: If conflicts cannot be auto-resolved
        """
        # Upload local changes
        try:
            upload_result = await self.upload_changes(local_changes, last_sync)
        except ConflictError as e:
            # Try to auto-resolve based on strategy
            if conflict_strategy == ConflictStrategy.MANUAL:
                raise

            for conflict in e.conflicts:
                if conflict_strategy == ConflictStrategy.LOCAL_WINS:
                    merged_data = conflict.local_data
                elif conflict_strategy == ConflictStrategy.REMOTE_WINS:
                    merged_data = conflict.remote_data
                else:  # LAST_WRITE_WINS
                    # Use whichever has higher version
                    merged_data = (
                        conflict.local_data
                        if conflict.local_version > conflict.remote_version
                        else conflict.remote_data
                    )

                await self.resolve_conflict(
                    conflict.conflict_id,
                    conflict_strategy,
                    merged_data,
                )

            # Retry upload after resolving conflicts
            upload_result = await self.upload_changes(local_changes, last_sync)

        # Download remote changes
        download_since = last_sync or datetime.now(UTC) - timedelta(days=30)
        remote_changes = await self.download_changes(download_since, project_id)

        return upload_result, remote_changes


# Backward-compat alias used in tests
SyncClient = ApiClient
