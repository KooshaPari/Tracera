# KInfra Quickstart: Shared Resource Setup

This guide walks you through setting up KInfra for multiple projects with shared resources, demonstrating advanced Phase 5 features for complex multi-service architectures.

## Prerequisites

- Python 3.11+
- pip or poetry
- Docker (for shared services)
- Basic understanding of microservices architecture

## Installation

```bash
# Install pheno-sdk with infra extras
pip install pheno-sdk[infra]

# Install additional dependencies for shared resources
pip install docker redis nats-py
```

## Architecture Overview

This setup demonstrates:
- **Multiple Projects**: API, Web, Worker projects
- **Shared Resources**: Redis, PostgreSQL, NATS
- **Global Resources**: Shared databases and message queues
- **Project Isolation**: Each project manages its own services
- **Resource Coordination**: Global resource sharing and cleanup

## Quick Start

### 1. Initialize Shared Infrastructure

```bash
# Initialize global KInfra configuration
kinfra config init --global

# Initialize project configurations
kinfra config init --project api-project
kinfra config init --project web-project  
kinfra config init --project worker-project
```

### 2. Start Shared Resources

```python
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.config_schemas import KInfraConfigManager

# Load configuration
config_manager = KInfraConfigManager()
config = config_manager.load()

# Initialize resource coordination
deployment_manager = DeploymentManager()
resource_coordinator = ResourceCoordinator(deployment_manager)

# Start shared resources
await resource_coordinator.initialize()

# Deploy global resources
redis_resource = await deployment_manager.deploy_resource(
    name="shared-redis",
    resource_type="redis",
    mode="global",
    config={
        "host": "localhost",
        "port": 6379,
        "db": 0
    }
)

postgres_resource = await deployment_manager.deploy_resource(
    name="shared-postgres",
    resource_type="postgres",
    mode="global", 
    config={
        "host": "localhost",
        "port": 5432,
        "database": "shared_db"
    }
)

nats_resource = await deployment_manager.deploy_resource(
    name="shared-nats",
    resource_type="nats",
    mode="global",
    config={
        "url": "nats://localhost:4222"
    }
)

print("✅ Shared resources deployed")
```

### 3. Project-Specific Setup

```python
from pheno.infra.project_context import project_infra_context
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy

# Initialize managers
process_manager = ProcessGovernanceManager()
tunnel_manager = TunnelGovernanceManager()
cleanup_manager = CleanupPolicyManager()

# API Project
with project_infra_context("api-project") as api_infra:
    # Start API services
    api_port = api_infra.start_service("api-server", port=8000)
    api_worker_port = api_infra.start_service("api-worker", port=8001)
    
    # Register processes
    api_metadata = ProcessMetadata(
        project="api-project",
        service="api-server",
        pid=1001,
        command_line=["python", "api_server.py"],
        environment={"PROJECT": "api-project", "REDIS_URL": "redis://localhost:6379/0"},
        scope="local",
        resource_type="api",
        tags={"web", "rest", "api"}
    )
    process_manager.register_process(1001, api_metadata)
    
    # Create tunnels
    api_tunnel = tunnel_manager.create_tunnel(
        project="api-project",
        service="api-server",
        port=api_port,
        provider="cloudflare",
        hostname="api.example.com"
    )
    
    print(f"✅ API Project: {api_tunnel.public_url}")

# Web Project  
with project_infra_context("web-project") as web_infra:
    # Start Web services
    web_port = web_infra.start_service("web-server", port=3000)
    web_worker_port = web_infra.start_service("web-worker", port=3001)
    
    # Register processes
    web_metadata = ProcessMetadata(
        project="web-project",
        service="web-server",
        pid=2001,
        command_line=["node", "web_server.js"],
        environment={"PROJECT": "web-project", "REDIS_URL": "redis://localhost:6379/1"},
        scope="local",
        resource_type="web",
        tags={"web", "frontend", "ui"}
    )
    process_manager.register_process(2001, web_metadata)
    
    # Create tunnels
    web_tunnel = tunnel_manager.create_tunnel(
        project="web-project",
        service="web-server",
        port=web_port,
        provider="cloudflare",
        hostname="web.example.com"
    )
    
    print(f"✅ Web Project: {web_tunnel.public_url}")

# Worker Project
with project_infra_context("worker-project") as worker_infra:
    # Start Worker services
    worker_port = worker_infra.start_service("worker-server", port=4000)
    worker_processor_port = worker_infra.start_service("worker-processor", port=4001)
    
    # Register processes
    worker_metadata = ProcessMetadata(
        project="worker-project",
        service="worker-server",
        pid=3001,
        command_line=["python", "worker_server.py"],
        environment={"PROJECT": "worker-project", "REDIS_URL": "redis://localhost:6379/2"},
        scope="local",
        resource_type="worker",
        tags={"worker", "background", "queue"}
    )
    process_manager.register_process(3001, worker_metadata)
    
    # Create tunnels
    worker_tunnel = tunnel_manager.create_tunnel(
        project="worker-project",
        service="worker-server",
        port=worker_port,
        provider="cloudflare",
        hostname="worker.example.com"
    )
    
    print(f"✅ Worker Project: {worker_tunnel.public_url}")
```

### 4. Advanced Cleanup Policies

```python
# Set up project-specific cleanup policies
projects = ["api-project", "web-project", "worker-project"]

for project in projects:
    # Create project-specific policy
    policy = cleanup_manager.create_default_policy(
        project_name=project,
        strategy=CleanupStrategy.MODERATE
    )
    
    # Customize cleanup rules based on project type
    if project == "api-project":
        # API projects need aggressive cleanup for performance
        cleanup_manager.update_project_rule(
            project_name=project,
            resource_type=ResourceType.PROCESS,
            strategy=CleanupStrategy.AGGRESSIVE,
            patterns=[f"{project}-*"],
            max_age=1800.0,
            force_cleanup=True
        )
    elif project == "web-project":
        # Web projects need moderate cleanup
        cleanup_manager.update_project_rule(
            project_name=project,
            resource_type=ResourceType.PROCESS,
            strategy=CleanupStrategy.MODERATE,
            patterns=[f"{project}-*"],
            max_age=3600.0,
            force_cleanup=False
        )
    elif project == "worker-project":
        # Worker projects need conservative cleanup
        cleanup_manager.update_project_rule(
            project_name=project,
            resource_type=ResourceType.PROCESS,
            strategy=CleanupStrategy.CONSERVATIVE,
            patterns=[f"{project}-*"],
            max_age=7200.0,
            force_cleanup=False
        )
    
    print(f"✅ Cleanup policy configured for {project}")
```

### 5. Global Resource Management

```python
from pheno.infra.global_registry import GlobalResourceRegistry

# Initialize global resource registry
global_registry = GlobalResourceRegistry()

# Register shared resources
await global_registry.register_resource(
    name="shared-redis",
    resource_type="redis",
    config={"host": "localhost", "port": 6379, "db": 0},
    metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]}
)

await global_registry.register_resource(
    name="shared-postgres",
    resource_type="postgres", 
    config={"host": "localhost", "port": 5432, "database": "shared_db"},
    metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]}
)

await global_registry.register_resource(
    name="shared-nats",
    resource_type="nats",
    config={"url": "nats://localhost:4222"},
    metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]}
)

print("✅ Global resources registered")
```

### 6. Status Monitoring and Dashboards

```python
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.proxy_gateway.health_dashboard import HealthDashboard

# Initialize status monitoring
status_manager = StatusPageManager()
health_dashboard = HealthDashboard()

# Update status for all projects
projects = ["api-project", "web-project", "worker-project"]
services = ["api-server", "web-server", "worker-server"]

for project in projects:
    for service in services:
        if f"{project.split('-')[0]}-server" == service:
            status_manager.update_service_status(
                project_name=project,
                service_name=service,
                status="running",
                port=8000 if "api" in service else 3000 if "web" in service else 4000,
                health_status="healthy"
            )

# Generate global status dashboard
global_status = status_manager.generate_status_page("global", "dashboard")
print("📊 Global status dashboard generated")

# Generate project-specific status pages
for project in projects:
    project_status = status_manager.generate_status_page(project, "status")
    print(f"📊 Status page generated for {project}")
```

## Docker Compose Integration

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Shared Resources
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - shared

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: shared_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - shared

  nats:
    image: nats:2.9-alpine
    ports:
      - "4222:4222"
    networks:
      - shared

  # KInfra Health Dashboard
  kinfra-dashboard:
    build: .
    ports:
      - "9090:9090"
    environment:
      - KINFRA_DEBUG=true
      - KINFRA_METRICS_PORT=9090
    depends_on:
      - redis
      - postgres
      - nats
    networks:
      - shared

  # API Project Services
  api-server:
    build: ./api-project
    ports:
      - "8000:8000"
    environment:
      - PROJECT=api-project
      - REDIS_URL=redis://redis:6379/0
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/shared_db
      - NATS_URL=nats://nats:4222
    depends_on:
      - redis
      - postgres
      - nats
    networks:
      - shared
      - api

  api-worker:
    build: ./api-project
    command: ["python", "worker.py"]
    environment:
      - PROJECT=api-project
      - REDIS_URL=redis://redis:6379/0
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/shared_db
      - NATS_URL=nats://nats:4222
    depends_on:
      - redis
      - postgres
      - nats
    networks:
      - shared
      - api

  # Web Project Services
  web-server:
    build: ./web-project
    ports:
      - "3000:3000"
    environment:
      - PROJECT=web-project
      - REDIS_URL=redis://redis:6379/1
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/shared_db
      - NATS_URL=nats://nats:4222
    depends_on:
      - redis
      - postgres
      - nats
    networks:
      - shared
      - web

  web-worker:
    build: ./web-project
    command: ["node", "worker.js"]
    environment:
      - PROJECT=web-project
      - REDIS_URL=redis://redis:6379/1
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/shared_db
      - NATS_URL=nats://nats:4222
    depends_on:
      - redis
      - postgres
      - nats
    networks:
      - shared
      - web

  # Worker Project Services
  worker-server:
    build: ./worker-project
    ports:
      - "4000:4000"
    environment:
      - PROJECT=worker-project
      - REDIS_URL=redis://redis:6379/2
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/shared_db
      - NATS_URL=nats://nats:4222
    depends_on:
      - redis
      - postgres
      - nats
    networks:
      - shared
      - worker

  worker-processor:
    build: ./worker-project
    command: ["python", "processor.py"]
    environment:
      - PROJECT=worker-project
      - REDIS_URL=redis://redis:6379/2
      - POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/shared_db
      - NATS_URL=nats://nats:4222
    depends_on:
      - redis
      - postgres
      - nats
    networks:
      - shared
      - worker

volumes:
  redis_data:
  postgres_data:

networks:
  shared:
    driver: bridge
  api:
    driver: bridge
  web:
    driver: bridge
  worker:
    driver: bridge
```

## CLI Usage for Shared Resources

### Global Resource Management

```bash
# Deploy global resources
kinfra resource deploy shared-redis redis --mode global --config redis.json
kinfra resource deploy shared-postgres postgres --mode global --config postgres.json
kinfra resource deploy shared-nats nats --mode global --config nats.json

# List global resources
kinfra resource list --mode global

# Show resource status
kinfra resource status shared-redis
kinfra resource status shared-postgres
kinfra resource status shared-nats
```

### Project-Specific Management

```bash
# Start projects
kinfra project start api-project --services api-server,api-worker
kinfra project start web-project --services web-server,web-worker
kinfra project start worker-project --services worker-server,worker-processor

# Create tunnels for all projects
kinfra tunnel create api-project api-server 8000 --provider cloudflare --hostname api.example.com
kinfra tunnel create web-project web-server 3000 --provider cloudflare --hostname web.example.com
kinfra tunnel create worker-project worker-server 4000 --provider cloudflare --hostname worker.example.com

# Set up cleanup policies
kinfra cleanup init-project api-project --strategy aggressive
kinfra cleanup init-project web-project --strategy moderate
kinfra cleanup init-project worker-project --strategy conservative
```

### Global Status Monitoring

```bash
# Show global status
kinfra status show-global --format html
kinfra status show-global --format json

# Show project status
kinfra status show-project api-project
kinfra status show-project web-project
kinfra status show-project worker-project

# Show resource status
kinfra resource status --all
kinfra resource status --mode global
kinfra resource status --mode tenanted
```

## Configuration

### Global Configuration

Create `~/.kinfra/config/kinfra.yaml`:

```yaml
app_name: "shared-infrastructure"
debug: false
log_level: "INFO"
environment: "production"

# Global resource settings
enable_nats: true
nats_url: "nats://localhost:4222"
enable_metrics: true
metrics_port: 9090

# Global cleanup policy
global_cleanup_policy:
  default_strategy: "conservative"
  max_concurrent_cleanups: 10
  cleanup_timeout: 600.0
  enabled: true

# Project configurations
projects:
  api-project:
    project_name: "api-project"
    default_strategy: "aggressive"
    enabled: true
    rules:
      process:
        resource_type: "process"
        strategy: "aggressive"
        patterns: ["api-project-*"]
        max_age: 1800.0
        force_cleanup: true
        enabled: true
      tunnel:
        resource_type: "tunnel"
        strategy: "moderate"
        patterns: ["api-project-*"]
        max_age: 3600.0
        force_cleanup: false
        enabled: true

  web-project:
    project_name: "web-project"
    default_strategy: "moderate"
    enabled: true
    rules:
      process:
        resource_type: "process"
        strategy: "moderate"
        patterns: ["web-project-*"]
        max_age: 3600.0
        force_cleanup: false
        enabled: true
      tunnel:
        resource_type: "tunnel"
        strategy: "conservative"
        patterns: ["web-project-*"]
        max_age: 7200.0
        force_cleanup: false
        enabled: true

  worker-project:
    project_name: "worker-project"
    default_strategy: "conservative"
    enabled: true
    rules:
      process:
        resource_type: "process"
        strategy: "conservative"
        patterns: ["worker-project-*"]
        max_age: 7200.0
        force_cleanup: false
        enabled: true
      tunnel:
        resource_type: "tunnel"
        strategy: "conservative"
        patterns: ["worker-project-*"]
        max_age: 7200.0
        force_cleanup: false
        enabled: true

# Project routing
project_routing:
  api-project:
    project_name: "api-project"
    domain: "api.example.com"
    base_path: "/"
    enable_health_checks: true
    health_check_interval: 5.0
    health_check_timeout: 2.0
    fallback_enabled: true
    maintenance_enabled: false

  web-project:
    project_name: "web-project"
    domain: "web.example.com"
    base_path: "/"
    enable_health_checks: true
    health_check_interval: 5.0
    health_check_timeout: 2.0
    fallback_enabled: true
    maintenance_enabled: false

  worker-project:
    project_name: "worker-project"
    domain: "worker.example.com"
    base_path: "/"
    enable_health_checks: true
    health_check_interval: 5.0
    health_check_timeout: 2.0
    fallback_enabled: true
    maintenance_enabled: false
```

## Complete Example

Here's a complete example that demonstrates shared resource management:

```python
#!/usr/bin/env python3
"""
Complete KInfra shared resource example with all Phase 5 features.
"""

import asyncio
import time
from pathlib import Path

from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.global_registry import GlobalResourceRegistry
from pheno.infra.project_context import project_infra_context
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
from pheno.infra.tunnel_governance import TunnelGovernanceManager
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.config_schemas import KInfraConfigManager


async def main():
    """Main shared resource example function."""
    print("🚀 Starting KInfra shared resource example...")
    
    # Initialize configuration
    config_manager = KInfraConfigManager()
    config = config_manager.load()
    print(f"✅ Configuration loaded: {config.app_name}")
    
    # Initialize managers
    deployment_manager = DeploymentManager()
    resource_coordinator = ResourceCoordinator(deployment_manager)
    global_registry = GlobalResourceRegistry()
    process_manager = ProcessGovernanceManager()
    tunnel_manager = TunnelGovernanceManager()
    cleanup_manager = CleanupPolicyManager()
    status_manager = StatusPageManager()
    
    # Initialize resource coordination
    await resource_coordinator.initialize()
    print("✅ Resource coordination initialized")
    
    # Deploy shared resources
    print("🏗️ Deploying shared resources...")
    
    redis_resource = await deployment_manager.deploy_resource(
        name="shared-redis",
        resource_type="redis",
        mode="global",
        config={
            "host": "localhost",
            "port": 6379,
            "db": 0
        }
    )
    
    postgres_resource = await deployment_manager.deploy_resource(
        name="shared-postgres",
        resource_type="postgres",
        mode="global",
        config={
            "host": "localhost",
            "port": 5432,
            "database": "shared_db"
        }
    )
    
    nats_resource = await deployment_manager.deploy_resource(
        name="shared-nats",
        resource_type="nats",
        mode="global",
        config={
            "url": "nats://localhost:4222"
        }
    )
    
    print("✅ Shared resources deployed")
    
    # Register global resources
    await global_registry.register_resource(
        name="shared-redis",
        resource_type="redis",
        config={"host": "localhost", "port": 6379, "db": 0},
        metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]}
    )
    
    await global_registry.register_resource(
        name="shared-postgres",
        resource_type="postgres",
        config={"host": "localhost", "port": 5432, "database": "shared_db"},
        metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]}
    )
    
    await global_registry.register_resource(
        name="shared-nats",
        resource_type="nats",
        config={"url": "nats://localhost:4222"},
        metadata={"shared": True, "projects": ["api-project", "web-project", "worker-project"]}
    )
    
    print("✅ Global resources registered")
    
    # Set up projects
    projects = ["api-project", "web-project", "worker-project"]
    
    for project in projects:
        print(f"🏗️ Setting up {project}...")
        
        # Set up cleanup policies
        strategy = CleanupStrategy.AGGRESSIVE if "api" in project else CleanupStrategy.MODERATE if "web" in project else CleanupStrategy.CONSERVATIVE
        policy = cleanup_manager.create_default_policy(
            project_name=project,
            strategy=strategy
        )
        
        # Use project context
        with project_infra_context(project) as infra:
            # Start services
            if "api" in project:
                api_port = infra.start_service("api-server", port=8000)
                worker_port = infra.start_service("api-worker", port=8001)
                
                # Register processes
                api_metadata = ProcessMetadata(
                    project=project,
                    service="api-server",
                    pid=1000 + hash(project) % 1000,
                    command_line=["python", "api_server.py"],
                    environment={"PROJECT": project, "REDIS_URL": "redis://localhost:6379/0"},
                    scope="local",
                    resource_type="api",
                    tags={"web", "rest", "api"}
                )
                process_manager.register_process(api_metadata.pid, api_metadata)
                
                # Create tunnels
                tunnel = tunnel_manager.create_tunnel(
                    project=project,
                    service="api-server",
                    port=api_port,
                    provider="cloudflare",
                    hostname=f"api-{project}.example.com"
                )
                
            elif "web" in project:
                web_port = infra.start_service("web-server", port=3000)
                worker_port = infra.start_service("web-worker", port=3001)
                
                # Register processes
                web_metadata = ProcessMetadata(
                    project=project,
                    service="web-server",
                    pid=2000 + hash(project) % 1000,
                    command_line=["node", "web_server.js"],
                    environment={"PROJECT": project, "REDIS_URL": "redis://localhost:6379/1"},
                    scope="local",
                    resource_type="web",
                    tags={"web", "frontend", "ui"}
                )
                process_manager.register_process(web_metadata.pid, web_metadata)
                
                # Create tunnels
                tunnel = tunnel_manager.create_tunnel(
                    project=project,
                    service="web-server",
                    port=web_port,
                    provider="cloudflare",
                    hostname=f"web-{project}.example.com"
                )
                
            elif "worker" in project:
                worker_port = infra.start_service("worker-server", port=4000)
                processor_port = infra.start_service("worker-processor", port=4001)
                
                # Register processes
                worker_metadata = ProcessMetadata(
                    project=project,
                    service="worker-server",
                    pid=3000 + hash(project) % 1000,
                    command_line=["python", "worker_server.py"],
                    environment={"PROJECT": project, "REDIS_URL": "redis://localhost:6379/2"},
                    scope="local",
                    resource_type="worker",
                    tags={"worker", "background", "queue"}
                )
                process_manager.register_process(worker_metadata.pid, worker_metadata)
                
                # Create tunnels
                tunnel = tunnel_manager.create_tunnel(
                    project=project,
                    service="worker-server",
                    port=worker_port,
                    provider="cloudflare",
                    hostname=f"worker-{project}.example.com"
                )
            
            print(f"✅ {project} setup complete: {tunnel.public_url}")
    
    # Update status for all projects
    print("📊 Updating status...")
    for project in projects:
        status_manager.update_service_status(
            project_name=project,
            service_name=f"{project.split('-')[0]}-server",
            status="running",
            port=8000 if "api" in project else 3000 if "web" in project else 4000,
            health_status="healthy"
        )
    
    # Generate global status dashboard
    global_status = status_manager.generate_status_page("global", "dashboard")
    print("📊 Global status dashboard generated")
    
    # Show statistics
    print("📈 Showing statistics...")
    process_stats = process_manager.get_cleanup_stats()
    tunnel_stats = tunnel_manager.get_tunnel_stats()
    print(f"Process stats: {process_stats}")
    print(f"Tunnel stats: {tunnel_stats}")
    
    # Simulate some work
    print("⏳ Simulating work...")
    await asyncio.sleep(10)
    
    print("✅ Shared resource example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
```

## Next Steps

1. **Read the CLI Reference**: See the [CLI Reference Guide](cli_reference.md)
2. **Learn about Integration Testing**: See the [Integration Testing Guide](integration_testing.md)
3. **Customize Configuration**: See the [Configuration Guide](configuration.md)
4. **Explore Advanced Features**: See the [Advanced Features Guide](advanced_features.md)

## Troubleshooting

### Common Issues

1. **Resource conflicts**: Ensure unique resource names and ports
2. **Network connectivity**: Check Docker networks and port mappings
3. **Cleanup policies**: Verify project-specific policies are configured correctly
4. **Status monitoring**: Ensure status callbacks are registered for all services

### Getting Help

- Check the [CLI Reference](cli_reference.md) for command details
- See the [Configuration Guide](configuration.md) for advanced configuration
- Review the [Integration Testing Guide](integration_testing.md) for testing patterns

## Conclusion

This shared resource setup guide has shown you how to:

- Deploy and manage shared resources across multiple projects
- Set up project-specific cleanup policies and governance
- Coordinate resource usage and cleanup
- Monitor status across all projects and services
- Use Docker Compose for complex multi-service architectures

You now have a sophisticated shared infrastructure setup that can scale to handle complex multi-service applications!