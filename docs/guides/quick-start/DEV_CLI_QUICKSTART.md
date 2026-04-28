# Development CLI Quick Start

Quick reference for the TraceRTM development CLI.

## Installation

```bash
# Install dev CLI dependencies
./scripts/shell/install-dev-cli.sh

# Or manually
pip install -r scripts/dev-requirements.txt
```

## Common Commands

### Daily Development

```bash
# Check if all services are healthy
make dev-health

# Start services
make dev

# View logs
make dev-logs

# Check service status
./scripts/dev status
```

### Database Operations

```bash
# Seed database with test data
make dev-seed

# Seed with comprehensive data
make dev-seed-full

# Reset database (WARNING: destructive)
make dev-reset

# Generate custom test data
make dev-generate USERS=50 PROJECTS=20 ITEMS=200
```

### Cache Management

```bash
# Clear all caches
make dev-clear

# Clear Redis only
make dev-clear-redis

# Clear Neo4j only
make dev-clear-neo4j
```

### Service Monitoring

```bash
# Health check all services
./scripts/dev health --verbose

# Show service status
./scripts/dev status

# View logs
./scripts/dev logs --service python --follow

# Show last 100 lines
./scripts/dev logs --service go --lines 100
```

## Quick Reference

| Command | Description |
|---------|-------------|
| `make dev-health` | Check service health |
| `make dev-seed` | Seed basic test data |
| `make dev-seed-full` | Seed comprehensive data |
| `make dev-reset` | Reset database |
| `make dev-clear` | Clear all caches |
| `make dev-generate` | Generate test data |
| `make dev-init` | Initialize environment |

## Service Health Checks

The health check verifies:

- ✅ PostgreSQL connection
- ✅ Redis connection
- ✅ Neo4j connection
- ✅ NATS broker
- ✅ Temporal workflow engine
- ✅ MinIO/S3 storage
- ✅ Go backend (if running)
- ✅ Python backend (if running)
- ✅ Gateway (if running)

## Troubleshooting

### Services Not Healthy

```bash
# Check what's down
./scripts/dev health --verbose

# View service logs
./scripts/dev logs --service <name> --follow

# Restart service
make dev-restart SERVICE=<name>
```

### Database Issues

```bash
# Reset database
make dev-reset

# Re-seed data
make dev-seed
```

### Cache Issues

```bash
# Clear all caches
make dev-clear

# Or clear specific cache
make dev-clear-redis
make dev-clear-neo4j
```

## Advanced Usage

### Custom Seeding

```bash
# Generate specific amounts of data
./scripts/dev generate \
  --users 100 \
  --projects 50 \
  --items 1000
```

### Database Backup

```python
from scripts.utils import db_utils

# Create backup
backup_file = db_utils.backup_database()
print(f"Backup saved: {backup_file}")

# Restore backup
db_utils.restore_database(backup_file)
```

### Service Utilities

```python
from scripts.utils import service_utils

# Get Redis stats
stats = service_utils.get_redis_stats()
print(f"Keys: {stats['total_keys']}")
print(f"Memory: {stats['used_memory']}")

# Get Neo4j stats
stats = service_utils.get_neo4j_stats()
print(f"Nodes: {stats['nodes']}")
print(f"Relationships: {stats['relationships']}")
```

## Environment Variables

The CLI reads from `.env`:

```bash
# Database
DATABASE_URL=postgresql://tracertm:password@localhost:5432/tracertm

# Redis
REDIS_URL=redis://localhost:6379

# Neo4j
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Services
GO_BACKEND_PORT=8080
PYTHON_BACKEND_PORT=8000
GATEWAY_PORT=4000
```

## Full Documentation

See [scripts/docs/README_DEV_CLI.md](../../../scripts/docs/README_DEV_CLI.md) for complete documentation.
