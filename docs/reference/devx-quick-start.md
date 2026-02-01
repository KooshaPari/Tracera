# DevX Quick Start Guide

**For new developers joining the TracerTM project**

This guide will get you from zero to productive in **under 30 minutes**.

---

## Prerequisites Check

Before you begin, verify you have these tools installed:

```bash
# Check versions
go version       # Need: 1.21+
python --version # Need: 3.11+
bun --version    # Need: 1.1+
git --version    # Any recent version

# Optional but recommended
uv --version     # Fast Python package manager
air --version    # Go hot reload
watchexec --version  # Config file watching
```

**Missing tools?** See [Installation Guide](/docs/guides/INSTALLATION_VERIFICATION.md)

---

## 1. Clone and Initial Setup (5 minutes)

```bash
# Clone the repository
git clone https://github.com/kooshapari/trace.git
cd trace

# Install native development dependencies
make install-native

# Verify installation
make verify-install
```

**What this does:**
- Installs Process Compose (service orchestration)
- Installs PostgreSQL, Redis, Neo4j, NATS
- Installs Caddy (reverse proxy)
- Installs Prometheus, Grafana (monitoring)

---

## 2. Environment Setup (3 minutes)

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Required:
DATABASE_URL=postgresql://tracertm:password@localhost:5432/tracertm
REDIS_URL=redis://localhost:6379
NEO4J_URI=bolt://localhost:7687
NEO4J_PASSWORD=password

# Optional (for WorkOS auth):
WORKOS_API_KEY=your_api_key
WORKOS_CLIENT_ID=your_client_id
```

---

## 3. Install Project Dependencies (5 minutes)

### Backend (Go)
```bash
cd backend
go mod download
cd ..
```

### Python API/CLI
```bash
# Using uv (recommended - 10x faster):
uv sync --all

# Or using pip:
pip install -e ".[dev]"
```

### Frontend
```bash
cd frontend
bun install
cd ..
```

---

## 4. Run Database Migrations (2 minutes)

**⚠️ IMPORTANT:** Run migrations before starting services to avoid 500 errors!

```bash
# Python (Alembic) migrations
./scripts/run_python_migrations.sh

# Or manually:
# uv run alembic upgrade head
```

---

## 5. Start Development Environment (2 minutes)

### Option A: Interactive TUI Dashboard (Recommended)
```bash
make dev-tui
```

**What you'll see:**
```
┌─────────────────────────────────────────┐
│ Process Compose - TraceRTM             │
├─────────────────────────────────────────┤
│ ✓ postgres        [RUNNING]            │
│ ✓ redis           [RUNNING]            │
│ ✓ neo4j           [RUNNING]            │
│ ✓ nats            [RUNNING]            │
│ ✓ go-backend      [RUNNING]            │
│ ✓ python-backend  [RUNNING]            │
│ ✓ frontend        [RUNNING]            │
│ ✓ caddy           [RUNNING]            │
└─────────────────────────────────────────┘
```

**Controls:**
- `↑/↓` - Navigate processes
- `Enter` - View logs
- `r` - Restart process
- `q` - Quit (stops all services)

### Option B: Background (Detached)
```bash
make dev

# View logs later:
make dev-logs

# Stop services:
make dev-down
```

---

## 6. Verify Everything Works (3 minutes)

### Check Services
```bash
# Gateway (main entry point)
curl http://localhost:4000/api/v1/health
# Expected: {"status": "ok"}

# Go API
curl http://localhost:8080/api/v1/health
# Expected: {"status": "ok"}

# Python API
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Open Web UI
```bash
# macOS:
open http://localhost:4000

# Linux:
xdg-open http://localhost:4000

# Manual:
# Visit http://localhost:4000 in your browser
```

### Check Monitoring
```bash
# Grafana (visualizations)
open http://localhost:3000
# Default credentials: admin/admin

# Prometheus (metrics)
open http://localhost:9090
```

---

## 7. IDE Setup (5 minutes)

### VS Code (Recommended)

```bash
# Install recommended extensions
code --install-extension charliermarsh.ruff
code --install-extension biomejs.biome
code --install-extension golang.go
code --install-extension ms-playwright.playwright
```

**Verify workspace settings:**
1. Open VS Code in project root: `code .`
2. Check `.vscode/settings.json` exists
3. If not, create from template (see below)

<details>
<summary><b>Minimal .vscode/settings.json</b></summary>

```json
{
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "[typescript]": {
    "editor.defaultFormatter": "biomejs.biome"
  },
  "[go]": {
    "editor.defaultFormatter": "golang.go"
  },
  "files.watcherExclude": {
    "**/node_modules/**": true,
    "**/ARCHIVE/**": true,
    "**/.turbo/**": true
  }
}
```
</details>

### JetBrains IDEs (GoLand, PyCharm, WebStorm)

1. **Open project** → Select project root
2. **Configure Python interpreter** → Select `.venv/bin/python`
3. **Configure Go SDK** → Auto-detected from `backend/go.mod`
4. **Enable formatters:**
   - Python: Settings → Tools → Ruff → Enable
   - TypeScript: Settings → Languages → JavaScript → Biome
   - Go: Settings → Tools → Go → Enable gofmt

### Neovim/Vim

```lua
-- Add to your init.lua or init.vim
-- LSP configurations for Go, Python, TypeScript
require('lspconfig').gopls.setup{}
require('lspconfig').pylsp.setup{
  settings = {
    pylsp = {
      plugins = {
        ruff = { enabled = true },
        mypy = { enabled = true }
      }
    }
  }
}
require('lspconfig').tsserver.setup{}
```

---

## 8. Run Your First Test (2 minutes)

### Frontend Tests (Vitest)
```bash
cd frontend/apps/web
bun test

# Watch mode (re-runs on file changes):
bun test --watch

# With UI:
bun test --ui
```

### Backend Go Tests
```bash
cd backend
go test ./internal/... -v

# With coverage:
go test ./internal/... -cover
```

### Python Tests
```bash
pytest tests/ -v

# With coverage:
pytest tests/ --cov=src/tracertm --cov-report=html
# Open htmlcov/index.html
```

---

## 9. Make Your First Change (5 minutes)

### Example: Add a new API endpoint

1. **Edit backend handler** (`backend/internal/handlers/example.go`):
   ```go
   func HandleExample(w http.ResponseWriter, r *http.Request) {
       json.NewEncoder(w).Encode(map[string]string{
           "message": "Hello from my new endpoint!",
       })
   }
   ```

2. **Hot reload automatically detects change** (no restart needed!)

3. **Test endpoint**:
   ```bash
   curl http://localhost:8080/api/v1/example
   ```

4. **See logs in Process Compose TUI** (if running `make dev-tui`)

---

## 10. Quality Checks Before Committing (3 minutes)

### Run all quality checks
```bash
# From project root:
make quality

# This runs:
# - Go: lint, build, test
# - Python: ruff, mypy, basedpyright, tach, pytest
# - Frontend: lint, typecheck, build, test
```

### Or run individually:
```bash
# Go only
make quality-go

# Python only
make quality-python

# Frontend only
make quality-frontend
```

### Pre-commit hooks (automatic)
```bash
# Install hooks
pre-commit install

# Now every commit automatically runs:
# - ruff (format + lint)
# - mypy (type checking)
# - basedpyright (strict type checking)
# - gofmt (Go formatting)
# - biome (frontend lint + format)
# - ... and more!
```

---

## Common Development Tasks

### Restart a specific service
```bash
# From TUI: select process and press 'r'

# From command line:
make dev-restart SERVICE=go-backend
make dev-restart SERVICE=frontend
make dev-restart SERVICE=postgres
```

### View logs for a service
```bash
# From TUI: select process and press Enter

# From command line:
make dev-logs-follow SERVICE=go-backend

# All logs:
make dev-logs
```

### Reset database
```bash
# Drops all tables and re-runs migrations
make db-reset

# Or manually:
uv run alembic downgrade base
uv run alembic upgrade head
```

### Generate OpenAPI types (after API changes)
```bash
# Frontend TypeScript types:
cd frontend/apps/web
bun run generate:types

# Python client:
./scripts/generate-python-client.sh

# Go client:
./scripts/generate-openapi-go.sh
```

### Run E2E tests
```bash
cd frontend/apps/web

# Interactive UI mode:
bun run test:e2e:ui

# Headless mode:
bun run test:e2e

# Debug mode:
bun run test:e2e:debug
```

---

## Debugging Tips

### Debug Go backend
```bash
# VS Code: F5 (uses .vscode/launch.json config)

# Manual with delve:
cd backend
dlv debug ./cmd/api -- --port 8080
```

### Debug Python backend
```bash
# VS Code: F5 (uses .vscode/launch.json config)

# Manual with debugpy:
python -m debugpy --listen 5678 --wait-for-client src/tracertm/api.py
```

### Debug frontend
```bash
# VS Code: F5 (launches Chrome with debugger attached)

# Browser DevTools:
# Open http://localhost:5173
# F12 → Sources tab → Set breakpoints
```

### View Process Compose logs
```bash
# Real-time logs for all services:
process-compose logs -f

# Specific service:
process-compose logs -f go-backend

# Or check file logs:
cat .process-compose/logs/go-backend.log
```

---

## Performance Optimization

### Frontend build times
```bash
# Use Turborepo cache:
cd frontend
bun run build  # First build: ~45-60s
bun run build  # Second build: ~5s (cached!)

# Fast build (skip typechecking):
bun run build:fast
```

### Python tests in parallel
```bash
# Install pytest-xdist:
uv add pytest-xdist --dev

# Run tests in parallel:
pytest tests/ -n auto
# ~2x faster on multi-core CPUs
```

### Go test caching
```bash
# Go automatically caches test results
# Re-run only changed tests:
go test ./internal/... -v

# Force re-run all:
go test ./internal/... -count=1
```

---

## Troubleshooting

### Services won't start

**Problem:** `Error: address already in use`

**Solution:**
```bash
# Check what's using the port:
lsof -i :8080  # Go backend
lsof -i :5173  # Frontend
lsof -i :5432  # PostgreSQL

# Kill process:
kill -9 <PID>

# Or use wrapper scripts (they check before starting):
bash scripts/postgres-if-not-running.sh
```

### Hot reload not working

**Problem:** File changes don't trigger rebuilds

**Solution:**
```bash
# Increase file watcher limit (Linux):
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Restart watcher service:
make dev-restart SERVICE=go-backend
```

### Database connection errors

**Problem:** `could not connect to database`

**Solution:**
```bash
# Check PostgreSQL is running:
pg_isready -h localhost -p 5432

# Verify credentials in .env:
DATABASE_URL=postgresql://tracertm:password@localhost:5432/tracertm

# Run migrations:
./scripts/run_python_migrations.sh
```

### Frontend build errors

**Problem:** `Module not found` or `Cannot find module`

**Solution:**
```bash
# Clear caches and reinstall:
cd frontend
rm -rf node_modules .turbo dist
bun install

# Regenerate OpenAPI types:
cd apps/web
bun run generate:types
```

### Tests failing

**Problem:** Random test failures

**Solution:**
```bash
# Run tests in isolation:
pytest tests/test_item.py::test_create_item -v

# Clear test caches:
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type d -name ".pytest_cache" -exec rm -rf {} +

# Frontend tests:
cd frontend/apps/web
bun test --run  # Force re-run (no watch mode)
```

---

## Next Steps

Now that you're set up, explore:

1. **📚 [Architecture Overview](/docs/guides/ARCHITECTURE.md)** - System design
2. **🧪 [Testing Guide](/docs/guides/TESTING_GUIDE.md)** - Writing tests
3. **🚀 [Deployment Guide](/docs/guides/DEPLOYMENT_GUIDE.md)** - Production deployment
4. **📖 [API Documentation](http://localhost:4000/docs)** - Interactive API docs
5. **🔍 [DevX Analysis](/docs/research/codebase-devx-analysis.md)** - Deep dive into tooling

---

## Getting Help

### Documentation
- **Main README:** [/README.md](/README.md)
- **Guides:** [/docs/guides/](/docs/guides/)
- **Checklists:** [/docs/checklists/](/docs/checklists/)

### Internal Tools
- **Process Compose TUI:** `make dev-tui` (interactive dashboard)
- **Grafana Dashboards:** http://localhost:3000
- **Prometheus Metrics:** http://localhost:9090

### Commands Reference
```bash
# Show all available commands:
make help

# Quality checks:
make quality          # All languages
make quality-go       # Go only
make quality-python   # Python only
make quality-frontend # Frontend only

# Testing:
make test             # All tests
make test-go          # Go tests
make test-python      # Python tests

# Development:
make dev              # Start services (background)
make dev-tui          # Start services (interactive)
make dev-down         # Stop all services
make dev-status       # Show service status

# Database:
make db-migrate       # Run migrations
make db-reset         # Reset database
make db-shell         # Open psql shell

# Monitoring:
make grafana-dashboard  # Open Grafana
make prometheus-ui      # Open Prometheus
make metrics            # Show quick metrics
```

---

## Estimated Setup Time

| Step | Time | Can Skip? |
|------|------|-----------|
| 1. Clone and initial setup | 5 min | ❌ Required |
| 2. Environment setup | 3 min | ❌ Required |
| 3. Install dependencies | 5 min | ❌ Required |
| 4. Run migrations | 2 min | ❌ Required |
| 5. Start dev environment | 2 min | ❌ Required |
| 6. Verify everything works | 3 min | ⚠️ Recommended |
| 7. IDE setup | 5 min | ⚠️ Recommended |
| 8. Run first test | 2 min | ✅ Optional |
| 9. Make first change | 5 min | ✅ Optional |
| 10. Quality checks | 3 min | ✅ Optional |

**Total minimum time:** ~17 minutes
**Total with recommended steps:** ~25 minutes
**Total with optional exploration:** ~35 minutes

---

## Checklist

Mark these off as you complete them:

- [ ] Installed native dependencies (`make install-native`)
- [ ] Created `.env` file with required variables
- [ ] Installed Go, Python, Frontend dependencies
- [ ] Ran database migrations
- [ ] Started development environment (`make dev-tui`)
- [ ] Verified services are running (health checks pass)
- [ ] Configured IDE (VS Code/JetBrains/Neovim)
- [ ] Ran first test successfully
- [ ] Made a small code change and saw hot reload
- [ ] Ran quality checks (`make quality`)
- [ ] Installed pre-commit hooks (`pre-commit install`)
- [ ] Explored monitoring dashboards (Grafana, Prometheus)

**Congratulations!** 🎉 You're ready to contribute to TracerTM.
