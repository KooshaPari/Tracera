# TraceRTM Unified Process Configuration
# Managed by Overmind - see docs/guides/DEPLOYMENT_GUIDE.md
# Strict deps order for preflight: go backend -> python -> frontend/others.

# Temporal workflow engine (skip if 7233 in use — e.g. already running elsewhere)
temporal: bash -c 'if (nc -z 127.0.0.1 7233 2>/dev/null) || (lsof -i :7233 -sTCP:LISTEN -t >/dev/null 2>&1); then echo "Port 7233 in use, skipping Temporal"; exec tail -f /dev/null; else exec temporal server start-dev --db-filename .temporal/dev.db; fi'

# Caddy reverse proxy & TLS termination (PATH set so caddy is found when script runs)
caddy: env PATH="/opt/homebrew/bin:/usr/local/bin:$PATH" bash scripts/run-caddy.sh

# Go API server (start first so Python/frontend preflights can reach it)
go: cd backend && air -c .air.toml

# Python FastAPI server (after Go; before frontend/worker)
python: PYTHONWARNINGS='ignore:remove second argument of ws_handler:DeprecationWarning' .venv/bin/python -m uvicorn src.tracertm.api.main:app --reload --host 0.0.0.0 --port 8000 --reload-exclude ARCHIVE --reload-exclude CONFIG

# Temporal worker (after Python)
temporal_worker: .venv/bin/python -m tracertm.workflows.worker

# Frontend development server (last)
frontend: cd frontend/apps/web && bun run dev --host 0.0.0.0

# gRPC proto file watcher (optional - uncomment to enable)
# Automatically regenerates gRPC code when proto files change
# Requires: brew install fswatch
# proto_watch: bash scripts/generate-grpc.sh --watch
