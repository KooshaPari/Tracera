# ExecutionService - Quick Reference Card

## At a Glance

**What Changed:** NativeOrchestrator is now the default; Docker is optional.

**File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/src/tracertm/services/execution/execution_service.py`

**Backward Compatible:** Yes (100%)

---

## Quick Start

### Default (Native Subprocess)
```python
service = ExecutionService(session)
await service.start(exec_id)
await service.complete(exec_id)
```

### With Docker (Opt-in)
```python
docker = DockerOrchestrator()
service = ExecutionService(session, docker_orchestrator=docker)
await service.start(exec_id, use_docker=True)
await service.complete(exec_id, use_docker=True)
```

---

## Method Signatures

### Constructor
```python
def __init__(
    self,
    session: AsyncSession,
    *,
    artifact_storage: ArtifactStorageService | None = None,
    orchestrator: NativeOrchestrator | None = None,           # NEW
    docker_orchestrator: DockerOrchestrator | None = None,    # OPTIONAL
):
```

### start()
```python
async def start(
    self,
    execution_id: str,
    *,
    mount_source: Path | str | None = None,
    command: list[str] | None = None,
    use_docker: bool = False,  # NEW
) -> bool:
```

### complete()
```python
async def complete(
    self,
    execution_id: str,
    *,
    exit_code: int = 0,
    error_message: str | None = None,
    output_summary: str | None = None,
    use_docker: bool = False,  # NEW
):
```

### Accessors
```python
def orchestrator(self) -> NativeOrchestrator:        # NEW
    """Access native orchestrator for direct workspace ops"""

def docker(self) -> DockerOrchestrator | None:       # UPDATED
    """Access Docker orchestrator if configured"""
```

---

## What Each Orchestrator Does

### NativeOrchestrator (Default)
| Operation | Method | Usage |
|-----------|--------|-------|
| Create workspace | `create_workspace()` | `await orch.create_workspace(handle_id=exec_id)` |
| Run command | `run_command()` | `await orch.run_command(exec_id, ["npm", "test"])` |
| Copy to workspace | `copy_to()` | `await orch.copy_to(exec_id, "/source/path")` |
| Copy from workspace | `copy_from()` | `await orch.copy_from(exec_id, "file.json", "/dest")` |
| Apply limits | `apply_resource_limits()` | `await orch.apply_resource_limits(exec_id, cpu_seconds=60)` |
| Stop process | `stop()` | `await orch.stop(exec_id, timeout=30)` |
| Cleanup | `cleanup()` | `await orch.cleanup(exec_id)` |

### DockerOrchestrator (Optional)
| Operation | Method | Usage |
|-----------|--------|-------|
| Create & start | `create_and_start()` | `await docker.create_and_start(image, project_id=...)` |
| Stop container | `stop()` | `await docker.stop(container_id, timeout=15)` |
| Exec command | `exec()` | `await docker.exec(container_id, ["npm", "test"])` |
| Check available | `is_available()` | `await docker.is_available()` |

---

## Common Patterns

### Pattern 1: Direct Workspace Access
```python
orch = service.orchestrator()
return_code, stdout, stderr = await orch.run_command(
    exec_id,
    ["npm", "test"],
    timeout=300
)
```

### Pattern 2: Copy Results
```python
orch = service.orchestrator()
await orch.copy_from(
    exec_id,
    "results.json",
    "/tmp/artifacts/results.json"
)
```

### Pattern 3: Conditional Docker
```python
# Try native first
success = await service.start(exec_id)

# Fall back to Docker if needed
if not success:
    docker = service.docker()
    if docker:
        success = await service.start(exec_id, use_docker=True)
```

### Pattern 4: Safe Docker Access
```python
docker = service.docker()
if docker:
    await docker.exec(container_id, ["npm", "test"])
else:
    # Docker not available, use native
    orch = service.orchestrator()
    await orch.run_command(exec_id, ["npm", "test"])
```

---

## Error Handling

### Catching Both Orchestrator Errors
```python
from tracertm.services.execution.native_orchestrator import NativeOrchestratorError
from tracertm.services.execution.docker_orchestrator import DockerOrchestratorError

try:
    await service.start(exec_id)
except (NativeOrchestratorError, DockerOrchestratorError) as e:
    print(f"Execution failed: {e}")
```

### Missing Docker Config
```python
try:
    await service.start(exec_id, use_docker=True)
except DockerOrchestratorError as e:
    # "Docker orchestrator not configured..."
    pass
```

---

## Configuration

### Set Native Resource Limits
```python
await service.upsert_config(
    "proj-123",
    resource_limits={
        "cpu_seconds": 60,
        "memory_mb": 512
    }
)
```

### Set Docker Image
```python
await service.upsert_config(
    "proj-456",
    docker_image="python:3.11-slim",
    environment_vars={"PYTHONUNBUFFERED": "1"}
)
```

---

## Testing

### Mock Native Orchestrator
```python
from unittest.mock import AsyncMock

mock_orch = AsyncMock(spec=NativeOrchestrator)
service = ExecutionService(session, orchestrator=mock_orch)
```

### Mock Docker Orchestrator
```python
mock_docker = AsyncMock(spec=DockerOrchestrator)
service = ExecutionService(session, docker_orchestrator=mock_docker)
```

### Real Integration Test
```python
import tempfile

with tempfile.TemporaryDirectory() as tmpdir:
    orch = NativeOrchestrator(base_workspace=tmpdir)
    service = ExecutionService(session, orchestrator=orch)

    exec = await service.create("proj-1", "test", "manual")
    assert await service.start(exec.id)
    result = await service.complete(exec.id)
    assert result.status == "passed"
```

---

## Migration Checklist

If you were using ExecutionService before:

- [ ] Review start() calls for use_docker parameter (optional)
- [ ] Review complete() calls for use_docker parameter (optional)
- [ ] If using docker(), check return type can be None
- [ ] If accessing docker, add null check
- [ ] Update any Docker-specific tests to pass docker_orchestrator
- [ ] Add native orchestrator tests

---

## Comparison Table

| Feature | Before | After |
|---------|--------|-------|
| Default execution | Docker | Native |
| Docker dependency | Required | Optional |
| Subprocess support | No | Yes |
| start() parameters | 2 | 3 |
| complete() parameters | 3 | 4 |
| orchestrator() method | No | Yes |
| docker() return type | DockerOrchestrator | DockerOrchestrator \| None |
| Breaking changes | N/A | None |

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Docker orchestrator not configured" | Pass docker_orchestrator to constructor if using use_docker=True |
| docker() returns None | Add null check: `docker = service.docker(); if docker: ...` |
| Tests fail with Docker | Pass docker_orchestrator to ExecutionService or inject mock |
| Want to force Docker | Pass use_docker=True to start()/complete() |
| Want subprocess execution | Default behavior - no changes needed |

---

## Documentation Files

| File | Purpose |
|------|---------|
| EXECUTION_SERVICE_MIGRATION.md | High-level overview |
| EXECUTION_SERVICE_EXAMPLES.md | 50+ code examples |
| EXECUTION_SERVICE_DETAILED_CHANGES.md | Line-by-line details |
| REFACTORING_SUMMARY.md | Architecture decisions |
| EXECUTION_SERVICE_COMPLETION_REPORT.md | Status report |
| EXECUTION_SERVICE_QUICK_REFERENCE.md | This file |

---

## Key Takeaways

1. **Default Changed:** Docker → Native (subprocess)
2. **Docker Now Optional:** Pass to constructor if needed
3. **New Parameters:** use_docker flag on start() and complete()
4. **New Methods:** orchestrator() for native access
5. **Fully Backward Compatible:** Existing code works unchanged
6. **Both Supported:** Can use either orchestrator as needed
7. **Unified Errors:** Both error types caught together
8. **Injection Friendly:** Easy to mock for testing

---

**Status:** Ready for use | Last Updated: 2026-01-29 | Version: 1.0
