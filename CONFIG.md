# Tracera Configuration Reference

This document describes all configuration keys across the Tracera stack:
- **Go Backend** (`backend/`) — primary backend service
- **Rust Core** (`crates/tracera-core/`) — core library with PyO3 bindings
- **Python Backend** (`src/tracertm/`) — FastAPI-based Python backend
- **Python CLI** (`src/tracertm/config/`) — CLI configuration via pydantic-settings

## Configuration Hierarchy

Configuration is resolved in this order (highest to lowest precedence):

1. CLI flags (Python CLI only)
2. Environment variables
3. `.env` file (loaded via `godotenv` in Go, `pydantic-settings` in Python)
4. YAML config file (Python CLI: `~/.tracertm/config.yaml`)
5. Hardcoded defaults

---

## Go Backend (`backend/internal/config/`)

All environment variables are read directly from `os.Getenv()`.
The primary entry point is `config.LoadConfig()`.

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `8080` | HTTP server port |
| `GRPC_PORT` | `9091` | gRPC server port |
| `ENV` | `development` | Environment name (development, staging, production) |
| `LOG_LEVEL` | `INFO` | Logging level |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | _(required)_ | PostgreSQL connection string |
| `NEO4J_URI` | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USER` | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | _(required)_ | Neo4j password |
| `NEO4J_DATABASE` | `neo4j` | Neo4j database name |

### Message Queue (NATS)

| Variable | Default | Description |
|----------|---------|-------------|
| `NATS_URL` | `nats://localhost:4222` | NATS server URL |
| `NATS_CREDS` | `` | NATS credentials file path |
| `NATS_USER_JWT` | `` | NATS user JWT |
| `NATS_USER_NKEY_SEED` | `` | NATS user nkey seed |

### Cache (Redis)

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |
| `UPSTASH_REDIS_REST_URL` | `` | Upstash Redis REST API URL (fallback) |
| `UPSTASH_REDIS_REST_TOKEN` | `` | Upstash Redis REST API token |

### Authentication

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET` | _(required)_ | JWT signing secret |
| `CSRF_SECRET` | `` | CSRF protection secret |
| `WORKOS_CLIENT_ID` | `` | WorkOS OAuth client ID |
| `WORKOS_API_KEY` | `` | WorkOS API key |
| `WORKOS_API_BASE_URL` | `https://api.workos.com` | WorkOS API base URL |
| `SERVICE_TOKEN` | `` | Internal service-to-service bearer token |

### Object Storage (S3)

| Variable | Default | Description |
|----------|---------|-------------|
| `S3_ENDPOINT` | `` | S3-compatible endpoint URL |
| `S3_ACCESS_KEY_ID` | `` | S3 access key ID |
| `S3_SECRET_ACCESS_KEY` | `` | S3 secret access key |
| `S3_BUCKET` | `` | S3 bucket name |
| `S3_REGION` | `us-east-1` | S3 region |

### Cross-Backend Communication

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHON_BACKEND_URL` | `http://127.0.0.1:8000` | Python backend HTTP URL |
| `PYTHON_BACKEND_GRPC_ADDR` | `127.0.0.1:9092` | Python backend gRPC address |

### Temporal Workflow Engine

| Variable | Default | Description |
|----------|---------|-------------|
| `TEMPORAL_HOST` | `localhost:7233` | Temporal server host:port |
| `TEMPORAL_NAMESPACE` | `default` | Temporal namespace |

### Observability (OpenTelemetry)

| Variable | Default | Description |
|----------|---------|-------------|
| `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` | `OTLP_ENDPOINT` fallback | OTLP gRPC collector endpoint |
| `PHENO_OBSERVABILITY_OTLP_HTTP_ENDPOINT` | `OTLP_HTTP_ENDPOINT` fallback | OTLP HTTP collector endpoint |
| `OTLP_ENDPOINT` | `127.0.0.1:4317` | OTLP gRPC fallback endpoint |
| `OTLP_HTTP_ENDPOINT` | `http://127.0.0.1:4318` | OTLP HTTP fallback endpoint |
| `TRACING_ENABLED` | `true` | Enable/disable distributed tracing |
| `TRACING_ENVIRONMENT` | `ENV` fallback | Tracing environment tag |
| `OTEL_SERVICE_NAME` | `tracera-live-backend` | OpenTelemetry service name |

### Sentry Error Tracking

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | `` | Sentry DSN |
| `SENTRY_ENVIRONMENT` | `ENV` fallback | Sentry environment tag |
| `SENTRY_RELEASE` | `unknown` | Sentry release version |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Traces sample rate (0.0–1.0) |
| `SENTRY_DEBUG` | `false` | Enable Sentry debug mode |

### Embeddings Provider

| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_PROVIDER` | `voyage` | Provider: `voyage`, `openrouter`, or `local` |
| `VOYAGE_API_KEY` | `` | VoyageAI API key |
| `VOYAGE_MODEL` | `voyage-3.5` | VoyageAI model name |
| `VOYAGE_DIMENSIONS` | `1024` | Embedding dimensions |
| `OPENROUTER_API_KEY` | `` | OpenRouter API key |
| `OPENROUTER_MODEL` | `openai/text-embedding-3-small` | OpenRouter model name |
| `RERANK_ENABLED` | `true` | Enable reranking |
| `RERANK_MODEL` | `rerank-2.5` | Reranking model name |
| `EMBEDDING_RATE_LIMIT` | `300` | Requests per minute limit |
| `EMBEDDING_TIMEOUT` | `60` | Request timeout in seconds |
| `EMBEDDING_MAX_RETRIES` | `3` | Max retry attempts |
| `EMBEDDING_BATCH_SIZE` | `128` | Max texts per batch |
| `INDEXER_ENABLED` | `true` | Enable background indexer |
| `INDEXER_WORKERS` | `3` | Number of concurrent indexer workers |
| `INDEXER_BATCH_SIZE` | `50` | Items per indexer batch |
| `INDEXER_POLL_INTERVAL` | `30` | Seconds between indexer polls |

### Preflight Checks

| Variable | Default | Description |
|----------|---------|-------------|
| `PREFLIGHT_CHECK_TIMEOUT_SECONDS` | `2` | Timeout (seconds) for individual preflight checks |
| `PREFLIGHT_PYTHON_TIMEOUT_SECONDS` | `5` | Timeout (seconds) for Python backend health check |
| `DEFAULT_POSTGRES_PORT` | `5432` | Default PostgreSQL port for URL resolution |
| `DEFAULT_REDIS_PORT` | `6379` | Default Redis port for URL resolution |
| `DEFAULT_NATS_PORT` | `4222` | Default NATS port for URL resolution |
| `DEFAULT_NEO4J_PORT` | `7687` | Default Neo4j port for URL resolution |
| `DEFAULT_HTTP_PORT` | `80` | Default HTTP port for URL resolution |
| `DEFAULT_HTTPS_PORT` | `443` | Default HTTPS port for URL resolution |

### CORS

| Variable | Default | Description |
|----------|---------|-------------|
| `CORS_ALLOWED_ORIGINS` | `` | Comma-separated allowed CORS origins |

---

## Rust Core (`crates/tracera-core/src/config.rs`)

The Rust config mirrors the Go config for cross-backend parity.
Loaded via `config::load_from_env()`.

### Application

| Variable | Default | Description |
|----------|---------|-------------|
| `ENV` | `development` | Environment name |
| `HTTP_PORT` | `8080` | HTTP server port |
| `HTTP_HOST` | `127.0.0.1` | HTTP server bind host |
| `HTTP_READ_TIMEOUT_SECONDS` | `30` | HTTP read timeout |
| `HTTP_WRITE_TIMEOUT_SECONDS` | `30` | HTTP write timeout |
| `HTTP_SHUTDOWN_TIMEOUT_SECONDS` | `15` | HTTP graceful shutdown timeout |
| `CORS_ALLOWED_ORIGINS` | `` | Comma-separated CORS origins |

### Database (Neo4j)

| Variable | Default | Description |
|----------|---------|-------------|
| `NEO4J_URI` | `` | Neo4j connection URI |
| `NEO4J_USER` | `` | Neo4j username |
| `NEO4J_PASSWORD` | `` | Neo4j password |
| `NEO4J_DATABASE` | `neo4j` | Neo4j database |
| `NEO4J_MAX_POOL_SIZE` | `50` | Max connection pool size |
| `NEO4J_CONNECTION_TIMEOUT_SECONDS` | `30` | Connection timeout |

### Object Storage (S3)

| Variable | Default | Description |
|----------|---------|-------------|
| `S3_BUCKET` | `` | S3 bucket |
| `S3_REGION` | `us-east-1` | S3 region |

### Cross-Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHON_BACKEND_URL` | `http://127.0.0.1:8000` | Python backend URL |
| `PYTHON_BACKEND_GRPC_ADDR` | `127.0.0.1:9092` | Python backend gRPC addr |
| `SERVICE_TOKEN` | `` | Internal service token |

### Observability

| Variable | Default | Description |
|----------|---------|-------------|
| `PHENO_OBSERVABILITY_OTLP_GRPC_ENDPOINT` | → `OTLP_ENDPOINT` | OTLP gRPC endpoint |
| `PHENO_OBSERVABILITY_OTLP_HTTP_ENDPOINT` | → `OTLP_HTTP_ENDPOINT` | OTLP HTTP endpoint |
| `OTLP_ENDPOINT` | `127.0.0.1:4317` | OTLP gRPC fallback |
| `OTLP_HTTP_ENDPOINT` | `http://127.0.0.1:4318` | OTLP HTTP fallback |
| `TRACING_ENABLED` | `true` | Enable tracing |
| `TRACING_ENVIRONMENT` | `ENV` fallback | Tracing environment |
| `OTEL_SERVICE_NAME` | `tracera-live-backend` | Service name for tracing |

### Sentry

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_DSN` | `` | Sentry DSN |
| `SENTRY_ENVIRONMENT` | `ENV` fallback | Sentry environment |
| `SENTRY_RELEASE` | `unknown` | Release version |
| `SENTRY_TRACES_SAMPLE_RATE` | `0.1` | Traces sample rate |
| `SENTRY_DEBUG` | `false` | Sentry debug mode |

### Embeddings

Uses the same env vars as the Go backend. See Go Embeddings section above.

---

## Python Backend (`src/tracertm/`)

The Python backend uses `os.getenv()` with fallback defaults in individual files.
Some services reference config via the `config_manager` module.

### NATS

| Variable | Default | Description |
|----------|---------|-------------|
| `NATS_URL` | `nats://localhost:4222` | NATS server URL |
| `NATS_CREDS_PATH` | `` | NATS credentials file path |

### Cache

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection URL |

### Cross-Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `GO_BACKEND_URL` | `http://localhost:8080` | Go backend URL |
| `SERVICE_TOKEN` | `` | Internal service token |
| `APP_URL` | `http://localhost:8000` | Application base URL |
| `CORS_ORIGINS` | `http://localhost:4000,http://127.0.0.1:4000,...` | Comma-separated CORS origins |

### Temporal

| Variable | Default | Description |
|----------|---------|-------------|
| `TEMPORAL_UI_URL` | `http://localhost:8233` | Temporal Web UI URL |

### Feature Flags

| Variable | Default | Description |
|----------|---------|-------------|
| `NATS_BRIDGE_ENABLED` | `true` | Enable NATS bridge |

---

## Python CLI (`src/tracertm/config/`)

CLI configuration uses `pydantic-settings` with `TRACERTM_` prefix.

### CLI Settings

| Variable / Key | Default | Description |
|----------------|---------|-------------|
| `TRACERTM_CURRENT_PROJECT_ID` | `None` | Currently active project ID |
| `TRACERTM_CURRENT_PROJECT_NAME` | `None` | Currently active project name |
| `TRACERTM_DEFAULT_VIEW` | `FEATURE` | Default view type |
| `TRACERTM_OUTPUT_FORMAT` | `table` | Default output format |
| `TRACERTM_MAX_AGENTS` | `1000` | Max concurrent agents |
| `TRACERTM_CACHE_TTL` | `300` | Cache TTL in seconds |
| `TRACERTM_BATCH_SIZE` | `100` | Batch operation size |
| `TRACERTM_LOG_LEVEL` | `INFO` | Logging level |
| `TRACERTM_ENABLE_CACHE` | `true` | Enable caching |
| `TRACERTM_ENABLE_ASYNC` | `true` | Enable async operations |
| `TRACERTM_ENABLE_VALIDATION` | `true` | Enable strict validation |
| `TRACERTM_CONFIG_DIR` | `~/.tracertm` | Config directory path |
| `DATABASE_URL` | `sqlite:///tracertm.db` | Database URL |
| `TRACERTM_DATABASE_URL` | `DATABASE_URL` fallback | Database URL via TRACERTM_ prefix |

### CLI Schema (`schema.py`)

| Key | Default | Description |
|-----|---------|-------------|
| `database_url` | `None` | Database URL |
| `current_project_id` | `None` | Active project ID |
| `current_project_name` | `None` | Active project name |
| `default_view` | `FEATURE` | Default view type |
| `output_format` | `table` | Output format |
| `max_agents` | `1000` | Max agents (1–10000) |
| `log_level` | `INFO` | Log level |
| `aliases` | `{}` | User command aliases |
| `api_url` | `https://api.tracertm.io` | Sync API URL |
| `api_token` | `None` | JWT API token |
| `api_timeout` | `30.0` | API timeout (1–300s) |
| `api_max_retries` | `3` | Max API retries (1–10) |
| `sync_enabled` | `true` | Enable sync |
| `sync_interval_seconds` | `300` | Auto-sync interval (≥10s) |
| `sync_conflict_strategy` | `last_write_wins` | Conflict resolution |
