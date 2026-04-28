# Infrastructure Architectural Mapping

**Date**: 2025-01-27
**Phase**: 4.1 Architectural Mapping
**Status**: Complete

## Overview

This document maps the responsibilities across service_manager, resource_manager, process/*, and other infrastructure components to identify consolidation opportunities and design a unified management system.

## Current Architecture

### 1. Service Management

#### 1.1 ServiceManager (`src/pheno/infra/service_manager/`)
- **File**: `src/pheno/infra/service_manager/manager.py`
- **Components**:
  - `ServiceManager`: Main service management class
  - `BaseServiceManager`: Base class with core functionality
  - `ProcessMixin`: Process management functionality
  - `HealthMixin`: Health checking functionality
  - `ResourcesMixin`: Resource management functionality
  - `MonitorMixin`: Monitoring functionality
  - `FallbackMixin`: Fallback server functionality
- **Responsibilities**:
  - Service lifecycle management (start/stop/restart)
  - Process monitoring and management
  - Health checking and auto-recovery
  - Resource allocation and management
  - File watching and change detection
  - Fallback server management
  - Log capture and monitoring
- **Dependencies**:
  - KInfra for core functionality
  - Rich for console output
  - asyncio for async operations

#### 1.2 Service Orchestrator (`src/pheno/infra/orchestrator.py`)
- **File**: `src/pheno/infra/orchestrator.py`
- **Components**:
  - `ServiceOrchestrator`: Service orchestration and coordination
- **Responsibilities**:
  - Service dependency management
  - Service startup sequencing
  - Service coordination and communication
  - Service discovery and registration
- **Dependencies**:
  - ServiceManager for service management
  - Process management for execution

### 2. Resource Management

#### 2.1 Resource Manager (`src/pheno/infra/resource_manager.py`)
- **File**: `src/pheno/infra/resource_manager.py`
- **Components**:
  - `ResourceManager`: Main resource management class
- **Responsibilities**:
  - Resource allocation and deallocation
  - Resource monitoring and health checking
  - Resource conflict resolution
  - Resource lifecycle management
- **Dependencies**:
  - ServiceManager for service integration
  - Health monitoring for resource health

#### 2.2 Resource Budget Manager (`src/pheno/resources/manager.py`)
- **File**: `src/pheno/resources/manager.py`
- **Components**:
  - `ResourceBudgetManager`: Resource budgeting and allocation
  - `ResourceAllocator`: Resource allocation logic
  - `ResourceTracker`: Resource usage tracking
- **Responsibilities**:
  - Resource budgeting and cost management
  - Resource allocation optimization
  - Resource usage tracking and reporting
  - Resource quota management
- **Dependencies**:
  - Resource definitions and providers
  - Cost optimization algorithms

### 3. Process Management

#### 3.1 Process Manager (`src/pheno/process/components/process_manager.py`)
- **File**: `src/pheno/process/components/process_manager.py`
- **Components**:
  - `ProcessManager`: Main process management class
  - `ProcessMonitor`: Process monitoring functionality
  - `ProcessFactory`: Process creation and management
- **Responsibilities**:
  - Process creation and management
  - Process monitoring and health checking
  - Process lifecycle management
  - Process communication and coordination
- **Dependencies**:
  - Process base classes and interfaces
  - Health monitoring for process health

#### 3.2 Process Services (`src/pheno/process/services/`)
- **Files**:
  - `go.py` - Go service management
  - `launcher.py` - Service launcher
  - `nextjs.py` - Next.js service management
- **Responsibilities**:
  - Language-specific service management
  - Service launcher functionality
  - Service-specific configuration
- **Dependencies**:
  - ProcessManager for process management
  - Service configuration

### 4. Infrastructure Management

#### 4.1 Infrastructure Manager (`src/pheno/shared/infrastructure/`)
- **File**: `src/pheno/shared/infrastructure/core.py`
- **Components**:
  - `InfrastructureManager`: Unified infrastructure management
  - `ServiceConfig`: Service configuration
  - `ResourceConfig`: Resource configuration
- **Responsibilities**:
  - Unified infrastructure and process management
  - Service lifecycle management
  - Infrastructure resource provisioning
  - Process orchestration and monitoring
  - Port allocation and conflict resolution
  - Health checking and auto-recovery
  - Multi-tenant resource management
- **Dependencies**:
  - Service orchestration
  - Resource management
  - Process management
  - Monitoring systems

#### 4.2 Control Center Engine (`src/pheno/infra/control_center/engine.py`)
- **File**: `src/pheno/infra/control_center/engine.py`
- **Components**:
  - `ControlCenterEngine`: Control center management
- **Responsibilities**:
  - Control center orchestration
  - Service coordination
  - Resource management
  - Monitoring and health checking
- **Dependencies**:
  - ServiceManager for service management
  - ResourceManager for resource management
  - Monitoring systems

### 5. MCP Management

#### 5.1 MCP Manager (`src/pheno/mcp/manager.py`)
- **File**: `src/pheno/mcp/manager.py`
- **Components**:
  - `MCPManager`: MCP server management
- **Responsibilities**:
  - MCP server lifecycle management
  - MCP server monitoring
  - MCP server configuration
  - MCP server communication
- **Dependencies**:
  - MCP server implementations
  - Service management for MCP services

### 6. Workflow Orchestration

#### 6.1 Agent Manager (`src/pheno/workflow/orchestration/agents/manager.py`)
- **File**: `src/pheno/workflow/orchestration/agents/manager.py`
- **Components**:
  - `AgentManager`: Agent orchestration and management
- **Responsibilities**:
  - Agent lifecycle management
  - Agent coordination and communication
  - Agent monitoring and health checking
  - Agent resource management
- **Dependencies**:
  - Agent implementations
  - Service management for agent services

## Duplication Analysis

### High Duplication Areas

1. **Service Lifecycle Management** (4 implementations)
   - `ServiceManager` - Main service management
   - `ServiceOrchestrator` - Service orchestration
   - `InfrastructureManager` - Unified infrastructure management
   - `ControlCenterEngine` - Control center management

2. **Process Management** (3 implementations)
   - `ProcessManager` - Process management
   - `ServiceManager` - Service process management
   - `InfrastructureManager` - Infrastructure process management

3. **Resource Management** (3 implementations)
   - `ResourceManager` - Resource management
   - `ResourceBudgetManager` - Resource budgeting
   - `InfrastructureManager` - Infrastructure resource management

4. **Health Monitoring** (4 implementations)
   - `HealthMixin` - Service health monitoring
   - `ProcessMonitor` - Process health monitoring
   - `InfrastructureManager` - Infrastructure health monitoring
   - `ControlCenterEngine` - Control center health monitoring

5. **Port Allocation** (2 implementations)
   - `PortAllocator` - Port allocation
   - `InfrastructureManager` - Infrastructure port allocation

### Common Patterns

1. **Lifecycle Management** (6 patterns)
   - Start/stop/restart operations
   - Health checking
   - Auto-recovery
   - Dependency management

2. **Resource Allocation** (4 patterns)
   - Port allocation
   - Resource allocation
   - Conflict resolution
   - Resource monitoring

3. **Monitoring** (5 patterns)
   - Health monitoring
   - Process monitoring
   - Resource monitoring
   - Metrics collection
   - Log capture

4. **Configuration Management** (4 patterns)
   - Service configuration
   - Resource configuration
   - Process configuration
   - Infrastructure configuration

## Consolidation Opportunities

### Immediate Consolidation (High Impact)

1. **Service Lifecycle Unification**
   - Consolidate all service lifecycle management
   - Create unified service interface
   - Standardize service operations

2. **Process Management Unification**
   - Consolidate process management functionality
   - Create unified process interface
   - Standardize process operations

3. **Resource Management Unification**
   - Consolidate resource management functionality
   - Create unified resource interface
   - Standardize resource operations

4. **Health Monitoring Unification**
   - Consolidate health monitoring functionality
   - Create unified health interface
   - Standardize health operations

### Medium-term Consolidation

1. **Configuration Management Unification**
   - Consolidate configuration management
   - Create unified configuration interface
   - Standardize configuration operations

2. **Monitoring and Metrics Unification**
   - Consolidate monitoring functionality
   - Create unified monitoring interface
   - Standardize monitoring operations

### Long-term Consolidation

1. **Orchestration Unification**
   - Consolidate orchestration functionality
   - Create unified orchestration interface
   - Standardize orchestration operations

2. **Multi-tenant Management**
   - Consolidate multi-tenant functionality
   - Create unified tenant interface
   - Standardize tenant operations

## Unified Manager Design

### Core Components

1. **UnifiedInfrastructureManager**
   - Central management system
   - Plugin-based architecture
   - Lifecycle management
   - Resource management
   - Process management
   - Health monitoring
   - Orchestration

2. **ServicePlugin**
   - Service lifecycle management
   - Service monitoring
   - Service configuration
   - Service communication

3. **ResourcePlugin**
   - Resource allocation
   - Resource monitoring
   - Resource configuration
   - Resource optimization

4. **ProcessPlugin**
   - Process management
   - Process monitoring
   - Process configuration
   - Process communication

5. **HealthPlugin**
   - Health checking
   - Health monitoring
   - Health reporting
   - Health recovery

6. **OrchestrationPlugin**
   - Service orchestration
   - Process orchestration
   - Resource orchestration
   - Workflow orchestration

### Plugin Architecture

```python
class InfrastructurePlugin(ABC):
    """Base class for infrastructure plugins."""

    @abstractmethod
    async def initialize(self, manager: UnifiedInfrastructureManager) -> None:
        """Initialize the plugin."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the plugin."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the plugin."""
        pass

    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Perform health check."""
        pass
```

### Unified Interface

```python
class UnifiedInfrastructureManager:
    """Unified infrastructure and process management system."""

    def __init__(self, config: InfrastructureConfig):
        self.config = config
        self.plugins: Dict[str, InfrastructurePlugin] = {}
        self.services: Dict[str, Service] = {}
        self.resources: Dict[str, Resource] = {}
        self.processes: Dict[str, Process] = {}

    async def start(self) -> None:
        """Start the infrastructure manager."""
        pass

    async def stop(self) -> None:
        """Stop the infrastructure manager."""
        pass

    async def add_service(self, service: Service) -> None:
        """Add a service."""
        pass

    async def remove_service(self, service_id: str) -> None:
        """Remove a service."""
        pass

    async def add_resource(self, resource: Resource) -> None:
        """Add a resource."""
        pass

    async def remove_resource(self, resource_id: str) -> None:
        """Remove a resource."""
        pass

    async def health_check(self) -> HealthStatus:
        """Perform health check."""
        pass
```

## Migration Strategy

### Phase 1: Core Unification
1. Create UnifiedInfrastructureManager
2. Implement plugin architecture
3. Create base plugin interfaces
4. Add core functionality

### Phase 2: Plugin Migration
1. Migrate ServiceManager to ServicePlugin
2. Migrate ResourceManager to ResourcePlugin
3. Migrate ProcessManager to ProcessPlugin
4. Migrate HealthMixin to HealthPlugin

### Phase 3: Integration
1. Integrate with existing systems
2. Update service registration
3. Migrate configuration
4. Test integration

### Phase 4: Cleanup
1. Remove duplicate implementations
2. Update documentation
3. Add comprehensive tests
4. Optimize performance

## Estimated Savings

- **Lines of Code**: ~4,000 LOC reduction
- **Files**: 15+ files can be consolidated
- **Complexity**: Significant reduction in maintenance burden
- **Consistency**: Unified patterns across all managers

## Success Metrics

### 1. Code Reduction
- **Target**: 4,000+ LOC reduction
- **Current**: 0 LOC reduced
- **Progress**: 0%

### 2. Manager Consolidation
- **Target**: 8+ managers → unified system
- **Current**: 8+ managers
- **Progress**: 0%

### 3. Performance Impact
- **Target**: No performance degradation
- **Current**: Not measured
- **Progress**: 0%

### 4. Breaking Changes
- **Target**: Zero breaking changes
- **Current**: Zero breaking changes
- **Progress**: 100%

## Timeline

### Week 1: Core Unification
- Design unified manager system
- Implement plugin architecture
- Create base interfaces
- Add core functionality

### Week 2: Plugin Migration
- Migrate existing managers
- Implement plugin interfaces
- Test plugin functionality
- Verify integration

### Week 3: Integration
- Integrate with existing systems
- Update service registration
- Migrate configuration
- Test integration

### Week 4: Cleanup and Documentation
- Remove duplicate code
- Optimize performance
- Add comprehensive tests
- Update documentation

## Risk Mitigation

### 1. Breaking Changes
- **Risk**: Manager interfaces change
- **Mitigation**: Maintain backward compatibility, gradual migration

### 2. Performance Impact
- **Risk**: System performance degrades
- **Mitigation**: Performance testing, optimization

### 3. Integration Issues
- **Risk**: System integration breaks
- **Mitigation**: Comprehensive testing, rollback capability

### 4. Complexity Increase
- **Risk**: System becomes more complex
- **Mitigation**: Clear documentation, simple interfaces

## Conclusion

The infrastructure architectural mapping reveals significant opportunities for consolidation. The unified manager system will provide:

1. **Consistency**: Unified patterns across all managers
2. **Maintainability**: Reduced duplication and complexity
3. **Extensibility**: Easy addition of new functionality
4. **Performance**: Optimized resource management
5. **Developer Experience**: Simplified infrastructure management

The migration strategy ensures zero breaking changes while achieving significant code reduction and improved maintainability.
