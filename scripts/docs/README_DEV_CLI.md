# TraceRTM Development CLI

A comprehensive command-line tool for local development workflows including service health checks, database seeding, cache management, and log monitoring.

## Installation

Install development dependencies:

```bash
pip install -r scripts/dev-requirements.txt
```

Or install into your virtual environment:

```bash
source .venv/bin/activate
pip install -r scripts/dev-requirements.txt
```

## Usage

The development CLI is available as `./scripts/dev` and provides several commands:

### Quick Start

```bash
# Initialize development environment
./scripts/dev init

# Check all services
./scripts/dev health

# Seed database with test data
./scripts/dev seed

# Show service status
./scripts/dev status
```

## Commands

### Health Check

Check the health of all required services:

```bash
./scripts/dev health
```

Checks:
- PostgreSQL database connection
- Redis cache connection
- Neo4j graph database connection
- NATS message broker
- Temporal workflow engine
- MinIO/S3 storage
- Go backend (if running)
- Python backend (if running)
- Gateway (if running)

Options:
- `--verbose, -v`: Show detailed information

### Database Seeding

Seed the database with test data:

```bash
# Basic seed data
./scripts/dev seed

# Comprehensive seed data
./scripts/dev seed --comprehensive

# Custom project name
./scripts/dev seed --project-name "My Test Project"
```

Available seed scripts:
- `seed.py`: Basic sample project with items, links, and agents
- `seed_comprehensive.py`: Comprehensive multi-project data
- `seed_rich_single_project.py`: Rich single project with extensive relationships
- `seed_swiftride_comprehensive.py`: SwiftRide demo project

### Database Reset

Reset the database (drop all tables and recreate):

```bash
./scripts/dev reset
```

This will:
1. Drop the public schema
2. Recreate the schema
3. Run all Alembic migrations

**Warning**: This is destructive and will delete all data!

### Cache Management

Clear caches and temporary data:

```bash
# Clear all caches
./scripts/dev clear --all

# Clear Redis only
./scripts/dev clear --redis

# Clear Neo4j only
./scripts/dev clear --neo4j
```

### Log Management

View service logs:

```bash
# Show all service logs (last 50 lines)
./scripts/dev logs

# Show specific service logs
./scripts/dev logs --service go

# Follow logs (like tail -f)
./scripts/dev logs --service python --follow

# Show more lines
./scripts/dev logs --service gateway --lines 100
```

Service names:
- `go`: Go backend
- `python`: Python backend
- `gateway`: API gateway
- `temporal`: Temporal workflow engine
- `nats`: NATS message broker

### Service Status

Show detailed status of all services:

```bash
./scripts/dev status
```

This shows:
- Whether process-compose is running
- All running service processes
- Resource usage

### Generate Test Data

Generate custom test data:

```bash
# Default: 10 users, 5 projects, 50 items
./scripts/dev generate

# Custom counts
./scripts/dev generate --users 20 --projects 10 --items 100

# Short flags
./scripts/dev generate -u 50 -p 20 -i 200
```

## Development Workflows

### Starting Fresh

```bash
# Reset everything
./scripts/dev reset
./scripts/dev clear --all

# Seed with test data
./scripts/dev seed --comprehensive

# Verify everything is working
./scripts/dev health
```

### Daily Development

```bash
# Check services are running
./scripts/dev health

# View logs if something is wrong
./scripts/dev logs --service go --follow
```

### Testing Different Scenarios

```bash
# Generate large dataset
./scripts/dev generate -u 100 -p 50 -i 1000

# Clear caches to test cold start
./scripts/dev clear --all

# Reset to clean state
./scripts/dev reset
./scripts/dev seed
```

## Utility Modules

The CLI uses utility modules in `scripts/utils/`:

### Database Utilities (`db_utils.py`)

```python
from scripts.utils import db_utils

# Get database configuration
config = db_utils.get_db_config()

# Check if table exists
if db_utils.table_exists("projects"):
    count = db_utils.get_table_count("projects")
    print(f"Projects: {count}")

# Run migrations
db_utils.run_migrations("up")

# Create backup
backup_file = db_utils.backup_database()
print(f"Backup saved to: {backup_file}")
```

### Service Utilities (`service_utils.py`)

```python
from scripts.utils import service_utils

# Clear Redis cache
deleted = service_utils.clear_redis_cache("user:*")
print(f"Deleted {deleted} keys")

# Get Redis stats
stats = service_utils.get_redis_stats()
print(f"Total keys: {stats['total_keys']}")

# Get Neo4j stats
stats = service_utils.get_neo4j_stats()
print(f"Nodes: {stats['nodes']}, Relationships: {stats['relationships']}")

# Check if port is available
if service_utils.check_port_available(8080):
    print("Port 8080 is available")
```

## Environment Variables

The CLI reads configuration from environment variables:

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

## Troubleshooting

### Services not healthy

```bash
# Check which services are down
./scripts/dev health --verbose

# Check if services are running
./scripts/dev status

# View service logs
./scripts/dev logs --service <name>
```

### Database connection errors

```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Reset database if corrupted
./scripts/dev reset
```

### Redis connection errors

```bash
# Check Redis is running
redis-cli ping

# Clear Redis cache
./scripts/dev clear --redis
```

### Neo4j connection errors

```bash
# Check Neo4j is running
cypher-shell -u neo4j -p password "RETURN 1"

# Clear Neo4j data
./scripts/dev clear --neo4j
```

## Advanced Usage

### Creating Custom Seed Scripts

Create a new seed script in `scripts/`:

```python
#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tracertm.models import Project, Item

def seed_custom_data():
    engine = create_engine(os.getenv("DATABASE_URL"))
    with Session(engine) as session:
        # Your seeding logic here
        project = Project(name="Custom Project")
        session.add(project)
        session.commit()

if __name__ == "__main__":
    seed_custom_data()
```

Run it with:

```bash
python scripts/your_seed_script.py
```

### Integrating with CI/CD

Use the dev CLI in CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Setup test environment
  run: |
    ./scripts/dev init
    ./scripts/dev health
    ./scripts/dev seed

- name: Run tests
  run: make test

- name: Cleanup
  run: ./scripts/dev reset
```

### Docker Integration

Use dev CLI in Docker containers:

```dockerfile
# Install dev dependencies
COPY scripts/dev-requirements.txt /app/scripts/
RUN pip install -r /app/scripts/dev-requirements.txt

# Run health checks
HEALTHCHECK CMD ./scripts/dev health || exit 1
```

## Best Practices

1. **Always check health before development**:
   ```bash
   ./scripts/dev health
   ```

2. **Use seed data consistently**:
   ```bash
   # Always use the same seed for reproducible testing
   ./scripts/dev reset && ./scripts/dev seed
   ```

3. **Clear caches when debugging**:
   ```bash
   ./scripts/dev clear --all
   ```

4. **Monitor logs during development**:
   ```bash
   ./scripts/dev logs --service python --follow
   ```

5. **Backup before major changes**:
   ```python
   from scripts.utils import db_utils
   backup = db_utils.backup_database()
   ```

## Contributing

When adding new commands:

1. Add the command to `scripts/dev`
2. Add any helper functions to `scripts/utils/`
3. Update this README with documentation
4. Add tests if applicable

## License

Part of the TraceRTM project.
