# Integration Testing Strategy: Live vs Mocked Services

## Principles
1. **Live First**: All infrastructure services (PostgreSQL, Redis, NATS, Neo4j, MinIO, Temporal) are available locally via `process-compose` and MUST be used for integration testing.
2. **Deterministic Errors**: Mocks should only be used to simulate rare error conditions (e.g., network timeout, 500 status codes) that are difficult to trigger on live services.
3. **External Cloud Mocks**: Third-party SaaS services that require API keys or internet access (WorkOS, OpenAI, Anthropic) are exempt from live testing and should remain mocked unless explicitly running E2E "Sanity" checks.

## Service Matrix

| Service | Mode | Reason |
|---------|------|--------|
| **PostgreSQL** | Live | Essential for schema validation and transaction logic. |
| **Redis** | Live | Essential for caching and rate limiting logic. |
| **NATS** | Live | Essential for event-driven architecture and WebSocket propagation. |
| **Neo4j** | Live | Essential for graph relationship validation. |
| **MinIO (S3)** | Live | Essential for snapshot and file storage logic. |
| **Temporal** | Live | Essential for workflow state machine validation. |
| **Python API** | Live | hitting the real Python backend verifies contract between Go and Python. |
| **WorkOS** | Mocked | Avoids hitting rate limits and dependency on external auth provider availability. |
| **OpenAI/Anthropic** | Mocked | Avoids costs, latency, and non-deterministic LLM responses in unit/integration tests. |

## Running Live Tests
To run tests against the live `process-compose` stack:
```bash
make test-integration-live
```

## Legacy / Isolated Tests
Existing tests using `testcontainers-go` or `pytest-docker` are still valid for CI environments where a global `process-compose` stack might not be active. However, for local development, hitting the shared dev stack is preferred for speed and accuracy.
