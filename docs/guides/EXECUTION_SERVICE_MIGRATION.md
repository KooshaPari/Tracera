# ExecutionService Migration: Docker to Native Default

## Overview
The `ExecutionService` has been refactored to use `NativeOrchestrator` (subprocess execution) as the default orchestrator, with `DockerOrchestrator` as an optional fallback.

## Changes Made

### 1. Imports
**Before:**
```python
from tracertm.services.execution.docker_orchestrator import (
    DockerOrchestrator,
    DockerOrchestratorError,
)
```

**After:**
```python
from tracertm.services.execution.native_orchestrator import (
    NativeOrchestrator,
    NativeOrchestratorError,
)
from tracertm.services.execution.docker_orchestrator import (
    DockerOrchestrator,
    DockerOrchestratorError,
)
```

### 2. Constructor (`__init__`)
**Before:**
```python
def __init__(
    self,
    session: AsyncSession,
    *,
    artifact_storage: ArtifactStorageService | None = None,
    docker_orchestrator: DockerOrchestrator | None = None,
):
    # ...
    self._docker = docker_orchestrator or DockerOrchestrator()
```

**After:**
```python
def __init__(
    self,
    session: AsyncSession,
    *,
    artifact_storage: ArtifactStorageService | None = None,
    orchestrator: NativeOrchestrator | None = None,
    docker_orchestrator: DockerOrchestrator | None = None,
):
    # ...
    self._orchestrator = orchestrator or NativeOrchestrator()
    self._docker = docker_orchestrator  # Optional, no default
```

**Key Points:**
- `NativeOrchestrator` is now instantiated by default
- `DockerOrchestrator` is optional (no default instance)
- Both can be injected for testing/customization

### 3. `start()` Method
**Changes:**
- Added `use_docker: bool = False` parameter
- Split implementation into `_start_with_native()` and `_start_with_docker()`
- Updated docstring to reflect native default

**Usage:**
```python
# Default: native subprocess execution
await service.start(execution_id, mount_source="/path")

# Optional: Docker container execution
await service.start(execution_id, mount_source="/path", use_docker=True)
```

**Native Workspace Creation:**
```python
workspace_id = await self._orchestrator.create_workspace(
    handle_id=execution_id,
    env=config.environment_vars if config else {},
)
```

**Docker Container Creation (unchanged):**
```python
container_id = await self._docker.create_and_start(...)
```

### 4. `complete()` Method
**Changes:**
- Added `use_docker: bool = False` parameter
- Cleanup adapted based on execution type

**Before:**
```python
if execution.container_id:
    try:
        await self._docker.stop(execution.container_id, timeout=15)
    except DockerOrchestratorError:
        pass
```

**After:**
```python
if execution.container_id:
    try:
        if use_docker:
            if self._docker:
                await self._docker.stop(execution.container_id, timeout=15)
        else:
            await self._orchestrator.cleanup(execution.container_id)
    except (NativeOrchestratorError, DockerOrchestratorError):
        pass
```

### 5. Accessor Methods

**Before:**
```python
def docker(self) -> DockerOrchestrator:
    """Return the Docker orchestrator (e.g. for exec/copy)."""
    return self._docker
```

**After:**
```python
def orchestrator(self) -> NativeOrchestrator:
    """Return the native orchestrator for direct workspace interaction.

    Use this to directly run commands or copy files in the workspace.
    """
    return self._orchestrator

def docker(self) -> DockerOrchestrator | None:
    """Return the Docker orchestrator if configured (e.g. for exec/copy).

    Returns None if Docker orchestrator was not provided during initialization.
    """
    return self._docker
```

## Migration Guide

### For Existing Code

#### 1. Default Behavior (No Changes Required)
```python
# Code works as-is, now uses NativeOrchestrator
service = ExecutionService(session)
await service.start(execution_id)
await service.complete(execution_id)
```

#### 2. To Explicitly Use Docker
```python
# Inject Docker orchestrator
docker_orch = DockerOrchestrator()
service = ExecutionService(session, docker_orchestrator=docker_orch)

# Use Docker for execution
await service.start(execution_id, use_docker=True)
await service.complete(execution_id, use_docker=True)
```

#### 3. Direct Orchestrator Access
```python
# Access native orchestrator
native = service.orchestrator()
await native.run_command(handle_id, "npm test")
await native.copy_from(handle_id, "results.json", "/tmp/results.json")

# Access Docker orchestrator (if configured)
docker = service.docker()
if docker:
    await docker.exec(container_id, ["npm", "test"])
```

## Benefits

1. **No Docker Dependency**: Subprocess execution doesn't require Docker daemon
2. **Simpler Default**: Most use cases work without Docker setup
3. **Flexible**: Easy to opt-in to Docker when needed
4. **Agnostic**: Service handles both execution models transparently
5. **Testable**: Both orchestrators can be injected for testing

## Interface Mapping

| NativeOrchestrator | DockerOrchestrator |
|---|---|
| `create_workspace()` | `create_and_start()` |
| `run_command()` | `exec()` (custom) |
| `start_background()` | N/A |
| `stop()` | `stop()` |
| `cleanup()` | `stop()` |
| `copy_to()` | `copy()` |
| `copy_from()` | `copy()` |
| `is_available()` | `is_available()` |
| `apply_resource_limits()` | resource_limits param |

## Error Handling

Both orchestrators raise their respective errors that are caught together:

```python
except (NativeOrchestratorError, DockerOrchestratorError) as e:
    # Handle either type
```

## Notes

- **Resource Limits**: Native execution uses environment variables; Docker uses native limits
- **Workspace ID**: For native, this is the handle_id; for Docker, this is container_id
- **Container Image**: Native execution reports "native-subprocess"; Docker reports actual image
- **Backward Compatibility**: All existing code continues to work; Docker must be explicitly requested
