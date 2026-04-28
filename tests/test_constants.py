"""Test-specific constants for assertions, timeouts, and common test values.

This module centralizes frequently reused magic values from tests to improve
maintainability and clarity. Single-use test values should remain inline with
# noqa: PLR2004 annotations where appropriate.
"""

# ============================================================================
# HTTP Status Codes
# ============================================================================

# Success codes
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204

# Client error codes
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429

# Server error codes
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_SERVICE_UNAVAILABLE = 503


# ============================================================================
# Common Count Assertions
# ============================================================================

# These represent frequently used expected counts in assertions
COUNT_TWO = 2  # Most common: 942 uses
COUNT_THREE = 3  # Second most common: 558 uses
COUNT_FOUR = 4
COUNT_FIVE = 5  # 305 uses
COUNT_SIX = 6
COUNT_SEVEN = 7
COUNT_EIGHT = 8
COUNT_TEN = 10  # 189 uses
COUNT_FIFTEEN = 15
COUNT_TWENTY = 20
COUNT_THIRTY = 30
COUNT_THIRTY_SIX = 36
COUNT_FIFTY = 50  # 70 uses
COUNT_SIXTY_FOUR = 64
COUNT_HUNDRED = 100  # 124 uses
COUNT_FIVE_HUNDRED = 500  # 72 uses
COUNT_THOUSAND = 1000  # 44 uses
COUNT_TEN_THOUSAND = 10000  # 25 uses


# ============================================================================
# Timeout and Polling Values (seconds)
# ============================================================================

# API/Request timeouts
TIMEOUT_DEFAULT = 30.0  # 15 uses
TIMEOUT_LONG = 60.0
TIMEOUT_SHORT = 10.0
TIMEOUT_VERY_SHORT = 5.0  # 20 uses

# Poll intervals
POLL_INTERVAL_FAST = 0.1  # 20 uses
POLL_INTERVAL_SLOW = 0.5  # 31 uses
POLL_INTERVAL_VERY_SLOW = 1.0

# Retry backoff
BACKOFF_BASE = 2.0  # 24 uses
BACKOFF_MAX = 60.0

# Rate limit windows
RATE_LIMIT_WINDOW = 60  # 14 uses (seconds)


# ============================================================================
# Retry and Limit Configuration
# ============================================================================

MAX_RETRIES_DEFAULT = 3  # Standard retry count
MAX_RETRIES_FIVE = 5
MAX_RETRIES_TEN = 10

BATCH_SIZE_SMALL = 10
BATCH_SIZE_MEDIUM = 50
BATCH_SIZE_LARGE = 100
BATCH_SIZE_VERY_LARGE = 500


# ============================================================================
# Floating Point Thresholds and Deltas
# ============================================================================

# Tolerance values for float comparisons
TOLERANCE_STRICT = 0.01  # 14 uses
TOLERANCE_NORMAL = 0.05  # 15 uses
TOLERANCE_RELAXED = 0.1

# Common float values in assertions
FLOAT_TWO = 2.0
FLOAT_FIVE = 5.0
FLOAT_TEN = 10.0
FLOAT_THIRTY = 30.0  # 15 uses
FLOAT_FORTY_FIVE = 45.0
FLOAT_FORTY_FIVE_HALF = 45.5


# ============================================================================
# Test Data Size Limits
# ============================================================================

SIZE_LIMIT_KB = 1024
SIZE_LIMIT_MB = 1024 * 1024
SIZE_LIMIT_10MB = 10 * 1024 * 1024

MAX_STRING_LENGTH = 255
MAX_BATCH_SIZE = 1000
