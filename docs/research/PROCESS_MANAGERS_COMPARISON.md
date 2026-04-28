# Process Managers Comparison for TraceRTM Local Development

**Research Date:** 2026-01-31
**Objective:** Find the best tool for running Python backend, Go backend, frontend, and services together with auto-reload capabilities.

---

## Executive Summary

**Recommended Solution: Overmind + Language-Specific Watchers**

For TraceRTM's multi-language stack (Python, Go, Node.js), **Overmind** is recommended as the primary process orchestrator combined with built-in language watchers:
- **Best Features:** tmux integration for debugging, individual process restart, clean log aggregation
- **Installation:** Simple via Homebrew (`brew install overmind`)
- **Auto-Reload:** Delegates to language-specific tools (uvicorn --reload, air, vite)
- **Developer Experience:** Superior debugging with tmux attach, color-coded logs, easy process control

**Alternative for Kubernetes Teams:** Tilt (if planning Kubernetes deployment)
**Simplest Option:** Hivemind (fewer features but easier than Overmind)

---

## Feature Comparison Matrix

| Feature | Overmind | Hivemind | Goreman | Foreman | Honcho | Tilt | Just |
|---------|----------|----------|---------|---------|--------|------|------|
| **Auto-Reload** | ⚠️ Delegate | ⚠️ Delegate | ⚠️ Delegate | ⚠️ Delegate | ⚠️ Delegate | ✅ Built-in | ❌ N/A |
| **Service Dependencies** | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual | ⚠️ Manual | ✅ Built-in | ✅ Built-in |
| **Health Checks** | ❌ No | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Yes | ❌ No |
| **Process Restart** | ✅ Individual | ❌ All | ❌ All | ❌ All | ❌ All | ✅ Smart | N/A |
| **Log Aggregation** | ✅ Excellent | ✅ Good | ✅ Good | ⚠️ Laggy | ⚠️ Basic | ✅ Excellent | N/A |
| **Debugging Support** | ✅ tmux attach | ❌ No | ❌ No | ❌ No | ❌ No | ✅ Port forward | N/A |
| **Colored Logs** | ✅ Preserved | ✅ Preserved | ✅ Yes | ⚠️ Broken | ✅ Yes | ✅ Yes | N/A |
| **Port Management** | ✅ Auto +100 | ✅ Auto +100 | ✅ Auto | ✅ Auto | ✅ Auto | ✅ Advanced | N/A |
| **Homebrew Install** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ❌ pip only | ✅ Yes | ✅ Yes |
| **Platform Support** | macOS, Linux | macOS, Linux, BSD | All | All | All | macOS, Linux | All |
| **Language** | Go | Go | Go | Ruby | Python | Go | Rust |
| **Dependencies** | tmux | None | None | Ruby | Python | Docker/K8s | None |
| **Configuration** | Procfile | Procfile | Procfile | Procfile | Procfile | Tiltfile | Justfile |
| **Export Capability** | ❌ No | ❌ No | ❌ No | ✅ systemd | ❌ No | ✅ K8s | N/A |

**Legend:**
✅ Full support | ⚠️ Limited/Manual | ❌ Not supported | N/A Not applicable

---

## Tool Details

### 1. Overmind ⭐ RECOMMENDED

**Overview:** Process manager built on tmux with superior debugging and process management.

**Strengths:**
- **tmux Integration:** Each process runs in its own tmux window for live debugging
- **Individual Process Control:** Restart single processes without touching others
- **Clean Output:** Preserves colors, prevents log clipping/delays
- **Developer Workflow:** `overmind connect <process>` for interactive debugging
- **Auto-Restart:** Can automatically restart crashed processes
- **Port Management:** Auto-assigns PORT env var (base 5000, step 100)

**Limitations:**
- Requires tmux installation
- No built-in file watching (delegate to language tools)
- No service dependency ordering (start manually or build retry logic)

**Installation:**
```bash
# Install dependencies
brew install tmux

# Install Overmind
brew install overmind

# Or via Go
go install github.com/DarthSim/overmind/v2@latest
```

**Commands:**
```bash
overmind start              # Start all processes
overmind start web api      # Start specific processes
overmind restart web        # Restart single process
overmind connect web        # Attach to process (Ctrl+B D to detach)
overmind kill web           # Kill specific process
overmind stop               # Stop all processes
```

**Sources:**
- [GitHub - DarthSim/overmind](https://github.com/DarthSim/overmind)
- [Control Your Dev Processes with Overmind](https://pragmaticpineapple.com/control-your-dev-processes-with-overmind/)
- [Overmind better bin/dev for Procfile](https://railsnotes.xyz/blog/overmind-better-bin-dev-for-your-procfile-dev)

---

### 2. Hivemind

**Overview:** Simpler alternative to Overmind by the same author, without tmux dependency.

**Strengths:**
- No external dependencies (single binary)
- Cleaner output than Foreman/Goreman
- Simpler than Overmind for basic use cases
- Port management built-in

**Limitations:**
- Cannot restart individual processes
- No interactive debugging (no tmux)
- Fewer features than Overmind

**Installation:**
```bash
brew install hivemind
```

**Use Case:** Choose if you want simplicity over debugging features.

**Sources:**
- [GitHub - DarthSim/hivemind](https://github.com/DarthSim/hivemind)
- [Introducing Overmind and Hivemind](https://evilmartians.com/chronicles/introducing-overmind-and-hivemind)

---

### 3. Goreman

**Overview:** Go port of Foreman with signal handling improvements.

**Strengths:**
- Single binary, no Ruby dependency
- Proper signal forwarding (SIGINT, SIGTERM, SIGHUP)
- RPC interface for programmatic control
- Cross-platform

**Limitations:**
- Cannot restart individual processes
- No tmux integration
- Less actively maintained than Overmind

**Installation:**
```bash
go install github.com/mattn/goreman@latest
```

**Sources:**
- [GitHub - mattn/goreman](https://github.com/mattn/goreman)

---

### 4. Foreman (Ruby Original)

**Overview:** The original Procfile-based process manager created by Heroku.

**Strengths:**
- De facto standard (Procfile format originated here)
- Export to systemd, launchd, upstart, supervisord
- Widely documented
- Mature and stable

**Limitations:**
- **Major Issue:** Output buffering causes severe lag
- Breaks colored output
- Cannot restart individual processes
- Requires Ruby installation

**Installation:**
```bash
gem install foreman
```

**Use Case:** Only if you need systemd export or have legacy Foreman setups.

**Sources:**
- [foreman(1) - manage Procfile-based applications](https://ddollar.github.io/foreman/)
- [GitHub - ddollar/foreman](https://github.com/ddollar/foreman)

---

### 5. Honcho (Python Port)

**Overview:** Python port of Foreman for Python-centric teams.

**Strengths:**
- Native Python (no Ruby dependency)
- Procfile compatible
- Good for Python-only projects

**Limitations:**
- Basic features only
- Cannot restart individual processes
- Less feature-rich than Overmind

**Installation:**
```bash
pip install honcho
```

**Use Case:** Python teams who want to avoid Ruby, but Overmind is still better.

**Sources:**
- [Honcho Documentation](https://honcho.readthedocs.io/en/latest/)
- [GitHub - nickstenning/honcho](https://github.com/nickstenning/honcho)
- [Honcho · PyPI](https://pypi.org/project/honcho/)

---

### 6. Tilt (Kubernetes Dev Tool)

**Overview:** Advanced development tool for Kubernetes-based microservices.

**Strengths:**
- **Built-in Auto-Reload:** Live Update deploys code in seconds
- **Smart File Watching:** Monitors changes and triggers rebuilds
- **Service Dependencies:** Resource ordering and health checks
- **Advanced Features:** Port forwarding, resource graphs, logs aggregation
- **Framework Support:** Works with hot-reload frameworks (Webpack, etc.)

**Limitations:**
- **Complexity:** Requires Docker/Kubernetes knowledge
- **Overkill:** For non-containerized development
- **Learning Curve:** Tiltfile configuration vs simple Procfile
- **Resource Intensive:** Runs containers locally

**Installation:**
```bash
brew install tilt
```

**Use Case:** ONLY if planning Kubernetes deployment or already using containers.

**Sources:**
- [Tilt | Kubernetes for Prod, Tilt for Dev](https://tilt.dev/)
- [Smart Rebuilds with Live Update](https://docs.tilt.dev/tutorial/5-live-update.html)
- [GitHub - tilt-dev/tilt](https://github.com/tilt-dev/tilt)

---

### 7. Just (Command Runner)

**Overview:** Modern alternative to Make for task automation.

**Strengths:**
- **Task Dependencies:** Define and execute task chains
- **Cross-Platform:** Works everywhere
- **Simple Syntax:** No mandatory tabs like Make
- **Auto-Discovery:** Lists tasks with descriptions

**Limitations:**
- **Not a Process Manager:** Doesn't keep processes running
- **No Log Aggregation:** Runs tasks sequentially
- **Use Case Mismatch:** Better for CI/CD tasks than dev servers

**Installation:**
```bash
brew install just
```

**Use Case:** Use for build tasks, not for running multiple services concurrently.

**Sources:**
- [GitHub - casey/just](https://github.com/casey/just)
- [I've tried the "just" task runner](https://twdev.blog/2024/06/just/)
- [Just vs. Make: Which Task Runner Stands Up Best?](https://spin.atomicobject.com/2022/09/27/just-task-runner/)

---

## Auto-Reload Implementation

**Important:** None of the Procfile-based tools have built-in file watching. They delegate to language-specific tools:

### Python Backend (FastAPI/Starlette)
```bash
# Use uvicorn's built-in reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Go Backend
```bash
# Install Air for Go hot-reload
go install github.com/cosmtrek/air@latest

# Run with Air
air
```

**Air Configuration (.air.toml):**
```toml
[build]
  cmd = "go build -o ./tmp/main ."
  bin = "./tmp/main"
  include_ext = ["go", "tpl", "tmpl", "html"]
  exclude_dir = ["assets", "tmp", "vendor"]
```

### Frontend (Vite)
```bash
# Vite has built-in HMR
bun run dev
```

### Node.js Services
```bash
# Use nodemon or Node's --watch flag (Node 22+)
node --watch server.js
nodemon server.js
```

**Sources:**
- [How To Set Up Hot Reloading in Docker](https://oneuptime.com/blog/post/2026-01-06-docker-hot-reloading/view)
- [Use File Watching and Subprocesses for Python](https://medium.com/@jnavarr56/use-file-watching-and-subprocesses-to-develop-python-scripts-with-live-reloading-9ffaa66fd648)
- [PM2 - Watch & Restart](https://pm2.keymetrics.io/docs/usage/watch-and-restart/)

---

## Service Dependencies & Health Checks

**Challenge:** Procfile-based tools don't natively handle "database must start before backend" dependencies.

### Solutions:

#### 1. **Build Retry Logic** (Recommended for TraceRTM)
Make each service resilient to dependency failures:

```python
# Python backend with Neo4j retry
from neo4j import GraphDatabase
import time

def connect_with_retry(uri, max_attempts=10):
    for attempt in range(max_attempts):
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            driver.verify_connectivity()
            return driver
        except Exception as e:
            if attempt < max_attempts - 1:
                time.sleep(2)
            else:
                raise
```

#### 2. **Manual Ordering in Procfile**
List dependencies first (no guarantee they're ready):

```procfile
# Services start in order listed
neo4j: neo4j console
redis: redis-server
postgres: postgres -D /usr/local/var/postgres
python_backend: sleep 5 && uvicorn app.main:app --reload
go_backend: sleep 5 && air
frontend: sleep 8 && bun run dev
```

#### 3. **Health Check Scripts**
Create wrapper scripts for each service:

```bash
#!/bin/bash
# wait-for-neo4j.sh
until curl -s http://localhost:7474 > /dev/null; do
  echo "Waiting for Neo4j..."
  sleep 2
done
echo "Neo4j is ready!"
uvicorn app.main:app --reload
```

```procfile
python_backend: ./scripts/wait-for-neo4j.sh
```

#### 4. **Docker Compose (Alternative Approach)**
If dependencies are complex, consider Docker Compose with health checks:

```yaml
services:
  neo4j:
    image: neo4j:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:7474"]
      interval: 5s
      timeout: 3s
      retries: 5

  backend:
    depends_on:
      neo4j:
        condition: service_healthy
```

**Sources:**
- [Wait for Services to Start in Docker Compose](https://medium.com/@pavel.loginov.dev/wait-for-services-to-start-in-docker-compose-wait-for-it-vs-healthcheck-e0248f54962b)
- [Docker Compose Health Checks Guide](https://last9.io/blog/docker-compose-health-checks/)
- [Control startup order - Docker Docs](https://docs.docker.com/compose/how-tos/startup-order/)

---

## Procfile Example for TraceRTM

```procfile
# TraceRTM Development Environment
# File: Procfile

# Databases & Services (start first)
neo4j: neo4j console
redis: redis-server
postgres: postgres -D /usr/local/var/postgres

# Python Backend (FastAPI with auto-reload)
python_api: sleep 5 && cd backend/python && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Go Backend (with Air for hot-reload)
go_api: sleep 5 && cd backend/go && air

# Frontend (Vite with HMR)
frontend: sleep 8 && cd frontend/apps/web && bun run dev

# Optional: Background workers
worker: sleep 8 && cd backend/python && celery -A app.worker worker --loglevel=info

# Optional: Monitoring
grafana: grafana server
```

**Environment Variables (.env):**
```bash
# Overmind will load these automatically
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://user:pass@localhost:5432/tracertm
WORKOS_API_KEY=sk_test_...
WORKOS_CLIENT_ID=client_...
```

---

## Running TraceRTM with Overmind

### Setup

1. **Install Dependencies:**
```bash
brew install tmux overmind
```

2. **Install Language Watchers:**
```bash
# Python: uvicorn has --reload built-in
pip install uvicorn[standard]

# Go: Install Air
go install github.com/cosmtrek/air@latest

# Frontend: Vite has HMR built-in
cd frontend/apps/web && bun install
```

3. **Create Procfile** (see example above)

4. **Create .env** with environment variables

### Daily Usage

```bash
# Start all services
overmind start

# Start specific services
overmind start frontend python_api

# In another terminal, restart a service
overmind restart python_api

# Attach to Python backend for debugging
overmind connect python_api
# (Use Ctrl+B D to detach without stopping)

# View logs for specific service
overmind connect python_api -N  # -N flag for read-only

# Stop all services
overmind stop
```

### Debugging Example

```bash
# Terminal 1: Start Overmind
overmind start

# Terminal 2: Attach to Python backend with debugger
overmind connect python_api

# Now you can:
# - See live logs
# - Use pdb/ipdb breakpoints interactively
# - Ctrl+C to restart
# - Ctrl+B D to detach
```

---

## Log Aggregation Comparison

### Overmind
```
system     | Tmux socket name: overmind-tracertm-12345
neo4j      | Started with PID 54321
neo4j      | 2026-01-31 10:00:00 INFO  Started.
redis      | Started with PID 54322
redis      | * Ready to accept connections
python_api | Started with PID 54323
python_api | INFO:     Started server process [54323]
python_api | INFO:     Waiting for application startup.
go_api     | Started with PID 54324
go_api     | Starting Go backend on :8080
frontend   | Started with PID 54325
frontend   | VITE v5.0.0  ready in 450 ms
frontend   | ➜  Local:   http://localhost:5173/
```

**Features:**
- Color-coded by process
- No buffering/lag
- Timestamps preserved
- Can attach to see full history

### Foreman (Not Recommended)
```
10:00:01 neo4j.1     | Started.
10:00:03 redis.1     | Ready to accept
10:00:05 python_api.1| [SEVERE LAG POSSIBLE]
```

**Issues:**
- Severe output lag
- Colors broken
- Log buffering issues

---

## Recommendation Summary

### For TraceRTM: **Overmind** ⭐

**Why:**
1. **Superior Debugging:** tmux integration for interactive sessions
2. **Individual Process Control:** Restart Python backend without touching Go/frontend
3. **Clean Logs:** Preserves colors and prevents buffering
4. **Developer Workflow:** `overmind connect` is invaluable for debugging
5. **Easy Installation:** Single `brew install overmind` command
6. **Battle-Tested:** Used by Evil Martians, Rails community

**Implementation:**
```bash
# One-time setup
brew install tmux overmind
go install github.com/cosmtrek/air@latest

# Daily usage
overmind start  # Start everything
overmind restart python_api  # Restart after code changes
overmind connect python_api  # Debug interactively
```

**With Auto-Reload:**
- Python: Use `uvicorn --reload`
- Go: Use `air` watcher
- Frontend: Vite HMR built-in
- Overmind orchestrates everything

### Alternative: **Hivemind**
Choose if you don't need debugging features and want maximum simplicity.

### Avoid: **Foreman**
Unless you specifically need systemd export, the output lag makes it unsuitable for active development.

### Consider: **Tilt**
Only if you're planning Kubernetes deployment and already containerizing services.

---

## Additional Resources

### Overmind
- [GitHub Repository](https://github.com/DarthSim/overmind)
- [Evil Martians - Overmind](https://evilmartians.com/opensource/overmind)
- [Harnessing the Power of the Overmind](https://www.simplethread.com/harnessing-the-power-of-the-overmind/)

### Hivemind
- [GitHub Repository](https://github.com/DarthSim/hivemind)

### Goreman
- [GitHub Repository](https://github.com/mattn/goreman)

### Foreman
- [Official Documentation](https://ddollar.github.io/foreman/)
- [GitHub Repository](https://github.com/ddollar/foreman)

### Honcho
- [Documentation](https://honcho.readthedocs.io/en/latest/)
- [PyPI Package](https://pypi.org/project/honcho/)

### Tilt
- [Official Website](https://tilt.dev/)
- [Documentation](https://docs.tilt.dev/)
- [GitHub Repository](https://github.com/tilt-dev/tilt)

### Just
- [GitHub Repository](https://github.com/casey/just)

### Auto-Reload Tools
- [Air for Go](https://github.com/cosmtrek/air)
- [Nodemon for Node.js](https://nodemon.io/)
- [PM2 Watch & Restart](https://pm2.keymetrics.io/docs/usage/watch-and-restart/)

### Service Dependencies
- [Docker Compose Health Checks](https://docs.docker.com/compose/how-tos/startup-order/)
- [Wait for Services to Start](https://medium.com/@pavel.loginov.dev/wait-for-services-to-start-in-docker-compose-wait-for-it-vs-healthcheck-e0248f54962b)

---

## Appendix: Quick Start Commands

### Install Overmind
```bash
brew install tmux overmind
```

### Install Language Watchers
```bash
# Go
go install github.com/cosmtrek/air@latest

# Python (uvicorn has --reload built-in)
pip install uvicorn[standard]

# Node.js (optional, for Node services)
npm install -g nodemon
```

### Create Procfile
```bash
cat > Procfile << 'EOF'
neo4j: neo4j console
redis: redis-server
python_api: sleep 5 && cd backend/python && uvicorn app.main:app --reload --port 8000
go_api: sleep 5 && cd backend/go && air
frontend: sleep 8 && cd frontend/apps/web && bun run dev
EOF
```

### Create .env
```bash
cat > .env << 'EOF'
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://localhost:5432/tracertm
WORKOS_API_KEY=sk_test_...
WORKOS_CLIENT_ID=client_...
EOF
```

### Run
```bash
# Start all services
overmind start

# Or start specific services
overmind start python_api frontend

# Restart a service
overmind restart python_api

# Attach to a service
overmind connect python_api

# Stop everything
overmind stop
```

---

**End of Research Report**
