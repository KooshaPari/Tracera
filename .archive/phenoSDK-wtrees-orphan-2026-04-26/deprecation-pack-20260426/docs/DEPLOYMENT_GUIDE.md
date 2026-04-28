# Pheno SDK Deployment Guide

**Version:** 2.0
**Status:** Production Ready
**Last Updated:** 2025-10-16

## Quick Start

### Installation

```bash
# Install pheno-sdk
pip install pheno-sdk

# Install optional dependencies
pip install nats-py pyyaml click
```

### Basic Deployment

```python
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.global_registry import ResourceMode

# Initialize manager
manager = DeploymentManager(
    instance_id="my-service-1",
    project_name="myapp"  # Optional, for tenanted mode
)

# Deploy a Docker resource globally
await manager.deploy_resource(
    name="postgres",
    config={
        "type": "docker",
        "image": "postgres:16",
        "ports": {5432: 5432},
        "environment": {"POSTGRES_PASSWORD": "secret"}
    },
    mode=ResourceMode.GLOBAL
)

# Start the resource
await manager.start_resource("postgres")
```

## Deployment Modes

### Global Resources

Global resources are singletons managed by the first instance to start. Other instances discover and connect to them.

**Use cases:**
- Shared databases
- Message queues
- Cache servers
- Tunnels (ai.kooshapari.com, morph.kooshapari.com)

**Features:**
- Automatic failover if manager dies
- Service discovery via NATS
- Health monitoring
- All instances can discover and use

**Example:**

```python
# Deploy as global
await manager.deploy_resource(
    name="shared-postgres",
    config={
        "type": "docker",
        "image": "postgres:16",
        "ports": {5432: 5432}
    },
    mode=ResourceMode.GLOBAL
)
```

### Tenanted Resources

Per-project scoped resources with complete isolation.

**Use cases:**
- Project-specific services
- Tenant-specific databases
- Private caches
- Isolated environments

**Features:**
- Complete resource isolation
- Per-project port allocation
- No port conflicts
- Clean per-tenant cleanup

**Example:**

```python
# Initialize for specific tenant
manager = DeploymentManager(
    instance_id="tenant-service-1",
    project_name="tenant-acme"  # Scopes all resources
)

await manager.deploy_resource(
    name="tenant-db",
    config={
        "type": "docker",
        "image": "postgres:16"
    },
    mode=ResourceMode.TENANTED
)
```

### Local Resources

Single-instance, local-only resources without coordination.

**Use cases:**
- Development environments
- Local testing
- Single-service deployments

**Example:**

```python
await manager.deploy_resource(
    name="redis",
    config={"type": "docker", "image": "redis:7"},
    mode=ResourceMode.LOCAL
)
```

## Resource Types

### Docker Containers

```python
await manager.deploy_resource(
    name="my-app",
    config={
        "type": "docker",
        "image": "my-app:latest",
        "container_name": "my-app-container",
        "ports": {8000: 8000, 8080: 8080},
        "environment": {
            "DEBUG": "true",
            "DATABASE_URL": "postgres://..."
        },
        "volumes": {
            "/data": "/app/data",
            "/logs": "/var/log/app"
        },
        "restart_policy": "always",
        "health_check": {
            "type": "http",
            "path": "/health",
            "interval": 30
        }
    },
    mode=ResourceMode.GLOBAL
)
```

### System Daemons (systemd/launchd)

```python
await manager.deploy_resource(
    name="my-daemon",
    config={
        "type": "daemon",
        "service_name": "my-service",
        "daemon_type": "systemd",  # or "launchd"
        "use_sudo": True,
        "health_check": {
            "type": "tcp",
            "port": 8000
        }
    },
    mode=ResourceMode.LOCAL
)
```

### Commands

```python
await manager.deploy_resource(
    name="init-db",
    config={
        "type": "command",
        "command": "/usr/local/bin/db-init.sh",
        "cwd": "/opt/app",
        "env": {"DB_HOST": "localhost"},
        "timeout": 300
    }
)
```

## CLI Usage

### Deploy Resources

```bash
# Deploy from config file
pheno --instance-id my-service deploy postgres \
  --config postgres-config.json \
  --mode global

# Deploy with metadata
pheno deploy my-app \
  --config app-config.json \
  --metadata version=1.0.0 \
  --metadata env=production
```

### Manage Resources

```bash
# Start resource
pheno start postgres

# Stop resource
pheno stop postgres --cleanup-global

# Check status
pheno status
pheno status postgres

# Discover resources
pheno discover
pheno discover --mode global
pheno discover postgres

# Cleanup
pheno cleanup --all
pheno cleanup --mode global
```

### JSON Output

```bash
# Get status as JSON
pheno status --json | jq .

# Discover as JSON
pheno discover --json | jq '.resources[]'
```

## Configuration Files

### JSON Format

```json
{
  "type": "docker",
  "image": "postgres:16",
  "container_name": "postgres-db",
  "ports": {
    "5432": 5432
  },
  "environment": {
    "POSTGRES_PASSWORD": "secret",
    "POSTGRES_DB": "myapp"
  },
  "volumes": {
    "postgres_data": "/var/lib/postgresql/data"
  },
  "health_check": {
    "type": "command",
    "command": ["pg_isready", "-U", "postgres"]
  },
  "restart_policy": "always"
}
```

### YAML Format

```yaml
type: docker
image: postgres:16
container_name: postgres-db
ports:
  5432: 5432
environment:
  POSTGRES_PASSWORD: secret
  POSTGRES_DB: myapp
volumes:
  postgres_data: /var/lib/postgresql/data
health_check:
  type: command
  command: [pg_isready, -U, postgres]
restart_policy: always
```

## Global Resource Discovery

### Service Discovery Flow

1. **First Instance Starts:**
   - Registers resource globally
   - Becomes the manager
   - Publishes heartbeat via NATS

2. **Second Instance Starts:**
   - Queries for existing managers
   - Discovers first instance
   - Becomes a participant
   - Connects to shared resource

3. **Manager Fails:**
   - Participants detect heartbeat timeout
   - Automatic election triggered
   - New manager takes over
   - Others reconnect

### Discovering Resources Programmatically

```python
# Discover specific resource
resource = await manager.discover_resource("postgres")
if resource:
    print(f"Found: {resource}")

# List all resources
resources = await manager.list_resources(mode=ResourceMode.GLOBAL)
for name in resources:
    status = await manager.get_resource_status(name)
    print(f"{name}: {status}")
```

## Advanced Configuration

### Health Checks

```python
# HTTP health check
health_check={
    "type": "http",
    "path": "/health",
    "interval": 30,
    "timeout": 10,
    "retries": 3
}

# TCP health check
health_check={
    "type": "tcp",
    "port": 5432,
    "interval": 30,
    "timeout": 5
}

# Command health check
health_check={
    "type": "command",
    "command": ["curl", "-f", "http://localhost:8000/health"],
    "interval": 30
}
```

### Resource Limits

```python
config = {
    "type": "docker",
    "image": "my-app:latest",
    "cpu_shares": 1024,
    "memory_limit": "512m",
    "memory_swap_limit": "1g"
}
```

### Logging Configuration

```python
config = {
    "type": "docker",
    "image": "my-app:latest",
    "logging": {
        "driver": "json-file",
        "options": {
            "max-size": "10m",
            "max-file": "3"
        }
    }
}
```

## Tunneling with Global Resources

### Deploy Tunnels

```python
from pheno.infra.global_registry import ResourceMode

# Deploy AI routing tunnel globally
await manager.deploy_resource(
    name="ai-tunnel",
    config={
        "type": "tunnel",
        "domain": "ai.kooshapari.com",
        "local_host": "127.0.0.1",
        "local_port": 8000,
        "protocol": "https",
        "tls": True
    },
    mode=ResourceMode.GLOBAL
)

# Deploy Morph MCP tunnel globally
await manager.deploy_resource(
    name="morph-tunnel",
    config={
        "type": "tunnel",
        "domain": "morph.kooshapari.com",
        "local_host": "127.0.0.1",
        "local_port": 9000,
        "protocol": "https",
        "tls": True
    },
    mode=ResourceMode.GLOBAL
)
```

### Tunnel Discovery

```python
# Discover tunnel status
ai_status = await manager.discover_resource("ai-tunnel")
morph_status = await manager.discover_resource("morph-tunnel")

print(f"AI Tunnel: {ai_status}")
print(f"Morph Tunnel: {morph_status}")
```

## Service Templates

### Generate SystemD Service File

```python
from pheno.infra.service_templates import SystemDTemplateGenerator

content = SystemDTemplateGenerator.generate_service_file(
    service_name="my-app",
    description="My Application",
    exec_start="/usr/bin/python3 /opt/app/main.py",
    user="www-data",
    environment={"LOG_LEVEL": "INFO"},
    restart_policy="on-failure",
    memory_limit="512M"
)

SystemDTemplateGenerator.save_service_file(
    "my-app",
    content,
    output_dir="/etc/systemd/system"
)
```

### Generate Docker Compose

```python
from pheno.infra.service_templates import DockerComposeTemplateGenerator

generator = DockerComposeTemplateGenerator()

postgres = generator.create_service(
    image="postgres:16",
    environment={"POSTGRES_PASSWORD": "secret"},
    volumes={"postgres_data": "/var/lib/postgresql/data"}
)

app = generator.create_service(
    image="my-app:latest",
    ports={8000: 8000},
    depends_on=["postgres"]
)

content = generator.generate_compose_file(
    services={"postgres": postgres, "app": app},
    volumes={"postgres_data": generator.create_volume()}
)

generator.save_compose_file(content, "docker-compose.yml")
```

### Generate Nginx Configuration

```python
from pheno.infra.service_templates import NginxTemplateGenerator

config = NginxTemplateGenerator.generate_server_block(
    server_name="example.com",
    upstream="backend",
    ssl_cert="/etc/letsencrypt/live/example.com/fullchain.pem",
    ssl_key="/etc/letsencrypt/live/example.com/privkey.pem",
    security_headers=True,
    compression=True,
    cache_enabled=True,
    cache_zone="default"
)

print(config)
```

## Troubleshooting

### Resource Not Found

```bash
# Check if resource exists
pheno discover myresource

# List all resources
pheno discover

# Check status of all resources
pheno status
```

### Health Check Failures

```bash
# Check resource status details
pheno status myresource --json | jq .local.healthy

# View logs if running in Docker
docker logs kinfra-myresource

# Check systemd status if running as daemon
sudo systemctl status my-service
```

### Port Conflicts

```bash
# List all allocated ports (for tenanted resources)
pheno status --json | jq '.[] | .local.port'

# Find which process uses a port
lsof -i :8000
netstat -tulpn | grep :8000
```

### NATS Connection Issues

```bash
# Verify NATS is running
nc -v localhost 4222

# Check NATS logs
docker logs nats-server
```

## Performance Considerations

### Resource Limits

```python
# Set reasonable limits to prevent resource exhaustion
config = {
    "type": "docker",
    "image": "my-app:latest",
    "memory_limit": "1g",
    "memory_swap_limit": "2g",
    "cpu_shares": 1024,  # 1 CPU equivalent
}
```

### Health Check Tuning

```python
# Reduce check frequency for stable services
health_check = {
    "type": "http",
    "path": "/health",
    "interval": 60,  # Check every 60 seconds
    "timeout": 5,
    "retries": 3
}
```

### Caching

```python
# Enable proxy caching for static content
config = {
    "type": "proxy",
    "cache_enabled": True,
    "cache_zone": "default",
    "cache_valid": {"200": "10m", "404": "1m"}
}
```

## Security Best Practices

1. **Use Strong Passwords**
   - Never commit passwords to git
   - Use environment variables or secrets management
   - Rotate credentials regularly

2. **Enable TLS**
   - Always use HTTPS for tunnels
   - Use valid SSL certificates (Let's Encrypt)
   - Enable HSTS headers

3. **Network Isolation**
   - Isolate resources by network
   - Use firewall rules to restrict access
   - Enable authentication/authorization

4. **Logging & Monitoring**
   - Enable comprehensive logging
   - Monitor resource health
   - Set up alerts for failures

5. **Secrets Management**
   ```python
   import os
   config = {
       "type": "docker",
       "environment": {
           "DB_PASSWORD": os.environ.get("DB_PASSWORD"),
           "API_KEY": os.environ.get("API_KEY")
       }
   }
   ```

## Production Deployment Checklist

- ✅ Test all resources locally
- ✅ Validate configuration files
- ✅ Set up health checks
- ✅ Configure logging
- ✅ Enable NATS coordination
- ✅ Implement monitoring/alerts
- ✅ Plan for failover scenarios
- ✅ Test disaster recovery
- ✅ Document deployment procedure
- ✅ Set up log aggregation

## See Also

- [GLOBAL_TENANTED_PATTERNS.md](./GLOBAL_TENANTED_PATTERNS.md) - Detailed patterns guide
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture
- [API Documentation](../README.md)
