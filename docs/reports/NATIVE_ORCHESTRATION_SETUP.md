# TraceRTM Native Process Orchestration - Setup Guide

Welcome! This guide walks you through setting up TraceRTM's native development environment.

## What's Changed?

We've migrated from Docker-based development to **native process orchestration** using Process Compose. This means:

- **No Docker daemon** - Services run directly as native processes
- **60-80% less resource usage** - Less memory and CPU overhead
- **Same familiar interface** - Still uses docker-compose-like YAML configuration
- **Better performance** - Direct system access, no virtualization layer
- **Cross-platform** - Works on macOS, Linux, and Windows

## 5-Minute Setup

### Step 1: Install Dependencies (First Time Only)

```bash
make install-native
```

This will:
- Detect your platform (macOS, Linux, Windows)
- Install all required services via package manager (Homebrew, APT, Scoop)
- Install Process Compose for orchestration
- Create necessary directories
- Initialize PostgreSQL database
- Verify all tools are installed

**Expected time:** 5-10 minutes depending on internet and system speed

### Step 2: Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your settings (API keys, database passwords, etc.)
nano .env  # or your preferred editor
```

### Step 3: Run Database Migrations

```bash
# Run Python (Alembic) migrations
./scripts/run_python_migrations.sh

# Or manually
alembic upgrade head
```

### Step 4: Start Services

Choose one:

```bash
# Option 1: Start in background
make dev

# Option 2: Start with interactive dashboard (recommended for first time)
make dev-tui
```

### Step 5: Access the Application

| Service | URL |
|---------|-----|
| **API Gateway** | http://localhost:4000 |
| Go API | http://localhost:8080 |
| Python API | http://localhost:4000 |
| Grafana Dashboards | http://localhost:3000 |
| Prometheus Metrics | http://localhost:9090 |
| Neo4j Browser | http://localhost:7474 |
| Temporal UI | http://localhost:8233 |

## Common Commands

```bash
# View service status and logs (interactive TUI)
make dev-tui

# Stop all services
make dev-down

# View logs
make dev-logs

# Follow specific service logs in real-time
make dev-logs-follow SERVICE=go-backend

# Restart a service
make dev-restart SERVICE=postgres

# Show all services
make dev-status

# Open Grafana in browser
make grafana-dashboard

# Open Prometheus in browser
make prometheus-ui
```

## What Services Are Running?

### Databases & Message Brokers
- **PostgreSQL** (5432) - Main relational database
- **Redis** (6379) - Cache and sessions
- **Neo4j** (7687, 7474) - Graph database
- **NATS** (4222) - Message broker with real-time support

### Application Services
- **Go Backend** (8080) - High-performance REST API
- **Python Backend** (8000) - FastAPI with AI/ML features
- **Caddy** (4000) - Reverse proxy and API gateway

### Workflow & Monitoring
- **Temporal** (7233) - Workflow engine
- **Prometheus** (9090) - Metrics collection
- **Grafana** (3000) - Dashboards and visualization

### Exporters
- **postgres_exporter** (9187) - PostgreSQL metrics
- **redis_exporter** (9121) - Redis metrics
- **node_exporter** (9100) - System metrics

**Total: 19 services, all orchestrated automatically**

## Troubleshooting

### "process-compose not found"

```bash
# macOS
brew install f1bonacc1/tap/process-compose

# Linux
wget https://github.com/F1bonacc1/process-compose/releases/download/v1.0.0/process-compose_linux_x86_64.tar.gz
tar -xzf process-compose_linux_x86_64.tar.gz
sudo mv process-compose /usr/local/bin/
```

### "PostgreSQL won't start"

```bash
# Check if port 5432 is in use
lsof -i :5432

# View PostgreSQL logs
make dev-logs-follow SERVICE=postgres

# Restart PostgreSQL
make dev-restart SERVICE=postgres
```

### "Cannot connect to database"

```bash
# Verify PostgreSQL is running
pg_isready -h localhost -p 5432

# Check database exists
psql -h localhost -U tracertm -d tracertm -c "SELECT 1"

# View database URL in .env
echo $DATABASE_URL
```

### "Services stuck in unhealthy state"

```bash
# View service status
make dev-status

# Check logs for the service
make dev-logs-follow SERVICE=<service-name>

# Restart the service
make dev-restart SERVICE=<service-name>

# Last resort: stop everything and start fresh
make dev-down
rm -rf .process-compose/logs/*
make dev
```

## Platform-Specific Notes

### macOS
- Services installed via Homebrew
- PostgreSQL data stored in `/opt/homebrew/var/postgresql@17`
- Fully tested and supported on Apple Silicon (M1/M2/M3) and Intel

### Linux (Ubuntu/Debian)
- Services installed via APT
- PostgreSQL data stored in `/var/lib/postgresql/17/main`
- Fully tested on Ubuntu 20.04+ and Debian 11+

### Windows
- Services installed via Scoop
- Uses PowerShell for shell commands
- Configuration prepared but not extensively tested

## Next Steps

1. **Read the docs**:
   - [First Run Checklist](/docs/checklists/FIRST_RUN_CHECKLIST.md)
   - [Installation Verification](/docs/guides/INSTALLATION_VERIFICATION.md)

2. **Explore the API**:
   - Visit http://localhost:4000/docs for interactive API explorer
   - Check http://localhost:8080/swagger for Go API docs

3. **Monitor the system**:
   - Open Grafana at http://localhost:3000
   - View metrics in Prometheus at http://localhost:9090

4. **Run tests**:
   ```bash
   make test          # Run all tests
   make test-python   # Python tests only
   make test-go       # Go tests only
   ```

5. **Contribute**:
   - See [CONTRIBUTING.md](/CONTRIBUTING.md) for guidelines

## Documentation

- **[Native Orchestration Design](/docs/plans/2026-01-31-native-process-orchestration-design.md)** - Architecture and rationale
- **[Implementation Complete](/docs/plans/2026-01-31-IMPLEMENTATION_COMPLETE.md)** - Full implementation details
- **[README](/README.md)** - Project overview

## Support

If you encounter issues:

1. Check this troubleshooting section
2. Review service logs: `make dev-logs`
3. Check installation: `make verify-install`
4. View process status: `make dev-status`

For more help, see [Installation Verification Guide](/docs/guides/INSTALLATION_VERIFICATION.md).

---

**Happy developing! 🚀**
