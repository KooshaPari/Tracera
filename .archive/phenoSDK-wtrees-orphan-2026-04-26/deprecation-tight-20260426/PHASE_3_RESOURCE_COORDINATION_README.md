# Phase 3: Resource Coordination - Implementation Complete

## Overview

Phase 3 of the KInfra transformation implements sophisticated resource coordination with intelligent global resource reuse, dependency resolution, and lifecycle rule enforcement. This phase builds upon the project context layer from Phase 2 to provide enterprise-grade resource management.

## Key Features Implemented

### 1. ResourceReferenceCache ✅
- **Conditional Global Resource Reuse**: Intelligently reuse global resources based on compatibility checks
- **Reference Counting**: Prevent premature cleanup of resources still in use
- **Compatibility Scoring**: Rate resource compatibility for smart reuse decisions
- **Automatic Cleanup**: Background task to clean up unused resources

### 2. ResourceCoordinator ✅
- **Enhanced Resource Management**: Sophisticated orchestration of resource lifecycle
- **Dependency Resolution**: Automatic resolution and validation of resource dependencies
- **Lifecycle Rule Enforcement**: Clear rules for project vs global resource management
- **Health Monitoring**: Continuous monitoring of resource health with automatic recovery

### 3. Resource Policies ✅
- **Configurable Policies**: Per-resource-type policies for lifecycle and reuse behavior
- **Lifecycle Rules**: PROJECT_SCOPED, GLOBAL_REUSE, SMART_DECISION, DEPENDENCY_DRIVEN
- **Reuse Strategies**: ALWAYS, CONDITIONAL, NEVER, SMART
- **Compatibility Requirements**: Version and configuration compatibility checking

### 4. Enhanced ProjectInfraContext Integration ✅
- **Seamless Integration**: ResourceCoordinator integrated into existing ProjectInfraContext
- **Backward Compatibility**: All existing functionality continues to work
- **Enhanced Methods**: New methods for policy management, dependency validation, and coordination status

### 5. Advanced CLI Commands ✅
- **Resource Policy Management**: Set and manage resource policies via CLI
- **Dependency Validation**: Validate project dependencies
- **Coordination Status**: Rich status reporting for resource coordination
- **Resource Lifecycle**: Request, release, and monitor resources

## Architecture

```
ResourceCoordinator
├── ResourceReferenceCache
│   ├── Global Resource Discovery
│   ├── Compatibility Checking
│   ├── Reference Counting
│   └── Automatic Cleanup
├── DeploymentManager (existing)
│   ├── ResourceManager
│   └── GlobalResourceRegistry
└── Policy Engine
    ├── Lifecycle Rules
    ├── Reuse Strategies
    └── Compatibility Requirements

ProjectInfraContext (Enhanced)
├── ResourceCoordinator Integration
├── Policy Management
├── Dependency Resolution
└── Enhanced Status Reporting
```

## Usage Examples

### Basic Resource Coordination

```python
from pheno.infra.project_context import project_infra_context
from pheno.infra.resource_coordinator import ResourcePolicy, LifecycleRule
from pheno.infra.resource_reference_cache import ResourceReuseStrategy

with project_infra_context("my-project") as ctx:
    # Set resource policies
    postgres_policy = ResourcePolicy(
        resource_type="postgres",
        lifecycle_rule=LifecycleRule.GLOBAL_REUSE,
        reuse_strategy=ResourceReuseStrategy.SMART,
        dependencies=["redis"],
        compatibility_requirements={
            "version": "16",
            "required_config": {"POSTGRES_DB": "myapp"}
        }
    )
    ctx.set_resource_policy(postgres_policy)
    
    # Deploy resources with dependencies
    await ctx.deploy_resource(
        name="postgres",
        config={
            "type": "docker",
            "image": "postgres:16",
            "ports": {5432: 5432},
            "environment": {"POSTGRES_DB": "myapp"}
        },
        dependencies=["redis"]
    )
```

### Global Resource Reuse

```python
# Project A creates a global resource
with project_infra_context("project-a") as ctx:
    redis_policy = ResourcePolicy(
        resource_type="redis",
        lifecycle_rule=LifecycleRule.GLOBAL_REUSE,
        reuse_strategy=ResourceReuseStrategy.ALWAYS,
    )
    ctx.set_resource_policy(redis_policy)
    
    await ctx.deploy_resource(
        name="shared-redis",
        config={"type": "docker", "image": "redis:7-alpine"},
        mode=ResourceMode.GLOBAL
    )

# Project B reuses the global resource
with project_infra_context("project-b") as ctx:
    ctx.set_resource_policy(redis_policy)
    
    success, resource_info = await ctx.deploy_resource(
        name="shared-redis",
        config={"type": "docker", "image": "redis:7-alpine"},
        mode=ResourceMode.GLOBAL
    )
    
    if resource_info and resource_info.get("is_reused"):
        print("Reused existing global resource!")
```

### Dependency Resolution

```python
with project_infra_context("api-project") as ctx:
    # Set up dependency chain
    api_policy = ResourcePolicy(
        resource_type="api",
        lifecycle_rule=LifecycleRule.DEPENDENCY_DRIVEN,
        dependencies=["postgres", "redis", "elasticsearch"],
    )
    ctx.set_resource_policy(api_policy)
    
    # Deploy with automatic dependency resolution
    await ctx.deploy_resource(
        name="api",
        config={"type": "docker", "image": "my-api:latest"},
        dependencies=["postgres", "redis", "elasticsearch"]
    )
    
    # Validate dependencies
    is_valid, missing = await ctx.validate_dependencies()
    if not is_valid:
        print(f"Missing dependencies: {missing}")
```

### CLI Usage

```bash
# Set resource policy
pheno resource set-policy postgres \
  --lifecycle-rule global_reuse \
  --reuse-strategy smart \
  --dependencies redis

# Request a resource
pheno resource request my-postgres postgres-config.json \
  --mode global \
  --dependencies redis

# Check resource status
pheno resource status my-postgres

# Validate dependencies
pheno resource validate

# Get coordination status
pheno resource coordination-status
```

## Resource Policies

### Lifecycle Rules

1. **PROJECT_SCOPED**: Always create project-specific resources
2. **GLOBAL_REUSE**: Reuse global resources when possible
3. **SMART_DECISION**: Use heuristics to decide based on resource type
4. **DEPENDENCY_DRIVEN**: Decision based on dependency requirements

### Reuse Strategies

1. **ALWAYS**: Always try to reuse if available
2. **CONDITIONAL**: Reuse based on compatibility checks
3. **NEVER**: Never reuse, always create project-scoped
4. **SMART**: Use heuristics to determine best strategy

### Compatibility Requirements

```python
compatibility_requirements = {
    "version": "16",  # Required version
    "required_config": {  # Required configuration
        "POSTGRES_DB": "myapp",
        "POSTGRES_USER": "user"
    },
    "optional_config": {  # Optional configuration
        "POSTGRES_PASSWORD": "secret"
    }
}
```

## Key Benefits

### 1. **Intelligent Resource Reuse**
- Automatic discovery and reuse of compatible global resources
- Reference counting prevents premature cleanup
- Compatibility scoring for optimal reuse decisions

### 2. **Dependency Management**
- Automatic dependency resolution
- Validation of dependency requirements
- Clear dependency chains and relationships

### 3. **Policy-Driven Management**
- Configurable policies per resource type
- Clear lifecycle rules and reuse strategies
- Flexible compatibility requirements

### 4. **Enhanced Monitoring**
- Resource health monitoring
- Coordination status reporting
- Dependency validation

### 5. **Production Ready**
- Error handling and recovery
- Graceful degradation
- Comprehensive logging

## File Structure

```
pheno-sdk/src/pheno/infra/
├── resource_reference_cache.py    # Resource reference management
├── resource_coordinator.py        # Main coordination orchestrator
├── cli/
│   └── resource_cli.py            # Enhanced CLI commands
├── project_context.py             # Enhanced with coordination
└── examples/
    └── resource_coordination_example.py  # Comprehensive examples
```

## Migration from Phase 2

Phase 3 is fully backward compatible with Phase 2:

```python
# Phase 2 usage (still works)
with project_infra_context("my-project") as ctx:
    await ctx.deploy_resource("redis", config)

# Phase 3 enhanced usage (recommended)
with project_infra_context("my-project") as ctx:
    # Set policies
    ctx.set_resource_policy(redis_policy)
    
    # Deploy with enhanced coordination
    await ctx.deploy_resource("redis", config, dependencies=["postgres"])
    
    # Validate dependencies
    is_valid, missing = await ctx.validate_dependencies()
```

## Testing

Run the comprehensive example to see Phase 3 in action:

```bash
cd pheno-sdk
python examples/resource_coordination_example.py
```

This demonstrates all the key features of Phase 3 resource coordination.

## Next Steps (Phase 4)

Phase 3 provides the foundation for Phase 4 (Advanced Orchestration), which will focus on:

1. **Multi-Project Coordination**: Cross-project resource sharing and coordination
2. **Resource Scheduling**: Intelligent scheduling and load balancing
3. **Advanced Monitoring**: Metrics collection and alerting
4. **Service Mesh Integration**: Integration with service mesh technologies

## Configuration

Resource coordination configurations are stored in `~/.kinfra/{project_name}.json` and include:

- Resource policies
- Dependency definitions
- Compatibility requirements
- Coordination settings

The system automatically manages these configurations and provides CLI commands for inspection and modification.

## Conclusion

Phase 3 successfully implements sophisticated resource coordination with intelligent global resource reuse, dependency resolution, and lifecycle rule enforcement. The implementation provides enterprise-grade resource management while maintaining the simplicity and power of the existing KInfra architecture.

The resource coordination layer enables efficient resource utilization, automatic dependency management, and intelligent resource reuse, making it ideal for complex multi-service applications with resource sharing requirements.