"""
Resource Coordination Example - Phase 3 Demonstration

Demonstrates enhanced resource coordination features:
- Resource policy management
- Global resource reuse with reference counting
- Dependency resolution
- Lifecycle rule enforcement
- Resource health monitoring
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any

from pheno.infra.project_context import project_infra_context
from pheno.infra.resource_coordinator import (
    ResourceCoordinator,
    ResourcePolicy,
    LifecycleRule,
)
from pheno.infra.resource_reference_cache import ResourceReuseStrategy
from pheno.infra.global_registry import ResourceMode

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def demonstrate_basic_coordination():
    """Demonstrate basic resource coordination."""
    print("\n=== Basic Resource Coordination ===")

    with project_infra_context("demo-project") as ctx:
        # Set resource policies
        postgres_policy = ResourcePolicy(
            resource_type="postgres",
            lifecycle_rule=LifecycleRule.GLOBAL_REUSE,
            reuse_strategy=ResourceReuseStrategy.SMART,
            dependencies=["redis"],
            compatibility_requirements={
                "version": "16",
                "required_config": {"POSTGRES_DB": "myapp"},
            },
        )
        ctx.set_resource_policy(postgres_policy)

        redis_policy = ResourcePolicy(
            resource_type="redis",
            lifecycle_rule=LifecycleRule.GLOBAL_REUSE,
            reuse_strategy=ResourceReuseStrategy.ALWAYS,
        )
        ctx.set_resource_policy(redis_policy)

        # Deploy resources with dependencies
        print("Deploying Redis...")
        redis_success = await ctx.deploy_resource(
            name="redis",
            config={
                "type": "docker",
                "image": "redis:7-alpine",
                "ports": {6379: 6379},
                "environment": {"REDIS_PASSWORD": "secret"},
            },
            mode=ResourceMode.TENANTED,
            dependencies=[],
        )

        print(f"Redis deployment: {'✓' if redis_success else '✗'}")

        print("Deploying PostgreSQL...")
        postgres_success = await ctx.deploy_resource(
            name="postgres",
            config={
                "type": "docker",
                "image": "postgres:16",
                "ports": {5432: 5432},
                "environment": {
                    "POSTGRES_DB": "myapp",
                    "POSTGRES_USER": "user",
                    "POSTGRES_PASSWORD": "secret",
                },
            },
            mode=ResourceMode.TENANTED,
            dependencies=["redis"],
        )

        print(f"PostgreSQL deployment: {'✓' if postgres_success else '✗'}")

        # Get resource status
        print("\nResource Status:")
        resources = await ctx.get_project_resources()
        for resource in resources:
            print(f"  {resource['name']}: {resource['mode']} - {resource['health']}")
            if resource.get("dependencies"):
                print(f"    Dependencies: {', '.join(resource['dependencies'])}")

        # Validate dependencies
        is_valid, missing = await ctx.validate_dependencies()
        print(f"\nDependencies valid: {'✓' if is_valid else '✗'}")
        if missing:
            print(f"Missing: {', '.join(missing)}")


async def demonstrate_global_reuse():
    """Demonstrate global resource reuse."""
    print("\n=== Global Resource Reuse ===")

    # First project
    with project_infra_context("project-a") as ctx:
        print("Project A deploying shared Redis...")

        redis_policy = ResourcePolicy(
            resource_type="redis",
            lifecycle_rule=LifecycleRule.GLOBAL_REUSE,
            reuse_strategy=ResourceReuseStrategy.ALWAYS,
        )
        ctx.set_resource_policy(redis_policy)

        success = await ctx.deploy_resource(
            name="shared-redis",
            config={
                "type": "docker",
                "image": "redis:7-alpine",
                "ports": {6379: 6379},
            },
            mode=ResourceMode.GLOBAL,
        )

        print(f"Project A Redis: {'✓' if success else '✗'}")

        # Get coordination status
        status = await ctx.get_coordination_status()
        print(f"Active requests: {status['active_requests']}")
        print(f"Resource health: {status['resource_health']}")

    # Second project (should reuse the global Redis)
    with project_infra_context("project-b") as ctx:
        print("\nProject B requesting shared Redis...")

        redis_policy = ResourcePolicy(
            resource_type="redis",
            lifecycle_rule=LifecycleRule.GLOBAL_REUSE,
            reuse_strategy=ResourceReuseStrategy.ALWAYS,
        )
        ctx.set_resource_policy(redis_policy)

        success = await ctx.deploy_resource(
            name="shared-redis",
            config={
                "type": "docker",
                "image": "redis:7-alpine",
                "ports": {6379: 6379},
            },
            mode=ResourceMode.GLOBAL,
        )

        print(f"Project B Redis: {'✓' if success else '✗'}")

        # Check if it was reused
        resources = await ctx.get_project_resources()
        for resource in resources:
            if resource["name"] == "shared-redis":
                print(f"Resource reused: {resource.get('is_reused', False)}")


async def demonstrate_dependency_resolution():
    """Demonstrate dependency resolution."""
    print("\n=== Dependency Resolution ===")

    with project_infra_context("dependency-demo") as ctx:
        # Set up complex dependency chain
        api_policy = ResourcePolicy(
            resource_type="api",
            lifecycle_rule=LifecycleRule.DEPENDENCY_DRIVEN,
            reuse_strategy=ResourceReuseStrategy.SMART,
            dependencies=["postgres", "redis", "elasticsearch"],
        )
        ctx.set_resource_policy(api_policy)

        postgres_policy = ResourcePolicy(
            resource_type="postgres",
            lifecycle_rule=LifecycleRule.PROJECT_SCOPED,
            reuse_strategy=ResourceReuseStrategy.NEVER,
            dependencies=["redis"],
        )
        ctx.set_resource_policy(postgres_policy)

        # Deploy in dependency order
        print("Deploying Redis (no dependencies)...")
        redis_success = await ctx.deploy_resource(
            name="redis",
            config={
                "type": "docker",
                "image": "redis:7-alpine",
                "ports": {6379: 6379},
            },
        )

        print("Deploying PostgreSQL (depends on Redis)...")
        postgres_success = await ctx.deploy_resource(
            name="postgres",
            config={
                "type": "docker",
                "image": "postgres:16",
                "ports": {5432: 5432},
                "environment": {
                    "POSTGRES_DB": "myapp",
                    "POSTGRES_USER": "user",
                    "POSTGRES_PASSWORD": "secret",
                },
            },
            dependencies=["redis"],
        )

        print("Deploying Elasticsearch (no dependencies)...")
        elasticsearch_success = await ctx.deploy_resource(
            name="elasticsearch",
            config={
                "type": "docker",
                "image": "elasticsearch:8.11.0",
                "ports": {9200: 9200},
                "environment": {"discovery.type": "single-node", "xpack.security.enabled": "false"},
            },
        )

        print("Deploying API (depends on postgres, redis, elasticsearch)...")
        api_success = await ctx.deploy_resource(
            name="api",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8080: 80},
            },
            dependencies=["postgres", "redis", "elasticsearch"],
        )

        print(f"\nDeployment Results:")
        print(f"  Redis: {'✓' if redis_success else '✗'}")
        print(f"  PostgreSQL: {'✓' if postgres_success else '✗'}")
        print(f"  Elasticsearch: {'✓' if elasticsearch_success else '✗'}")
        print(f"  API: {'✓' if api_success else '✗'}")

        # Validate all dependencies
        is_valid, missing = await ctx.validate_dependencies()
        print(f"\nAll dependencies satisfied: {'✓' if is_valid else '✗'}")
        if missing:
            print(f"Missing dependencies: {', '.join(missing)}")


async def demonstrate_lifecycle_rules():
    """Demonstrate different lifecycle rules."""
    print("\n=== Lifecycle Rules ===")

    with project_infra_context("lifecycle-demo") as ctx:
        # Project-scoped resource
        print("Deploying project-scoped resource...")
        project_policy = ResourcePolicy(
            resource_type="project-service",
            lifecycle_rule=LifecycleRule.PROJECT_SCOPED,
            reuse_strategy=ResourceReuseStrategy.NEVER,
        )
        ctx.set_resource_policy(project_policy)

        project_success = await ctx.deploy_resource(
            name="project-service",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8080: 80},
            },
        )

        # Global resource
        print("Deploying global resource...")
        global_policy = ResourcePolicy(
            resource_type="global-service",
            lifecycle_rule=LifecycleRule.GLOBAL_REUSE,
            reuse_strategy=ResourceReuseStrategy.ALWAYS,
        )
        ctx.set_resource_policy(global_policy)

        global_success = await ctx.deploy_resource(
            name="global-service",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8081: 80},
            },
            mode=ResourceMode.GLOBAL,
        )

        # Smart decision resource
        print("Deploying smart-decision resource...")
        smart_policy = ResourcePolicy(
            resource_type="smart-service",
            lifecycle_rule=LifecycleRule.SMART_DECISION,
            reuse_strategy=ResourceReuseStrategy.SMART,
        )
        ctx.set_resource_policy(smart_policy)

        smart_success = await ctx.deploy_resource(
            name="smart-service",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8082: 80},
            },
        )

        print(f"\nLifecycle Rule Results:")
        print(f"  Project-scoped: {'✓' if project_success else '✗'}")
        print(f"  Global reuse: {'✓' if global_success else '✗'}")
        print(f"  Smart decision: {'✓' if smart_success else '✗'}")

        # Show resource details
        resources = await ctx.get_project_resources()
        for resource in resources:
            print(f"  {resource['name']}: {resource['mode']} - {resource.get('is_reused', False)}")


async def demonstrate_health_monitoring():
    """Demonstrate resource health monitoring."""
    print("\n=== Health Monitoring ===")

    with project_infra_context("health-demo") as ctx:
        # Deploy a resource
        success = await ctx.deploy_resource(
            name="monitored-service",
            config={
                "type": "docker",
                "image": "nginx:alpine",
                "ports": {8080: 80},
            },
        )

        if success:
            print("Resource deployed, monitoring health...")

            # Monitor for a few seconds
            for i in range(5):
                status = await ctx.get_resource_status("monitored-service")
                if status:
                    print(f"  Health check {i+1}: {status.get('health', 'unknown')}")
                await asyncio.sleep(1)

            # Get coordination status
            coord_status = await ctx.get_coordination_status()
            print(f"\nCoordination Status:")
            print(f"  Active requests: {coord_status['active_requests']}")
            print(f"  Resource health: {coord_status['resource_health']}")


async def main():
    """Run all demonstrations."""
    print("Phase 3: Resource Coordination Demonstration")
    print("=" * 50)

    try:
        await demonstrate_basic_coordination()
        await demonstrate_global_reuse()
        await demonstrate_dependency_resolution()
        await demonstrate_lifecycle_rules()
        await demonstrate_health_monitoring()

        print("\n" + "=" * 50)
        print("Phase 3 demonstration completed successfully!")

    except Exception as e:
        logger.error(f"Demonstration failed: {e}")
        print(f"\n✗ Demonstration failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
