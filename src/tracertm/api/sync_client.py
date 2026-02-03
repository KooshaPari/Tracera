"""
HTTP API client for TraceRTM sync operations.

Handles communication with the backend API for synchronization of local changes.
"""

import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

import httpx
from loguru import logger

from tracertm.config.manager import ConfigManager


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
    timeout: float = 30.0
    max_retries: int = 3
    retry_backoff_base: float = 2.0
    retry_backoff_max: float = 60.0
    verify_ssl: bool = True

    @classmethod
    def from_config_manager(cls, config_manager: ConfigManager | None = None) -> "ApiConfig":
        """
        Create ApiConfig from ConfigManager.

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
        timeout = float(timeout_value) if timeout_value is not None else 30.0

        # Handle max_retries - could be string or numeric
        retries_value = config_manager.get("api_max_retries")
        max_retries = int(retries_value) if retries_value is not None else 3

        return cls(
            base_url=api_url.rstrip("/"),
            token=token,
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
            conflict_id=data["conflict_id"],
            entity_type=data["entity_type"],
            entity_id=data["entity_id"],
            local_version=data["local_version"],
            remote_version=data["remote_version"],
            local_data=data["local_data"],
            remote_data=data["remote_data"],
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now(UTC).isoformat())),
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
        return cls(
            applied=data.get("applied", []),
            conflicts=[Conflict.from_dict(c) for c in data.get("conflicts", [])],
            server_time=datetime.fromisoformat(data["server_time"]),
            errors=data.get("errors", []),
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
        if data.get("last_sync"):
            last_sync = datetime.fromisoformat(data["last_sync"])

        server_time = None
        if data.get("server_time"):
            server_time = datetime.fromisoformat(data["server_time"])

        return cls(
            last_sync=last_sync,
            pending_changes=data.get("pending_changes", 0),
            online=data.get("online", False),
            server_time=server_time,
            conflicts_pending=data.get("conflicts_pending", 0),
        )


class ApiError(Exception):
    """Base exception for API errors."""

    def __init__(self, message: str, status_code: int | None = None, response_data: dict[str, Any] | None = None):
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
        retry_after: int | float | None = None,
        status_code: int | None = None,
        response_data: dict[str, Any] | None = None,
    ):
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
    ):
        super().__init__(message, status_code, response_data)
        self.conflicts = conflicts


class ApiClient:
    """
    Async HTTP client for TraceRTM backend API.

    Handles authentication, retries, and error handling for sync operations.
    """

    def __init__(self, config: ApiConfig | None = None):
        """
        Initialize API client.

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

    async def __aenter__(self) -> "ApiClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def _retry_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Execute HTTP request with exponential backoff retry logic.

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
                if response.status_code == 429:
                    retry_after_raw = response.headers.get("Retry-After", "60")
                    try:
                        retry_after = float(retry_after_raw)
                    except Exception:
                        retry_after = 60.0
                    raise RateLimitError(
                        f"Rate limit exceeded. Retry after {retry_after}s",
                        retry_after=retry_after,
                        status_code=429,
                        response_data=response.json() if response.content else {},
                    )

                # Check for auth errors
                if response.status_code == 401:
                    raise AuthenticationError(
                        "Authentication failed. Check API token.",
                        status_code=401,
                        response_data=response.json() if response.content else {},
                    )

                # Raise for other HTTP errors
                response.raise_for_status()
                return response

            except httpx.HTTPStatusError as e:
                # Handle 409 Conflict errors specially
                if e.response.status_code == 409:
                    data = e.response.json() if e.response.content else {}
                    conflicts = [Conflict.from_dict(c) for c in data.get("conflicts", [])]
                    raise ConflictError(
                        "Conflicts detected during request",
                        conflicts=conflicts,
                        status_code=409,
                        response_data=data,
                    ) from e
                last_error = e
                logger.warning(
                    f"HTTP error on attempt {attempt + 1}/{self.config.max_retries}: "
                    f"{e.response.status_code} - {e.response.text}"
                )

            except httpx.TimeoutException as e:
                # Wrap timeout exceptions as NetworkError
                last_error = e
                logger.warning(f"Timeout error on attempt {attempt + 1}/{self.config.max_retries}: {e}")

            except httpx.NetworkError as e:
                last_error = e
                logger.warning(f"Network error on attempt {attempt + 1}/{self.config.max_retries}: {e}")

            except RateLimitError as e:
                last_error = e
                # For rate limiting, wait the specified time and retry
                if e.retry_after and attempt < self.config.max_retries - 1:
                    logger.info(f"Rate limited. Waiting {e.retry_after}s before retry...")
                    await asyncio.sleep(e.retry_after)
                    continue
                # If no more retries or no retry_after, raise immediately
                raise

            except AuthenticationError:
                # Don't retry auth errors
                raise

            # Exponential backoff with jitter (not crypto-sensitive)
            if attempt < self.config.max_retries - 1:
                import random

                jitter = random.uniform(0, 0.1 * delay)  # noqa: S311
                sleep_time = min(delay + jitter, self.config.retry_backoff_max)
                logger.debug(f"Retrying in {sleep_time:.2f}s...")
                await asyncio.sleep(sleep_time)
                delay *= self.config.retry_backoff_base

        # All retries failed
        if isinstance(last_error, (httpx.TimeoutException, httpx.NetworkError)):
            raise NetworkError(f"Network error after {self.config.max_retries} retries: {last_error}")
        if isinstance(last_error, httpx.HTTPStatusError):
            raise ApiError(
                f"HTTP error after {self.config.max_retries} retries: {last_error}",
                status_code=last_error.response.status_code,
                response_data=last_error.response.json() if last_error.response.content else {},
            )
        raise ApiError(f"Request failed after {self.config.max_retries} retries: {last_error}")

    async def health_check(self) -> bool:
        """
        Check API health.

        Returns:
            True if API is healthy, False otherwise
        """
        try:
            response = await self._retry_request("GET", "/api/health")
            data = response.json()
            status_result: Any = data.get("status")
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
        """
        Upload local changes to server.

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
            if exc.response is not None and exc.response.status_code == 409:
                response_payload = exc.response.json()
                conflicts_raw: list[Any] = response_payload.get("conflicts", [])
                conflicts: list[Conflict] = [
                    Conflict.from_dict(c) if isinstance(c, dict) else c
                    for c in conflicts_raw
                    if isinstance(c, (dict, Conflict))
                ]
                raise ConflictError("Sync conflicts detected", conflicts=conflicts) from exc
            raise

    async def download_changes(
        self,
        since: datetime,
        project_id: str | None = None,
    ) -> list[Change]:
        """
        Download remote changes since timestamp.

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
        """
        Resolve a sync conflict.

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
        resolved_result: Any = data.get("resolved", False)
        return bool(resolved_result)

    async def get_sync_status(self) -> SyncStatus:
        """
        Get current sync status.

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
        """
        Perform full bidirectional sync.

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
