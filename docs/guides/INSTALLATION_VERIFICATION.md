# Installation Verification Guide

**Version:** 1.0.0
**Last Updated:** January 31, 2026
**Audience:** Developers setting up TracerTM for the first time

## Overview

This guide walks you through verifying your TracerTM installation step-by-step, from prerequisites to running the complete system. Follow each section in order.

---

## Table of Contents

1. [Prerequisites Check](#prerequisites-check)
2. [Tool Installation Verification](#tool-installation-verification)
3. [Service Startup Verification](#service-startup-verification)
4. [First-Time Setup Walkthrough](#first-time-setup-walkthrough)
5. [Common Installation Issues](#common-installation-issues)

---

## Prerequisites Check

### System Requirements

Before installing TracerTM, verify your system meets the minimum requirements:

#### Operating System
- [ ] **macOS** 12+ (Monterey or later)
- [ ] **Linux** (Ubuntu 20.04+, Debian 11+, Fedora 35+, or equivalent)
- [ ] **Windows** 10/11 with WSL2

#### Hardware
- [ ] **CPU:** 4+ cores recommended
- [ ] **RAM:** 8GB minimum, 16GB recommended
- [ ] **Disk:** 10GB free space minimum
- [ ] **Network:** Internet connection for initial setup

### Check System Resources

```bash
# Check CPU cores
nproc --all  # Linux
sysctl -n hw.ncpu  # macOS

# Check available RAM (should show 8GB+)
free -h  # Linux
vm_stat | head -1  # macOS

# Check disk space (should show 10GB+ free)
df -h .
```

**Expected:**
- [ ] 4+ CPU cores available
- [ ] 8GB+ RAM available
- [ ] 10GB+ disk space free

---

## Tool Installation Verification

### 1. Go

```bash
# Check Go version
go version
```

**Expected Output:**
```
go version go1.21.0 darwin/arm64
```

**Requirements:**
- [ ] Go version 1.21 or higher
- [ ] `GOPATH` and `GOBIN` configured

**If not installed:**
```bash
# macOS (using Homebrew)
brew install go

# Linux (using snap)
sudo snap install go --classic

# Or download from: https://go.dev/dl/
```

### 2. Node.js and Bun

```bash
# Check Node.js version
node --version

# Check Bun version
bun --version
```

**Expected Output:**
```
v20.10.0
1.0.21
```

**Requirements:**
- [ ] Node.js version 18 or higher
- [ ] Bun version 1.0 or higher (recommended)

**If not installed:**
```bash
# Install Node.js (macOS)
brew install node

# Install Node.js (Linux)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Bun
curl -fsSL https://bun.sh/install | bash
```

### 3. Python

```bash
# Check Python version
python3 --version

# Check pip version
pip3 --version
```

**Expected Output:**
```
Python 3.11.5
pip 23.2.1 from /usr/local/lib/python3.11/site-packages/pip (python 3.11)
```

**Requirements:**
- [ ] Python version 3.11 or higher
- [ ] pip installed and working

**If not installed:**
```bash
# macOS
brew install python@3.11

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3.11 python3-pip

# Verify
python3 --version
```

### 4. PostgreSQL

```bash
# Check PostgreSQL version
psql --version

# Check if PostgreSQL is running
pg_isready
```

**Expected Output:**
```
psql (PostgreSQL) 14.10
/tmp:5432 - accepting connections
```

**Requirements:**
- [ ] PostgreSQL version 14 or higher
- [ ] PostgreSQL service running
- [ ] Can connect to database

**If not installed:**
```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# Linux (Ubuntu/Debian)
sudo apt-get install postgresql-14
sudo systemctl start postgresql

# Create database and user
psql postgres -c "CREATE DATABASE tracertm;"
psql postgres -c "CREATE USER tracertm_user WITH PASSWORD 'your_password';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE tracertm TO tracertm_user;"
```

### 5. Neo4j (Optional)

```bash
# Check Neo4j version
neo4j version

# Check if Neo4j is running
curl -f http://localhost:7474
```

**Expected Output:**
```
neo4j 5.13.0
```

**Requirements:**
- [ ] Neo4j version 5.0 or higher
- [ ] Neo4j service running (optional for basic features)

**If not installed:**
```bash
# macOS
brew install neo4j
brew services start neo4j

# Linux - download from: https://neo4j.com/download/

# Access Neo4j Browser at http://localhost:7474
# Default credentials: neo4j/neo4j (change on first login)
```

### 6. NATS (Optional)

```bash
# Check NATS version
nats-server --version

# Check if NATS is running
curl -f http://localhost:8222/varz
```

**Expected Output:**
```
nats-server: v2.10.7
```

**Requirements:**
- [ ] NATS version 2.9 or higher
- [ ] NATS service running (optional for real-time features)

**If not installed:**
```bash
# macOS
brew install nats-server
brew services start nats-server

# Linux - download from: https://nats.io/download/

# Or use Docker:
docker run -d --name nats -p 4222:4222 -p 8222:8222 nats:latest
```

### 7. Caddy

```bash
# Check Caddy version
caddy version
```

**Expected Output:**
```
v2.7.6 h1:w0NymbG2m9PcvKWsrXO6EEkY9Ru4FJK8uQbYcev1p3A=
```

**Requirements:**
- [ ] Caddy version 2.7 or higher

**If not installed:**
```bash
# macOS
brew install caddy

# Linux (Ubuntu/Debian)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
```

### 8. Overmind

```bash
# Check Overmind version
overmind version
```

**Expected Output:**
```
Overmind 2.4.0
```

**Requirements:**
- [ ] Overmind version 2.4 or higher
- [ ] tmux installed (Overmind dependency)

**If not installed:**
```bash
# macOS
brew install overmind tmux

# Linux
# Install tmux first
sudo apt-get install tmux  # Ubuntu/Debian
sudo yum install tmux      # RHEL/CentOS

# Install Overmind
wget https://github.com/DarthSim/overmind/releases/download/v2.4.0/overmind-v2.4.0-linux-amd64.gz
gunzip overmind-v2.4.0-linux-amd64.gz
chmod +x overmind-v2.4.0-linux-amd64
sudo mv overmind-v2.4.0-linux-amd64 /usr/local/bin/overmind
```

### 9. Additional Tools

```bash
# Check git
git --version

# Check curl
curl --version

# Check jq (JSON processor)
jq --version

# Check make (optional, for build automation)
make --version
```

**Expected:**
- [ ] Git 2.30 or higher
- [ ] curl 7.70 or higher
- [ ] jq 1.6 or higher
- [ ] make 4.0 or higher (optional)

---

## Service Startup Verification

### 1. Clone Repository

```bash
# Clone the repository
git clone https://github.com/yourusername/tracertm.git
cd tracertm

# Verify you're in the right directory
ls -la
```

**Expected files:**
- [ ] `README.md`
- [ ] `backend/` directory
- [ ] `frontend/` directory
- [ ] `src/` directory (Python CLI)
- [ ] `.env.example`
- [ ] `Procfile` or similar process file

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or vim, or your preferred editor
```

**Required environment variables:**

```bash
# Database
DATABASE_URL=postgresql://tracertm_user:your_password@localhost:5432/tracertm

# Neo4j (optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_neo4j_password

# NATS (optional)
NATS_URL=nats://localhost:4222

# Ports
API_PORT=8080
FRONTEND_PORT=5173
PROXY_PORT=4000

# Auth (WorkOS) - get from https://dashboard.workos.com
WORKOS_API_KEY=sk_test_your_key_here
WORKOS_CLIENT_ID=client_your_id_here
WORKOS_REDIRECT_URI=http://localhost:4000/auth/callback

# Environment
NODE_ENV=development
GO_ENV=development
```

**Verification:**
- [ ] All required variables are set
- [ ] Database credentials are correct
- [ ] Neo4j credentials are correct (if using)
- [ ] WorkOS credentials are valid (if using auth)

### 3. Database Setup

```bash
# Test database connection
psql -h localhost -U tracertm_user -d tracertm -c "SELECT 1;"
```

**Expected Output:**
```
 ?column?
----------
        1
(1 row)
```

**If connection fails:**
```bash
# Create database if it doesn't exist
createdb -h localhost -U postgres tracertm

# Grant permissions
psql -h localhost -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE tracertm TO tracertm_user;"
```

**Verification:**
- [ ] Database exists
- [ ] Can connect successfully
- [ ] User has proper permissions

### 4. Install Development Tools

```bash
# Install TracerTM development tools
rtm dev install
```

**Expected Output:**
```
Installing development tools...
✓ Installing backend dependencies
✓ Installing frontend dependencies
✓ Installing Python CLI in development mode
✓ Installing pre-commit hooks
✓ Setting up database schema

Installation complete!

Next steps:
  rtm dev start    # Start all services
  rtm dev status   # Check service status
```

**Verification:**
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Python CLI installed
- [ ] No error messages

### 5. Verify Tool Installation

```bash
# Run verification check
rtm dev install --verify
```

**Expected Output:**
```
Verifying development environment...

✓ Go 1.21.5 installed
✓ Bun 1.0.21 installed
✓ Python 3.11.5 installed
✓ PostgreSQL 14.10 running
✓ Neo4j 5.13.0 running
✓ NATS 2.10.7 running
✓ Caddy 2.7.6 installed
✓ Overmind 2.4.0 installed

All prerequisites met! Ready to start development.
```

**Verification:**
- [ ] All tools show as installed
- [ ] All required services show as running
- [ ] Versions meet minimum requirements

---

## First-Time Setup Walkthrough

### Step 1: Start Services

```bash
# Start all services with Overmind
rtm dev start
```

**Expected Output:**
```
system | Tmux socket name: overmind-TracerTM-abc123
system | Starting…
caddy  | started with pid 12345
api    | started with pid 12346
frontend | started with pid 12347
python | started with pid 12348

caddy  | Caddy 2.7.6
caddy  | Serving HTTP proxy on :4000

api    | Starting Go API server...
api    | Database connected: postgresql://...
api    | Server listening on :8080

frontend | VITE v5.0.0 ready in 234 ms
frontend | ➜ Local: http://localhost:5173/
frontend | ➜ Network: use --host to expose

python | Starting Python CLI server...
python | Server ready on :8000
```

**Verification:**
- [ ] All 4 services started (caddy, api, frontend, python)
- [ ] No error messages
- [ ] PIDs assigned to each service
- [ ] Startup completed in < 30 seconds

### Step 2: Verify Frontend Access

```bash
# Open browser to frontend
open http://localhost:4000  # macOS
xdg-open http://localhost:4000  # Linux

# Or test with curl
curl -f http://localhost:4000
```

**In Browser:**
- [ ] Page loads successfully
- [ ] No errors in browser console (F12)
- [ ] React application renders
- [ ] Navigation works

### Step 3: Verify API Access

```bash
# Test API health endpoint
curl -f http://localhost:4000/api/v1/health | jq .
```

**Expected Output:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-31T12:00:00Z",
  "version": "1.0.0",
  "services": {
    "database": "connected",
    "neo4j": "connected",
    "nats": "connected"
  }
}
```

**Verification:**
- [ ] HTTP 200 response
- [ ] Status is "healthy"
- [ ] All services show as connected

### Step 4: Test API Documentation

```bash
# Open API documentation
open http://localhost:4000/docs  # macOS
xdg-open http://localhost:4000/docs  # Linux
```

**In Browser:**
- [ ] Swagger/OpenAPI UI loads
- [ ] API endpoints are listed
- [ ] Can expand and view endpoint details
- [ ] Can test endpoints (try /api/v1/health)

### Step 5: Verify Python CLI

```bash
# Test Python CLI health
curl -f http://localhost:4000/api/py/health | jq .

# Or use the CLI directly
tracertm --help
```

**Expected Output (CLI):**
```
Usage: tracertm [OPTIONS] COMMAND [ARGS]...

TracerTM - Requirements Traceability Matrix CLI

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  init      Initialize a new TracerTM project
  projects  Manage projects
  items     Manage items
  sync      Sync with remote server
```

**Verification:**
- [ ] Python CLI responds to health check
- [ ] CLI command works
- [ ] Help text displays correctly

### Step 6: Test Hot Reload

```bash
# Make a test change to frontend
echo "// Hot reload test" >> frontend/apps/web/src/App.tsx

# Watch logs to see reload
rtm dev logs frontend
```

**Expected:**
- [ ] Vite detects file change
- [ ] Page updates automatically in browser
- [ ] No page refresh required
- [ ] Update appears in < 1 second

**Cleanup:**
```bash
# Revert test change
git checkout frontend/apps/web/src/App.tsx
```

### Step 7: Verify Database Migrations

```bash
# Check database schema
psql -h localhost -U tracertm_user -d tracertm -c "\dt"
```

**Expected Output:**
```
              List of relations
 Schema |       Name        | Type  |    Owner
--------+-------------------+-------+--------------
 public | projects          | table | tracertm_user
 public | items             | table | tracertm_user
 public | users             | table | tracertm_user
 public | schema_migrations | table | tracertm_user
```

**Verification:**
- [ ] All expected tables exist
- [ ] No migration errors
- [ ] Schema version is current

### Step 8: Create Test Data

```bash
# Create a test project via API
curl -X POST http://localhost:4000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Project",
    "description": "Installation verification test"
  }' | jq .
```

**Expected Output:**
```json
{
  "id": "proj_abc123",
  "name": "Test Project",
  "description": "Installation verification test",
  "created_at": "2026-01-31T12:00:00Z"
}
```

**Verification:**
- [ ] Project created successfully
- [ ] Returns valid project ID
- [ ] No errors in API logs

### Step 9: Verify in Browser

**Open:** http://localhost:4000

**Actions:**
1. [ ] Navigate to Projects page
2. [ ] See "Test Project" in list
3. [ ] Click on project to view details
4. [ ] Verify all UI components load
5. [ ] No console errors

### Step 10: Clean Shutdown

```bash
# Stop all services gracefully
rtm dev stop
```

**Expected Output:**
```
Stopping all services...
✓ caddy stopped
✓ api stopped
✓ frontend stopped
✓ python stopped

All services stopped successfully.
```

**Verification:**
- [ ] All services stop cleanly
- [ ] No error messages
- [ ] Ports are released
- [ ] No orphaned processes

```bash
# Verify ports are free
lsof -i :4000,5173,8080,8000
# Should return nothing
```

---

## Common Installation Issues

### Issue 1: Port Already in Use

**Symptom:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find process using the port
lsof -i :4000  # or :5173, :8080, :8000

# Kill the process
kill -9 <PID>

# Or find and kill all at once
lsof -ti :4000 | xargs kill -9
```

### Issue 2: Database Connection Refused

**Symptom:**
```
Error: connection to server at "localhost" (127.0.0.1), port 5432 failed: Connection refused
```

**Solution:**
```bash
# Check if PostgreSQL is running
pg_isready

# If not, start it
# macOS
brew services start postgresql@14

# Linux
sudo systemctl start postgresql

# Verify it's running
pg_isready
# Expected: /tmp:5432 - accepting connections
```

### Issue 3: Permission Denied on Database

**Symptom:**
```
Error: permission denied for database tracertm
```

**Solution:**
```bash
# Grant permissions to user
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE tracertm TO tracertm_user;"

# Verify permissions
psql -U tracertm_user -d tracertm -c "SELECT 1;"
```

### Issue 4: Go Build Fails

**Symptom:**
```
Error: package not found or build fails
```

**Solution:**
```bash
# Clear Go module cache
go clean -modcache

# Download dependencies
cd backend
go mod download
go mod tidy

# Try building again
go build ./cmd/api
```

### Issue 5: Frontend Build Fails

**Symptom:**
```
Error: Cannot find module or dependency errors
```

**Solution:**
```bash
# Clear node_modules and lockfile
cd frontend
rm -rf node_modules bun.lockb

# Reinstall dependencies
bun install

# Try building again
bun run build
```

### Issue 6: Python Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'tracertm'
```

**Solution:**
```bash
# Reinstall in development mode
pip install -e .

# Or create virtual environment first
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows
pip install -e .
```

### Issue 7: Caddy Won't Start

**Symptom:**
```
Error: caddy: command not found
```

**Solution:**
```bash
# Install Caddy
# macOS
brew install caddy

# Linux
sudo apt install caddy

# Verify installation
caddy version
```

### Issue 8: Overmind Not Found

**Symptom:**
```
Error: overmind: command not found
```

**Solution:**
```bash
# Install Overmind
# macOS
brew install overmind

# Linux - see manual installation in prerequisites

# Verify installation
overmind version
```

### Issue 9: Environment Variables Not Loaded

**Symptom:**
```
Error: missing required environment variable
```

**Solution:**
```bash
# Ensure .env file exists
ls -la .env

# If not, copy from example
cp .env.example .env

# Edit .env with correct values
nano .env

# Verify variables are exported
source .env
echo $DATABASE_URL
```

### Issue 10: Hot Reload Not Working

**Symptom:**
- Code changes don't trigger rebuild
- Browser doesn't update

**Solution:**
```bash
# Increase file watcher limit (Linux)
echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
sudo sysctl -p

# Restart the specific service
overmind restart frontend
overmind restart api
```

### Issue 11: Neo4j Connection Fails

**Symptom:**
```
Error: Failed to connect to Neo4j
```

**Solution:**
```bash
# Check if Neo4j is running
curl http://localhost:7474

# Start Neo4j
brew services start neo4j  # macOS
sudo systemctl start neo4j  # Linux

# Check credentials in .env
# Default: neo4j/neo4j (must be changed on first login)
```

### Issue 12: WebSocket Connection Failed

**Symptom:**
```
WebSocket connection to 'ws://localhost:4000/ws' failed
```

**Solution:**
```bash
# Check if Caddy is routing WebSocket correctly
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" http://localhost:4000/ws

# Verify Caddy config includes WebSocket routing
cat Caddyfile | grep ws

# Restart Caddy
overmind restart caddy
```

---

## Troubleshooting Checklist

Use this checklist when encountering issues:

- [ ] Are all required tools installed and at correct versions?
- [ ] Are PostgreSQL, Neo4j, NATS running?
- [ ] Is .env file present and configured?
- [ ] Are all ports free (4000, 5173, 8080, 8000)?
- [ ] Have dependencies been installed (go mod, bun install, pip install)?
- [ ] Are there any error messages in logs?
- [ ] Have you tried stopping and restarting services?
- [ ] Is firewall blocking any ports?
- [ ] Are file permissions correct?
- [ ] Have you checked documentation for recent changes?

---

## Getting Help

If you're still experiencing issues:

1. **Check logs:**
   ```bash
   rtm dev logs api
   rtm dev logs frontend
   rtm dev logs python
   rtm dev logs caddy
   ```

2. **Check status:**
   ```bash
   rtm dev status
   ```

3. **Search existing issues:**
   - GitHub Issues: https://github.com/yourusername/tracertm/issues

4. **Ask for help:**
   - Create a new issue with:
     - System information (OS, versions)
     - Steps to reproduce
     - Error messages
     - Logs

---

## Next Steps

Once installation is verified:

1. **Read the User Guide:** Learn how to use TracerTM effectively
2. **Complete E2E Verification:** Run the full [E2E Verification Checklist](/docs/checklists/E2E_VERIFICATION_CHECKLIST.md)
3. **Explore Features:** Try creating projects, items, and exploring the graph view
4. **Set Up CI/CD:** Configure continuous integration for your workflow
5. **Join the Community:** Connect with other TracerTM users

---

**Installation Complete!** You're ready to start using TracerTM.
