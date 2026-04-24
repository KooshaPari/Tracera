"""Python API for TraceRTM.

Provides:
- TraceRTMClient: Local database access for AI agents (FR36)
- ApiClient: HTTP client for sync operations with backend API
"""

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
    SyncOperation,
    SyncStatus,
    UploadResult,
)

__all__ = [
    # HTTP sync client
    "ApiClient",
    "ApiConfig",
    # Exceptions
    "ApiError",
    "AuthenticationError",
    # Data models
    "Change",
    "Conflict",
    "ConflictError",
    "ConflictStrategy",
    "NetworkError",
    "RateLimitError",
    "SyncOperation",
    "SyncStatus",
    # Local client
    "TraceRTMClient",
    "UploadResult",
]
