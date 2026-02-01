# API Retry and Robust Clients

Wait+retry and robust API tooling is applied across frontend, Python, and Go so transient failures (network, 5xx, timeouts) are retried with backoff instead of failing immediately.

## Frontend (web app)

- **Global fetch** is patched at app bootstrap in `frontend/apps/web/src/main.tsx` with `createRetryFetch()` from `frontend/apps/web/src/lib/fetch-retry.ts`.
- **All** `fetch()` calls (including those from `openapi-fetch` in `api/client.ts`) therefore get:
  - Up to 3 attempts
  - 15s timeout per attempt
  - Exponential backoff (500ms → 1s → 2s, capped at 10s)
  - Retry on: network errors, timeouts, and HTTP 408, 429, 502, 503, 504
  - No retry on: 4xx (except 408, 429)
- **Preflight** health checks use the same patched fetch, so backend checks are retried before showing "Backend resources unavailable".

## Python

- **TraceRTMHttpClient** (`src/tracertm/api/http_client.py`): uses `tenacity` to retry on `httpx.NetworkError`, `httpx.TimeoutException`, and on 5xx/408/429 responses (exponential backoff, 3 attempts, 1–10s wait).
- **GoBackendClient** (`src/tracertm/clients/go_client.py`): already uses tenacity retry for network/timeout (3 attempts, exponential backoff).
- **Sync API client** (`src/tracertm/api/sync_client.py`): already implements `_retry_request` with configurable `max_retries` and exponential backoff.
- **Preflight** (`src/tracertm/preflight.py`): HTTP and TCP checks use `run_single_check_with_retry()` (3 attempts, 1s initial delay, 2x backoff, max 30s delay) so services that are still starting get a chance.

## Go

- **E2E tests** (`backend/tests/e2e/setup.go`): `waitForServices` uses exponential backoff (500ms + 250ms per attempt, max 5s) when polling `/health` until the server is ready.

## Configuration

- **Frontend**: `frontend/apps/web/src/lib/fetch-retry.ts` — `RetryFetchOptions`: `maxRetries`, `timeoutMs`, `initialDelayMs`, `maxDelayMs`, `backoffMultiplier`, `retryStatuses`, `jitter`.
- **Python TraceRTMHttpClient**: `max_retries` in constructor (default 3); tenacity uses 1–10s wait.
- **Python preflight**: `PREFLIGHT_MAX_ATTEMPTS`, `PREFLIGHT_INITIAL_DELAY`, `PREFLIGHT_BACKOFF` in `src/tracertm/preflight.py`.
- **Python sync client**: `ApiConfig.max_retries`, `retry_backoff_base`, `retry_backoff_max` (from config or defaults).

## Python third-party clients

- **GitHub** (`src/tracertm/clients/github_client.py`): `_request_once` is wrapped with tenacity; retries on `NetworkError`, `TimeoutException`, and 5xx (3 attempts, exponential 1–10s). Rate limit (403) and auth/not-found (401, 404) are not retried.
- **Linear** (`src/tracertm/clients/linear_client.py`): `_query_once` is wrapped with tenacity; same retry policy (3 attempts, 1–10s, network/timeout/5xx). Rate limit (429) and auth/GraphQL errors are not retried.

## Adding retry to new clients

- **Frontend**: Use `fetch()` as usual; it is already the retry-wrapped fetch after bootstrap. For a custom fetch (e.g. in tests), use `createRetryFetch(originalFetch, options)` from `@/lib/fetch-retry`.
- **Python**: Use `TraceRTMHttpClient` for TraceRTM API, or add `@retry` with `tenacity` (e.g. `retry_if_exception_type((httpx.NetworkError, httpx.TimeoutException))`) and `wait_exponential(min=1, max=10)` for new httpx-based clients.
