# Router Project KInfra Adoption Guide

## Overview

This guide provides step-by-step instructions for adopting KInfra Phase 5 features in the Router project. The Router project is a complex routing system with multiple services that will benefit significantly from shared infrastructure management.

## Current Architecture

### Services
- **API Server**: Main REST API for routing requests
- **Worker Processes**: Background processing for routing tasks
- **Routing Engine**: Core routing logic and decision making

### Dependencies
- **Redis**: Caching and session storage
- **PostgreSQL**: Persistent data storage
- **NATS**: Message queuing and service communication

### Current Infrastructure
- Custom port management
- Basic process control
- Manual resource allocation
- Limited monitoring and observability

## Migration Benefits

### Phase 1: Enable Metadata
- **Benefit**: Better process tracking and debugging
- **Impact**: Low - additive changes only
- **Timeline**: 3 days

### Phase 2: Adopt ProjectInfraContext
- **Benefit**: Project-scoped resource management
- **Impact**: Medium - requires code changes
- **Timeline**: 4 days

### Phase 3: Resource Helpers
- **Benefit**: Shared resource coordination and reuse
- **Impact**: Medium - infrastructure changes
- **Timeline**: 4 days

### Phase 4: Advanced Features
- **Benefit**: Process governance, tunnel management, cleanup policies
- **Impact**: Low - optional features
- **Timeline**: 3 days

## Step-by-Step Migration

### Phase 1: Enable Metadata (Week 1)

#### 1.1 Update Port Allocation
```python
# Before (router/api/server.py)
from pheno.infra.port_allocator import SmartPortAllocator
port_allocator = SmartPortAllocator()
port = port_allocator.allocate_port("router-api", 8000)

# After
from pheno.infra.port_allocator import SmartPortAllocator
port_allocator = SmartPortAllocator()
port = port_allocator.allocate_port(
    "router-api", 
    8000,
    metadata={
        "project": "router",
        "service": "api",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "1.0.0",
        "component": "web-server"
    }
)
```

#### 1.2 Update Process Registration
```python
# Before (router/worker/process_manager.py)
from pheno.infra.service_infra.base import ServiceInfraManager
service_manager = ServiceInfraManager()
service_manager.register_process(pid, command_line)

# After
from pheno.infra.service_infra.base import ServiceInfraManager
from pheno.infra.process_governance import ProcessMetadata

service_manager = ServiceInfraManager()
metadata = ProcessMetadata(
    project="router",
    service="worker",
    pid=pid,
    command_line=command_line,
    environment=dict(os.environ),
    scope="local",
    resource_type="worker",
    tags={"background", "processing", "routing"}
)
service_manager.register_process(pid, command_line, metadata=metadata)
```

#### 1.3 Update Configuration
```yaml
# router/kinfra_config.yaml
app_name: "router"
debug: false
log_level: "INFO"
environment: "production"

# Enable metadata tracking
enable_metadata_tracking: true
metadata_fields:
  - project
  - service
  - environment
  - version
  - component

# Project-specific settings
project_name: "router"
project_services:
  - api
  - worker
  - routing-engine
```

### Phase 2: Adopt ProjectInfraContext (Week 2)

#### 2.1 Update Main Application
```python
# Before (router/main.py)
from pheno.infra.service_infra.base import ServiceInfraManager
import asyncio

async def main():
    service_manager = ServiceInfraManager()
    await service_manager.start_all()
    # ... rest of application

# After
from pheno.infra.project_context import project_infra_context
from pheno.infra.service_infra.base import ServiceInfraManager
import asyncio

async def main():
    async with project_infra_context("router") as infra:
        service_manager = ServiceInfraManager()
        await service_manager.start_all()
        # ... rest of application
        # All services now have router project context
```

#### 2.2 Update Service Initialization
```python
# Before (router/api/server.py)
from pheno.infra.service_infra.base import ServiceInfraManager

class APIServer:
    def __init__(self):
        self.service_manager = ServiceInfraManager()
    
    async def start(self):
        await self.service_manager.start_all()

# After
from pheno.infra.project_context import project_infra_context
from pheno.infra.service_infra.base import ServiceInfraManager

class APIServer:
    def __init__(self):
        self.service_manager = ServiceInfraManager()
    
    async def start(self):
        async with project_infra_context("router") as infra:
            await self.service_manager.start_all()
            # All services now have router project context
```

#### 2.3 Update Configuration
```yaml
# router/kinfra_config.yaml
# ... existing config ...

# Project context settings
project_name: "router"
enable_project_isolation: true
project_services:
  - api
  - worker
  - routing-engine

# Project-specific resource settings
project_resources:
  redis:
    type: "redis"
    config:
      host: "localhost"
      port: 6379
      db: 0
  postgres:
    type: "postgres"
    config:
      host: "localhost"
      port: 5432
      database: "router"
  nats:
    type: "nats"
    config:
      url: "nats://localhost:4222"
```

### Phase 3: Resource Helpers (Week 3)

#### 3.1 Update Resource Management
```python
# Before (router/infrastructure/resource_manager.py)
from pheno.infra.deployment_manager import DeploymentManager

class ResourceManager:
    def __init__(self):
        self.deployment_manager = DeploymentManager()
    
    async def setup_redis(self):
        return await self.deployment_manager.deploy_resource(
            "router-redis", "redis", "local", 
            {"host": "localhost", "port": 6379, "db": 0}
        )
    
    async def setup_postgres(self):
        return await self.deployment_manager.deploy_resource(
            "router-postgres", "postgres", "local",
            {"host": "localhost", "port": 5432, "database": "router"}
        )

# After
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.deployment_manager import DeploymentManager

class ResourceManager:
    def __init__(self):
        self.deployment_manager = DeploymentManager()
        self.resource_coordinator = ResourceCoordinator(self.deployment_manager)
    
    async def initialize(self):
        await self.resource_coordinator.initialize()
    
    async def setup_redis(self):
        # Try to use shared Redis first, fall back to project-specific
        return await self.resource_coordinator.get_or_deploy_resource(
            "shared-redis", "redis", "global",
            {"host": "localhost", "port": 6379, "db": 0}
        )
    
    async def setup_postgres(self):
        # Try to use shared PostgreSQL first, fall back to project-specific
        return await self.resource_coordinator.get_or_deploy_resource(
            "shared-postgres", "postgres", "global",
            {"host": "localhost", "port": 5432, "database": "shared"}
        )
```

#### 3.2 Update Service Dependencies
```python
# Before (router/api/dependencies.py)
from pheno.infra.deployment_manager import DeploymentManager

async def get_redis():
    deployment_manager = DeploymentManager()
    return await deployment_manager.get_resource("router-redis")

async def get_postgres():
    deployment_manager = DeploymentManager()
    return await deployment_manager.get_resource("router-postgres")

# After
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.deployment_manager import DeploymentManager

resource_coordinator = ResourceCoordinator(DeploymentManager())
await resource_coordinator.initialize()

async def get_redis():
    return await resource_coordinator.get_resource("shared-redis")

async def get_postgres():
    return await resource_coordinator.get_resource("shared-postgres")
```

#### 3.3 Update Configuration
```yaml
# router/kinfra_config.yaml
# ... existing config ...

# Resource coordination settings
enable_resource_sharing: true
resource_coordination: true
shared_resources:
  - redis
  - postgres
  - nats

# Global resource settings
global_resources:
  redis:
    type: "redis"
    config:
      host: "localhost"
      port: 6379
      db: 0
    shared: true
  postgres:
    type: "postgres"
    config:
      host: "localhost"
      port: 5432
      database: "shared"
    shared: true
  nats:
    type: "nats"
    config:
      url: "nats://localhost:4222"
    shared: true
```

### Phase 4: Advanced Features (Week 4)

#### 4.1 Add Process Governance
```python
# router/governance/process_governance.py
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
import os
import sys

class RouterProcessGovernance:
    def __init__(self):
        self.process_manager = ProcessGovernanceManager()
    
    def register_api_server(self, pid: int):
        metadata = ProcessMetadata(
            project="router",
            service="api",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="api",
            tags={"web", "rest", "api", "router"}
        )
        self.process_manager.register_process(pid, metadata)
    
    def register_worker(self, pid: int, worker_type: str):
        metadata = ProcessMetadata(
            project="router",
            service=f"worker-{worker_type}",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="worker",
            tags={"background", "processing", "routing", worker_type}
        )
        self.process_manager.register_process(pid, metadata)
    
    def register_routing_engine(self, pid: int):
        metadata = ProcessMetadata(
            project="router",
            service="routing-engine",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="engine",
            tags={"routing", "engine", "core", "router"}
        )
        self.process_manager.register_process(pid, metadata)
    
    def cleanup_project_processes(self):
        return self.process_manager.cleanup_project_processes("router")
```

#### 4.2 Add Tunnel Governance
```python
# router/governance/tunnel_governance.py
from pheno.infra.tunnel_governance import TunnelGovernanceManager

class RouterTunnelGovernance:
    def __init__(self):
        self.tunnel_manager = TunnelGovernanceManager()
    
    def create_api_tunnel(self, port: int):
        return self.tunnel_manager.create_tunnel(
            project="router",
            service="api",
            port=port,
            provider="cloudflare",
            reuse_existing=True
        )
    
    def create_worker_tunnel(self, port: int, worker_type: str):
        return self.tunnel_manager.create_tunnel(
            project="router",
            service=f"worker-{worker_type}",
            port=port,
            provider="cloudflare",
            reuse_existing=True
        )
    
    def cleanup_project_tunnels(self):
        return self.tunnel_manager.cleanup_project_tunnels("router")
```

#### 4.3 Add Cleanup Policies
```python
# router/governance/cleanup_policies.py
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType

class RouterCleanupPolicies:
    def __init__(self):
        self.cleanup_manager = CleanupPolicyManager()
        self.setup_policies()
    
    def setup_policies(self):
        # Create project-specific cleanup policy
        policy = self.cleanup_manager.create_default_policy(
            project_name="router",
            strategy=CleanupStrategy.MODERATE
        )
        
        # Set up process cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="router",
            resource_type=ResourceType.PROCESS,
            strategy=CleanupStrategy.AGGRESSIVE,
            patterns=["router-*", "api-*", "worker-*"],
            max_age=1800.0,  # 30 minutes
            force_cleanup=True
        )
        
        # Set up tunnel cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="router",
            resource_type=ResourceType.TUNNEL,
            strategy=CleanupStrategy.CONSERVATIVE,
            patterns=["router-*"],
            max_age=3600.0,  # 1 hour
            force_cleanup=False
        )
        
        # Set up port cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="router",
            resource_type=ResourceType.PORT,
            strategy=CleanupStrategy.AGGRESSIVE,
            patterns=["router-*"],
            max_age=900.0,  # 15 minutes
            force_cleanup=True
        )
        
        self.cleanup_manager.set_project_policy("router", policy)
```

#### 4.4 Add Status Monitoring
```python
# router/monitoring/status_monitoring.py
from pheno.infra.fallback_site.status_pages import StatusPageManager

class RouterStatusMonitoring:
    def __init__(self):
        self.status_manager = StatusPageManager()
    
    def update_api_status(self, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="router",
            service_name="api",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_worker_status(self, worker_type: str, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="router",
            service_name=f"worker-{worker_type}",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_routing_engine_status(self, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="router",
            service_name="routing-engine",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_tunnel_status(self, service: str, status: str, hostname: str):
        self.status_manager.update_tunnel_status(
            project_name="router",
            service_name=service,
            status=status,
            hostname=hostname,
            provider="cloudflare"
        )
    
    def generate_status_page(self):
        return self.status_manager.generate_status_page("router", "status")
    
    def generate_project_summary(self):
        return self.status_manager.generate_project_summary("router")
```

#### 4.5 Update Configuration
```yaml
# router/kinfra_config.yaml
# ... existing config ...

# Advanced features
enable_process_governance: true
enable_tunnel_governance: true
enable_cleanup_policies: true
enable_status_monitoring: true

# Process governance settings
process_governance:
  enable_metadata_tracking: true
  max_process_age: 1800.0
  cleanup_interval: 300.0
  force_cleanup: false

# Tunnel governance settings
tunnel_governance:
  default_lifecycle_policy: "smart"
  tunnel_reuse_threshold: 1800.0
  max_tunnel_age: 3600.0
  credential_scope: "project"

# Cleanup policy settings
cleanup_policies:
  project_name: "router"
  default_strategy: "moderate"
  enabled: true
  rules:
    process:
      resource_type: "process"
      strategy: "aggressive"
      patterns: ["router-*", "api-*", "worker-*"]
      max_age: 1800.0
      force_cleanup: true
      enabled: true
    tunnel:
      resource_type: "tunnel"
      strategy: "conservative"
      patterns: ["router-*"]
      max_age: 3600.0
      force_cleanup: false
      enabled: true
    port:
      resource_type: "port"
      strategy: "aggressive"
      patterns: ["router-*"]
      max_age: 900.0
      force_cleanup: true
      enabled: true

# Status monitoring settings
status_monitoring:
  auto_refresh_interval: 5
  include_service_details: true
  include_tunnel_details: true
  include_health_metrics: true
  theme: "default"
```

## Testing Strategy

### Unit Tests
```python
# router/tests/test_kinfra_integration.py
import pytest
from router.governance.process_governance import RouterProcessGovernance
from router.governance.tunnel_governance import RouterTunnelGovernance
from router.governance.cleanup_policies import RouterCleanupPolicies
from router.monitoring.status_monitoring import RouterStatusMonitoring

class TestRouterKInfraIntegration:
    def test_process_governance(self):
        governance = RouterProcessGovernance()
        governance.register_api_server(12345)
        
        processes = governance.process_manager.get_project_processes("router")
        assert len(processes) == 1
        assert processes[0].service == "api"
    
    def test_tunnel_governance(self):
        governance = RouterTunnelGovernance()
        tunnel = governance.create_api_tunnel(8000)
        
        assert tunnel.project == "router"
        assert tunnel.service == "api"
        assert tunnel.port == 8000
    
    def test_cleanup_policies(self):
        policies = RouterCleanupPolicies()
        policy = policies.cleanup_manager.get_project_policy("router")
        
        assert policy.project_name == "router"
        assert policy.default_strategy == CleanupStrategy.MODERATE
    
    def test_status_monitoring(self):
        monitoring = RouterStatusMonitoring()
        monitoring.update_api_status("running", "healthy", 8000)
        
        project_status = monitoring.status_manager.get_project_status("router")
        assert "api" in project_status.services
        assert project_status.services["api"].status == "running"
```

### Integration Tests
```python
# router/tests/test_kinfra_integration_full.py
import pytest
import asyncio
from pheno.infra.project_context import project_infra_context

class TestRouterKInfraIntegrationFull:
    @pytest.mark.asyncio
    async def test_full_integration(self):
        async with project_infra_context("router") as infra:
            # Test complete integration
            governance = RouterProcessGovernance()
            tunnel_governance = RouterTunnelGovernance()
            cleanup_policies = RouterCleanupPolicies()
            status_monitoring = RouterStatusMonitoring()
            
            # Register processes
            governance.register_api_server(12345)
            governance.register_worker(12346, "routing")
            governance.register_routing_engine(12347)
            
            # Create tunnels
            api_tunnel = tunnel_governance.create_api_tunnel(8000)
            worker_tunnel = tunnel_governance.create_worker_tunnel(8001, "routing")
            
            # Update status
            status_monitoring.update_api_status("running", "healthy", 8000)
            status_monitoring.update_worker_status("routing", "running", "healthy", 8001)
            status_monitoring.update_routing_engine_status("running", "healthy", 8002)
            
            # Verify everything is working
            processes = governance.process_manager.get_project_processes("router")
            assert len(processes) == 3
            
            tunnels = tunnel_governance.tunnel_manager.get_project_tunnels("router")
            assert len(tunnels) == 2
            
            project_status = status_monitoring.status_manager.get_project_status("router")
            assert len(project_status.services) == 3
            assert len(project_status.tunnels) == 2
```

## Deployment

### Docker Integration
```dockerfile
# router/Dockerfile.kinfra
FROM python:3.11-slim

# Install KInfra
COPY pheno-sdk /app/pheno-sdk
WORKDIR /app/pheno-sdk
RUN pip install -e .

# Copy router application
COPY . /app/router
WORKDIR /app/router

# Install router dependencies
RUN pip install -r requirements.txt

# Set up KInfra configuration
COPY kinfra_config.yaml /app/router/

# Start with KInfra
CMD ["python", "-m", "pheno.infra.main", "--project", "router"]
```

### Docker Compose Integration
```yaml
# router/docker-compose.kinfra.yml
version: '3.8'

services:
  router-api:
    build:
      context: .
      dockerfile: Dockerfile.kinfra
    ports:
      - "8000:8000"
    environment:
      - PROJECT_NAME=router
      - SERVICE_NAME=api
      - KINFRA_CONFIG_PATH=/app/router/kinfra_config.yaml
    depends_on:
      - redis
      - postgres
      - nats
  
  router-worker:
    build:
      context: .
      dockerfile: Dockerfile.kinfra
    environment:
      - PROJECT_NAME=router
      - SERVICE_NAME=worker
      - KINFRA_CONFIG_PATH=/app/router/kinfra_config.yaml
    depends_on:
      - redis
      - postgres
      - nats
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=shared
      - POSTGRES_USER=router
      - POSTGRES_PASSWORD=router
    ports:
      - "5432:5432"
  
  nats:
    image: nats:2.9-alpine
    ports:
      - "4222:4222"
```

## Monitoring and Observability

### Health Checks
```python
# router/health/kinfra_health.py
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager

class RouterHealthChecker:
    def __init__(self):
        self.status_manager = StatusPageManager()
        self.process_manager = ProcessGovernanceManager()
        self.tunnel_manager = TunnelGovernanceManager()
    
    def check_health(self):
        health_status = {
            "overall": "healthy",
            "services": {},
            "tunnels": {},
            "processes": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # Check service health
        project_status = self.status_manager.get_project_status("router")
        for service_name, service_status in project_status.services.items():
            health_status["services"][service_name] = {
                "status": service_status.status,
                "health": service_status.health_status,
                "port": service_status.port
            }
        
        # Check tunnel health
        for tunnel_name, tunnel_status in project_status.tunnels.items():
            health_status["tunnels"][tunnel_name] = {
                "status": tunnel_status.status,
                "hostname": tunnel_status.hostname,
                "provider": tunnel_status.provider
            }
        
        # Check process health
        processes = self.process_manager.get_project_processes("router")
        for process in processes:
            health_status["processes"][process.service] = {
                "pid": process.pid,
                "status": "running" if self._is_process_running(process.pid) else "stopped",
                "age": time.time() - process.created_at
            }
        
        return health_status
    
    def _is_process_running(self, pid: int) -> bool:
        try:
            import psutil
            return psutil.pid_exists(pid)
        except ImportError:
            return True  # Assume running if psutil not available
```

### Metrics Collection
```python
# router/metrics/kinfra_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

class RouterKInfraMetrics:
    def __init__(self):
        self.request_count = Counter('router_requests_total', 'Total requests', ['service', 'method'])
        self.request_duration = Histogram('router_request_duration_seconds', 'Request duration', ['service'])
        self.active_processes = Gauge('router_active_processes', 'Active processes', ['service'])
        self.active_tunnels = Gauge('router_active_tunnels', 'Active tunnels', ['service'])
        self.resource_usage = Gauge('router_resource_usage', 'Resource usage', ['resource_type', 'service'])
    
    def record_request(self, service: str, method: str, duration: float):
        self.request_count.labels(service=service, method=method).inc()
        self.request_duration.labels(service=service).observe(duration)
    
    def update_process_metrics(self, service: str, count: int):
        self.active_processes.labels(service=service).set(count)
    
    def update_tunnel_metrics(self, service: str, count: int):
        self.active_tunnels.labels(service=service).set(count)
    
    def update_resource_metrics(self, resource_type: str, service: str, usage: float):
        self.resource_usage.labels(resource_type=resource_type, service=service).set(usage)
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts
```bash
# Check for port conflicts
kinfra port list --project router

# Resolve conflicts
kinfra port cleanup --project router --force
```

#### 2. Process Cleanup Issues
```bash
# Check process status
kinfra process list --project router

# Clean up stale processes
kinfra process cleanup-stale --project router
```

#### 3. Tunnel Connection Issues
```bash
# Check tunnel status
kinfra tunnel list --project router

# Test tunnel connectivity
kinfra tunnel test --project router --service api
```

#### 4. Resource Coordination Issues
```bash
# Check resource status
kinfra resource list --project router

# Test resource connectivity
kinfra resource test --project router --resource redis
```

### Debugging

#### Enable Debug Logging
```yaml
# router/kinfra_config.yaml
debug: true
log_level: "DEBUG"
```

#### Check KInfra Status
```bash
# Check overall status
kinfra status show-global

# Check project status
kinfra status show-project router

# Check health
kinfra health --project router
```

#### View Logs
```bash
# View KInfra logs
kinfra logs --project router

# View specific service logs
kinfra logs --project router --service api
```

## Best Practices

### 1. Resource Management
- Use shared resources when possible
- Implement proper resource cleanup
- Monitor resource usage and performance

### 2. Process Management
- Register all processes with metadata
- Implement proper process cleanup
- Monitor process health and performance

### 3. Tunnel Management
- Reuse tunnels when possible
- Implement proper tunnel cleanup
- Monitor tunnel connectivity and performance

### 4. Monitoring and Observability
- Implement comprehensive health checks
- Collect and expose metrics
- Set up alerting for critical issues

### 5. Configuration Management
- Use environment-specific configurations
- Implement configuration validation
- Document all configuration options

## Conclusion

This guide provides a comprehensive approach to adopting KInfra Phase 5 features in the Router project. The migration is designed to be gradual, safe, and backward-compatible, allowing the team to adopt new features incrementally while maintaining existing functionality.

The migration will result in:
- Better resource coordination and sharing
- Improved process and tunnel management
- Enhanced monitoring and observability
- Simplified infrastructure management
- Better developer experience

**Ready to begin Router migration!** 🚀