# Global and Tenanted Resource Patterns

**Status:** Production Ready
**Last Updated:** 2025-10-16
**Author:** Pheno SDK Team

## Overview

This guide explains the distinction between **global** and **tenanted** resources in Pheno SDK, when to use each pattern, and how to implement them correctly.

## Global Resources Pattern

### What Are Global Resources?

Global resources are singleton instances managed by the **first service instance that starts**. Once registered, they can be discovered and used by any other service instance without duplication.

### Key Characteristics

| Aspect | Detail |
|--------|--------|
| **Scope** | Application-wide singleton |
| **Management** | First instance becomes manager |
| **Sharing** | All instances share the same resource |
| **Discovery** | Via NATS/service registry |
| **Failover** | Automatic election if manager dies |
| **Coordination** | NATS-based distributed protocol |

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Global Resource                      │
│              (e.g., Shared Database)                    │
└─────────────────────────────────────────────────────────┘
            ▲              ▲              ▲
            │              │              │
    ┌───────┴───────┬──────┴──────┬──────┴────────┐
    │               │             │               │
┌───┴──┐       ┌────┴──┐    ┌────┴──┐       ┌───┴──┐
│App 1 │       │App 2  │    │App 3  │       │App N │
│      │       │       │    │       │       │      │
│Mgr   │       │Parti  │    │Parti  │       │Parti │
└──────┘       └───────┘    └───────┘       └──────┘

Flow:
1. App 1 starts → Registers globally → Becomes Manager
2. App 2 starts → Discovers App 1 → Connects as Participant
3. App 3 starts → Discovers App 1 → Connects as Participant
4. If App 1 fails → Apps 2,3 detect it → Elect new manager
```

### Use Cases

**Perfect for:**
- ✅ Shared databases (PostgreSQL, MongoDB)
- ✅ Message queues (RabbitMQ, NATS)
- ✅ Cache servers (Redis)
- ✅ Tunnels (reverse proxies)
- ✅ Load balancers
- ✅ Registry/discovery services
- ✅ Logging aggregators

**Not suitable for:**
- ❌ User-specific data
- ❌ Project-isolated resources
- ❌ Multi-tenant data stores

### Implementation Example

```python
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.global_registry import ResourceMode

# Initialize (any service instance)
manager = DeploymentManager(
    instance_id="service-1",
    project_name=None  # No project = global scope
)

# Deploy as global
await manager.deploy_resource(
    name="shared-postgres",
    config={
        "type": "docker",
        "image": "postgres:16",
        "ports": {5432: 5432},
        "environment": {
            "POSTGRES_PASSWORD": "secure-password",
            "POSTGRES_DB": "shared_db"
        }
    },
    mode=ResourceMode.GLOBAL
)

# Starting sequence:
# Service 1 starts → Becomes PostgreSQL manager
# Service 2 starts → Discovers Service 1's PostgreSQL → Connects
# Service 3 starts → Discovers Service 1's PostgreSQL → Connects
```

### Discovery and Failover

```python
# Any service can discover a global resource
resource = await manager.discover_resource("shared-postgres")
print(f"Found: {resource['manager_location']}")

# If manager fails, automatic election occurs
# Participants detect heartbeat timeout
# Highest priority participant becomes new manager
# All reconnect automatically
```

### Global Resource Manager Responsibilities

The manager of a global resource:
1. Owns the resource lifecycle (start/stop)
2. Sends periodic heartbeats
3. Handles configuration updates
4. Coordinates failover election
5. Maintains state consistency

## Tenanted Resources Pattern

### What Are Tenanted Resources?

Tenanted resources are project-scoped instances completely isolated per tenant/project. Each project gets its own copy of the resource.

### Key Characteristics

| Aspect | Detail |
|--------|--------|
| **Scope** | Project-specific |
| **Isolation** | Complete per-project |
| **Sharing** | Never shared across projects |
| **Port Allocation** | Automatic per-project |
| **Cleanup** | Isolated per-tenant |
| **Coordination** | Local tenant manager |

### Architecture

```
Project A                           Project B
┌──────────────────────┐           ┌──────────────────────┐
│  Tenant A Resources  │           │  Tenant B Resources  │
│  ┌────────────────┐  │           │  ┌────────────────┐  │
│  │ Database       │  │           │  │ Database       │  │
│  │ Port: 5400     │  │           │  │ Port: 5401     │  │
│  └────────────────┘  │           │  └────────────────┘  │
│  ┌────────────────┐  │           │  ┌────────────────┐  │
│  │ Cache          │  │           │  │ Cache          │  │
│  │ Port: 6400     │  │           │  │ Port: 6401     │  │
│  └────────────────┘  │           │  └────────────────┘  │
└──────────────────────┘           └──────────────────────┘

App Instances (can belong to both)
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│  App 1   │  │  App 2   │  │  App 3   │  │  App 4   │
│ Tenant A │  │ Tenant A │  │ Tenant B │  │ Tenant B │
└──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### Use Cases

**Perfect for:**
- ✅ Multi-tenant SaaS applications
- ✅ Isolated tenant data stores
- ✅ Per-customer deployments
- ✅ Project-specific resources
- ✅ Isolated development/testing
- ✅ Compliance-required isolation
- ✅ Per-organization infrastructure

**Not suitable for:**
- ❌ Shared infrastructure
- ❌ Cost-sensitive deployments
- ❌ Resources used by all projects
- ❌ Services needing global coordination

### Implementation Example

```python
from pheno.infra.deployment_manager import DeploymentManager
from pheno.infra.global_registry import ResourceMode

# Initialize for specific tenant
manager = DeploymentManager(
    instance_id="service-acme-1",
    project_name="acme-corp"  # Project scope
)

# Deploy as tenanted (auto-scoped to acme-corp)
await manager.deploy_resource(
    name="database",
    config={
        "type": "docker",
        "image": "postgres:16",
        "ports": {5432: 5432},
        "environment": {
            "POSTGRES_PASSWORD": "acme-password",
            "POSTGRES_DB": "acme_db"
        }
    },
    mode=ResourceMode.TENANTED
)

# Port allocation:
# ACME tenant DB → localhost:5432 (project-specific port)
# OTHER tenant DB → localhost:5433 (different port)
# No conflicts, completely isolated
```

### Tenant Isolation

```python
# App for ACME tenant
manager_acme = DeploymentManager(
    instance_id="app-acme",
    project_name="acme-corp"
)

# App for OTHER tenant
manager_other = DeploymentManager(
    instance_id="app-other",
    project_name="other-corp"
)

# Each deploys its own isolated database
# No port conflicts, no data sharing
# Cleanup is independent
```

## Pattern Comparison

### Side-by-Side Comparison

```
┌─────────────────────────────────────────────────────────┐
│ Feature                 │ Global      │ Tenanted       │
├─────────────────────────────────────────────────────────┤
│ Instances               │ Singleton   │ One per tenant │
│ Cost                    │ Lower       │ Higher         │
│ Isolation               │ Shared      │ Complete       │
│ Port conflicts          │ None        │ None (auto)    │
│ Failover                │ Automatic   │ Per-tenant     │
│ Sharing                 │ All tenants │ Single tenant  │
│ Management              │ Distributed │ Local          │
│ Complexity              │ High        │ Medium         │
│ Scalability             │ Better      │ Horizontal     │
│ Data Security           │ Shared      │ Isolated       │
└─────────────────────────────────────────────────────────┘
```

### When to Choose

**Choose GLOBAL if:**
- Resource is truly shared
- Cost is a concern
- All services need access
- High availability is critical
- Coordination needed across all instances

**Choose TENANTED if:**
- Data isolation is required (compliance)
- Multi-tenant SaaS application
- Per-project infrastructure
- Different configurations per tenant
- Security policies require isolation

## Hybrid Deployment

### Best Practice: Global + Tenanted Mix

Many applications use both patterns:

```python
# Global resources (shared infrastructure)
manager = DeploymentManager(instance_id="master-1", project_name=None)

# Shared database (expensive to replicate)
await manager.deploy_resource(
    name="shared-postgres",
    config={"type": "docker", "image": "postgres:16"},
    mode=ResourceMode.GLOBAL
)

# Shared cache (high-performance, shared data)
await manager.deploy_resource(
    name="shared-redis",
    config={"type": "docker", "image": "redis:7"},
    mode=ResourceMode.GLOBAL
)

# Tenanted resources (isolated per project)
manager_acme = DeploymentManager(
    instance_id="app-acme",
    project_name="acme-corp"
)

# Tenant-specific cache (per-tenant isolation required)
await manager_acme.deploy_resource(
    name="cache",
    config={"type": "docker", "image": "redis:7"},
    mode=ResourceMode.TENANTED
)

# Tenant-specific app service
await manager_acme.deploy_resource(
    name="app-service",
    config={"type": "docker", "image": "acme-app:latest"},
    mode=ResourceMode.TENANTED
)
```

### Architecture Diagram

```
┌──────────────────────────────────────────────────────┐
│           Global Shared Infrastructure               │
│  ┌────────────────┐    ┌────────────────┐           │
│  │ PostgreSQL     │    │ Redis Cache    │           │
│  │ (global)       │    │ (global)       │           │
│  └────────────────┘    └────────────────┘           │
└──────────────────────────────────────────────────────┘
         △                      △
         │                      │
    ┌────┴────────┬─────────────┴──────────┬─────────┐
    │             │                        │         │
┌───┴──────┐  ┌──┴────────┐    ┌──────────┴──┐  ┌──┴────────┐
│ Tenant A │  │ Tenant B  │    │ Tenant C    │  │ Tenant N  │
│┌────────┐│  │┌────────┐ │    │┌────────────┐ │  │┌────────┐│
││App     ││  ││App     │ │    ││App        │ │  ││App     ││
│└────────┘│  │└────────┘ │    │└────────────┘ │  │└────────┘│
│┌────────┐│  │┌────────┐ │    │┌────────────┐ │  │┌────────┐│
││Cache   ││  ││Cache   │ │    ││Cache      │ │  ││Cache   ││
│└────────┘│  │└────────┘ │    │└────────────┘ │  │└────────┘│
└──────────┘  └───────────┘    └───────────────┘  └──────────┘
  Isolated       Isolated          Isolated         Isolated
```

## Advanced Patterns

### Pattern 1: Global Manager with Tenanted Failover

```python
# Global manager (production)
manager_prod = DeploymentManager(
    instance_id="prod-1",
    project_name=None
)

# Deploy as global
await manager_prod.deploy_resource(
    name="postgres",
    config={...},
    mode=ResourceMode.GLOBAL
)

# Tenant-specific failover managers
manager_tenant = DeploymentManager(
    instance_id="tenant-backup",
    project_name="acme-corp"
)

# Deploy local replica for failover
await manager_tenant.deploy_resource(
    name="postgres-replica",
    config={...},
    mode=ResourceMode.LOCAL  # Local only, ready for failover
)
```

### Pattern 2: Cascading Discovery

```python
# Three-level hierarchy:
# 1. Global resources (shared by all)
# 2. Tenant resources (per-project)
# 3. Local resources (service-specific)

async def setup_hierarchy(project_name):
    manager = DeploymentManager(
        instance_id=f"service-{project_name}",
        project_name=project_name
    )

    # Discover global resource
    global_db = await manager.discover_resource("shared-postgres")

    # Use for tenanted setup
    if global_db:
        await manager.deploy_resource(
            name="tenant-schema",
            config={"depends_on": global_db},
            mode=ResourceMode.TENANTED
        )

    # Deploy local resource
    await manager.deploy_resource(
        name="local-cache",
        config={...},
        mode=ResourceMode.LOCAL
    )
```

### Pattern 3: Multi-Region Global Resources

```python
# Deploy to multiple regions with global coordination
await manager.deploy_resource(
    name="postgres-us-east",
    config={
        "type": "docker",
        "image": "postgres:16",
        "labels": {"region": "us-east"}
    },
    mode=ResourceMode.GLOBAL,
    metadata={"region": "us-east", "primary": True}
)

# Secondary region (lower priority)
await manager.deploy_resource(
    name="postgres-eu-west",
    config={
        "type": "docker",
        "image": "postgres:16",
        "labels": {"region": "eu-west"}
    },
    mode=ResourceMode.GLOBAL,
    metadata={"region": "eu-west", "replica": True}
)
```

## Operations

### Scaling Patterns

**Global Resource Scaling:**
```python
# Scale instances accessing global resource
# Resource stays singleton, instances just connect

manager1 = DeploymentManager(instance_id="app-1", project_name=None)
manager2 = DeploymentManager(instance_id="app-2", project_name=None)
manager3 = DeploymentManager(instance_id="app-3", project_name=None)

# All discover and use same global resource
db = await manager1.discover_resource("postgres")
```

**Tenanted Resource Scaling:**
```python
# Scale by adding tenants (horizontal scaling)

for tenant_id in ["tenant-a", "tenant-b", "tenant-c"]:
    manager = DeploymentManager(
        instance_id=f"service-{tenant_id}",
        project_name=tenant_id
    )
    await manager.deploy_resource(
        name="app",
        config={"type": "docker", ...},
        mode=ResourceMode.TENANTED
    )
```

### Monitoring and Observability

```python
# Monitor global resource health
global_status = await manager.get_resource_status("shared-postgres")
print(f"Manager: {global_status['global']['manager_id']}")
print(f"Health: {global_status['global']['health']}")
print(f"Participants: {global_status['global']['participant_count']}")

# Monitor tenanted resources
tenants = await manager.list_resources(mode=ResourceMode.TENANTED)
for tenant in tenants:
    status = await manager.get_resource_status(tenant)
    print(f"Tenant {status['project']}: {status['local']['running']}")
```

## Troubleshooting

### Global Resource Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Can't discover resource | Manager hasn't started | Wait for first instance |
| Multiple managers | Timing issue | Use distributed lock |
| Failover not working | NATS down | Check NATS connectivity |
| Stale heartbeats | Network delay | Increase timeout |

### Tenanted Resource Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Port conflict | Multiple tenants | Use TenantManager |
| Cleanup partial | Process killed | Manual cleanup |
| Data isolation broken | Shared resource | Switch to local |

## Best Practices

### Global Resources

1. **Always enable health checks**
   ```python
   config = {
       "health_check": {
           "type": "tcp",
           "port": 5432,
           "interval": 30
       }
   }
   ```

2. **Use exponential backoff for discovery**
   ```python
   max_retries = 5
   for attempt in range(max_retries):
       resource = await manager.discover_resource("postgres")
       if resource:
           break
       await asyncio.sleep(2 ** attempt)
   ```

3. **Monitor manager elections**
   ```python
   def on_manager_change(event):
       print(f"Manager changed: {event}")

   manager.global_registry.register_manager_callback(
       "postgres",
       on_manager_change
   )
   ```

### Tenanted Resources

1. **Always use TenantManager for multi-tenant**
   ```python
   manager = DeploymentManager(
       instance_id="service-1",
       project_name="tenant-a"  # Scoped deployment
   )
   ```

2. **Clean up on tenant removal**
   ```python
   await manager.stop_all()
   await manager.deployment_manager.shutdown()
   ```

3. **Validate tenant isolation**
   ```python
   assert manager.project_name == "tenant-a"
   resources = await manager.list_resources()
   # Verify no other tenant's resources
   ```

## See Also

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Deployment instructions
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System design details
- API Documentation - API reference
