# TracerTM Development Quick Reference

**Version:** 2.0.0
**Last Updated:** January 31, 2026

## One-Page Quick Reference

### Daily Commands

```bash
# Start development environment
overmind start

# Stop all services
overmind kill

# Restart a service
overmind restart go|python|frontend

# View logs
overmind connect go|python|frontend|caddy
# Detach: Ctrl+B, then D

# Check status
overmind ps
```

---

## Service Ports

| Service | Port | URL |
|---------|------|-----|
| **Gateway** | 80 | http://localhost |
| **Go Backend** | 8080 | http://localhost:8080 |
| **Python Backend** | 8000 | http://localhost:4000 |
| **Frontend** | 5173 | http://localhost:5173 |
| **Temporal UI** | 8233 | http://localhost:8233 |
| **PostgreSQL** | 5432 | postgresql://localhost:5432 |
| **Redis** | 6379 | redis://localhost:6379 |
| **Neo4j** | 7474 | http://localhost:7474 |
| **NATS** | 4222 | nats://localhost:4222 |
| **Grafana** | 3000 | http://localhost:3000 |

### Frontend expectations (API / WebSocket on port 4000)

The web app uses `VITE_API_URL` (default `http://localhost:4000`) for both REST and WebSocket. The process on port 4000 (gateway or backend) must expose:

- **REST**: e.g. `GET /api/v1/items/{item_id}` — 404 here usually means backend not running, gateway not routing, or the item does not exist.
- **WebSocket**: `GET /api/v1/ws` (upgraded to WebSocket). Connection failures mean the server is not handling `/api/v1/ws` or is down.

Ensure the service on port 4000 is running and routes these paths to the appropriate backend.

---

## RTM CLI Commands

### Testing
```bash
./rtm test                    # All tests
./rtm test:unit              # Unit tests
./rtm test:integration       # Integration tests
./rtm test:e2e               # End-to-end tests
./rtm test:coverage          # With coverage
./rtm test:watch             # Watch mode
```

### Development
```bash
./rtm dev                    # Start dev server
./rtm dev:all                # All dev servers
./rtm dev:storybook          # Storybook
```

### Building
```bash
./rtm build                  # Build all
./rtm build:web              # Web app only
./rtm build:docker           # Docker images
```

### Code Quality
```bash
./rtm lint                   # Run linters
./rtm lint:fix               # Auto-fix issues
./rtm format                 # Format code
./rtm typecheck              # Type checking
```

### Database
```bash
./rtm db:migrate             # Run migrations
./rtm db:seed                # Seed database
./rtm db:reset               # Reset database
```

### Docker
```bash
./rtm docker:up              # Start stack
./rtm docker:down            # Stop stack
./rtm docker:build           # Build images
./rtm docker:logs            # View logs
```

---

## Overmind Quick Reference

### Process Management
```bash
overmind start               # Start all services
overmind start go python     # Start specific services
overmind kill                # Stop all
overmind stop go             # Stop one service
overmind restart go          # Restart service
overmind ps                  # List services
```

### Interactive
```bash
overmind connect go          # Attach to service
# Ctrl+B, D to detach

overmind run go "go test"    # Run command in context
overmind echo                # View all logs (multiplexed)
```

### Debugging
```bash
# Stop service to debug manually
overmind stop go
cd backend && dlv debug      # Start debugger

# Restart when done
overmind start go
```

---

## Caddy Gateway Routes

### Go Backend Routes (8080)
```
/api/v1/projects/*           # Project management
/api/v1/items/*              # Requirements/features/tasks
/api/v1/links/*              # Traceability links
/api/v1/graph/*              # Graph analysis
/api/v1/search/*             # Full-text search
/api/v1/agents/*             # AI agent coordination
/api/v1/temporal/*           # Temporal workflows
/api/v1/code/*               # Code analysis
/api/v1/ws                   # WebSocket (real-time)
```

### Python Backend Routes (8000)
```
/api/v1/specifications/*     # Specifications
/api/v1/executions/*         # Test executions
/api/v1/mcp/*                # Model Context Protocol
/api/v1/quality/*            # Quality metrics
/api/v1/auth/*               # Authentication
/api/v1/notifications/*      # Notifications
```

### Health Checks
```
/health                      # Gateway health
/health/go                   # Go backend health
/health/python               # Python backend health
```

---

## Hot Reload Mechanisms

### Frontend (Vite HMR)
- **Trigger:** Edit .tsx/.ts file
- **Speed:** <100ms
- **Preserves:** Application state

### Go Backend (Air)
- **Trigger:** Edit .go file
- **Speed:** 1-3 seconds
- **Process:** Auto-recompile → restart

### Python Backend (Uvicorn)
- **Trigger:** Edit .py file
- **Speed:** <1 second
- **Process:** Auto-reload workers

### Caddy (Watch)
- **Trigger:** Edit Caddyfile
- **Speed:** Instant
- **Process:** Zero-downtime reload

---

## Common Troubleshooting

### Port Already in Use
```bash
# Find process
lsof -i :8080

# Kill process
kill -9 <PID>
```

### Service Won't Start
```bash
# Check database
pg_isready -h localhost -p 5432
redis-cli ping

# Start databases
brew services start postgresql@15
brew services start redis
neo4j start
```

### Hot Reload Not Working
```bash
# Frontend: Clear cache
rm -rf frontend/apps/web/node_modules/.vite

# Go: Check Air config
cd backend && air -d

# Python: Restart service
overmind restart python
```

### Database Connection Error
```bash
# PostgreSQL
psql -U tracertm -d tracertm

# Redis
redis-cli

# Neo4j
curl http://localhost:7474
```

### High CPU/Memory
```bash
# Check usage
top -o cpu

# Restart services
overmind kill && overmind start

# Clear Redis cache
redis-cli FLUSHDB
```

---

## Debugging Quick Tips

### Go Debugging
```bash
# Using Delve
overmind stop go
cd backend
dlv debug --headless --listen=:2345 --api-version=2

# In VS Code: attach to :2345
```

### Python Debugging
```python
# Add breakpoint
import ipdb; ipdb.set_trace()

# Or debugpy
import debugpy
debugpy.listen(5678)
debugpy.wait_for_client()

# In VS Code: attach to :5678
```

### Frontend Debugging
```javascript
// Console log
console.log('State:', state)

// React DevTools (browser extension)
// TanStack Query DevTools (auto-enabled in dev)

// Network tab in browser DevTools
```

### View Database Data
```bash
# PostgreSQL
psql -U tracertm -d tracertm -c "SELECT * FROM items LIMIT 10;"

# Redis
redis-cli
KEYS tracertm:*

# Neo4j
# Open http://localhost:7474
MATCH (n) RETURN n LIMIT 10;
```

---

## Git Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes, test
bun test && go test ./... && pytest

# Commit with conventional commits
git commit -m "feat: add feature"
git commit -m "fix: resolve bug"

# Push and create PR
git push origin feature/my-feature
```

---

## Testing Quick Reference

### Frontend Tests
```bash
cd frontend/apps/web

# Run all tests
bun test

# Watch mode
bun test --watch

# With UI
bun test --ui

# Coverage
bun test --coverage

# E2E tests
bun run test:e2e
```

### Go Tests
```bash
cd backend

# Run all tests
go test ./...

# Verbose
go test -v ./...

# With coverage
go test -cover ./...

# Specific package
go test ./internal/services/...
```

### Python Tests
```bash
# Run all tests
pytest

# Watch mode
pytest --watch

# With coverage
pytest --cov=src/tracertm

# Specific markers
pytest -m unit
pytest -m integration
```

---

## Logs & Monitoring

### View Service Logs
```bash
# Real-time (multiplexed)
overmind echo

# Specific service
overmind connect go|python|frontend|caddy

# Caddy access log
tail -f /tmp/caddy-tracertm-access.log | jq '.'

# Caddy error log
tail -f /tmp/caddy-tracertm.log | jq '.'
```

### Monitoring Endpoints
```bash
# Prometheus metrics
curl http://localhost:9090

# Grafana dashboards
open http://localhost:3000

# NATS monitoring
curl http://localhost:8222/varz | jq '.'

# Temporal UI
open http://localhost:8233
```

---

## Performance Optimization

### Increase File Watchers (macOS)
```bash
echo kern.maxfiles=65536 | sudo tee -a /etc/sysctl.conf
sudo sysctl -w kern.maxfiles=65536
```

### Clear Caches
```bash
# Frontend
rm -rf frontend/apps/web/node_modules/.vite

# Go
go clean -cache

# Redis
redis-cli FLUSHDB
```

### Limit Parallelism
```bash
# Go builds
export GOMAXPROCS=4

# Bun/Node
export NODE_OPTIONS="--max-old-space-size=4096"
```

---

## Docker Quick Reference

### Development with Docker Compose
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild images
docker-compose build

# Remove volumes
docker-compose down -v
```

### Production Deployment
```bash
# Build images
make docker-build

# Deploy to K8s
make k8s-deploy

# Check status
make k8s-status

# View logs
make k8s-logs
```

---

## Environment Variables

### Required (.env)
```bash
# Database
DATABASE_URL=postgresql://tracertm:password@localhost:5432/tracertm

# Redis
REDIS_URL=redis://localhost:6379

# NATS
NATS_URL=nats://localhost:4222

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Temporal
TEMPORAL_URL=localhost:7233
```

### Optional
```bash
# Authentication
WORKOS_API_KEY=<your-key>
WORKOS_CLIENT_ID=<your-id>

# AI/ML
ANTHROPIC_API_KEY=<your-key>

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ADMIN_PASSWORD=admin
```

---

## Keyboard Shortcuts (Overmind/tmux)

| Action | Shortcut |
|--------|----------|
| **Detach from service** | Ctrl+B, D |
| **List sessions** | tmux ls |
| **Attach to session** | tmux attach -t overmind-... |
| **Kill session** | Ctrl+C (in overmind connect) |
| **Switch panes** | Ctrl+B, arrow keys |
| **New window** | Ctrl+B, C |
| **Previous window** | Ctrl+B, P |
| **Next window** | Ctrl+B, N |

---

## Build & Deploy

### Local Build
```bash
# Frontend
cd frontend/apps/web && bun run build

# Go
cd backend && go build -o bin/server .

# Python
pip install build && python -m build
```

### Docker Build
```bash
# Build all images
make docker-build

# Tag and push
make docker-push DOCKER_REGISTRY=registry.example.com
```

### Deploy to Production
```bash
# Using Make
make k8s-deploy NAMESPACE=tracertm IMAGE_TAG=v1.0.0

# Using kubectl directly
kubectl apply -f k8s/
```

---

## Helpful URLs (Development)

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | Web application |
| **Gateway** | http://localhost | Unified API entry |
| **Go API** | http://localhost:8080 | Go backend API |
| **Python API** | http://localhost:4000 | Python backend API |
| **Temporal UI** | http://localhost:8233 | Workflows |
| **Neo4j Browser** | http://localhost:7474 | Graph database |
| **Grafana** | http://localhost:3000 | Monitoring |
| **Prometheus** | http://localhost:9090 | Metrics |
| **Storybook** | http://localhost:6006 | Component library |

---

## Emergency Commands

### Kill Everything
```bash
# Stop overmind
overmind kill

# Kill all processes
pkill -f overmind
pkill -f air
pkill -f uvicorn
pkill -f bun

# Clear all ports
lsof -ti:80,8080,8000,5173 | xargs kill -9
```

### Reset Database
```bash
# PostgreSQL
dropdb tracertm && createdb tracertm
make db-migrate

# Redis
redis-cli FLUSHALL

# Neo4j
# Open http://localhost:7474
MATCH (n) DETACH DELETE n
```

### Complete Clean
```bash
# Remove all caches and builds
make clean:all

# Reinstall dependencies
rm -rf node_modules bun.lockb
bun install

rm -rf vendor go.sum
go mod download

pip install -e ".[dev]" --force-reinstall
```

---

## Getting Help

- **Architecture**: See `docs/guides/UNIFIED_ARCHITECTURE.md`
- **Workflow**: See `docs/guides/DEVELOPMENT_WORKFLOW.md`
- **Implementation**: See `docs/reports/UNIFIED_INFRASTRUCTURE_IMPLEMENTATION.md`
- **Deployment**: See `docs/guides/DEPLOYMENT_GUIDE.md`
- **Issues**: Check GitHub Issues or ask in team chat

---

**Pro Tip:** Print this page and keep it near your desk for quick reference!

---

**Document Version:** 2.0.0
**Last Updated:** January 31, 2026
**Maintained By:** TracerTM Engineering Team
