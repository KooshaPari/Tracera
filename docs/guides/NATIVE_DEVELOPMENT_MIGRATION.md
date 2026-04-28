# Native Development Migration Guide

This guide helps you migrate from Docker-based development to native process orchestration.

## Overview

**Before (Docker):**
- Docker daemon runs all services in containers
- High resource usage (~2-4GB RAM)
- `docker-compose up` to start
- Services isolated in containers

**After (Native):**
- Services run as native processes
- Low resource usage (~500MB-1GB RAM)
- `make dev` or `process-compose up` to start
- Services run directly on your system

## Prerequisites

### Check Current Installation

```bash
# Verify Homebrew services
brew services list | grep -E "(postgres|redis|neo4j|nats)"

# Check running services
lsof -i :5432,6379,7687,4222
```

### Stop Docker Services

If you have Docker running:

```bash
# Stop Docker Compose stack
docker-compose down

# Optionally stop Docker daemon
# macOS: Stop Docker Desktop app
# Linux: sudo systemctl stop docker
```

## Installation Steps

### 1. Run Installation Script

```bash
# Install all native dependencies
make install-native
```

This will:
- Install Process Compose
- Install all required services via Homebrew (macOS) or APT (Linux)
- Initialize PostgreSQL database
- Create working directories
- Verify installation

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit if needed (defaults should work)
nano .env
```

### 3. Run Database Migrations

```bash
# Ensure PostgreSQL is running
brew services start postgresql@17  # macOS
# sudo systemctl start postgresql  # Linux

# Run migrations
alembic upgrade head
```

### 4. Start Services

```bash
# Option A: Interactive TUI (recommended for first run)
make dev-tui

# Option B: Detached mode
make dev
```

## Platform-Specific Notes

### macOS

All services installed via Homebrew:

```bash
# Check Homebrew services
brew services list

# Start/stop individual service
brew services start postgresql@17
brew services stop postgresql@17
```

### Linux (Ubuntu/Debian)

Services installed via APT and binaries:

```bash
# Check systemd services
systemctl status postgresql
systemctl status redis

# Start/stop individual service
sudo systemctl start postgresql
sudo systemctl stop redis
```

### Windows

Services installed via Scoop:

```bash
# Use Windows-specific config
process-compose -f process-compose.windows.yaml up
```

## Verification

### Test All Services

```bash
# Check Process Compose status
make dev-status

# Test database connection
psql -h localhost -U tracertm -d tracertm -c "SELECT 1;"

# Test Redis
redis-cli ping

# Test Neo4j
curl http://localhost:7474

# Test NATS
curl http://localhost:8222/healthz

# Test backends
curl http://localhost:8080/health  # Go
curl http://localhost:4000/health  # Python

# Test gateway
curl http://localhost:4000/health  # Caddy
```

### View Monitoring

```bash
# Open Grafana
make grafana-dashboard

# Open Prometheus
make prometheus-ui

# Check metrics
make metrics
```

## Common Migration Issues

### Issue: PostgreSQL won't start

**Solution:**

```bash
# Check if data directory exists
ls -la /opt/homebrew/var/postgresql@17

# Initialize if needed
initdb /opt/homebrew/var/postgresql@17

# Check logs
tail -f /opt/homebrew/var/log/postgresql@17.log
```

### Issue: Port already in use

**Solution:**

```bash
# Find process using port
lsof -i :5432

# Kill process if safe
kill -9 <PID>

# Or change port in process-compose.yaml
```

### Issue: Service dependencies timeout

**Solution:**

```bash
# Start infrastructure services first
process-compose up postgres redis neo4j nats

# Verify they're healthy
make dev-status

# Then start application services
make dev
```

### Issue: Process Compose not found

**Solution:**

```bash
# Reinstall Process Compose
brew install f1bonacc1/tap/process-compose

# Or manually:
# Linux:
wget https://github.com/F1bonacc1/process-compose/releases/latest/download/process-compose_linux_amd64.tar.gz
tar -xzf process-compose_linux_amd64.tar.gz
sudo mv process-compose /usr/local/bin/

# Verify installation
process-compose version
```

## Comparison: Docker vs Native Commands

| Task | Docker | Native |
|------|--------|--------|
| Start services | `docker-compose up` | `make dev` or `process-compose up` |
| Start with UI | N/A | `make dev-tui` |
| Stop services | `docker-compose down` | `make dev-down` |
| View logs | `docker-compose logs -f` | `make dev-logs` |
| Restart service | `docker-compose restart redis` | `make dev-restart SERVICE=redis` |
| Shell into service | `docker exec -it container bash` | Direct: `psql -h localhost -U tracertm` |
| Check status | `docker-compose ps` | `make dev-status` |
| Clean data | `docker-compose down -v` | `make data-clean` |

## Performance Comparison

### Resource Usage (Typical)

**Docker-based:**
- Docker daemon: ~1.5GB RAM
- All services: ~2-3GB RAM
- Total: ~3.5-4.5GB RAM

**Native:**
- All services: ~800MB-1.2GB RAM
- Total: ~800MB-1.2GB RAM

**Savings: ~70-75% less memory**

### Startup Time

**Docker-based:**
- Cold start: 30-45 seconds
- Warm start: 15-25 seconds

**Native:**
- Cold start: 8-12 seconds
- Warm start: 3-5 seconds

**Improvement: ~3-4x faster**

## Rollback to Docker (If Needed)

If you need to rollback:

```bash
# Stop native services
make dev-down

# Stop Homebrew services
brew services stop postgresql@17 redis neo4j nats-server

# Start Docker
docker-compose up -d
```

## Next Steps

1. **Team Onboarding:** Share `make install-native` with team
2. **CI/CD:** Keep Docker for CI/CD (native for dev only)
3. **Documentation:** Update any team docs referencing Docker
4. **Monitoring:** Configure Grafana dashboards for your services

## Support

- Process Compose Issues: https://github.com/F1bonacc1/process-compose/issues
- TraceRTM Issues: [Your issue tracker]
- Team Slack: #dev-infrastructure
