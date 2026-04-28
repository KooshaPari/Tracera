# PyDevKit

## At a Glance
- **Purpose:** Lightweight utility toolbox extracted from production systems—HTTP, configuration, security, data structures, async helpers, and more.
- **Best For:** Projects that want foundational utilities with minimal dependencies (httpx required for HTTP).
- **Key Building Blocks:** Modules under `pydevkit.*` (http, config, security, data_structures, async_utils, functional, validation, etc.).

## Core Capabilities
- HTTP client and retry strategies powered by httpx (`pydevkit.http`).
- Configuration loaders and environment helpers (`pydevkit.config`).
- Security primitives (password hashing, JWT, HMAC, PII scanning) (`pydevkit.security`).
- Data structures (LRU cache, bloom filter, tries) (`pydevkit.data_structures`).
- Async utilities (task queues, event bus, throttlers) (`pydevkit.async_utils`, `pydevkit.concurrency`).
- Validation helpers for common formats (`pydevkit.validation`).
- Functional programming helpers and high-performance utilities.

## Getting Started

### Installation
```
pip install pydevkit
# Optional extras
pip install "pydevkit[crypto]" "pydevkit[yaml]"
```

### Minimal Example
```python
from pydevkit.http import create_client
from pydevkit import LRUCache

client = create_client(base_url="https://api.example.com")
response = client.get("/status")
print(response.json())

cache = LRUCache(capacity=100)
cache.set("token", "abc123")
```

## How It Works
- Modules are organized by domain (e.g., `pydevkit.http.client`, `pydevkit.security.jwt`).
- Each module is self-contained; HTTP pieces require httpx. Extras like crypto/yaml are optional.
- Correlation ID helpers integrate with observability-kit when both are installed.
- Utilities are designed to be imported selectively to keep runtime footprint small.

## Usage Recipes
- **Configuration:**
  ```python
  from pydevkit.config import ConfigManager
  config = ConfigManager()
  config.load_from_env(prefix="APP_")
  ```
- **Security:**
  ```python
  from pydevkit.security import jwt
  token = jwt.encode({"sub": "user-1"}, secret="secret")
  ```
- **Async tools:**
  ```python
  from pydevkit.async_utils import TaskQueue
  queue = TaskQueue(max_workers=5)
  queue.submit(lambda: print("done"))
  ```
- **Validation:**
  ```python
  from pydevkit.validation import is_email
  assert is_email("user@example.com")
  ```

## Interoperability
- Observability-kit reads correlation IDs from `pydevkit.tracing.correlation_id` helpers.
- Config-kit can coexist with pydevkit config utilities; choose one per service for clarity.
- Event-kit and workflow-kit can leverage pydevkit’s async utilities for lightweight scenarios.

- httpx tracing: use `pydevkit.http.build_httpx_otel_hooks()` with `create_client` to emit spans.

## Operations & Observability
- Minimal runtime overhead; suitable for serverless and edge environments.
- Provide your own logging hooks or integrate with observability-kit for structured logs.
- Combine with resource-management-kit to monitor CPU/memory when using concurrency helpers.

## Testing & QA
- Modules are pure or offer in-memory implementations—easy to unit test.
- Reuse fixtures from `pydevkit/tests` to validate custom extensions (e.g., new validators).
- Keep snapshots of expected outputs for data structure serialization.

## Troubleshooting
- **Missing extras functionality:** install the relevant extra (`[crypto]`, `[yaml]`, etc.).
- **HTTP timeouts:** adjust retry/backoff parameters in `create_client`/`create_async_client` or set custom timeouts.
- **Validation false positives:** review regex or validation logic; extend with custom validators if needed.

## Primary API Surface (Selected)
- `pydevkit.http.create_client`, `create_async_client`, `request_with_retries`
- `pydevkit.config.ConfigManager`, `EnvLoader`
- `pydevkit.security.jwt.encode/decode`
- `pydevkit.data_structures.LRUCache`, `BloomFilter`
- `pydevkit.async_utils.TaskQueue`, `EventBus`
- `pydevkit.validation.is_email`, `is_url`
- `pydevkit.tracing.correlation_id.set_correlation_id`

## Additional Resources
- Examples: `pydevkit/examples/`
- Tests: `pydevkit/tests/`
- Related concepts: [Patterns](../concepts/patterns.md)
