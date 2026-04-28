# Atoms Project KInfra Adoption Guide

## Overview

This guide provides step-by-step instructions for adopting KInfra Phase 5 features in the Atoms project. The Atoms project is an MCP server with atomic operations that will benefit significantly from better resource coordination and process management.

## Current Architecture

### Services
- **MCP Server**: Main MCP protocol server
- **Atomic Operations**: Core atomic operation processing
- **Data Processor**: Background data processing tasks

### Dependencies
- **Redis**: Caching and session storage
- **PostgreSQL**: Persistent data storage
- **External APIs**: Various external service integrations

### Current Infrastructure
- Basic port allocation
- Simple process management
- Manual resource allocation
- Limited monitoring and observability

## Migration Benefits

### Phase 1: Enable Metadata
- **Benefit**: Better process tracking and debugging
- **Impact**: Low - additive changes only
- **Timeline**: 2 days

### Phase 2: Adopt ProjectInfraContext
- **Benefit**: Project-scoped resource management
- **Impact**: Medium - requires code changes
- **Timeline**: 3 days

### Phase 3: Resource Helpers
- **Benefit**: Shared resource coordination and reuse
- **Impact**: Medium - infrastructure changes
- **Timeline**: 3 days

### Phase 4: Advanced Features
- **Benefit**: Process governance, tunnel management, cleanup policies
- **Impact**: Low - optional features
- **Timeline**: 2 days

## Step-by-Step Migration

### Phase 1: Enable Metadata (Week 1)

#### 1.1 Update Port Allocation
```python
# Before (atoms-mcp-prod/server.py)
from pheno.infra.port_allocator import SmartPortAllocator
port_allocator = SmartPortAllocator()
port = port_allocator.allocate_port("atoms-mcp", 8001)

# After
from pheno.infra.port_allocator import SmartPortAllocator
port_allocator = SmartPortAllocator()
port = port_allocator.allocate_port(
    "atoms-mcp", 
    8001,
    metadata={
        "project": "atoms",
        "service": "mcp-server",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "version": "2.0.0",
        "component": "mcp-server"
    }
)
```

#### 1.2 Update Process Registration
```python
# Before (atoms-mcp-prod/atoms_entry.py)
from pheno.infra.service_infra.base import ServiceInfraManager
service_manager = ServiceInfraManager()
service_manager.register_process(pid, command_line)

# After
from pheno.infra.service_infra.base import ServiceInfraManager
from pheno.infra.process_governance import ProcessMetadata

service_manager = ServiceInfraManager()
metadata = ProcessMetadata(
    project="atoms",
    service="mcp-server",
    pid=pid,
    command_line=command_line,
    environment=dict(os.environ),
    scope="local",
    resource_type="mcp-server",
    tags={"mcp", "server", "atoms", "atomic"}
)
service_manager.register_process(pid, command_line, metadata=metadata)
```

#### 1.3 Update Configuration
```yaml
# atoms-mcp-prod/kinfra_config.yaml
app_name: "atoms"
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
project_name: "atoms"
project_services:
  - mcp-server
  - atomic-ops
  - data-processor
```

### Phase 2: Adopt ProjectInfraContext (Week 2)

#### 2.1 Update Main Application
```python
# Before (atoms-mcp-prod/atoms_entry.py)
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
    async with project_infra_context("atoms") as infra:
        service_manager = ServiceInfraManager()
        await service_manager.start_all()
        # ... rest of application
        # All services now have atoms project context
```

#### 2.2 Update MCP Server Initialization
```python
# Before (atoms-mcp-prod/server.py)
from pheno.infra.service_infra.base import ServiceInfraManager

class MCPServer:
    def __init__(self):
        self.service_manager = ServiceInfraManager()
    
    async def start(self):
        await self.service_manager.start_all()

# After
from pheno.infra.project_context import project_infra_context
from pheno.infra.service_infra.base import ServiceInfraManager

class MCPServer:
    def __init__(self):
        self.service_manager = ServiceInfraManager()
    
    async def start(self):
        async with project_infra_context("atoms") as infra:
            await self.service_manager.start_all()
            # All services now have atoms project context
```

#### 2.3 Update Configuration
```yaml
# atoms-mcp-prod/kinfra_config.yaml
# ... existing config ...

# Project context settings
project_name: "atoms"
enable_project_isolation: true
project_services:
  - mcp-server
  - atomic-ops
  - data-processor

# Project-specific resource settings
project_resources:
  redis:
    type: "redis"
    config:
      host: "localhost"
      port: 6379
      db: 1
  postgres:
    type: "postgres"
    config:
      host: "localhost"
      port: 5432
      database: "atoms"
```

### Phase 3: Resource Helpers (Week 3)

#### 3.1 Update Resource Management
```python
# Before (atoms-mcp-prod/infrastructure/resource_manager.py)
from pheno.infra.deployment_manager import DeploymentManager

class ResourceManager:
    def __init__(self):
        self.deployment_manager = DeploymentManager()
    
    async def setup_redis(self):
        return await self.deployment_manager.deploy_resource(
            "atoms-redis", "redis", "local", 
            {"host": "localhost", "port": 6379, "db": 1}
        )
    
    async def setup_postgres(self):
        return await self.deployment_manager.deploy_resource(
            "atoms-postgres", "postgres", "local",
            {"host": "localhost", "port": 5432, "database": "atoms"}
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
            {"host": "localhost", "port": 6379, "db": 1}
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
# Before (atoms-mcp-prod/dependencies.py)
from pheno.infra.deployment_manager import DeploymentManager

async def get_redis():
    deployment_manager = DeploymentManager()
    return await deployment_manager.get_resource("atoms-redis")

async def get_postgres():
    deployment_manager = DeploymentManager()
    return await deployment_manager.get_resource("atoms-postgres")

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
# atoms-mcp-prod/kinfra_config.yaml
# ... existing config ...

# Resource coordination settings
enable_resource_sharing: true
resource_coordination: true
shared_resources:
  - redis
  - postgres

# Global resource settings
global_resources:
  redis:
    type: "redis"
    config:
      host: "localhost"
      port: 6379
      db: 1
    shared: true
  postgres:
    type: "postgres"
    config:
      host: "localhost"
      port: 5432
      database: "shared"
    shared: true
```

### Phase 4: Advanced Features (Week 4)

#### 4.1 Add Process Governance
```python
# atoms-mcp-prod/governance/process_governance.py
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata
import os
import sys

class AtomsProcessGovernance:
    def __init__(self):
        self.process_manager = ProcessGovernanceManager()
    
    def register_mcp_server(self, pid: int):
        metadata = ProcessMetadata(
            project="atoms",
            service="mcp-server",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="mcp-server",
            tags={"mcp", "server", "atoms", "atomic"}
        )
        self.process_manager.register_process(pid, metadata)
    
    def register_atomic_ops(self, pid: int):
        metadata = ProcessMetadata(
            project="atoms",
            service="atomic-ops",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="worker",
            tags={"atomic", "operations", "processing", "atoms"}
        )
        self.process_manager.register_process(pid, metadata)
    
    def register_data_processor(self, pid: int):
        metadata = ProcessMetadata(
            project="atoms",
            service="data-processor",
            pid=pid,
            command_line=sys.argv,
            environment=dict(os.environ),
            scope="local",
            resource_type="worker",
            tags={"data", "processing", "background", "atoms"}
        )
        self.process_manager.register_process(pid, metadata)
    
    def cleanup_project_processes(self):
        return self.process_manager.cleanup_project_processes("atoms")
```

#### 4.2 Add Tunnel Governance
```python
# atoms-mcp-prod/governance/tunnel_governance.py
from pheno.infra.tunnel_governance import TunnelGovernanceManager

class AtomsTunnelGovernance:
    def __init__(self):
        self.tunnel_manager = TunnelGovernanceManager()
    
    def create_mcp_tunnel(self, port: int):
        return self.tunnel_manager.create_tunnel(
            project="atoms",
            service="mcp-server",
            port=port,
            provider="cloudflare",
            reuse_existing=True
        )
    
    def create_worker_tunnel(self, port: int, worker_type: str):
        return self.tunnel_manager.create_tunnel(
            project="atoms",
            service=f"worker-{worker_type}",
            port=port,
            provider="cloudflare",
            reuse_existing=True
        )
    
    def cleanup_project_tunnels(self):
        return self.tunnel_manager.cleanup_project_tunnels("atoms")
```

#### 4.3 Add Cleanup Policies
```python
# atoms-mcp-prod/governance/cleanup_policies.py
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy, ResourceType

class AtomsCleanupPolicies:
    def __init__(self):
        self.cleanup_manager = CleanupPolicyManager()
        self.setup_policies()
    
    def setup_policies(self):
        # Create project-specific cleanup policy
        policy = self.cleanup_manager.create_default_policy(
            project_name="atoms",
            strategy=CleanupStrategy.MODERATE
        )
        
        # Set up process cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="atoms",
            resource_type=ResourceType.PROCESS,
            strategy=CleanupStrategy.MODERATE,
            patterns=["atoms-*", "mcp-*", "atomic-*"],
            max_age=3600.0,  # 1 hour
            force_cleanup=False
        )
        
        # Set up tunnel cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="atoms",
            resource_type=ResourceType.TUNNEL,
            strategy=CleanupStrategy.CONSERVATIVE,
            patterns=["atoms-*"],
            max_age=7200.0,  # 2 hours
            force_cleanup=False
        )
        
        # Set up port cleanup rules
        self.cleanup_manager.update_project_rule(
            project_name="atoms",
            resource_type=ResourceType.PORT,
            strategy=CleanupStrategy.MODERATE,
            patterns=["atoms-*"],
            max_age=1800.0,  # 30 minutes
            force_cleanup=True
        )
        
        self.cleanup_manager.set_project_policy("atoms", policy)
```

#### 4.4 Add Status Monitoring
```python
# atoms-mcp-prod/monitoring/status_monitoring.py
from pheno.infra.fallback_site.status_pages import StatusPageManager

class AtomsStatusMonitoring:
    def __init__(self):
        self.status_manager = StatusPageManager()
    
    def update_mcp_status(self, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="atoms",
            service_name="mcp-server",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_atomic_ops_status(self, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="atoms",
            service_name="atomic-ops",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_data_processor_status(self, status: str, health: str, port: int):
        self.status_manager.update_service_status(
            project_name="atoms",
            service_name="data-processor",
            status=status,
            port=port,
            health_status=health
        )
    
    def update_tunnel_status(self, service: str, status: str, hostname: str):
        self.status_manager.update_tunnel_status(
            project_name="atoms",
            service_name=service,
            status=status,
            hostname=hostname,
            provider="cloudflare"
        )
    
    def generate_status_page(self):
        return self.status_manager.generate_status_page("atoms", "status")
    
    def generate_project_summary(self):
        return self.status_manager.generate_project_summary("atoms")
```

#### 4.5 Update Configuration
```yaml
# atoms-mcp-prod/kinfra_config.yaml
# ... existing config ...

# Advanced features
enable_process_governance: true
enable_tunnel_governance: true
enable_cleanup_policies: true
enable_status_monitoring: true

# Process governance settings
process_governance:
  enable_metadata_tracking: true
  max_process_age: 3600.0
  cleanup_interval: 600.0
  force_cleanup: false

# Tunnel governance settings
tunnel_governance:
  default_lifecycle_policy: "smart"
  tunnel_reuse_threshold: 1800.0
  max_tunnel_age: 7200.0
  credential_scope: "project"

# Cleanup policy settings
cleanup_policies:
  project_name: "atoms"
  default_strategy: "moderate"
  enabled: true
  rules:
    process:
      resource_type: "process"
      strategy: "moderate"
      patterns: ["atoms-*", "mcp-*", "atomic-*"]
      max_age: 3600.0
      force_cleanup: false
      enabled: true
    tunnel:
      resource_type: "tunnel"
      strategy: "conservative"
      patterns: ["atoms-*"]
      max_age: 7200.0
      force_cleanup: false
      enabled: true
    port:
      resource_type: "port"
      strategy: "moderate"
      patterns: ["atoms-*"]
      max_age: 1800.0
      force_cleanup: true
      enabled: true

# Status monitoring settings
status_monitoring:
  auto_refresh_interval: 10
  include_service_details: true
  include_tunnel_details: true
  include_health_metrics: true
  theme: "default"
```

## Testing Strategy

### Unit Tests
```python
# atoms-mcp-prod/tests/test_kinfra_integration.py
import pytest
from atoms.governance.process_governance import AtomsProcessGovernance
from atoms.governance.tunnel_governance import AtomsTunnelGovernance
from atoms.governance.cleanup_policies import AtomsCleanupPolicies
from atoms.monitoring.status_monitoring import AtomsStatusMonitoring

class TestAtomsKInfraIntegration:
    def test_process_governance(self):
        governance = AtomsProcessGovernance()
        governance.register_mcp_server(12345)
        
        processes = governance.process_manager.get_project_processes("atoms")
        assert len(processes) == 1
        assert processes[0].service == "mcp-server"
    
    def test_tunnel_governance(self):
        governance = AtomsTunnelGovernance()
        tunnel = governance.create_mcp_tunnel(8001)
        
        assert tunnel.project == "atoms"
        assert tunnel.service == "mcp-server"
        assert tunnel.port == 8001
    
    def test_cleanup_policies(self):
        policies = AtomsCleanupPolicies()
        policy = policies.cleanup_manager.get_project_policy("atoms")
        
        assert policy.project_name == "atoms"
        assert policy.default_strategy == CleanupStrategy.MODERATE
    
    def test_status_monitoring(self):
        monitoring = AtomsStatusMonitoring()
        monitoring.update_mcp_status("running", "healthy", 8001)
        
        project_status = monitoring.status_manager.get_project_status("atoms")
        assert "mcp-server" in project_status.services
        assert project_status.services["mcp-server"].status == "running"
```

### Integration Tests
```python
# atoms-mcp-prod/tests/test_kinfra_integration_full.py
import pytest
import asyncio
from pheno.infra.project_context import project_infra_context

class TestAtomsKInfraIntegrationFull:
    @pytest.mark.asyncio
    async def test_full_integration(self):
        async with project_infra_context("atoms") as infra:
            # Test complete integration
            governance = AtomsProcessGovernance()
            tunnel_governance = AtomsTunnelGovernance()
            cleanup_policies = AtomsCleanupPolicies()
            status_monitoring = AtomsStatusMonitoring()
            
            # Register processes
            governance.register_mcp_server(12345)
            governance.register_atomic_ops(12346)
            governance.register_data_processor(12347)
            
            # Create tunnels
            mcp_tunnel = tunnel_governance.create_mcp_tunnel(8001)
            worker_tunnel = tunnel_governance.create_worker_tunnel(8002, "atomic-ops")
            
            # Update status
            status_monitoring.update_mcp_status("running", "healthy", 8001)
            status_monitoring.update_atomic_ops_status("running", "healthy", 8002)
            status_monitoring.update_data_processor_status("running", "healthy", 8003)
            
            # Verify everything is working
            processes = governance.process_manager.get_project_processes("atoms")
            assert len(processes) == 3
            
            tunnels = tunnel_governance.tunnel_manager.get_project_tunnels("atoms")
            assert len(tunnels) == 2
            
            project_status = status_monitoring.status_manager.get_project_status("atoms")
            assert len(project_status.services) == 3
            assert len(project_status.tunnels) == 2
```

## Deployment

### Docker Integration
```dockerfile
# atoms-mcp-prod/Dockerfile.kinfra
FROM python:3.11-slim

# Install KInfra
COPY pheno-sdk /app/pheno-sdk
WORKDIR /app/pheno-sdk
RUN pip install -e .

# Copy atoms application
COPY . /app/atoms
WORKDIR /app/atoms

# Install atoms dependencies
RUN pip install -r requirements-prod.txt

# Set up KInfra configuration
COPY kinfra_config.yaml /app/atoms/

# Start with KInfra
CMD ["python", "-m", "pheno.infra.main", "--project", "atoms"]
```

### Docker Compose Integration
```yaml
# atoms-mcp-prod/docker-compose.kinfra.yml
version: '3.8'

services:
  atoms-mcp:
    build:
      context: .
      dockerfile: Dockerfile.kinfra
    ports:
      - "8001:8001"
    environment:
      - PROJECT_NAME=atoms
      - SERVICE_NAME=mcp-server
      - KINFRA_CONFIG_PATH=/app/atoms/kinfra_config.yaml
    depends_on:
      - redis
      - postgres
  
  atoms-worker:
    build:
      context: .
      dockerfile: Dockerfile.kinfra
    environment:
      - PROJECT_NAME=atoms
      - SERVICE_NAME=worker
      - KINFRA_CONFIG_PATH=/app/atoms/kinfra_config.yaml
    depends_on:
      - redis
      - postgres
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=shared
      - POSTGRES_USER=atoms
      - POSTGRES_PASSWORD=atoms
    ports:
      - "5432:5432"
```

## Monitoring and Observability

### Health Checks
```python
# atoms-mcp-prod/health/kinfra_health.py
from pheno.infra.fallback_site.status_pages import StatusPageManager
from pheno.infra.process_governance import ProcessGovernanceManager
from pheno.infra.tunnel_governance import TunnelGovernanceManager

class AtomsHealthChecker:
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
        project_status = self.status_manager.get_project_status("atoms")
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
        processes = self.process_manager.get_project_processes("atoms")
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
# atoms-mcp-prod/metrics/kinfra_metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

class AtomsKInfraMetrics:
    def __init__(self):
        self.atomic_ops_count = Counter('atoms_atomic_ops_total', 'Total atomic operations', ['operation_type'])
        self.operation_duration = Histogram('atoms_operation_duration_seconds', 'Operation duration', ['operation_type'])
        self.active_processes = Gauge('atoms_active_processes', 'Active processes', ['service'])
        self.active_tunnels = Gauge('atoms_active_tunnels', 'Active tunnels', ['service'])
        self.resource_usage = Gauge('atoms_resource_usage', 'Resource usage', ['resource_type', 'service'])
    
    def record_atomic_operation(self, operation_type: str, duration: float):
        self.atomic_ops_count.labels(operation_type=operation_type).inc()
        self.operation_duration.labels(operation_type=operation_type).observe(duration)
    
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
kinfra port list --project atoms

# Resolve conflicts
kinfra port cleanup --project atoms --force
```

#### 2. Process Cleanup Issues
```bash
# Check process status
kinfra process list --project atoms

# Clean up stale processes
kinfra process cleanup-stale --project atoms
```

#### 3. Tunnel Connection Issues
```bash
# Check tunnel status
kinfra tunnel list --project atoms

# Test tunnel connectivity
kinfra tunnel test --project atoms --service mcp-server
```

#### 4. Resource Coordination Issues
```bash
# Check resource status
kinfra resource list --project atoms

# Test resource connectivity
kinfra resource test --project atoms --resource redis
```

### Debugging

#### Enable Debug Logging
```yaml
# atoms-mcp-prod/kinfra_config.yaml
debug: true
log_level: "DEBUG"
```

#### Check KInfra Status
```bash
# Check overall status
kinfra status show-global

# Check project status
kinfra status show-project atoms

# Check health
kinfra health --project atoms
```

#### View Logs
```bash
# View KInfra logs
kinfra logs --project atoms

# View specific service logs
kinfra logs --project atoms --service mcp-server
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

This guide provides a comprehensive approach to adopting KInfra Phase 5 features in the Atoms project. The migration is designed to be gradual, safe, and backward-compatible, allowing the team to adopt new features incrementally while maintaining existing functionality.

The migration will result in:
- Better resource coordination and sharing
- Improved process and tunnel management
- Enhanced monitoring and observability
- Simplified infrastructure management
- Better developer experience

**Ready to begin Atoms migration!** 🚀