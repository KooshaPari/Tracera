# TracerTM Development Workflow

**Version:** 2.0.0
**Date:** January 31, 2026
**Audience:** Developers

## Table of Contents

1. [Quick Start](#quick-start)
2. [Daily Development Workflow](#daily-development-workflow)
3. [Service Management](#service-management)
4. [Debugging Services](#debugging-services)
5. [Viewing Logs](#viewing-logs)
6. [Common Troubleshooting](#common-troubleshooting)
7. [Performance Tips](#performance-tips)
8. [Best Practices](#best-practices)

---

## Quick Start

### First-Time Setup

```bash
# 1. Clone repository
git clone https://github.com/kooshapari/tracertm.git
cd tracertm

# 2. Install dependencies
bun install              # Frontend
cd backend && go mod download  # Go backend
cd .. && pip install -e ".[dev]"  # Python backend

# 3. Install required tools
brew install overmind caddy air temporal
# or
go install github.com/DarthSim/overmind/v2@latest
go install github.com/cosmtrek/air@latest

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your values

# 5. Start all services
overmind start
```

### Verify Installation

```bash
# Check all services are running
overmind ps

# Test health endpoints
curl http://localhost/health        # Gateway
curl http://localhost:8080/health   # Go backend
curl http://localhost:4000/health   # Python backend
curl http://localhost:5173          # Frontend
```

---

## Daily Development Workflow

### Morning Startup

```bash
# 1. Start all services
cd /path/to/tracertm
overmind start

# Expected output:
# system    | Tmux socket name: overmind-tracertm-...
# temporal  | temporal server started on :7233
# caddy     | Caddy server started on :80
# go        | Air watching files...
# python    | Uvicorn running on http://0.0.0.0:8000
# frontend  | VITE v6.x.x ready in XXX ms
# temporal_worker | Worker started, listening on queue 'tracertm-tasks'

# 2. Verify all services
overmind ps
```

### Typical Development Session

```bash
# Option 1: Work in IDE/editor with auto-reload
# Just edit files - changes auto-reload in all services

# Option 2: Monitor a specific service
overmind connect go        # Attach to Go backend
# Press Ctrl+B, then D to detach

# Option 3: Run commands in service context
overmind run go "go test ./..."
overmind run frontend "bun test"
```

### Making Changes

#### Frontend Changes
```bash
# Edit any .tsx/.ts file
# - Vite HMR picks up changes instantly (<100ms)
# - Browser auto-refreshes
# - State preserved when possible

# Run tests while developing
cd frontend/apps/web
bun test --watch
```

#### Go Backend Changes
```bash
# Edit any .go file
# - Air detects changes
# - Recompiles binary (~1-3s)
# - Restarts server
# - Logs appear in overmind

# Check compilation
overmind connect go
# Watch for build errors
```

#### Python Backend Changes
```bash
# Edit any .py file
# - Uvicorn detects changes
# - Reloads worker (<1s)
# - Preserves state
# - Logs appear in overmind

# Run Python tests
pytest tests/ -v --watch
```

### End of Day Shutdown

```bash
# Stop all services gracefully
overmind kill

# Or keep services running for next day
# (Uses ~500MB RAM idle)
```

---

## Service Management

### Starting Services

```bash
# Start all services
overmind start

# Start only specific services
overmind start go python frontend

# Start services in background (no tmux)
overmind start -D

# Start with custom Procfile
overmind start -f Procfile.dev
```

### Stopping Services

```bash
# Stop all services
overmind kill

# Stop specific service
overmind stop go

# Quit overmind (keep services running)
overmind quit
```

### Restarting Services

```bash
# Restart specific service
overmind restart go
overmind restart python
overmind restart frontend

# Restart all services
overmind kill && overmind start
```

### Checking Service Status

```bash
# List all services and their status
overmind ps

# Expected output:
# temporal       | running | pid 12345
# caddy          | running | pid 12346
# go             | running | pid 12347
# python         | running | pid 12348
# frontend       | running | pid 12349
# temporal_worker| running | pid 12350
```

### Connecting to Services (Interactive)

```bash
# Attach to service output
overmind connect <service-name>

# Examples:
overmind connect go        # View Go logs
overmind connect python    # View Python logs
overmind connect frontend  # View Vite output

# Detach from service: Ctrl+B, then D
# Kill service: Ctrl+C (will auto-restart)
```

---

## Debugging Services

### Go Backend Debugging

#### Using Delve (Go Debugger)

```bash
# 1. Stop overmind's go service
overmind stop go

# 2. Start Go backend with debugger
cd backend
dlv debug --headless --listen=:2345 --api-version=2 --accept-multiclient

# 3. In VS Code, attach to :2345
# Or use Goland's remote debugger
```

#### Logging

```go
// Add debug logs
log.Printf("DEBUG: variable = %+v", variable)

// Use structured logging
logger.WithFields(log.Fields{
    "user_id": userID,
    "action": "create_item",
}).Info("Creating item")
```

#### Common Issues

```bash
# Port already in use
lsof -ti:8080 | xargs kill -9

# Database connection failed
psql -U tracertm -d tracertm -h localhost -p 5432

# Redis connection failed
redis-cli ping
```

### Python Backend Debugging

#### Using Debugpy

```python
# Add to src/tracertm/api/main.py
import debugpy
debugpy.listen(5678)
print("Waiting for debugger attach...")
debugpy.wait_for_client()

# In VS Code, attach to :5678
```

#### IPython/PDB

```python
# Add breakpoint in code
import ipdb; ipdb.set_trace()

# Or use built-in
breakpoint()
```

#### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Variable: %s", variable)
logger.info("Operation successful")
logger.error("Error occurred", exc_info=True)
```

### Frontend Debugging

#### Browser DevTools

```javascript
// Add console.log
console.log('State:', state)

// Use React DevTools
// Install browser extension for component inspection

// Use TanStack Query DevTools
// Automatically available in dev mode
```

#### Network Debugging

```bash
# View all API requests
# Open browser DevTools → Network tab
# Filter by "Fetch/XHR"

# Inspect WebSocket connections
# Network tab → WS filter
```

### Database Debugging

```bash
# PostgreSQL
psql -U tracertm -d tracertm
\dt                    # List tables
\d items               # Describe table
SELECT * FROM items LIMIT 10;

# Redis
redis-cli
KEYS tracertm:*        # List keys
GET tracertm:cache:xyz # Get value
FLUSHDB                # Clear database (dev only!)

# Neo4j
# Open http://localhost:7474
# Run Cypher queries in browser
MATCH (n) RETURN n LIMIT 10;
```

---

## Viewing Logs

### Real-time Service Logs

```bash
# View all logs (multiplexed)
overmind echo

# View specific service log
overmind connect <service>

# Examples:
overmind connect go        # Go backend logs
overmind connect python    # Python backend logs
overmind connect frontend  # Vite dev server logs
overmind connect caddy     # Gateway logs
```

### Caddy Gateway Logs

```bash
# Access log (all requests)
tail -f /tmp/caddy-tracertm-access.log | jq '.'

# Error log
tail -f /tmp/caddy-tracertm.log | jq '.'

# Filter by URL pattern
tail -f /tmp/caddy-tracertm-access.log | jq 'select(.request.uri | contains("/api/v1/items"))'
```

### Go Backend Logs

```bash
# View logs in real-time
overmind connect go

# Check build errors
cat backend/tmp/build-errors.log

# View Air logs
cat backend/.air.log
```

### Python Backend Logs

```bash
# View logs in real-time
overmind connect python

# Filter by log level
overmind connect python | grep "ERROR"
overmind connect python | grep "WARNING"

# View with timestamps
overmind connect python | ts
```

### Frontend Logs

```bash
# Vite dev server logs
overmind connect frontend

# Browser console
# Open DevTools → Console tab

# Network requests
# DevTools → Network tab
```

### NATS Logs

```bash
# Monitor NATS
curl http://localhost:8222/varz | jq '.'

# View connections
curl http://localhost:8222/connz | jq '.'

# View subscriptions
curl http://localhost:8222/subsz | jq '.'
```

### Temporal Logs

```bash
# Temporal UI
open http://localhost:8233

# Workflow execution logs
# Click on workflow instance in UI

# Worker logs
overmind connect temporal_worker
```

---

## Common Troubleshooting

### Service Won't Start

#### Port Already in Use

```bash
# Find process using port
lsof -i :8080
lsof -i :8000
lsof -i :5173

# Kill process
kill -9 <PID>

# Or kill all node processes
pkill -f node
pkill -f bun
```

#### Database Connection Failed

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Start PostgreSQL
brew services start postgresql@15

# Check Redis
redis-cli ping

# Start Redis
brew services start redis

# Check Neo4j
curl http://localhost:7474

# Start Neo4j
neo4j start
```

#### Dependency Issues

```bash
# Frontend
cd frontend
rm -rf node_modules bun.lockb
bun install

# Go
cd backend
rm go.sum
go mod download
go mod tidy

# Python
pip install -e ".[dev]" --force-reinstall
```

### Hot Reload Not Working

#### Frontend (Vite)

```bash
# Increase file watcher limit (macOS/Linux)
echo kern.maxfiles=65536 | sudo tee -a /etc/sysctl.conf
echo kern.maxfilesperproc=65536 | sudo tee -a /etc/sysctl.conf
sudo sysctl -w kern.maxfiles=65536
sudo sysctl -w kern.maxfilesperproc=65536

# Clear Vite cache
rm -rf frontend/apps/web/node_modules/.vite
```

#### Go (Air)

```bash
# Verify Air is watching
cd backend
air -d  # Debug mode

# Check .air.toml paths are correct
# Ensure tmp/ directory exists
mkdir -p tmp
```

#### Python (Uvicorn)

```bash
# Ensure --reload flag is set in Procfile
# Check file permissions
ls -la src/tracertm/api/

# Try manual reload
overmind restart python
```

### Performance Issues

#### High CPU Usage

```bash
# Check which service is using CPU
top -o cpu

# Go: Check for infinite loops
overmind connect go

# Python: Enable profiling
pip install py-spy
py-spy top --pid <python-pid>

# Frontend: Check bundle size
cd frontend/apps/web
bun run build --analyze
```

#### High Memory Usage

```bash
# Check memory per service
ps aux | grep -E '(air|uvicorn|bun|caddy)'

# Restart services to free memory
overmind kill && overmind start

# Clear Redis cache
redis-cli FLUSHDB
```

#### Slow API Responses

```bash
# Check Redis cache
redis-cli INFO stats

# Check PostgreSQL queries
psql -U tracertm -d tracertm -c "SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;"

# Check Neo4j queries
# Open http://localhost:7474
# Run: CALL dbms.listQueries()

# Check Caddy logs for slow requests
tail -f /tmp/caddy-tracertm-access.log | jq 'select(.duration > 1000)'
```

### Build Errors

#### Go Build Fails

```bash
# View build errors
cat backend/tmp/build-errors.log

# Clean and rebuild
cd backend
go clean
go build -v ./...

# Update dependencies
go get -u ./...
go mod tidy
```

#### Python Import Errors

```bash
# Reinstall package
pip install -e ".[dev]" --force-reinstall

# Check PYTHONPATH
echo $PYTHONPATH

# Add to .env if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

#### Frontend Build Fails

```bash
# Clear cache and rebuild
cd frontend/apps/web
rm -rf node_modules/.vite dist
bun install
bun run build

# Check TypeScript errors
bun run typecheck
```

---

## Performance Tips

### Optimizing Development Speed

#### Use SSD for Repository

```bash
# Clone to SSD, not HDD
# Improves file watching and rebuilds
```

#### Increase File Watcher Limits

```bash
# macOS
echo kern.maxfiles=65536 | sudo tee -a /etc/sysctl.conf
sudo sysctl -w kern.maxfiles=65536

# Linux
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

#### Configure Exclusions

```bash
# Add to .air.toml
exclude_dir = ["node_modules", ".git", "tmp", "dist", "vendor"]

# Add to .gitignore
.vite/
.turbo/
tmp/
*.log
```

### Memory Optimization

```bash
# Limit Go compilation parallelism
export GOMAXPROCS=4

# Reduce Vite chunk size
# In vite.config.ts:
build: {
  chunkSizeWarningLimit: 1000,
  rollupOptions: {
    output: {
      manualChunks: {...}
    }
  }
}
```

### Network Optimization

```bash
# Use local DNS cache
brew install dnsmasq
# Configure for *.local domains

# Use HTTP/2 (Caddy already configured)
# Use Redis for session storage (configured)
```

---

## Best Practices

### Code Organization

```bash
# Keep Procfile services minimal
# Use scripts/ for complex startup logic
# Store configs in root: Caddyfile, .air.toml, etc.

# Frontend structure
frontend/
  apps/web/          # Main web app
  apps/desktop/      # Desktop app
  packages/          # Shared packages

# Backend structure
backend/
  cmd/              # Entry points
  internal/         # Private code
  pkg/              # Public libraries

# Python structure
src/tracertm/
  api/              # FastAPI routes
  services/         # Business logic
  models/           # Data models
```

### Git Workflow

```bash
# Always work on feature branches
git checkout -b feature/my-feature

# Run tests before committing
bun test
go test ./...
pytest

# Commit with conventional commits
git commit -m "feat: add new feature"
git commit -m "fix: resolve bug"

# Push and create PR
git push origin feature/my-feature
```

### Testing Strategy

```bash
# Run tests frequently
cd frontend/apps/web && bun test --watch
cd backend && go test ./... -v
pytest tests/ --watch

# Run E2E before PR
cd frontend/apps/web
bun run test:e2e

# Check coverage
bun run test:coverage
go test -cover ./...
pytest --cov
```

### Documentation

```bash
# Update README when adding features
# Add inline comments for complex logic
# Keep API docs up-to-date (Swagger/OpenAPI)

# Generate Go docs
godoc -http=:6060

# View Python docs
cd docs && mkdocs serve
```

---

## Quick Reference

### Essential Commands

**Code quality:** Python uses Ruff (lint/format) + ty (typecheck). Go uses golangci-lint (backend). Frontend uses oxlint (lint/typecheck) + oxfmt (format). Pre-commit runs all of these; install with `pre-commit install`.

| Task | Command |
|------|---------|
| Start all services | `overmind start` |
| Stop all services | `overmind kill` |
| Restart service | `overmind restart <service>` |
| View service logs | `overmind connect <service>` |
| Check service status | `overmind ps` |
| Run tests (frontend) | `cd frontend/apps/web && bun test` |
| Run tests (Go) | `cd backend && go test ./...` |
| Run tests (Python) | `pytest tests/` |
| Build frontend | `cd frontend/apps/web && bun run build` |
| Build Go backend | `cd backend && go build ./...` |
| Format code | `cd frontend && bun run format`; `cd backend && gofmt -s -w ./...`; `ruff format .` |
| Lint code | `cd frontend && bun run check`; `cd backend && golangci-lint run`; `ruff check src/` |
| Typecheck (frontend) | `cd frontend && bun run typecheck` |
| Run all pre-commit checks | `pre-commit run --all-files` |

### Port Quick Reference

| Service | Port | URL |
|---------|------|-----|
| Caddy Gateway | 80 | http://localhost |
| Go Backend | 8080 | http://localhost:8080 |
| Python Backend | 8000 | http://localhost:4000 |
| Frontend | 5173 | http://localhost:5173 |
| Temporal UI | 8233 | http://localhost:8233 |
| Neo4j Browser | 7474 | http://localhost:7474 |
| Grafana | 3000 | http://localhost:3000 |

---

## Next Steps

- See [UNIFIED_ARCHITECTURE.md](./UNIFIED_ARCHITECTURE.md) for architecture details
- See [RTM_DEV_QUICK_REFERENCE.md](../reference/RTM_DEV_QUICK_REFERENCE.md) for command cheat sheet
- See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for production deployment

---

**Document Version:** 2.0.0
**Last Updated:** January 31, 2026
**Maintained By:** TracerTM Engineering Team
