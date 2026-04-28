# KInfra Migration Plan: Router, Atoms, and Zen

## Overview

This document provides a comprehensive migration plan for existing codebases (router, atoms, zen) to adopt KInfra Phase 5 features. The migration is designed to be gradual, safe, and backward-compatible, allowing teams to adopt new features incrementally while maintaining existing functionality.

## Migration Strategy

### Phase 1: Enable Metadata (Week 1-2)
- **Goal**: Enable metadata tracking without breaking existing functionality
- **Scope**: All three codebases (router, atoms, zen)
- **Risk**: Low - additive changes only
- **Rollback**: Easy - metadata can be disabled

### Phase 2: Adopt ProjectInfraContext (Week 3-4)
- **Goal**: Migrate to project-scoped infrastructure management
- **Scope**: Router and atoms first, then zen
- **Risk**: Medium - requires code changes
- **Rollback**: Moderate - requires reverting infrastructure changes

### Phase 3: Resource Helpers (Week 5-6)
- **Goal**: Adopt shared resource management and coordination
- **Scope**: All three codebases
- **Risk**: Medium - requires infrastructure changes
- **Rollback**: Moderate - requires reverting resource changes

### Phase 4: Advanced Features (Week 7-8)
- **Goal**: Adopt process governance, tunnel governance, and cleanup policies
- **Scope**: All three codebases
- **Risk**: Low - optional features
- **Rollback**: Easy - features can be disabled

## Codebase Analysis

### Router Project
- **Current State**: Complex routing system with multiple services
- **Infrastructure**: Custom port management, basic process control
- **Migration Priority**: High - benefits most from shared infrastructure
- **Key Services**: API server, worker processes, routing engine
- **Dependencies**: Redis, PostgreSQL, NATS

### Atoms Project
- **Current State**: MCP server with atomic operations
- **Infrastructure**: Basic port allocation, simple process management
- **Migration Priority**: High - needs better resource coordination
- **Key Services**: MCP server, atomic operations, data processing
- **Dependencies**: Redis, PostgreSQL, external APIs

### Zen Project
- **Current State**: Complex multi-service architecture
- **Infrastructure**: Docker-based deployment, service orchestration
- **Migration Priority**: Medium - already has good infrastructure
- **Key Services**: API gateway, microservices, database services
- **Dependencies**: PostgreSQL, Redis, external services

## Migration Steps

### Step 1: Enable Metadata Tracking

#### Router Migration
```python
# Before
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
        "environment": "production",
        "version": "1.0.0"
    }
)
```

#### Atoms Migration
```python
# Before
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
        "service": "mcp",
        "environment": "production",
        "version": "2.0.0"
    }
)
```

#### Zen Migration
```python
# Before
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
        "service": "api",
        "environment": "production",
        "version": "6.1.0"
    }
)
```

### Step 2: Adopt ProjectInfraContext

#### Router Migration
```python
# Before
from pheno.infra.service_infra.base import ServiceInfraManager
service_manager = ServiceInfraManager()
await service_manager.start_all()

# After
from pheno.infra.project_context import project_infra_context
from pheno.infra.service_infra.base import ServiceInfraManager

async with project_infra_context("router") as infra:
    service_manager = ServiceInfraManager()
    await service_manager.start_all()
    # All services now have router project context
```

#### Atoms Migration
```python
# Before
from pheno.infra.service_infra.base import ServiceInfraManager
service_manager = ServiceInfraManager()
await service_manager.start_all()

# After
from pheno.infra.project_context import project_infra_context
from pheno.infra.service_infra.base import ServiceInfraManager

async with project_infra_context("atoms") as infra:
    service_manager = ServiceInfraManager()
    await service_manager.start_all()
    # All services now have atoms project context
```

#### Zen Migration
```python
# Before
from pheno.infra.service_infra.base import ServiceInfraManager
service_manager = ServiceInfraManager()
await service_manager.start_all()

# After
from pheno.infra.project_context import project_infra_context
from pheno.infra.service_infra.base import ServiceInfraManager

async with project_infra_context("zen") as infra:
    service_manager = ServiceInfraManager()
    await service_manager.start_all()
    # All services now have zen project context
```

### Step 3: Adopt Resource Helpers

#### Router Migration
```python
# Before
from pheno.infra.deployment_manager import DeploymentManager
deployment_manager = DeploymentManager()
redis_resource = await deployment_manager.deploy_resource(
    "router-redis", "redis", "local", {"host": "localhost", "port": 6379}
)

# After
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.deployment_manager import DeploymentManager

deployment_manager = DeploymentManager()
resource_coordinator = ResourceCoordinator(deployment_manager)
await resource_coordinator.initialize()

# Use shared Redis if available, otherwise create project-specific
redis_resource = await resource_coordinator.get_or_deploy_resource(
    "shared-redis", "redis", "global", 
    {"host": "localhost", "port": 6379, "db": 0}
)
```

#### Atoms Migration
```python
# Before
from pheno.infra.deployment_manager import DeploymentManager
deployment_manager = DeploymentManager()
postgres_resource = await deployment_manager.deploy_resource(
    "atoms-postgres", "postgres", "local", 
    {"host": "localhost", "port": 5432, "database": "atoms"}
)

# After
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.deployment_manager import DeploymentManager

deployment_manager = DeploymentManager()
resource_coordinator = ResourceCoordinator(deployment_manager)
await resource_coordinator.initialize()

# Use shared PostgreSQL if available, otherwise create project-specific
postgres_resource = await resource_coordinator.get_or_deploy_resource(
    "shared-postgres", "postgres", "global",
    {"host": "localhost", "port": 5432, "database": "shared"}
)
```

#### Zen Migration
```python
# Before
from pheno.infra.deployment_manager import DeploymentManager
deployment_manager = DeploymentManager()
nats_resource = await deployment_manager.deploy_resource(
    "zen-nats", "nats", "local",
    {"url": "nats://localhost:4222"}
)

# After
from pheno.infra.resource_coordinator import ResourceCoordinator
from pheno.infra.deployment_manager import DeploymentManager

deployment_manager = DeploymentManager()
resource_coordinator = ResourceCoordinator(deployment_manager)
await resource_coordinator.initialize()

# Use shared NATS if available, otherwise create project-specific
nats_resource = await resource_coordinator.get_or_deploy_resource(
    "shared-nats", "nats", "global",
    {"url": "nats://localhost:4222"}
)
```

### Step 4: Adopt Advanced Features

#### Process Governance
```python
# All projects
from pheno.infra.process_governance import ProcessGovernanceManager, ProcessMetadata

process_manager = ProcessGovernanceManager()

# Register processes with metadata
metadata = ProcessMetadata(
    project="router",  # or "atoms", "zen"
    service="api",
    pid=os.getpid(),
    command_line=sys.argv,
    environment=dict(os.environ),
    scope="local",
    resource_type="api",
    tags={"web", "rest", "api"}
)

process_manager.register_process(os.getpid(), metadata)
```

#### Tunnel Governance
```python
# All projects
from pheno.infra.tunnel_governance import TunnelGovernanceManager

tunnel_manager = TunnelGovernanceManager()

# Create tunnels with project context
tunnel = tunnel_manager.create_tunnel(
    project="router",  # or "atoms", "zen"
    service="api",
    port=8000,
    provider="cloudflare",
    reuse_existing=True
)
```

#### Cleanup Policies
```python
# All projects
from pheno.infra.cleanup_policies import CleanupPolicyManager, CleanupStrategy

cleanup_manager = CleanupPolicyManager()

# Set up project-specific cleanup policies
cleanup_manager.set_project_policy(
    "router",  # or "atoms", "zen"
    cleanup_manager.create_default_policy(
        project_name="router",
        strategy=CleanupStrategy.MODERATE
    )
)
```

#### Status Monitoring
```python
# All projects
from pheno.infra.fallback_site.status_pages import StatusPageManager

status_manager = StatusPageManager()

# Update service status
status_manager.update_service_status(
    project_name="router",  # or "atoms", "zen"
    service_name="api",
    status="running",
    port=8000,
    health_status="healthy"
)
```

## Migration Tools

### 1. Migration Script Generator
```bash
# Generate migration scripts for a project
python scripts/kinfra-migrate.py generate --project router --phase 1
python scripts/kinfra-migrate.py generate --project atoms --phase 2
python scripts/kinfra-migrate.py generate --project zen --phase 3
```

### 2. Migration Validator
```bash
# Validate migration progress
python scripts/kinfra-migrate.py validate --project router
python scripts/kinfra-migrate.py validate --project atoms
python scripts/kinfra-migrate.py validate --project zen
```

### 3. Rollback Scripts
```bash
# Rollback migration if needed
python scripts/kinfra-migrate.py rollback --project router --phase 1
python scripts/kinfra-migrate.py rollback --project atoms --phase 2
python scripts/kinfra-migrate.py rollback --project zen --phase 3
```

## Testing Strategy

### 1. Unit Tests
- Test each migration step in isolation
- Verify backward compatibility
- Test error handling and rollback scenarios

### 2. Integration Tests
- Test complete migration workflows
- Verify cross-project resource sharing
- Test cleanup and governance features

### 3. End-to-End Tests
- Test complete application functionality
- Verify performance characteristics
- Test monitoring and observability

## Rollback Plan

### Phase 1 Rollback
1. Disable metadata tracking in configuration
2. Revert port allocation calls to original format
3. Restart services

### Phase 2 Rollback
1. Remove ProjectInfraContext usage
2. Revert to direct ServiceInfraManager usage
3. Update resource references

### Phase 3 Rollback
1. Revert to direct DeploymentManager usage
2. Remove ResourceCoordinator usage
3. Update resource configurations

### Phase 4 Rollback
1. Disable advanced features in configuration
2. Remove process/tunnel governance calls
3. Remove status monitoring calls

## Success Metrics

### Phase 1 Success Criteria
- [ ] Metadata tracking enabled for all projects
- [ ] No performance degradation
- [ ] All existing tests pass
- [ ] Monitoring shows metadata in logs

### Phase 2 Success Criteria
- [ ] ProjectInfraContext adopted by all projects
- [ ] Project isolation working correctly
- [ ] Resource cleanup working per project
- [ ] All existing tests pass

### Phase 3 Success Criteria
- [ ] Resource sharing working across projects
- [ ] Resource coordination functioning
- [ ] Performance improved or maintained
- [ ] All existing tests pass

### Phase 4 Success Criteria
- [ ] Process governance working
- [ ] Tunnel governance working
- [ ] Cleanup policies enforced
- [ ] Status monitoring functional
- [ ] All existing tests pass

## Timeline

### Week 1-2: Phase 1 - Enable Metadata
- **Router**: 3 days
- **Atoms**: 2 days
- **Zen**: 3 days
- **Testing**: 2 days

### Week 3-4: Phase 2 - Adopt ProjectInfraContext
- **Router**: 4 days
- **Atoms**: 3 days
- **Zen**: 4 days
- **Testing**: 3 days

### Week 5-6: Phase 3 - Resource Helpers
- **Router**: 4 days
- **Atoms**: 3 days
- **Zen**: 4 days
- **Testing**: 3 days

### Week 7-8: Phase 4 - Advanced Features
- **Router**: 3 days
- **Atoms**: 2 days
- **Zen**: 3 days
- **Testing**: 2 days

## Risk Mitigation

### Technical Risks
- **Backward Compatibility**: Maintained through gradual migration
- **Performance Impact**: Monitored and optimized
- **Resource Conflicts**: Handled through coordination
- **Data Loss**: Prevented through careful resource management

### Process Risks
- **Team Coordination**: Managed through clear communication
- **Timeline Delays**: Mitigated through parallel work
- **Testing Coverage**: Ensured through comprehensive testing
- **Rollback Complexity**: Minimized through phased approach

## Support and Training

### Documentation
- Migration guides for each project
- API reference for new features
- Troubleshooting guides
- Best practices documentation

### Training
- Team training sessions
- Code review guidelines
- Migration tool usage
- Monitoring and debugging

### Support
- Migration support team
- Regular check-ins
- Issue escalation process
- Rollback support

## Conclusion

This migration plan provides a comprehensive, safe, and gradual approach to adopting KInfra Phase 5 features across all three codebases. The phased approach minimizes risk while maximizing benefits, and the extensive tooling and support ensure successful migration.

The migration will result in:
- Better resource coordination and sharing
- Improved process and tunnel management
- Enhanced monitoring and observability
- Simplified infrastructure management
- Better developer experience

**Ready to begin migration!** 🚀