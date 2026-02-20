# Dev Container Setup Guide for TracerTM

## Overview

This guide provides step-by-step instructions for setting up a development container (devcontainer) for TracerTM, enabling cloud-based development with GitHub Codespaces, Gitpod, or local Remote Containers.

**What You'll Get:**
- One-click development environment setup
- All dependencies pre-installed (Go, Python, Node.js, Bun)
- Database services (PostgreSQL, Redis, Neo4j)
- Monitoring stack (Prometheus, Grafana)
- Hot reload for all services
- Consistent environment across all developers

---

## Quick Start

### GitHub Codespaces

1. Open TracerTM repository on GitHub
2. Click green "Code" button → "Codespaces" tab
3. Click "Create codespace on main"
4. Wait 2-5 minutes for container to build
5. Run `make dev-tui` to start all services

**First time:** Container builds all layers (~5 min)
**Subsequent:** Uses prebuild (~30 seconds)

### Gitpod

1. Go to `https://gitpod.io/#https://github.com/YOUR_ORG/tracertm`
2. Authorize Gitpod with GitHub
3. Wait for workspace to start (~1-2 min)
4. Services start automatically via .gitpod.yml

### Local (VS Code Remote Containers)

1. Install Docker Desktop
2. Install VS Code extension: "Dev Containers"
3. Open TracerTM folder in VS Code
4. Press `Cmd+Shift+P` → "Dev Containers: Reopen in Container"
5. Wait for container to build
6. Run `make dev-tui`

---

## File Structure

```
tracertm/
├── .devcontainer/
│   ├── devcontainer.json       # Main configuration
│   ├── docker-compose.yml      # Services (DB, Redis, etc.)
│   ├── Dockerfile              # Development image
│   └── postCreate.sh           # Post-creation setup script
├── .gitpod.yml                 # Gitpod configuration
└── docker-compose.yml          # Production/standalone compose
```

---

## Configuration Files

### 1. devcontainer.json

Located at `.devcontainer/devcontainer.json`, this file defines:
- Base Docker image or Dockerfile
- VS Code extensions to install
- Port forwarding
- Environment variables
- Post-creation commands

See [.devcontainer/devcontainer.json](/.devcontainer/devcontainer.json) for the complete configuration.

### 2. docker-compose.yml

Located at `.devcontainer/docker-compose.yml`, defines:
- Application service (workspace)
- PostgreSQL database
- Redis cache
- Neo4j graph database
- NATS messaging
- Temporal workflow engine
- Monitoring services

### 3. Dockerfile

Located at `.devcontainer/Dockerfile`, defines:
- Base image (Ubuntu with multiple language runtimes)
- Installed tools (Go, Python, Node.js, Bun)
- System dependencies
- Development utilities

### 4. postCreate.sh

Located at `.devcontainer/postCreate.sh`, runs after container creation:
- Installs project dependencies
- Runs database migrations
- Seeds database with sample data
- Sets up Git hooks

---

## devcontainer.json Features

### Recommended Extensions

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        // Go
        "golang.go",

        // Python
        "ms-python.python",
        "ms-python.vscode-pylance",

        // JavaScript/TypeScript
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",

        // Docker
        "ms-azuretools.vscode-docker",

        // Database
        "mtxr.sqltools",
        "mtxr.sqltools-driver-pg",

        // Git
        "eamodio.gitlens",

        // Utilities
        "streetsidesoftware.code-spell-checker",
        "editorconfig.editorconfig"
      ]
    }
  }
}
```

### Port Forwarding

```json
{
  "forwardPorts": [
    4000,  // Caddy gateway
    8080,  // Go backend
    8000,  // Python backend
    5173,  // Vite frontend
    5432,  // PostgreSQL
    6379,  // Redis
    7474,  // Neo4j browser
    4222,  // NATS
    7233,  // Temporal
    9090,  // Prometheus
    3000   // Grafana
  ],
  "portsAttributes": {
    "4000": {
      "label": "Gateway",
      "onAutoForward": "notify"
    },
    "5173": {
      "label": "Frontend",
      "onAutoForward": "openPreview"
    }
  }
}
```

### Environment Variables

```json
{
  "containerEnv": {
    "PYTHONUNBUFFERED": "1",
    "GO_ENV": "development",
    "GIN_MODE": "debug",
    "WATCHPACK_POLLING": "true",
    "CHOKIDAR_USEPOLLING": "true"
  }
}
```

### Post-Creation Command

```json
{
  "postCreateCommand": "bash .devcontainer/postCreate.sh"
}
```

---

## Hot Reload Configuration

### React (Vite)

**Issue:** File system events don't propagate correctly in Docker on macOS/Windows.

**Solution:** Enable polling.

```bash
# .devcontainer/devcontainer.json
"containerEnv": {
  "WATCHPACK_POLLING": "true",
  "CHOKIDAR_USEPOLLING": "true"
}
```

**Alternative:** Use `VITE_USE_POLLING=true` in frontend/.env

### Python (uvicorn)

**Configuration:** Add `--reload` flag to uvicorn command.

```yaml
# process-compose.yaml
python-backend:
  command: ".venv/bin/python -m uvicorn tracertm.api.main:app --reload --host 0.0.0.0 --port 8000"
```

**Mount:** Bind mount source code (already configured in docker-compose.yml).

```yaml
services:
  workspace:
    volumes:
      - ..:/workspace:cached
```

### Go (Air)

**Tool:** Air provides live reload for Go applications.

**Installation:** Included in devcontainer Dockerfile.

```dockerfile
RUN go install github.com/air-verse/air@latest
```

**Configuration:** `.air.toml` in backend directory.

```toml
[build]
  cmd = "go build -o ./tmp/main ./cmd/api"
  bin = "tmp/main"
  include_ext = ["go", "tpl", "tmpl", "html"]
  exclude_dir = ["tmp", "vendor"]
  delay = 1000

[misc]
  clean_on_exit = true
```

**Command:**

```bash
# In backend directory
air
```

---

## Database Setup

### Automatic Migrations

Migrations run automatically on container creation via `postCreate.sh`:

```bash
#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h postgres -p 5432 -U tracertm; do
  sleep 2
done

echo "Running Python migrations..."
cd /workspace
uv run alembic upgrade head

echo "Seeding database..."
# Add seed script here if needed

echo "Installing frontend dependencies..."
cd /workspace/frontend
bun install

echo "Setup complete!"
```

### Manual Migration

If you need to run migrations manually:

```bash
# Python (Alembic)
uv run alembic upgrade head

# Go (if using Goose or similar)
cd backend
go run ./cmd/migrate up
```

### Database Connection

From inside the container:

```bash
# PostgreSQL
psql -h postgres -U tracertm -d tracertm

# Redis
redis-cli -h redis

# Neo4j browser
# Open http://localhost:7474 in browser
# Bolt: bolt://neo4j:7687
```

---

## Service Management

### Using process-compose

**Start all services:**

```bash
make dev-tui
# or
process-compose up
```

**View logs:**

```bash
# In TUI: press 'l' on a service
# Or check logs directory
cat .process-compose/logs/go-backend.log
```

**Restart a service:**

```bash
# In TUI: press 'r' on a service
# Or via CLI
process-compose restart go-backend
```

### Using Docker Compose

**Alternative to process-compose:**

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f go-backend

# Restart service
docker-compose restart go-backend
```

---

## Troubleshooting

### Hot Reload Not Working

**React:**
```bash
# Add to frontend/.env.local
WATCHPACK_POLLING=true
CHOKIDAR_USEPOLLING=true
```

**Python:**
```bash
# Verify uvicorn has --reload flag
ps aux | grep uvicorn
```

**Go:**
```bash
# Check Air is running
ps aux | grep air

# View Air logs
tail -f .process-compose/logs/go-backend.log
```

### Services Not Starting

**Check dependencies:**

```bash
# PostgreSQL
pg_isready -h postgres -p 5432 -U tracertm

# Redis
redis-cli -h redis ping

# NATS
curl http://nats:8222/healthz
```

**Check logs:**

```bash
# Process Compose
cat .process-compose/logs/<service>.log

# Docker Compose
docker-compose logs <service>
```

### Port Already in Use

**Solution 1:** Stop conflicting services

```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>
```

**Solution 2:** Change ports in devcontainer.json

### Out of Memory

**Increase Docker memory:**

Docker Desktop → Settings → Resources → Memory → 8 GB or more

**For TracerTM, recommended:**
- Memory: 8 GB minimum, 12 GB ideal
- CPUs: 4 cores minimum, 8 ideal
- Disk: 50 GB

### Slow Performance

**Use volume caching:**

```yaml
services:
  workspace:
    volumes:
      - ..:/workspace:cached
      - node_modules:/workspace/frontend/node_modules
      - go-pkg:/go/pkg
```

**Enable BuildKit:**

```bash
export DOCKER_BUILDKIT=1
```

**Use prebuilds:**

GitHub Codespaces: Configure in `.devcontainer/devcontainer.json`

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  }
}
```

---

## Best Practices

### 1. Use Prebuilds

**GitHub Codespaces:**

Create `.github/workflows/codespaces-prebuild.yml`:

```yaml
name: Codespaces Prebuild

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  prebuild:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build devcontainer
        uses: devcontainers/ci@v0.3
        with:
          imageName: ghcr.io/${{ github.repository }}-devcontainer
          cacheFrom: ghcr.io/${{ github.repository }}-devcontainer
          push: always
```

**Gitpod:**

Configure in `.gitpod.yml`:

```yaml
image:
  file: .devcontainer/Dockerfile

tasks:
  - init: |
      # Pre-install dependencies
      cd frontend && bun install
      cd ../backend && go mod download
  - command: make dev-tui
```

### 2. Optimize Layer Caching

**Dockerfile:**

```dockerfile
# Install system dependencies first (rarely change)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git

# Install language runtimes next (occasionally change)
RUN curl -fsSL https://get.docker.com | sh

# Copy dependency files (change more often)
COPY go.mod go.sum /tmp/
RUN cd /tmp && go mod download

# Copy source code last (changes frequently)
COPY . /workspace
```

### 3. Use Named Volumes

**For node_modules, go/pkg, etc.:**

```yaml
services:
  workspace:
    volumes:
      - ..:/workspace:cached
      - node_modules:/workspace/frontend/node_modules
      - go-pkg:/go/pkg
      - cargo-registry:/usr/local/cargo/registry

volumes:
  node_modules:
  go-pkg:
  cargo-registry:
```

**Benefits:**
- Faster builds (cache persists)
- Avoid permission issues
- Reduce container size

### 4. Set Resource Limits

```yaml
services:
  workspace:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G
```

### 5. Use .dockerignore

```
# .dockerignore
node_modules
.next
.venv
__pycache__
*.pyc
.git
.env*
tmp
.process-compose
```

---

## Advanced Configuration

### Multi-Stage Build

```dockerfile
# Stage 1: Build dependencies
FROM golang:1.21 AS go-builder
WORKDIR /build
COPY backend/go.mod backend/go.sum ./
RUN go mod download

FROM node:20 AS node-builder
WORKDIR /build
COPY frontend/package.json frontend/bun.lockb ./
RUN bun install

# Stage 2: Development environment
FROM ubuntu:22.04
COPY --from=go-builder /go/pkg /go/pkg
COPY --from=node-builder /build/node_modules /workspace/frontend/node_modules
```

### Custom Features

```json
{
  "features": {
    "ghcr.io/devcontainers/features/docker-in-docker:2": {},
    "ghcr.io/devcontainers/features/go:1": {
      "version": "1.21"
    },
    "ghcr.io/devcontainers/features/node:1": {
      "version": "20"
    },
    "ghcr.io/devcontainers/features/python:1": {
      "version": "3.11"
    }
  }
}
```

### Lifecycle Scripts

```json
{
  "postCreateCommand": "bash .devcontainer/postCreate.sh",
  "postStartCommand": "echo 'Container started!'",
  "postAttachCommand": "make dev-tui"
}
```

---

## GitHub Codespaces-Specific

### Secrets Management

**Add secrets in GitHub:**

Settings → Codespaces → New secret

**Access in devcontainer:**

```json
{
  "remoteEnv": {
    "OPENAI_API_KEY": "${localEnv:OPENAI_API_KEY}",
    "ANTHROPIC_API_KEY": "${localEnv:ANTHROPIC_API_KEY}"
  }
}
```

### Machine Types

**Configure in .devcontainer.json:**

```json
{
  "hostRequirements": {
    "cpus": 4,
    "memory": "8gb",
    "storage": "32gb"
  }
}
```

**Available machines:**
- 2-core: $0.18/hour
- 4-core: $0.36/hour (recommended for TracerTM)
- 8-core: $0.72/hour
- 16-core: $1.44/hour

### Prebuilds Configuration

**In repository settings:**

Settings → Codespaces → Prebuilds → New prebuild

- Trigger: On push to main
- Region: All available
- Template: Default configuration

---

## Gitpod-Specific

### .gitpod.yml Configuration

```yaml
image:
  file: .devcontainer/Dockerfile

ports:
  - port: 4000
    onOpen: open-preview
  - port: 8080
    onOpen: ignore
  - port: 5173
    onOpen: notify

tasks:
  - init: |
      # Pre-install dependencies (runs in prebuilds)
      cd frontend && bun install
      cd ../backend && go mod download
      uv sync
  - command: |
      # Start services
      make dev-tui

vscode:
  extensions:
    - golang.go
    - ms-python.python
    - dbaeumer.vscode-eslint
```

### Prebuilds

Gitpod automatically creates prebuilds on:
- Push to main branch
- New pull requests

**Check prebuild status:**

```bash
gp prebuild list
```

---

## Cost Optimization

### 1. Use Smaller Machines

For light editing:
- 2-core machine ($0.18/hour)

For full development:
- 4-core machine ($0.36/hour) ← TracerTM recommended

### 2. Stop When Not in Use

**GitHub Codespaces:**

Settings → Default idle timeout → 30 minutes

**Gitpod:**

Workspaces auto-stop after 30 minutes of inactivity (default)

### 3. Delete Old Workspaces

**GitHub Codespaces:**

```bash
gh codespace list
gh codespace delete -c <codespace-name>
```

**Gitpod:**

Dashboard → Delete inactive workspaces

### 4. Use Prebuilds

Reduces active compute time by 60-80% (dependencies pre-installed)

---

## Migration Guide

### From Local to Devcontainer

**1. Backup local environment:**

```bash
cp .env .env.local.backup
```

**2. Export database:**

```bash
pg_dump tracertm > tracertm_backup.sql
```

**3. Create devcontainer:**

```bash
# Reopen in container
# VS Code: Cmd+Shift+P → "Dev Containers: Reopen in Container"
```

**4. Import database:**

```bash
psql -h postgres -U tracertm -d tracertm < tracertm_backup.sql
```

**5. Test services:**

```bash
make dev-tui
```

### From Docker Compose to Dev Container

**Reuse existing docker-compose.yml:**

```json
{
  "dockerComposeFile": ["../docker-compose.yml"],
  "service": "workspace",
  "workspaceFolder": "/workspace"
}
```

---

## Testing & CI/CD

### Run Tests in Devcontainer

```bash
# Go tests
cd backend
go test ./...

# Python tests
pytest

# Frontend tests
cd frontend
bun test

# E2E tests
bun test:e2e
```

### CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build devcontainer
        uses: devcontainers/ci@v0.3
        with:
          runCmd: |
            make test
```

---

## Resources

### Official Documentation

- [Dev Containers Specification](https://containers.dev/)
- [VS Code Remote Development](https://code.visualstudio.com/docs/devcontainers/containers)
- [GitHub Codespaces Docs](https://docs.github.com/en/codespaces)
- [Gitpod Documentation](https://www.gitpod.io/docs)

### Examples & Templates

- [Awesome Dev Containers](https://github.com/manekinekko/awesome-devcontainers)
- [VS Code Dev Containers Templates](https://github.com/microsoft/vscode-dev-containers)

### TracerTM-Specific

- [Web-Based DevX Evaluation](/docs/research/web-based-devx-evaluation.md)
- [Process Compose Configuration](/process-compose.yaml)
- [Docker Compose Configuration](/docker-compose.yml)

---

**Document Version:** 1.0
**Last Updated:** 2026-02-01
**Maintained By:** TracerTM Team
