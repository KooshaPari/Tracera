# Integration Guide

## Overview

This guide explains how to integrate Pheno SDK modules into your projects (atoms, router, morph, zen-mcp-server, and others). The extracted modules are designed for seamless integration with minimal configuration.

## Installation Methods

### 1. PyPI Installation (Recommended)

```bash
# Install latest stable version
pip install pheno-sdk

# Install with specific extras
pip install pheno-sdk[cache,database,deployment]

# Install everything
pip install pheno-sdk[all]
```

### 2. GitHub Packages (Private Registry)

```bash
# Configure authentication
export GITHUB_TOKEN=your_personal_access_token

# Install from GitHub Packages
pip install pheno-sdk \
  --index-url https://${GITHUB_TOKEN}@github.com/your-org/_registry/pypi/simple
```

### 3. Git URL with PAT

```bash
# Direct installation from Git
pip install git+https://${GITHUB_TOKEN}@github.com/your-org/pheno-sdk.git

# Install specific branch or tag
pip install git+https://${GITHUB_TOKEN}@github.com/your-org/pheno-sdk.git@v1.0.0
```

### 4. Local Development

```bash
# Clone and install in development mode
git clone https://github.com/your-org/pheno-sdk.git
cd pheno-sdk
pip install -e ".[dev,test]"
```

## Project-Specific Integration

### Atoms Integration

```python
# atoms/requirements.txt
pheno-sdk>=1.0.0

# atoms/src/atoms/core.py
from pheno.testing.mcp_qa import MCPTestRunner
from pheno.utilities.cache import HotCache
from pheno.database import DatabaseClient

class AtomsCore:
    def __init__(self):
        self.cache = HotCache(max_size=1000)
        self.db = DatabaseClient(url=os.getenv("DATABASE_URL"))
        self.test_runner = MCPTestRunner()

    async def process_request(self, request):
        # Check cache first
        cached = await self.cache.get(request.id)
        if cached:
            return cached

        # Process and cache
        result = await self._process(request)
        await self.cache.set(request.id, result, ttl=300)
        return result
```

### Router Integration

```python
# router/pyproject.toml
[tool.poetry.dependencies]
pheno-sdk = "^1.0.0"

# router/router_core/optimization.py
from pheno.llm.optimization import HTTPPool, RateLimiter
from pheno.storage.cache import DistributedCache

class RouterOptimizer:
    def __init__(self):
        self.http_pool = HTTPPool(max_connections=100)
        self.rate_limiter = RateLimiter(default_limit="1000/minute")
        self.cache = DistributedCache(backend="redis")

    async def route_request(self, request):
        # Check rate limits
        if not await self.rate_limiter.check_rate_limit(request.user_id):
            raise RateLimitExceeded()

        # Check cache
        cache_key = f"route:{request.endpoint}:{request.params_hash}"
        cached_route = await self.cache.get(cache_key)
        if cached_route:
            return cached_route

        # Compute optimal route
        route = await self._compute_route(request)
        await self.cache.set(cache_key, route, ttl=60)
        return route
```

### Morph Integration

```python
# morph/requirements.txt
pheno-sdk[database,deployment]>=1.0.0

# morph/src/morph/deploy.py
from pheno.deployment import DeploymentManager
from pheno.deployment.platforms import VercelDeployer
from pheno.database import MigrationRunner

class MorphDeployer:
    def __init__(self):
        self.deployer = DeploymentManager()
        self.vercel = VercelDeployer(token=os.getenv("VERCEL_TOKEN"))
        self.migrations = MigrationRunner(migrations_dir="./migrations")

    async def deploy_application(self, config):
        # Run migrations first
        await self.migrations.migrate()

        # Deploy to Vercel
        deployment = await self.vercel.deploy(
            project=config.project_name,
            environment=config.environment,
            domains=config.domains
        )

        # Health check
        await deployment.wait_until_ready()
        return deployment.url
```

### Zen MCP Server Integration

```python
# zen-mcp-server/pyproject.toml
[dependencies]
pheno-sdk = {version = "^1.0.0", extras = ["mcp", "testing"]}

# zen-mcp-server/src/zen/server.py
from pheno.mcp.server import MCPServer
from pheno.testing.mcp_qa import BaseClientAdapter
from pheno.auth.oauth import OAuthProvider

class ZenMCPServer(MCPServer):
    def __init__(self):
        super().__init__()
        self.oauth = OAuthProvider(provider="github")

    async def handle_tool_call(self, tool_name, arguments):
        # Authenticate if needed
        if self.requires_auth(tool_name):
            token = await self.oauth.get_token()
            arguments["auth_token"] = token

        # Process tool call
        return await super().handle_tool_call(tool_name, arguments)

# Testing
class ZenTestAdapter(BaseClientAdapter):
    def _process_result(self, result, tool_name, params):
        # Custom result processing for Zen
        return result.get("data", result)
```

## Configuration Patterns

### Environment Variables

```bash
# .env file for all projects using pheno-sdk
# Cache Configuration
PHENO_CACHE_DIR=/var/cache/pheno
PHENO_HOT_CACHE_SIZE=1000
PHENO_CACHE_TTL=300

# Database Configuration
PHENO_DATABASE_URL=postgresql://localhost/mydb
PHENO_DB_POOL_SIZE=20
PHENO_DB_ECHO=false

# HTTP Optimization
PHENO_HTTP_MAX_CONNECTIONS=100
PHENO_HTTP_KEEPALIVE=30

# OAuth Configuration
PHENO_OAUTH_GITHUB_CLIENT_ID=your_client_id
PHENO_OAUTH_GITHUB_CLIENT_SECRET=your_secret
```

### Shared Configuration

```python
# shared_config.py - Used by all projects
from pheno.config import PhenoConfig

config = PhenoConfig(
    cache={
        "hot_cache_size": 1000,
        "cold_cache_path": "/cache",
        "distributed_backend": "redis"
    },
    database={
        "url": os.getenv("DATABASE_URL"),
        "pool_size": 20,
        "echo": False
    },
    optimization={
        "http_pool_size": 100,
        "rate_limit_default": "1000/hour",
        "compression_enabled": True
    }
)

# Export for use in projects
PHENO_CONFIG = config
```

## Import Migration

### Old Imports (Before Pheno SDK)

```python
# In atoms
from atoms.vendor.cache import HotCache
from atoms.vendor.database import DatabaseClient
from atoms.vendor.testing.mcp_qa import TestRunner

# In router
from router.vendor.optimization import HTTPPool
from router.vendor.cache import ColdCache

# In morph
from morph.vendor.deployment import Deployer
```

### New Imports (With Pheno SDK)

```python
# Unified imports across all projects
from pheno.utilities.cache import HotCache
from pheno.storage.cache import ColdCache
from pheno.database import DatabaseClient
from pheno.testing.mcp_qa import MCPTestRunner
from pheno.llm.optimization import HTTPPool
from pheno.deployment import DeploymentManager
```

## Dependency Management

### Poetry Projects

```toml
# pyproject.toml
[tool.poetry.dependencies]
python = "^3.11"
pheno-sdk = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pheno-sdk = {version = "^1.0.0", extras = ["dev", "test"]}
```

### Pip Requirements

```txt
# requirements.txt
pheno-sdk>=1.0.0,<2.0.0

# requirements-dev.txt
pheno-sdk[dev,test]>=1.0.0
```

### Docker Integration

```dockerfile
# Dockerfile
FROM python:3.11-slim

# Install pheno-sdk
RUN pip install pheno-sdk==1.0.0

# Or from GitHub Packages
ARG GITHUB_TOKEN
RUN pip install pheno-sdk \
  --index-url https://${GITHUB_TOKEN}@github.com/org/_registry/pypi/simple

# Copy application
COPY . /app
WORKDIR /app

CMD ["python", "main.py"]
```

## Testing Integration

### Pytest Configuration

```ini
# pytest.ini
[pytest]
plugins = pheno.testing.mcp_qa.pytest_plugin
markers =
    mcp: MCP-specific tests
    integration: Integration tests
    slow: Slow-running tests

testpaths = tests
asyncio_mode = auto
```

### Test Fixtures

```python
# conftest.py
from pheno.testing.fixtures import *
from pheno.testing.mcp_qa import mcp_client, oauth_token

@pytest.fixture
async def app_with_pheno():
    """Application with Pheno SDK integration"""
    from pheno.database import DatabaseClient
    from pheno.utilities.cache import HotCache

    app = create_app()
    app.db = DatabaseClient(url="postgresql://test")
    app.cache = HotCache()

    yield app

    await app.db.close()
    await app.cache.clear()
```

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test with Pheno SDK

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install Pheno SDK
        run: |
          pip install pheno-sdk[test]

      - name: Run tests
        run: |
          pytest --cov=myapp --cov-report=html
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    environment:
      - PHENO_DATABASE_URL=postgresql://db:5432/mydb
      - PHENO_CACHE_BACKEND=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: mydb

  redis:
    image: redis:7
```

## Performance Tuning

### Optimization Configuration

```python
# performance_config.py
from pheno.optimization import PerformanceProfile

# Development profile
dev_profile = PerformanceProfile(
    cache_enabled=False,
    http_connections=10,
    db_connections=5,
    compression_enabled=False
)

# Production profile
prod_profile = PerformanceProfile(
    cache_enabled=True,
    cache_size=10000,
    http_connections=100,
    db_connections=20,
    compression_enabled=True,
    rate_limiting_enabled=True
)

# Apply based on environment
profile = prod_profile if os.getenv("ENV") == "production" else dev_profile
```

## Monitoring Integration

```python
# monitoring.py
from pheno.observability import MetricsCollector, Tracer

metrics = MetricsCollector(
    backend="prometheus",
    port=9090
)

tracer = Tracer(
    backend="jaeger",
    service_name="my-app"
)

# Track Pheno SDK metrics
@metrics.track("pheno.cache.hit_rate")
async def check_cache_performance():
    from pheno.utilities.cache import get_global_cache
    cache = get_global_cache()
    return cache.get_statistics()["hit_rate"]
```

## Troubleshooting

### Common Issues

#### Import Errors
```python
# Problem: ImportError: cannot import name 'HotCache'
# Solution: Ensure pheno-sdk is installed
pip install pheno-sdk

# Verify installation
python -c "import pheno; print(pheno.__version__)"
```

#### Version Conflicts
```bash
# Check for conflicts
pip check

# Force reinstall
pip install --force-reinstall pheno-sdk
```

#### Missing Extras
```python
# Problem: ImportError when using specific features
# Solution: Install required extras
pip install pheno-sdk[cache,database,deployment]
```

## Best Practices

1. **Version Pinning**: Always pin pheno-sdk version in production
2. **Selective Imports**: Import only what you need
3. **Configuration Management**: Use environment variables
4. **Error Handling**: Wrap pheno-sdk calls in try-except blocks
5. **Testing**: Use provided test fixtures and utilities
6. **Monitoring**: Track pheno-sdk metrics in production

## Migration Checklist

- [ ] Install pheno-sdk in project
- [ ] Update import statements
- [ ] Configure environment variables
- [ ] Update CI/CD pipelines
- [ ] Run tests to verify integration
- [ ] Update documentation
- [ ] Monitor performance metrics
- [ ] Remove old vendor code

## Support

- [Documentation](https://your-org.github.io/pheno-sdk/)
- [GitHub Issues](https://github.com/your-org/pheno-sdk/issues)
- [Discord Community](https://discord.gg/pheno-sdk)

---

*Version: 1.0.0*
*Last Updated: October 2024*
