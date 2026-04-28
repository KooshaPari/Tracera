# Zen Project KInfra Adoption Guide

## Overview

This guide provides step-by-step instructions for adopting KInfra Phase 5 features in the Zen project. The Zen project is a complex multi-service architecture that already has good infrastructure but will benefit from enhanced coordination and governance.

## Current Architecture

### Services
- **API Gateway**: Main entry point for all requests
- **Microservices**: Various backend services
- **Database Services**: Database management and operations

### Dependencies
- **PostgreSQL**: Primary database
- **Redis**: Caching and session storage
- **External Services**: Various external integrations

### Current Infrastructure
- Docker-based deployment
- Service orchestration
- Good monitoring and observability
- Manual resource management

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
# Before (zen-mcp-server/api/gateway.py)
from pheno.infra.port_allocator import SmartPortAllocator
port_allocator = SmartPortAllocator()
port = port_allocator.allocate_port("zen-api", 8002)

# After
from pheno.infra.port_allocator import SmartPortAllocator
port_allocator = SmartPortAllocator()
port = port_allocator.allocate_port(
    "zen-api", 
    8002,
    metadata={
        "project": "zen",
        "service": "api-gateway",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "6.1.0",
        "component": "api-gateway"
    }
)
```

#### 1.2 Update Process Registration
```python
# Before (zen-mcp-server/main.py)
from pheno.infra.service_infra.base import ServiceInfraManager
service_manager = ServiceInfraManager()
service_manager.register_process(pid, command_line)

# After
from pheno.infra.service_infra.base import ServiceInfraManager
from pheno.infra.process_governance import ProcessMetadata

service_manager = ServiceInfraManager()
metadata = ProcessMetadata(
    project="zen",
    service="api-gateway",
    pid=pid,
    command_line=command_line,
    environment=dict(os.environ),
    scope="local",
    resource_type="api-gateway",
    tags={"web", "rest", "api", "gateway", "zen"}
)
service_manager.register_process(pid, command_line, metadata=metadata)
```

#### 1.3 Update Configuration
```yaml
# zen-mcp-server/kinfra_config.yaml
app_name: "zen"
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
project_name: "zen"
project_services:
  - api-gateway
  - microservices
  - db-services
```

### Phase 2: Adopt ProjectInfraContext (Week 2)

#### 2.1 Update Main Application
```python
# Before (zen-mcp-server/main.py)
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
    async with project_infra_context("zen") as infra:
        service_manager = ServiceInfraManager()
        await service_manager.start_all()
        # ... rest of application
        # All services now have zen project context
```

#### 2.2 Update API Gateway Initialization
```python
# Before (zen-mcp-server/api/gateway.py)
from pheno.infra.service_infra.base import ServiceInfraManager

class APIGateway:
    def __init__(self):
        self.service_manager = ServiceInfraManager()
    
    async def start(self):
        await self.service_manager.start_all()

# After
from pheno.infra.project_context import project_infra_context
from pheno.infra.service_infra.base import ServiceInfraManager

class APIGateway:
    def __init__(self):
        self.service_manager = ServiceInfraManager()
    
    async def start(self):
        async with project_infra_context("zen") as infra:
            await self.service_manager.start_all()
            # All services now have zen project context
```

#### 2.3 Update Configuration
```yaml
# zen-mcp-server/kinfra_config.yaml
# ... existing config ...

# Project context settings
project_name: "zen"
enable_project_isolation: true
project_services:
  - api-gateway
  - microservices
  - db-services

# Project-specific resource settings
project_resources:
  postgres:
    type: "postgres"
    config:
      host: "localhost"
      port: 5432
      database: "zen"
  redis:
    type: "redis"
    config:
      host: "localhost"
      port: 6379
      db: 2
```

### Phase 3: Resource Helpers (Week 3)

#### 3.1 Update Resource Management
```python
# Before (zen-mcp-server/infrastructure/resource_manager.py)
from pheno.infra.deployment_manager import DeploymentManager

class ResourceManager:
    def __init__(self):
        self.deployment_manager = DeploymentManager()
    
    async def setup_postgres(self):
        return await self.deployment_manager.deploy_resource(
            "zen-postgres", "postgres", "local", 
            {"host": "localhost", "port": 5432, "database": "zen"}
        )
    
    async def setup_redis(self):
        return await self.deployment_manager.deploy_resource(
            "zen-redis", "redis", "local",
            {"host": "localhost", "port": 6379, "db": 2}
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
    
    async def setup_postgres(self):
        # Try to use shared PostgreSQL first, fall back to project-specific
        return await self.resource_coordinator.get_or_deploy_resource(
            "shared-postgres", "postgres", "global",
            {"host": "localhost", "port": 5432, "database": "shared"}
        )
    
    async def setup_redis(self):
        # Try to use shared Redis first, fall back to project-specific
        return await self.resource_coordinator.get_or_deploy_resource(
            "shared-redis", "redis", "global",
            {"host": "localhost", "port": 6379, "db": 2}
        )
```

#### 3.2 Update Service Dependencies
```python
# Before (zen-mcp-server/dependencies.py)
from pheno.infra.deployment_manager import DeploymentManager

async def get_postgres():
    deployment_manager = DeploymentManager()
    return await deployment_manager.get_resource("zen-postgres")

async def get_redis():
    deployment_manager = DeploymentManager()
    return await deployment_manager.get_resource("zen-redis")

# After
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.deployment_manager import DeploymentManager

resource_coordinator = ResourceCoordinator(DeploymentManager())
await resource_coordinator.initialize()

async def get_postgres():
    return await resource_coordinator.get_resource("shared-postgres")

async def get_redis():
    return await resource_coordinator.get_resource("shared-redis")
```

#### 3.3 Update Configuration
```yaml
# zen-mcp-server/kinfra_config.yaml
# ... existing config ...

# Resource coordination settings
enable_resource_sharing: true
resource_coordination: true
shared_resources:
  - postgres
  - redis

# Global resource settings
global_resources:
  postgres:
    type: "postgres"
    config:
      host: "localhost"
      port: 5432
      database: "shared"
    shared: true
  redis:
    type: "redis"
    config:
      host: "localhost"
      port: 6379
      db: 2
    shared: true
```

### Phase 4: Advanced Features (Week 4)

#### 4.1 Add Process Governance
```python
# zen-mcp-server/governance/process_governance.py
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
import os
import sys

class ZenProcessGovernance:
    def __init__(self):
        self.process_manager = ProcessGovernanceManager()
    
    def register_api_gateway(self, pid: int):
        metadata = ProcessMetadata(
            project="zen",
            service="api-gateway",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="api-gateway",
            tags={"web", "rest", "api", "gateway", "zen"}
        )
        self.process_manager.register_process(pid, metadata)
    
    def register_microservice(self, pid: int, service_name: str):
        metadata = ProcessMetadata(
            project="zen",
            service=f"microservice-{service_name}",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="microservice",
            tags={"microservice", "backend", "zen", service_name}
        )
        self.process_manager.register_process(pid, metadata)
    
    def register_db_service(self, pid: int):
        metadata = ProcessMetadata(
            project="zen",
            service="db-service",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="db-service",
            tags={"database", "service", "zen", "db"}
        )
        self.process_manager.register_process(pid, metadata)
    
    def cleanup_project_processes(self):
        return self.process_manager.cleanup_project_processes("zen")
```

#### 4.2 Add Tunnel Governance
```python
# zen-mcp-server/governance/tunnel_governance.py
from pheno.infra.tunnel_governance import TunnelGovernanceManager

class ZenTunnelGovernance:
    def __init__(self):
        self.tunnel_manager = TunnelGovernanceManager()
    
    def create_api_gateway_tunnel(self, port: int):
        return self.tunnel_manager.create_tunnel(
            project="zen",
            service="api-gateway",
            port=port,
            provider="cloudflare",
            reuse_existing=True
        )
    
    def create_microservice_tunnel(self, port: int, service_name: str):
        return self.tunnel_manager.create_tunnel(
            project="zen",
            service=f"microservice-{service_name}",
            port=port,
            provider="cloudflare",
            reuse_existing=True
        )
    
    def cleanup_project_tunnels(self):
        return self.tunnel_manager.cleanup_project_tunnels("zen")
```

#### 4.3 Add Cleanup Policies
```python
# zen-mcp-server/governance/cleanup_policies.py
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType

class ZenCleanupPolicies:
    def __init__(self):
        self.cleanup_manager = CleanupPolicyManager()
        self.setup_policies()
    
    def setup_policies(self):
        # Create project-specific cleanup policy
        policy = self.cleanup_manager.create_default_policy(
            project_name="zen",
            strategy=CleanupStrategy.CONSERVATIVE
        )
        
        # Set up process cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="zen",
            resource_type=ResourceType.PROCESS,
            strategy=CleanupStrategy.CONSERVATIVE,
            patterns=["zen-*", "api-*", "microservice-*"],
            max_age=7200.0,  # 2 hours
            force_cleanup=False
        )
        
        # Set up tunnel cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="zen",
            resource_type=ResourceType.TUNNEL,
            strategy=CleanupStrategy.CONSERVATIVE,
            patterns=["zen-*"],
            max_age=14400.0,  # 4 hours
            force_cleanup=False
        )
        
        # Set up port cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="zen",
            resource_type=ResourceType.PORT,
            strategy=CleanupStrategy.MODERATE,
            patterns=["zen-*"],
            max_age=3600.0,  # 1 hour
            force_cleanup=True
        )
        
        self.cleanup_manager.set_project_policy("zen", policy)
```

#### 4.4 Add Status Monitoring
```python
# zen-mcp-server/monitoring/status_monitoring.py
from pheno.infra.fallback_site.status_pages import StatusPageManager

class ZenStatusMonitoring:
    def __init__(self):
        self.status_manager = StatusPageManager()
    
    def update_api_gateway_status(self, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="zen",
            service_name="api-gateway",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_microservice_status(self, service_name: str, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="zen",
            service_name=f"microservice-{service_name}",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_db_service_status(self, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="zen",
            service_name="db-service",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_tunnel_status(self, service: str, status: str, hostname: str):
        self.status_manager.update_tunnel_status(
            project_name="zen",
            service_name=service,
            status=status,
            hostname=hostname,
            provider="cloudflare"
        )
    
    def generate_status_page(self):
        return self.status_manager.generate_status_page("zen", "status")
    
    def generate_project_summary(self):
        return self.status_manager.generate_project_summary("zen")
```

#### 4.5 Update Configuration
```yaml
# zen-mcp-server/kinfra_config.yaml
# ... existing config ...

# Advanced features
enable_process_governance: true
enable_tunnel_governance: true
enable_cleanup_policies: true
enable_status_monitoring: true

# Process governance settings
process_governance:
  enable_metadata_tracking: true
  max_process_age: 7200.0
  cleanup_interval: 900.0
  force_cleanup: false

# Tunnel governance settings
tunnel_governance:
  default_lifecycle_policy: "reuse"
  tunnel_reuse_threshold: 3600.0
  max_tunnel_age: 14400.0
  credential_scope: "project"

# Cleanup policy settings
cleanup_policies:
  project_name: "zen"
  default_strategy: "conservative"
  enabled: true
  rules:
    process:
      resource_type: "process"
      strategy: "conservative"
      patterns: ["zen-*", "api-*", "microservice-*"]
      max_age: 7200.0
      force_cleanup: false
      enabled: true
    tunnel:
      resource_type: "tunnel"
      strategy: "conservative"
      patterns: ["zen-*"]
      max_age: 14400.0
      force_cleanup: false
      enabled: true
    port:
      resource_type: "port"
      strategy: "moderate"
      patterns: ["zen-*"]
      max_age: 3600.0
      force_cleanup: true
      enabled: true

# Status monitoring settings
status_monitoring:
  auto_refresh_interval: 15
  include_service_details: true
  include_tunnel_details: true
  include_health_metrics: true
  theme: "default"
```

## Testing Strategy

### Unit Tests
```python
# zen-mcp-server/tests/test_kinfra_integration.py
import pytest
from zen.governance.process_governance import ZenProcessGovernance
from zen.governance.tunnel_governance import ZenTunnelGovernance
from zen.governance.cleanup_policies import ZenCleanupPolicies
from zen.monitoring.status_monitoring import ZenStatusMonitoring

class TestZenKInfraIntegration:
    def test_process_governance(self):
        governance = ZenProcessGovernance()
        governance.register_api_gateway(12345)
        
        processes = governance.process_manager.get_project_processes("zen")
        assert len(processes) == 1
        assert processes[0].service == "api-gateway"
    
    def test_tunnel_governance(self):
        governance = ZenTunnelGovernance()
        tunnel = governance.create_api_gateway_tunnel(8002)
        
        assert tunnel.project == "zen"
        assert tunnel.service == "api-gateway"
        assert tunnel.port == 8002
    
    def test_cleanup_policies(self):
        policies = ZenCleanupPolicies()
        policy = policies.cleanup_manager.get_project_policy("zen")
        
        assert policy.project_name == "zen"
        assert policy.default_strategy == CleanupStrategy.CONSERVATIVE
    
    def test_status_monitoring(self):
        monitoring = ZenStatusMonitoring()
        monitoring.update_api_gateway_status("running", "healthy", 8002)
        
        project_status = monitoring.status_manager.get_project_status("zen")
        assert "api-gateway" in project_status.services
        assert project_status.services["api-gateway"].status == "running"
```

### Integration Tests
```python
# zen-mcp-server/tests/test_kinfra_integration_full.py
import pytest
import asyncio
from pheno.infra.project_context import project_infra_context

class TestZenKInfraIntegrationFull:
    @pytest.mark.asyncio
    async def test_full_integration(self):
        async with project_infra_context("zen") as infra:
            # Test complete integration
            governance = ZenProcessGovernance()
            tunnel_governance = ZenTunnelGovernance()
            cleanup_policies = ZenCleanupPolicies()
            status_monitoring = ZenStatusMonitoring()
            
            # Register processes
            governance.register_api_gateway(12345)
            governance.register_microservice(12346, "user-service")
            governance.register_db_service(12347)
            
            # Create tunnels
            api_tunnel = tunnel_governance.create_api_gateway_tunnel(8002)
            microservice_tunnel = tunnel_governance.create_microservice_tunnel(8003, "user-service")
            
            # Update status
            status_monitoring.update_api_gateway_status("running", "healthy", 8002)
            status_monitoring.update_microservice_status("user-service", "running", "healthy", 8003)
            status_monitoring.update_db_service_status("running", "healthy", 8004)
            
            # Verify everything is working
            processes = governance.process_manager.get_project_processes("zen")
            assert len(processes) == 3
            
            tunnels = tunnel_governance.tunnel_manager.get_project_tunnels("zen")
            assert len(tunnels) == 2
            
            project_status = status_monitoring.status_manager.get_project_status("zen")
            assert len(project_status.services) == 3
            assert len(project_status.tunnels) == 2
```

## Deployment

### Docker Integration
```dockerfile
# zen-mcp-server/Dockerfile.kinfra
FROM python:3.11-slim

# Install KInfra
COPY pheno-sdk /app/pheno-sdk
WORKDIR /app/pheno-sdk
RUN pip install -e .

# Copy zen application
COPY . /app/zen
WORKDIR /app/zen

# Install zen dependencies
RUN pip install -r requirements.txt

# Set up KInfra configuration
COPY kinfra_config.yaml /app/zen/

# Start with KInfra
CMD ["python", "-m", "pheno.infra.main", "--project", "zen"]
```

### Docker Compose Integration
```yaml
# zen-mcp-server/docker-compose.kinfra.yml
version: '3.8'

services:
  zen-api-gateway:
    build:
      context: .
      dockerfile: Dockerfile.kinfra
    ports:
      - "8002:8002"
    environment:
      - PROJECT_NAME=zen
      - SERVICE_NAME=api-gateway
      - KINFRA_CONFIG_PATH=/app/zen/kinfra_config.yaml
    depends_on:
      - postgres
      - redis
  
  zen-microservices:
    build:
      context: .
      dockerfile: Dockerfile.kinfra
    environment:
      - PROJECT_NAME=zen
      - SERVICE_NAME=microservices
      - KINFRA_CONFIG_PATH=/app/zen/kinfra_config.yaml
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=shared
      - POSTGRES_USER=zen
      - POSTGRES_PASSWORD=zen
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Monitoring and Observability

### Health Checks
```python
# zen-mcp-server/health/kinfra_health.py
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager

class ZenHealthChecker:
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
        project_status = self.status_manager.get_project_status("zen")
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
        processes = self.process_manager.get_project_processes("zen")
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
# zen-mcp-server/metrics/kinfra_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

class ZenKInfraMetrics:
    def __init__(self):
        self.request_count = Counter('zen_requests_total', 'Total requests', ['service', 'method'])
        self.request_duration = Histogram('zen_request_duration_seconds', 'Request duration', ['service'])
        self.active_processes = Gauge('zen_active_processes', 'Active processes', ['service'])
        self.active_tunnels = Gauge('zen_active_tunnels', 'Active tunnels', ['service'])
        self.resource_usage = Gauge('zen_resource_usage', 'Resource usage', ['resource_type', 'service'])
    
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
kinfra port list --project zen

# Resolve conflicts
kinfra port cleanup --project zen --force
```

#### 2. Process Cleanup Issues
```bash
# Check process status
kinfra process list --project zen

# Clean up stale processes
kinfra process cleanup-stale --project zen
```

#### 3. Tunnel Connection Issues
```bash
# Check tunnel status
kinfra tunnel list --project zen

# Test tunnel connectivity
kinfra tunnel test --project zen --service api-gateway
```

#### 4. Resource Coordination Issues
```bash
# Check resource status
kinfra resource list --project zen

# Test resource connectivity
kinfra resource test --project zen --resource postgres
```

### Debugging

#### Enable Debug Logging
```yaml
# zen-mcp-server/kinfra_config.yaml
debug: true
log_level: "DEBUG"
```

#### Check KInfra Status
```bash
# Check overall status
kinfra status show-global

# Check project status
kinfra status show-project zen

# Check health
kinfra health --project zen
```

#### View Logs
```bash
# View KInfra logs
kinfra logs --project zen

# View specific service logs
kinfra logs --project zen --service api-gateway
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

This guide provides a comprehensive approach to adopting KInfra Phase 5 features in the Zen project. The migration is designed to be gradual, safe, and backward-compatible, allowing the team to adopt new features incrementally while maintaining existing functionality.

The migration will result in:
- Better resource coordination and sharing
- Improved process and tunnel management
- Enhanced monitoring and observability
- Simplified infrastructure management
- Better developer experience

**Ready to begin Zen migration!** 🚀