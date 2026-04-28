"""Unified Infrastructure and Process Management System.

This module provides a comprehensive infrastructure and process management system
that consolidates all infrastructure, process, and orchestration functionality
into a single, cohesive system.

Key Features:
- Unified service lifecycle management
- Infrastructure resource provisioning
- Process orchestration and monitoring
- Port allocation and conflict resolution
- Health checking and auto-recovery
- Multi-tenant resource management
- Cost optimization and resource pooling

This is the CANONICAL infrastructure system. All other infrastructure
and process management components should be deprecated in favor of this
unified system.

Usage:
    from pheno.shared.infrastructure import InfrastructureManager, ServiceConfig

    # Initialize infrastructure manager
    infra = InfrastructureManager()

    # Define services
    services = [
        ServiceConfig("api", "python -m api", port=8000),
        ServiceConfig("worker", "python -m worker", depends_on=["api"])
    ]

    # Start infrastructure
    await infra.start_services(services)
    await infra.monitor()
"""

from .allocation import PortAllocator, ResourceAllocator
from .core import InfrastructureManager, ResourceConfig, ServiceConfig
from .monitoring import HealthMonitor, MetricsCollector
from .orchestrator import OrchestrationConfig, ServiceOrchestrator
from .processes import ProcessConfig, ProcessManager
from .resources import ResourceManager, ResourceProvider

__all__ = [
    # Monitoring
    "HealthMonitor",
    # Core infrastructure
    "InfrastructureManager",
    "MetricsCollector",
    "OrchestrationConfig",
    # Allocation
    "PortAllocator",
    "ProcessConfig",
    # Process management
    "ProcessManager",
    "ResourceAllocator",
    "ResourceConfig",
    # Resource management
    "ResourceManager",
    "ResourceProvider",
    "ServiceConfig",
    # Orchestration
    "ServiceOrchestrator",
]
