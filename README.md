# TracerTM

Agent-native, multi-view requirements traceability and project management system.

## Overview

TracerTM is a comprehensive requirements traceability matrix (RTM) system designed for modern software development workflows. It provides:

- **Multi-view project management** - View your projects through code, API, database, deployment, and documentation lenses
- **AI agent integration** - Native support for AI-assisted traceability and analysis
- **Real-time sync** - WebSocket-based live updates across all clients
- **Graph visualization** - Interactive dependency graphs and impact analysis
- **Full traceability** - Link requirements to code, tests, and deployments

## Root layout (tier 1)

- **`deploy/`** – k8s, infrastructure, nginx, monitoring, Procfile  
- **`data/`** – backup, exports, tmp, test.db, runtime artifacts  
- **`samples/`** – DEMO_PROJECT, examples  
- **`config/`** – process-compose, Caddy, redis.conf  
- **`docs/`** – documentation; **`docs/site/`** – Fumadocs site  
- **`load-tests/`** – load test scripts; **`load-tests/results/`** – k6 output  

## Architecture

The system consists of three main components:

- **Backend** (Go) - High-performance API server with PostgreSQL, Neo4j, and NATS
- **Frontend** (TypeScript/React) - Modern SPA with TanStack Router and Zustand
- **Python CLI/TUI** - Terminal interface with Textual for local workflows

## Getting Started

### First run (new clone or new environment)

Before starting services, run database migrations so project pages (Test Cases, Links, Graphs, Test Runs) don’t return 500:

1. Set **DATABASE_URL** (or **TRACERTM_DATABASE_URL**) in `.env`.
2. Run **Python (Alembic) migrations**: `./scripts/shell/run_python_migrations.sh` (or `uv run alembic upgrade head`).

Full steps (deps, env, Go migrations if any, Python migrations, start): **[First Run Checklist](/docs/checklists/FIRST_RUN_CHECKLIST.md)**.

### Prerequisites

**Required:**
- **Process Compose** - Process orchestration (installed via setup script)
- **PostgreSQL** 17+ - Main database
- **Redis** 7+ - Cache and sessions
- **Python** 3.11+ - Backend services
- **Go** 1.21+ - API server
- **Node.js/Bun** - Frontend build

**Optional (installed via setup script):**
- **Neo4j** 5.0+ - Graph features
- **NATS** 2.9+ - Real-time messaging
- **Temporal** - Workflow engine
- **Caddy** 2.7+ - Reverse proxy
- **Prometheus** - Metrics collection
- **Grafana** - Visualization

### Quick Start (Native Process Orchestration)

The new native development environment uses Process Compose to orchestrate all services as native processes, eliminating Docker daemon overhead.

```bash
# One-time installation of all dependencies
make install-native

# Run Python DB migrations (required for Test Cases, Links, Graphs — avoid 500s)
./scripts/shell/run_python_migrations.sh

# Start all services with interactive dashboard
make dev-tui

# Or start in background
make dev

# Access the application (use the gateway only – do not open port 5173 directly)
# Gateway:    http://localhost:4000   ← single dev URL (frontend + API + docs)
# Go API:     http://localhost:8080   (internal; use /api/v1/* via gateway)
# Python API: http://localhost:4000   (internal; use /api/py/* via gateway)
# Grafana:    http://localhost:3000
# Prometheus: http://localhost:9090
```

### Traditional Setup (Individual Services)

If you prefer to run services individually:

#### Backend

```bash
cd backend
go build ./...
go run ./cmd/api
```

#### Frontend

```bash
cd frontend
bun install
bun run dev
```

#### Python CLI

```bash
pip install -e .
tracertm --help
```

## Development Environment

### Native Process Architecture

All services run as native processes orchestrated by Process Compose:

```
http://localhost:4000 (Caddy Gateway)
├── /api/v1/*      → Go API server (:8080)
├── /api/py/*      → Python API server (:8000)
├── /docs          → API documentation
├── /prometheus/*  → Prometheus metrics
├── /grafana/*     → Grafana dashboards
└── /ws/*          → WebSocket connections

Native Services:
├── PostgreSQL     → :5432
├── Redis          → :6379
├── Neo4j          → :7687, :7474
├── NATS           → :4222, :8222
├── Temporal       → :7233
├── Prometheus     → :9090
└── Grafana        → :3000
```

### Benefits

- **Resource Efficient** - 60-80% less memory/CPU vs Docker
- **Native Performance** - Direct system access, no virtualization
- **Cross-Platform** - macOS, Linux, Windows support
- **Single Port** - Unified gateway on port 4000 (use **http://localhost:4000** only; Vite on 5173 is internal)
- **No CORS** - All services on same origin when using the gateway
- **Hot Reload** - All services support live reloading
- **Process Management** - Process Compose TUI dashboard
- **Easy Debugging** - Direct process access, no container exec

### Development Commands

```bash
# Start all services (detached)
make dev

# Start with interactive TUI dashboard
make dev-tui

# View logs for all services
make dev-logs

# View logs for specific service
make dev-logs-follow SERVICE=go-backend

# Restart specific service
make dev-restart SERVICE=postgres

# Show service status
make dev-status

# Stop all services
make dev-down

# Scale a service (run multiple instances)
make dev-scale SERVICE=worker REPLICAS=3

# Open monitoring dashboards
make grafana-dashboard   # Opens Grafana
make prometheus-ui       # Opens Prometheus
```

### Port Configuration

**Use http://localhost:4000 as the only dev URL.** The frontend (Vite) runs on 5173 internally; Caddy proxies it. Do not open port 5173 in the browser.

| Service | Port | Access |
|---------|------|--------|
| Caddy (Gateway) | 4000 | **http://localhost:4000** (frontend + API + doc sites – use this only) |
| Go API | 8080 | Via gateway /api/v1/* |
| Python API | 8000 | Via gateway /api/py/* |
| Doc site (Next.js) | 3001 | http://localhost:3001 or http://localhost:4000/documentation |
| Storybook | 6006 | http://localhost:6006 or http://localhost:4000/storybook |
| PostgreSQL | 5432 | localhost:5432 |
| Redis | 6379 | localhost:6379 |
| Neo4j (Bolt) | 7687 | bolt://localhost:7687 |
| Neo4j (HTTP) | 7474 | http://localhost:7474 |
| NATS | 4222 | nats://localhost:4222 |
| NATS Monitor | 8222 | http://localhost:8222 |
| Temporal | 7233 | localhost:7233 |
| Prometheus | 9090 | http://localhost:9090 |
| Grafana | 3000 | http://localhost:3000 |
| Loki | 3100 | http://localhost:3100 |
| Promtail | 9080 | http://localhost:9080 |
| Jaeger UI | 16686 | http://localhost:16686 |
| Postgres Exporter | 9187 | http://localhost:9187/metrics |
| Redis Exporter | 9121 | http://localhost:9121/metrics |
| Node Exporter | 9100 | http://localhost:9100/metrics |

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/tracertm
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# NATS
NATS_URL=nats://localhost:4222

# API
API_PORT=8080
FRONTEND_PORT=5173   # Internal only; use gateway http://localhost:4000
PROXY_PORT=4000

# Auth (WorkOS)
WORKOS_API_KEY=your_api_key
WORKOS_CLIENT_ID=your_client_id
```

See `.env.example` for a complete list of configuration options.

### Secrets Management

For production deployments, use HashiCorp Vault for secure secrets management:

```bash
# Local dev: use .env (fastest)
cp .env.example .env
# Edit .env with USE_VAULT=false

# Local dev with Vault (for testing)
make dev  # Vault starts automatically
./scripts/shell/vault-setup-secrets.sh .env
# Edit .env with USE_VAULT=true

# Production: use proper Vault setup
# See docs/guides/SECRETS_MANAGEMENT.md for details
```

**Documentation:**
- **Full Guide:** [Secrets Management Guide](/docs/guides/SECRETS_MANAGEMENT.md)
- **Quick Reference:** [Vault Quick Reference](/docs/reference/VAULT_QUICK_REFERENCE.md)

## Observability

TracerTM includes comprehensive observability with metrics, logs, and distributed tracing.

### Metrics (Prometheus + Grafana)

- **Prometheus**: Collects metrics from all services
- **Grafana**: Visualizes metrics with pre-built dashboards
- **Exporters**: Postgres, Redis, and Node metrics

Access Grafana at http://localhost:3000 (admin/admin)

### Log Aggregation (Loki + Promtail)

- **Loki**: Centralized log storage and querying
- **Promtail**: Collects logs from all services
- **Structured Logging**: JSON logs with context for powerful queries

```bash
# Check Loki installation
./scripts/shell/check-loki-installation.sh

# View logs in Grafana
# 1. Open http://localhost:3000/explore
# 2. Select "Loki" data source
# 3. Run queries like: {job="python-backend"} | json | level="ERROR"
```

**Structured Logging Example:**

```python
from tracertm.logging_config import get_structlog_logger

logger = get_structlog_logger(__name__)
logger.info("user_login", user_id=user.id, ip=request.client.host)
```

**Log Retention:**
- Loki: 7 days (local development)
- Error logs: 30 days (file-based)

### Distributed Tracing & APM (Jaeger + OpenTelemetry)

TraceRTM includes comprehensive Application Performance Monitoring (APM):

- **Distributed Tracing**: Track requests across Go and Python backends
- **Database Instrumentation**: Trace SQL queries and optimize performance
- **HTTP Client Tracing**: Monitor external API calls
- **Custom Instrumentation**: Add tracing to your own code

**Access Points:**
- **Jaeger UI**: http://localhost:16686 - Search traces, view timelines
- **Grafana APM Dashboards**: http://localhost:3001 - Performance metrics
  - APM Performance: Response times, throughput, cache metrics
  - Distributed Tracing: Trace analysis, error rates, top endpoints

**Quick Start:**

```bash
# 1. Enable tracing in .env
TRACING_ENABLED=true
JAEGER_ENDPOINT=localhost:4317
TRACING_ENVIRONMENT=development

# 2. Start services
make dev

# 3. View traces
# - Jaeger UI: http://localhost:16686
# - Grafana: http://localhost:3001 → Dashboards → APM Performance
```

**Instrumentation:**

```go
// Go Backend - Database tracing
import "github.com/kooshapari/tracertm-backend/internal/tracing"

ctx, dbSpan := tracing.StartDBSpan(ctx, tracing.dbOperationSelect, "items")
defer dbSpan.End()
dbSpan.SetQuery("SELECT * FROM items WHERE id = $1")
```

```python
# Python Backend - Custom tracing
from tracertm.observability import trace_method

@trace_method(span_name="process_data")
async def process_data(data: dict) -> Result:
    return result
```

Access Jaeger UI at http://localhost:16686

**Documentation:**
- [Structured Logging Guide](/docs/guides/structured-logging-guide.md)
- [Adding Structured Logging Examples](/docs/guides/adding-structured-logging-example.md)
- [Loki Quick Reference](/docs/reference/loki-quick-reference.md)

## Development

### Running Tests

```bash
# Go backend
cd backend && go test ./internal/...

# Frontend
cd frontend && bun test

# Python
pytest tests/

# E2E tests (requires running services)
cd frontend/apps/web && bun run test:e2e
```

### Linting & typechecking

```bash
# Run fast pre-commit checks (<5s - recommended for commits)
pre-commit run --all-files

# Measure pre-commit performance
./scripts/shell/measure-precommit-performance.sh

# Run comprehensive checks (CI-level validation)
# Type checking
uv run mypy src/
uv run basedpyright src/

# Security scanning
uv run bandit -r src/
semgrep --config=p/security-audit src/

# Architecture validation
uv run tach check

# Per language quick checks
cd backend && golangci-lint run          # Go (lint + fmt)
cd frontend && bun run check            # Frontend (Biome lint + format)
cd frontend && bun run typecheck        # Frontend TypeScript
ruff check src/ && ruff format --check . # Python
```

**Note**: Pre-commit hooks are optimized for speed (<5s). Comprehensive checks (type checking, security scans, tests) run in CI. See [Pre-commit Optimization Guide](docs/guides/quick-start/PRE_COMMIT_OPTIMIZATION.md) for details.

### Dependency Management

TracerTM uses Dependabot for automated dependency updates across all package ecosystems:

```bash
# List Dependabot PRs
gh pr list --author "dependabot[bot]"

# Validate Dependabot configuration
./scripts/shell/validate-dependabot.sh

# View update schedules and auto-merge rules
cat .github/dependabot.yml
```

**Auto-merge policy**:
- ✅ Patch updates (x.y.Z) - Auto-merged after tests pass
- ✅ Minor updates (x.Y.z) - Auto-merged after tests pass
- ⚠️ Major updates (X.y.z) - Require manual review

**Resources**:
- **[Dependabot Guide](/docs/guides/DEPENDABOT_GUIDE.md)** - Full configuration and usage
- **[Quick Reference](/docs/reference/DEPENDABOT_QUICK_REFERENCE.md)** - Common commands

### Debugging

```bash
# Connect to a running service for interactive debugging
overmind connect api        # Go API
overmind connect frontend   # Frontend
overmind connect python     # Python CLI

# View real-time logs
rtm dev logs --follow api

# Restart a misbehaving service
overmind restart api
```

## Documentation

- **[First Run Checklist](/docs/checklists/FIRST_RUN_CHECKLIST.md)** - New clone setup (deps, env, migrations, start)
- **[Installation Verification Guide](/docs/guides/INSTALLATION_VERIFICATION.md)** - First-time setup walkthrough
- **[E2E Verification Checklist](/docs/checklists/E2E_VERIFICATION_CHECKLIST.md)** - Complete system testing
- **[Testing Matrix](/docs/checklists/TESTING_MATRIX.md)** - Test phases and criteria
- **[Deployment Guide](/docs/guides/DEPLOYMENT_GUIDE.md)** - Production deployment procedures
- **[API Documentation](http://localhost:4000/docs)** - Interactive API explorer (when running)

## Troubleshooting

### Services won't start

```bash
# Check if required tools are installed
make verify-install

# Check process status
make dev-status

# View logs for failing service
make dev-logs-follow SERVICE=postgres

# Restart specific service
make dev-restart SERVICE=redis

# Clean logs and restart
make logs-clean && make dev
```

### Hot reload not working

```bash
# Restart the specific service
overmind restart frontend
overmind restart api

# Check if file watchers are at system limit
sysctl fs.inotify.max_user_watches  # Linux
# Increase if needed: sudo sysctl -w fs.inotify.max_user_watches=524288
```

### Database connection issues

```bash
# Verify PostgreSQL is running
pg_isready -h localhost -p 5432

# Check Neo4j status
cypher-shell "RETURN 1"

# Reset databases (destructive!)
make db-reset
```

### Process Compose issues

```bash
# View Process Compose version
process-compose version

# Validate configuration
process-compose config

# Check for config errors
process-compose -f config/process-compose.yaml validate

# Start with debug logging
PROCESS_COMPOSE_LOG_LEVEL=debug make dev-tui

# Force stop all processes
pkill -f "process-compose"
```

For more troubleshooting, see [Installation Verification Guide](/docs/guides/INSTALLATION_VERIFICATION.md).

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see LICENSE file for details.
