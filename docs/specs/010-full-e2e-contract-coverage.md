# Spec 010: Full End-to-End Contract Coverage

| Field | Value |
|-------|-------|
| **Spec ID** | TRACERA-SPEC-010 |
| **Title** | YAML Contract Testing for All Active Endpoints |
| **Status** | Draft |
| **Version** | 2.0 |
| **Author** | Tracera Core Team |
| **Date** | 2026-08-30 |
| **Supersedes** | 1.0 |
| **Depends on** | SPEC-009 (API Schema Definitions) |

---

## 1. Introduction

Tracera exposes **27 active HTTP endpoints** across server, ingestion, desktop/tray, and dashboard domains. Without rigorous contract testing, API consumers and internal modules are vulnerable to schema drift, breaking changes, and behavioral regressions. This specification defines a comprehensive YAML-based contract testing framework ensuring every endpoint's request/response schema, status codes, and behavioral invariants are validated automatically on every CI run.

### 1.1 Goals

- **Schema Fidelity** — request and response payloads match declared schemas.
- **Behavioral Invariants** — status codes, error formats, rate limiting, timeout, idempotency.
- **Regression Prevention** — detect breaking changes before production.
- **Full Coverage** — 100% endpoint coverage with 7 test cases per endpoint (189 total).
- **Automation** — integrated into CI/CD with SARIF and JSON reporting.

### 1.2 Non-Goals

- Performance benchmarking (see SPEC-012).
- Load/stress testing (see SPEC-012).
- Unit testing of internal business logic.

---

## 2. Endpoint Inventory (27 Endpoints)

### 2.1 Server Endpoints (16)

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 01 | POST | `/api/v1/auth/login` | No | User authentication |
| 02 | POST | `/api/v1/auth/refresh` | Yes | Token refresh |
| 03 | GET | `/api/v1/graph/nodes` | Yes | List graph nodes |
| 04 | POST | `/api/v1/graph/nodes` | Yes | Create graph node |
| 05 | GET | `/api/v1/graph/nodes/:id` | Yes | Get node by ID |
| 06 | PATCH | `/api/v1/graph/nodes/:id` | Yes | Update node |
| 07 | DELETE | `/api/v1/graph/nodes/:id` | Yes | Delete node |
| 08 | GET | `/api/v1/graph/edges` | Yes | List graph edges |
| 09 | POST | `/api/v1/graph/edges` | Yes | Create graph edge |
| 10 | GET | `/api/v1/graph/query` | Yes | Graph query |
| 11 | GET | `/api/v1/coverage/summary` | Yes | Coverage summary |
| 12 | GET | `/api/v1/coverage/detail` | Yes | Coverage detail |
| 13 | POST | `/api/v1/coverage/enrich` | Yes | Trigger enrichment |
| 14 | GET | `/api/v1/distillation/patterns` | Yes | List patterns |
| 15 | POST | `/api/v1/distillation/run` | Yes | Trigger distillation |
| 16 | GET | `/api/v1/health` | No | Health check |

### 2.2 Ingestion Endpoints (3)

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 17 | POST | `/api/v1/ingest/agileplus` | Yes | AgilePlus ingestion |
| 18 | POST | `/api/v1/ingest/github` | Signature | GitHub webhook |
| 19 | POST | `/api/v1/ingest/jira` | Yes | Jira webhook |

### 2.3 Desktop/Tray Endpoints (4)

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 20 | GET | `/tray/status` | No | Tray app status |
| 21 | POST | `/tray/action` | Yes | Execute tray action |
| 22 | GET | `/tray/notifications` | Yes | Pending notifications |
| 23 | POST | `/tray/notifications/ack` | Yes | Acknowledge notification |

### 2.4 Dashboard Endpoints (4)

| # | Method | Path | Auth | Description |
|---|--------|------|------|-------------|
| 24 | GET | `/api/v1/dashboard/panels` | Yes | Panel configuration |
| 25 | POST | `/api/v1/dashboard/query` | Yes | Data query |
| 26 | GET | `/api/v1/dashboard/realtime` | Yes | WebSocket live data |
| 27 | GET | `/api/v1/dashboard/export` | Yes | Export PDF/CSV |

---

## 3. Shared Schemas and YAML Structure

### 3.1 Shared Schema Definitions

```yaml
# shared/schemas.yaml
schemas:
  Error:
    type: object
    required: [error, message]
    properties:
      error: { type: string }
      message: { type: string }
      details: { type: array, items: { type: object } }

  PaginatedResponse:
    type: object
    required: [data, total, page, per_page]
    properties:
      data: { type: array }
      total: { type: integer }
      page: { type: integer }
      per_page: { type: integer }

  HealthResponse:
    type: object
    required: [status, timestamp]
    properties:
      status: { type: string, enum: [ok, degraded, error] }
      timestamp: { type: string, format: date-time }

  AuthToken:
    type: object
    required: [access_token, refresh_token, expires_in]
    properties:
      access_token: { type: string }
      refresh_token: { type: string }
      expires_in: { type: integer, minimum: 300 }
```

### 3.2 Contract File Structure

Each endpoint has a dedicated YAML file:

```yaml
contract:
  endpoint: POST /api/v1/auth/login
  version: "2026-08-30"
  description: "User authentication endpoint"
  shared_schemas: [Error, AuthToken]
  schemas:
    request:
      type: object
      required: [email, password]
      properties:
        email: { type: string, format: email }
        password: { type: string, minLength: 8 }
    response_200:
      $ref: "#/shared/AuthToken"
    response_422:
      $ref: "#/shared/Error"
    response_429:
      $ref: "#/shared/Error"
  tests:
    - name: happy_path
      request:
        body: { email: "test@tracera.io", password: "secureP@ss123" }
      expect:
        status: 200
        schema: response_200
        headers: { content-type: application/json }
    - name: empty_input
      request:
        body: {}
      expect:
        status: 422
        schema: response_422
    - name: malformed_json
      request:
        raw_body: "{invalid json"
        content_type: application/json
      expect:
        status: 400
    - name: unauthorized
      request:
        body: { email: "wrong@example.com", password: "wrong" }
      expect:
        status: 401
    - name: rate_limit
      request:
        repeat: 120
        interval_ms: 10
      expect:
        last_response: { status: 429 }
        headers: { x-ratelimit-remaining: "0" }
    - name: timeout
      request:
        delay_ms: 30000
        simulated_server_delay_ms: 35000
      expect:
        status: [408, 504]
    - name: idempotency
      request:
        idempotency_key: "idem-login-001"
        repeat: 2
        interval_ms: 100
      expect:
        responses_identical: true
        first_status: 200
```

---

## 4. Test Case Definitions (7 Per Endpoint)

| # | Test Case | Purpose | Key Validation |
|---|-----------|---------|----------------|
| 1 | `happy_path` | Valid input succeeds | Schema validation, 200/201 |
| 2 | `empty_input` | Missing fields rejected | 400/422, error schema |
| 3 | `malformed_json` | Parse error handling | 400, no stack trace |
| 4 | `unauthorized` | Auth enforcement | 401, error schema |
| 5 | `rate_limit` | Throttling behavior | 429, retry-after headers |
| 6 | `timeout` | Slow request handling | 408/504, graceful degradation |
| 7 | `idempotency` | Request deduplication | Cached responses, idempotency keys |

### 4.1 Happy Path

Validates well-formed request with valid auth returns expected schema and status code. This is the baseline ensuring the endpoint functions correctly under normal conditions.

### 4.2 Empty Input

Validates rejection of empty or missing required fields. POST/PATCH endpoints return 400 or 422 with structured error response.

### 4.3 Malformed JSON

Validates graceful handling of invalid JSON. Server returns 400 with descriptive error message without crashes or internal stack traces.

### 4.4 Unauthorized

Validates that protected endpoints reject requests without valid tokens (401). Unauth-required endpoints still run the case expecting appropriate behavior.

### 4.5 Rate Limit

Validates enforcement after exceeding threshold. Response is 429 with `Retry-After` and `X-RateLimit-*` headers.

### 4.6 Timeout

Validates graceful handling of stalled requests. Response is 408 or 504 with structured error.

### 4.7 Idempotency

Validates that identical `Idempotency-Key` headers return cached responses with same status, headers, and body.

---

## 5. Test Runner Architecture

```rust
pub struct ContractRunner {
    base_url: String,
    http_client: reqwest::Client,
    schema_validator: jsonschema::Validator,
    results: Vec<TestResult>,
    config: RunnerConfig,
}

pub struct RunnerConfig {
    timeout_ms: u64,           // default: 30000
    rate_limit_threshold: u32, // default: 100
    parallel_workers: usize,   // default: 4
    output_format: OutputFormat,
    filter: Option<String>,
}

pub struct TestResult {
    endpoint: String,
    test_name: String,
    status: TestStatus,
    actual_status: u16,
    expected_status: Vec<u16>,
    schema_valid: bool,
    duration_ms: u64,
    error: Option<String>,
}
```

### 5.1 Execution Flow

1. **Discovery** — scan `contracts/` for all YAML files.
2. **Parsing** — load and validate YAML against meta-schema.
3. **Execution** — run tests (parallel for independent endpoints).
4. **Validation** — compare responses against schemas.
5. **Reporting** — generate JSON + SARIF outputs.

---

## 6. CI Integration

### 6.1 GitHub Actions Workflow

```yaml
name: Contract Tests
on:
  pull_request: { branches: [main, develop] }
  push: { branches: [main] }
  schedule: [{ cron: '0 2 * * *' }]

jobs:
  contract-tests:
    runs-on: ubuntu-latest
    services:
      tracera-server:
        image: tracera/server:latest
        ports: [8080:8080]
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo build --release --bin contract-runner
      - run: |
          ./target/release/contract-runner \
            --base-url http://localhost:8080 \
            --output-format json,sarif
      - uses: github/codeql-action/upload-sarif@v3
        if: always()
        with: { sarif_file: contract-results.sarif }
```

### 6.2 Gate Rules

- **Blocking**: All 189 tests must pass for PR merge.
- **Required reviewers**: 1 approval from `@tracera/core-team`.
- **Post-deploy smoke**: happy_path for all 27 endpoints; auto-rollback on failure.

---

## 7. Traceability Matrix

| Domain | Endpoints | Tests Each | Total Tests |
|--------|-----------|------------|-------------|
| Server | 16 | 7 | 112 |
| Ingestion | 3 | 7 | 21 |
| Desktop/Tray | 4 | 7 | 28 |
| Dashboard | 4 | 7 | 28 |
| **Total** | **27** | **7** | **189** |

---

## 8. Schema Evolution Strategy

- **Minor version**: additive changes only (new optional fields, enum values).
- **Major version**: breaking changes (removed fields, type changes, status code changes).
- **Drift detection**: `contract-runner --detect-drift --openapi ./openapi.yaml`
  - Warning: contract field not in OpenAPI.
  - Error: OpenAPI field not in contract.
  - Critical: schema mismatch (blocking).

---

## 9. Performance Requirements

| Metric | Target |
|--------|--------|
| Total suite execution | < 30 seconds |
| Per-endpoint test (non-timeout) | < 2 seconds |
| Schema validation overhead | < 50ms per response |
| Memory usage | < 512MB |
| Concurrent workers | 4 (configurable) |

---

## 10. Acceptance Criteria

| # | Criterion |
|---|-----------|
| AC-01 | All 27 endpoints have YAML contract files |
| AC-02 | Each endpoint has exactly 7 test cases |
| AC-03 | Happy path returns 200/201 for every endpoint |
| AC-04 | Empty input returns 400/422 for POST/PATCH endpoints |
| AC-05 | Malformed JSON returns 400 with error schema |
| AC-06 | Unauthorized returns 401 for protected endpoints |
| AC-07 | Rate limit returns 429 after threshold exceeded |
| AC-08 | Timeout returns 408/504 for slow requests |
| AC-09 | Idempotency key produces identical cached responses |
| AC-10 | Total suite execution < 30 seconds |
| AC-11 | Shared schemas use `$ref`, not duplication |
| AC-12 | CI fails on any contract test failure |
| AC-13 | JSON and SARIF reports generated |
| AC-14 | Coverage shows 100% endpoint coverage |
| AC-15 | Schema drift detected against OpenAPI |
| AC-16 | WebSocket contract validated for realtime endpoint |
| AC-17 | Export format contracts produce valid PDF/CSV |
| AC-18 | Tests run locally without external dependencies |
| AC-19 | `--filter` flag enables selective execution |
| AC-20 | Mutation kill rate > 90% on test assertions |

---

## 11. Rollout Plan (5 Phases)

| Phase | Deliverables | Duration |
|-------|-------------|----------|
| 1 | Core runner, shared schemas, 5 core contracts | Weeks 1-2 |
| 2 | Remaining 11 server contracts, `$ref` validation | Weeks 3-4 |
| 3 | Desktop/Tray + Dashboard contracts, WebSocket validation | Weeks 5-6 |
| 4 | CI integration, SARIF, coverage badge | Week 7 |
| 5 | Mutation testing, drift detection, docs | Week 8 |

---

## Appendix: File Structure

```
contracts/
├── shared/schemas.yaml
├── server/
│   ├── auth-login.yaml          ├── graph-nodes-delete.yaml
│   ├── auth-refresh.yaml        ├── graph-edges-list.yaml
│   ├── graph-nodes-list.yaml    ├── graph-edges-create.yaml
│   ├── graph-nodes-create.yaml  ├── graph-query.yaml
│   ├── graph-nodes-get.yaml     ├── coverage-summary.yaml
│   ├── graph-nodes-update.yaml  ├── coverage-detail.yaml
│   │   ├── coverage-enrich.yaml
│   │   ├── distillation-patterns.yaml
│   │   ├── distillation-run.yaml
│   │   └── health.yaml
├── ingestion/
│   ├── agileplus.yaml  ├── github.yaml  └── jira.yaml
├── tray/
│   ├── status.yaml  ├── action.yaml
│   ├── notifications.yaml  └── notifications-ack.yaml
└── dashboard/
    ├── panels.yaml  ├── query.yaml
    ├── realtime.yaml  └── export.yaml
```

---

*End of Spec 010 — TRACERA-SPEC-010 v2.0*
