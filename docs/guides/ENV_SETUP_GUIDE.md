# Environment Setup Guide - Simplified Local Development

**Quick setup for running all TracerTM services individually**

---

## Overview

This guide helps you set up and run TracerTM services **individually** for local development. No Docker required - just native services running in separate terminals.

### Services Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Frontend   │────▶│ Python API   │────▶│  Go Backend  │
│  (Vite)     │     │  (FastAPI)   │     │    (Gin)     │
│  Port 3000  │     │  Port 8000   │     │  Port 8080   │
└─────────────┘     └──────────────┘     └──────────────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────────────────────┐
                    │     Infrastructure           │
                    │  • PostgreSQL (5432)         │
                    │  • Redis (6379)              │
                    │  • NATS (4222)               │
                    └──────────────────────────────┘
```

---

## Quick Start (5 Minutes)

### 1. Install Prerequisites

```bash
# macOS (using Homebrew)
brew install postgresql@14 redis nats-server

# Ubuntu/Debian
sudo apt install postgresql redis-server
# NATS: Download from https://nats.io/download/

# Start PostgreSQL
brew services start postgresql@14  # macOS
# or
sudo systemctl start postgresql    # Linux
```

### 2. Setup Environment Files

```bash
# Run the automated setup script
./scripts/setup-env.sh

# This creates:
# - backend/.env (Go backend)
# - .env (Python backend)
# - frontend/apps/web/.env.local (Frontend)
```

### 3. Update Secrets

Edit the created `.env` files and update these critical values:

```bash
# Generate secrets
openssl rand -hex 32  # Use for JWT_SECRET
openssl rand -hex 32  # Use for CSRF_SECRET

# Update in backend/.env and .env (root):
JWT_SECRET=<your-generated-secret>
CSRF_SECRET=<your-generated-secret>  # Go backend only

# Add your API keys (optional for basic dev):
WORKOS_CLIENT_ID=client_xxx
WORKOS_API_KEY=sk_test_xxx
VOYAGE_API_KEY=pa_xxx  # Or other embedding provider
```

### 4. Start Services (Separate Terminals)

```bash
# Terminal 1: Dependencies
./scripts/start-services.sh deps

# Terminal 2: Go Backend
./scripts/start-services.sh go-backend

# Terminal 3: Python Backend
./scripts/start-services.sh python-backend

# Terminal 4: Frontend
./scripts/start-services.sh frontend
```

### 5. Verify Everything Works

Open browser to `http://localhost:3000` - you should see the TracerTM dashboard.

---

## Environment Files Explained

### 📁 File Structure

```
tracertm/
├── .env.shared              # Shared variables (both backends)
├── .env.go-backend          # Go-specific variables
├── .env.python-backend      # Python-specific variables
├── .env.frontend            # Frontend-specific variables
│
├── .env                     # ✅ Python backend (generated)
├── backend/.env             # ✅ Go backend (generated)
└── frontend/apps/web/.env.local  # ✅ Frontend (generated)
```

### 🔐 What Goes Where?

**Shared Variables** (Both Backends)
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis cache
- `NATS_URL` - Message broker
- `JWT_SECRET` - **CRITICAL**: Must be identical
- `NEO4J_*` - Graph database (optional)
- `WORKOS_*` - Authentication
- `VOYAGE_API_KEY` - AI embeddings

**Go Backend Only**
- `PORT` - Server port (8080)
- `GIN_MODE` - Debug/release mode
- `CSRF_SECRET` - CSRF protection
- `S3_*` - Object storage (optional)

**Python Backend Only**
- `LOG_LEVEL` - Logging verbosity
- `ANTHROPIC_API_KEY` - Claude API
- `OPENAI_API_KEY` - OpenAI API
- `REALTIME_PROVIDER` - NATS or Supabase

**Frontend Only**
- `VITE_API_URL` - Python backend URL
- `VITE_WS_URL` - WebSocket URL
- `VITE_WORKOS_*` - WorkOS auth config
- `VITE_ENABLE_*` - Feature flags

---

## Detailed Setup Instructions

### Option 1: Automated Setup (Recommended)

```bash
# 1. Run setup script
./scripts/setup-env.sh

# 2. Edit generated files to add your secrets
vim backend/.env              # Go backend
vim .env                      # Python backend
vim frontend/apps/web/.env.local  # Frontend

# 3. Start services
./scripts/start-services.sh deps  # Dependencies first
```

### Option 2: Manual Setup

**Step 1: Create Go Backend .env**

```bash
# Combine shared + Go-specific
cat .env.shared .env.go-backend > backend/.env

# Fix DATABASE_URL format (Go uses postgres://, not postgresql+asyncpg://)
sed -i '' 's|postgresql+asyncpg://|postgres://|g' backend/.env
```

**Step 2: Create Python Backend .env**

```bash
# Combine shared + Python-specific
cat .env.shared .env.python-backend > .env
```

**Step 3: Create Frontend .env.local**

```bash
# Copy frontend template
cp .env.frontend frontend/apps/web/.env.local
```

**Step 4: Update Secrets**

Edit each file and update:
- `JWT_SECRET` (must match in both backends)
- `CSRF_SECRET` (Go backend only)
- `WORKOS_CLIENT_ID` and `WORKOS_API_KEY`
- Any API keys you need

---

## Starting Services Individually

### Dependencies (Start Once)

```bash
# PostgreSQL
brew services start postgresql@14  # macOS
sudo systemctl start postgresql    # Linux

# Redis
./scripts/start-services.sh redis

# NATS
./scripts/start-services.sh nats

# Or start all dependencies at once:
./scripts/start-services.sh deps
```

### Go Backend

```bash
# Terminal 1
cd backend

# Option A: With hot-reload (recommended)
air

# Option B: Direct run
go run main.go

# Check it's running:
curl http://localhost:8080/health
```

### Python Backend

```bash
# Terminal 2
# Activate virtual environment (if not already)
source .venv/bin/activate

# Start with hot-reload
uvicorn tracertm.api.main:app --reload

# Check it's running:
curl http://localhost:4000/health
```

### Frontend

```bash
# Terminal 3
cd frontend/apps/web

# Install dependencies (first time only)
bun install

# Start dev server
bun run dev

# Open browser:
open http://localhost:3000
```

### Using Helper Script

```bash
# Start dependencies first
./scripts/start-services.sh deps

# Then in separate terminals:
./scripts/start-services.sh go-backend      # Terminal 1
./scripts/start-services.sh python-backend  # Terminal 2
./scripts/start-services.sh frontend        # Terminal 3
```

---

## Stopping Services

```bash
# Stop all background services
./scripts/start-services.sh stop

# Or manually:
redis-cli shutdown         # Stop Redis
pkill nats-server          # Stop NATS
brew services stop postgresql@14  # Stop PostgreSQL (optional)

# Backends/Frontend: Just Ctrl+C in their terminals
```

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using a port
lsof -i :8080  # Go backend
lsof -i :8000  # Python backend
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>
```

### Database Connection Errors

```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep tracertm

# Create if missing
createdb tracertm

# Run migrations
alembic upgrade head
```

### Go Backend Won't Start

```bash
# Check .env file exists
ls -la backend/.env

# Verify DATABASE_URL format (should be postgres://, not postgresql+asyncpg://)
grep DATABASE_URL backend/.env

# Install dependencies
cd backend
go mod download
```

### Python Backend Won't Start

```bash
# Check .env file exists
ls -la .env

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Check database connection
python -c "from sqlalchemy import create_engine; import os; engine = create_engine(os.getenv('DATABASE_URL')); print('OK')"
```

### Frontend Won't Connect to Backends

```bash
# Check .env.local exists
ls -la frontend/apps/web/.env.local

# Verify API URLs
cat frontend/apps/web/.env.local | grep VITE_API_URL

# Should be:
# VITE_API_URL=http://localhost:4000
# VITE_WS_URL=ws://localhost:4000

# Restart frontend after changing .env.local
```

### Redis Connection Issues

```bash
# Check Redis is running
redis-cli ping  # Should return "PONG"

# Start Redis if not running
redis-server --daemonize yes

# Check Redis URL in .env files
grep REDIS_URL backend/.env
grep REDIS_URL .env
```

### NATS Connection Issues

```bash
# Check NATS is running
curl http://localhost:8222/varz

# Start NATS if not running
nats-server -js -D

# Check NATS URL in .env files
grep NATS_URL backend/.env
grep NATS_URL .env
```

---

## Environment Variable Reference

### Critical Variables (Required)

| Variable | Where | Example | Purpose |
|----------|-------|---------|---------|
| `DATABASE_URL` | Both backends | `postgres://user:pass@localhost:5432/db` | PostgreSQL |
| `REDIS_URL` | Both backends | `redis://localhost:6379` | Redis cache |
| `NATS_URL` | Both backends | `nats://localhost:4222` | Message broker |
| `JWT_SECRET` | Both backends | `<32+ chars>` | **MUST MATCH** |
| `WORKOS_CLIENT_ID` | Frontend + Python | `client_xxx` | Auth |
| `WORKOS_API_KEY` | Python only | `sk_test_xxx` | Auth |

### Optional Variables

| Variable | Where | Purpose |
|----------|-------|---------|
| `NEO4J_URI` | Both backends | Graph database |
| `VOYAGE_API_KEY` | Both backends | AI embeddings |
| `OPENAI_API_KEY` | Python | OpenAI API |
| `ANTHROPIC_API_KEY` | Python | Claude API |
| `S3_*` | Go only | File storage |

### Development vs Production

**Development** (`.env.local`, `.env`)
- Local PostgreSQL, Redis, NATS
- Debug logging
- Feature flags enabled
- Mock service worker enabled

**Production** (`.env.production`)
- Managed services (Supabase, Upstash, NGS NATS)
- Info-level logging
- Feature flags configured per environment
- Real service integrations

---

## Next Steps

### Verify Installation

```bash
# Check all services running
curl http://localhost:8080/health  # Go backend
curl http://localhost:4000/health  # Python backend
open http://localhost:3000         # Frontend

# Run backend consolidation verification
./scripts/verify_consolidation.sh
```

### Run Tests

```bash
# Go backend tests
cd backend && go test ./...

# Python backend tests
pytest

# Frontend tests
cd frontend/apps/web && bun test
```

### Apply Database Migrations

```bash
# Run migrations
alembic upgrade head

# Verify
psql tracertm -c "SELECT indexname FROM pg_indexes WHERE tablename = 'items';"
```

---

## Quick Reference

```bash
# Setup (once)
./scripts/setup-env.sh

# Start dependencies (once)
./scripts/start-services.sh deps

# Start services (separate terminals)
./scripts/start-services.sh go-backend      # Terminal 1: Go
./scripts/start-services.sh python-backend  # Terminal 2: Python
./scripts/start-services.sh frontend        # Terminal 3: Frontend

# Stop all
./scripts/start-services.sh stop

# Restart a service: Ctrl+C then re-run start command
```

---

## Additional Resources

- **Full Documentation**: `docs/01-getting-started/README.md`
- **Backend Consolidation**: `.trace/BACKEND_CONSOLIDATION_IMPLEMENTATION_COMPLETE.md`
- **Verification Guide**: `.trace/VERIFICATION_GUIDE.md`
- **API Documentation**: `http://localhost:4000/docs` (when Python backend running)

---

**Need Help?**
- Check logs in each terminal for error messages
- Review `.env` files for correct variable values
- Ensure all dependencies are installed and running
- Verify database migrations are up to date
