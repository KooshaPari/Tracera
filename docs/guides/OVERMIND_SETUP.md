# Overmind Process Orchestration Setup

## Overview

Phase 3 of the TraceRTM Unified Infrastructure Architecture implements Overmind for process orchestration, providing a single command to run all development services.

## What is Overmind?

Overmind is a process manager for Procfile-based applications, similar to Foreman but with better multiplexing and restart capabilities. It runs multiple processes concurrently and manages their lifecycle.

## Architecture

### Process Configuration

The `Procfile` defines five core processes:

1. **temporal**: Temporal workflow engine for complex, long-running workflows
2. **caddy**: Reverse proxy and TLS termination
3. **go**: Go API server with hot reload (via Air)
4. **python**: Python FastAPI server with hot reload
5. **frontend**: React/TypeScript frontend with hot reload

### Process Dependencies

```
Frontend (3000) → Caddy (443/80) → {
  Go API (8080)
  Python API (8000)
  Temporal UI (8233)
}
```

## Files Created

### 1. Procfile (Project Root)

```procfile
# Temporal workflow engine
temporal: temporal server start-dev --db-filename .temporal/dev.db

# Caddy reverse proxy & TLS termination
caddy: caddy run --config Caddyfile --watch

# Go API server with hot reload
go: cd backend && air -c .air.toml

# Python FastAPI server with hot reload
python: uvicorn src.tracertm.api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend development server
frontend: cd frontend/apps/web && bun run dev --host 0.0.0.0
```

### 2. backend/.air.toml

Air configuration for Go hot reload:
- Watches `*.go` files (excluding tests)
- Builds to `./tmp/main`
- 1-second delay on changes
- Excludes: `tmp/`, `vendor/`, `testdata/`

### 3. .overmind.env

Environment configuration:
- Sources main `.env` file
- Sets `OVERMIND_PROCFILE=Procfile`
- Enables colored output

### 4. .temporal/

Directory for Temporal's development database (SQLite).

## Usage

### Prerequisites

Install required tools (see DEPLOYMENT_GUIDE.md Phase 1-2):
- Overmind: `brew install overmind`
- Temporal CLI: `brew install temporal`
- Caddy: `brew install caddy`
- Air: `go install github.com/cosmtrek/air@latest`

### Starting All Services

```bash
# Start all processes
overmind start

# Start with specific processes
overmind start -f Procfile go python frontend

# Start in background
overmind start -D
```

### Managing Processes

```bash
# Connect to running Overmind session
overmind connect

# Restart a specific process
overmind restart go

# Stop a specific process
overmind stop temporal

# Stop all processes
overmind kill
```

### Viewing Logs

```bash
# Follow logs for all processes
overmind connect

# View logs for specific process
overmind connect go

# Exit log view: Ctrl+B, D
```

## Process Details

### Temporal

- **Purpose**: Workflow orchestration engine
- **Port**: 7233 (gRPC), 8233 (UI)
- **Database**: `.temporal/dev.db` (SQLite)
- **UI**: http://localhost:8233

### Caddy

- **Purpose**: Reverse proxy, TLS termination
- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Config**: `Caddyfile`
- **Features**: Auto-reload on config changes

### Go API

- **Purpose**: Main API server
- **Port**: 8080 (internal)
- **Hot Reload**: Air (1s delay)
- **Build Output**: `backend/tmp/main`

### Python API

- **Purpose**: FastAPI microservice
- **Port**: 8000 (internal)
- **Hot Reload**: Uvicorn native
- **Access**: Via Caddy at `/api/python`

### Frontend

- **Purpose**: React/TypeScript UI
- **Port**: 3000 (internal)
- **Hot Reload**: Vite native
- **Access**: Via Caddy at `/`

## Hot Reload Behavior

All services support hot reload:

| Service | Trigger | Reload Time | Tool |
|---------|---------|-------------|------|
| Go | `*.go` change | ~1-2s | Air |
| Python | `*.py` change | <1s | Uvicorn |
| Frontend | `*.tsx/*.ts` change | <1s | Vite |
| Caddy | Caddyfile change | <1s | Caddy |

## Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -ti:8080 | xargs kill -9

# Or use Overmind to kill existing session
overmind kill
```

### Process Won't Start

```bash
# Check logs for specific process
overmind connect <process-name>

# Restart individual process
overmind restart <process-name>
```

### Environment Variables Not Loaded

Ensure `.overmind.env` properly sources `.env`:
```bash
# Test environment loading
source .overmind.env && env | grep TRACERTM
```

### Air Build Failures

Check `backend/build-errors.log` for Go compilation errors.

## Integration with Other Phases

### Phase 1: Tool Installation
- Overmind requires tools installed in Phase 1
- Verify: `overmind --version`, `temporal --version`, `caddy version`

### Phase 2: Caddy Configuration
- Procfile references `Caddyfile` from Phase 2
- Caddy routes traffic to Go/Python/Frontend

### Phase 4: Monorepo Scripts (Next)
- Will add `bun run dev` script to start Overmind
- Will integrate with CI/CD pipelines

## Next Steps

After Phase 3 completion:
1. Test Overmind startup (after tool installation)
2. Verify all processes start correctly
3. Test hot reload for each service
4. Proceed to Phase 4: Monorepo Scripts

## Benefits

- **Single Command**: `overmind start` runs entire stack
- **Process Management**: Restart/stop individual services
- **Multiplexing**: All logs in one terminal (tmux-based)
- **Auto-Restart**: Processes restart on crash
- **Hot Reload**: All services support live reload
- **Development Efficiency**: No manual process juggling

## References

- [Overmind Documentation](https://github.com/DarthSim/overmind)
- [Air Documentation](https://github.com/cosmtrek/air)
- [Procfile Format](https://devcenter.heroku.com/articles/procfile)
- [Temporal CLI](https://docs.temporal.io/cli)
