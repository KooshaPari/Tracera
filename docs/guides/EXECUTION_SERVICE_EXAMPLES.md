# ExecutionService Usage Examples

## Basic Usage (Native Default)

### Simplest Case
```python
from tracertm.services.execution import ExecutionService

# Initialize with native orchestrator (default)
service = ExecutionService(session)

# Create execution
execution = await service.create(
    project_id="proj-123",
    execution_type="test",
    trigger_source="manual"
)

# Start execution (uses native subprocess by default)
success = await service.start(execution.id)
if success:
    print("Execution started in native workspace")

# Complete execution
result = await service.complete(execution.id)
print(f"Execution status: {result.status}")
```

## Advanced: Native Execution with Workspace Access

### Run Commands Directly
```python
service = ExecutionService(session)

# Start execution
exec_id = "exec-001"
await service.create(...)
await service.start(exec_id)

# Access workspace directly
orchestrator = service.orchestrator()
workspace_path = orchestrator.get_workspace_path(exec_id)

# Run command in workspace
return_code, stdout, stderr = await orchestrator.run_command(
    exec_id,
    ["npm", "test"],
    timeout=300
)

# Copy results from workspace
await orchestrator.copy_from(exec_id, "results.json", "/artifacts/results.json")

# Complete execution
await service.complete(exec_id)
```

### With File Mounting
```python
# Mount source directory into workspace
await service.start(
    exec_id,
    mount_source="/path/to/project"
)

orchestrator = service.orchestrator()

# List workspace contents
workspace = orchestrator.get_workspace_path(exec_id)
files = list(workspace.iterdir())

# Run tests in mounted directory
return_code, stdout, stderr = await orchestrator.run_command(
    exec_id,
    ["npm", "test"],
    timeout=300
)
```

### Background Process
```python
orchestrator = service.orchestrator()

# Create workspace
workspace_id = await orchestrator.create_workspace(
    handle_id="long-running-001",
    env={"LOG_LEVEL": "debug"}
)

# Start long-running process
await orchestrator.start_background(
    workspace_id,
    ["python", "server.py"],
    timeout=3600  # 1 hour max
)

# Do other work...

# Stop when done
await orchestrator.stop(workspace_id)
await orchestrator.cleanup(workspace_id)
```

### Resource Limits
```python
# Create config with resource limits
await service.upsert_config(
    "proj-123",
    resource_limits={
        "cpu_seconds": 60,
        "memory_mb": 512
    }
)

# Start execution - limits are applied
await service.start(exec_id)

# Orchestrator receives limits via environment variables
orchestrator = service.orchestrator()
handle = orchestrator._get_handle(exec_id)
print(handle.env)  # {'CPU_SECONDS': '60', 'MEMORY_MB': '512'}
```

## Docker Usage (Optional)

### Docker as Fallback
```python
from tracertm.services.execution.docker_orchestrator import DockerOrchestrator

# Initialize with Docker orchestrator
docker_orch = DockerOrchestrator()
service = ExecutionService(session, docker_orchestrator=docker_orch)

# Start with Docker
success = await service.start(
    exec_id,
    mount_source="/path/to/project",
    use_docker=True
)

if success:
    print("Execution started in Docker container")
```

### Conditional Docker Usage
```python
def use_docker() -> bool:
    # Check if Docker is available
    return subprocess.run(["docker", "info"], capture_output=True).returncode == 0

service = ExecutionService(session, docker_orchestrator=DockerOrchestrator())

# Auto-select based on availability
success = await service.start(exec_id, use_docker=use_docker())
```

### Custom Docker Image
```python
# Set Docker image in project config
await service.upsert_config(
    "proj-123",
    docker_image="node:20-bullseye",
    environment_vars={
        "NODE_ENV": "test",
        "CI": "true"
    }
)

# Start with Docker
await service.start(exec_id, use_docker=True)
await service.complete(exec_id, use_docker=True)
```

### Direct Docker Access
```python
docker = service.docker()
if docker and await docker.is_available():
    # Direct access to Docker orchestrator
    container_id = await docker.create_and_start(
        image="node:20",
        project_id="proj-123",
        execution_id="exec-001",
        command=["npm", "test"]
    )

    # Later...
    await docker.stop(container_id, timeout=15)
```

## Artifact Handling

### Store Execution Artifacts
```python
exec_id = "exec-001"

# Run tests and capture artifacts
await service.start(exec_id)
orchestrator = service.orchestrator()

# Run tests
await orchestrator.run_command(exec_id, ["npm", "test"])

# Store artifacts
await service.store_artifact(
    exec_id,
    source_path=f"{orchestrator.get_workspace_path(exec_id)}/coverage.json",
    artifact_type="coverage_report"
)

await service.store_artifact(
    exec_id,
    source_path=f"{orchestrator.get_workspace_path(exec_id)}/results.json",
    artifact_type="test_results"
)

# Complete and retrieve artifacts
await service.complete(exec_id)

artifacts = await service.list_artifacts(exec_id)
for artifact in artifacts:
    print(f"{artifact.artifact_type}: {artifact.file_path}")
```

## Error Handling

### Graceful Degradation
```python
try:
    # Try native execution first
    success = await service.start(exec_id)
    if not success:
        print("Native execution unavailable, trying Docker...")

        # Fallback to Docker
        docker = service.docker()
        if docker:
            success = await service.start(exec_id, use_docker=True)

except NativeOrchestratorError as e:
    print(f"Native orchestrator error: {e}")
    # Fallback logic

except DockerOrchestratorError as e:
    print(f"Docker orchestrator error: {e}")
    # Alternative handling
```

### Cleanup on Failure
```python
exec_id = "exec-001"

try:
    await service.start(exec_id)

    orchestrator = service.orchestrator()
    return_code, stdout, stderr = await orchestrator.run_command(
        exec_id,
        ["npm", "test"]
    )

    await service.complete(
        exec_id,
        exit_code=return_code,
        output_summary=f"Tests: {stdout}"
    )

except Exception as e:
    # Ensure cleanup happens
    execution = await service.get(exec_id)
    if execution:
        await service.complete(
            exec_id,
            exit_code=1,
            error_message=str(e)
        )
    raise
```

## Testing

### Mock Native Orchestrator
```python
from unittest.mock import AsyncMock, MagicMock
from tracertm.services.execution.native_orchestrator import NativeOrchestrator

mock_orchestrator = AsyncMock(spec=NativeOrchestrator)
mock_orchestrator.is_available = AsyncMock(return_value=True)
mock_orchestrator.create_workspace = AsyncMock(return_value="exec-001")
mock_orchestrator.cleanup = AsyncMock()

service = ExecutionService(
    session,
    orchestrator=mock_orchestrator
)

# Now tests use mock orchestrator
await service.start("exec-001")
mock_orchestrator.create_workspace.assert_called_once()
```

### Integration Test
```python
import tempfile
from pathlib import Path

# Use temporary directory for testing
with tempfile.TemporaryDirectory() as tmpdir:
    orchestrator = NativeOrchestrator(base_workspace=tmpdir)
    service = ExecutionService(session, orchestrator=orchestrator)

    # Create test script
    test_file = Path(tmpdir) / "test.sh"
    test_file.write_text("#!/bin/bash\necho 'test passed'\nexit 0")
    test_file.chmod(0o755)

    # Run full lifecycle
    execution = await service.create("proj-1", "test", "manual")
    await service.start(execution.id)

    result = await orchestrator.run_command(
        execution.id,
        [str(test_file)]
    )

    assert result[0] == 0  # exit code
    assert "test passed" in result[1]  # stdout
```

## Configuration Examples

### Project-Specific Config
```python
# Set native execution limits
await service.upsert_config(
    "proj-123",
    resource_limits={
        "cpu_seconds": 30,
        "memory_mb": 256
    },
    environment_vars={
        "NODE_ENV": "test",
        "CI": "true",
        "TIMEOUT": "30000"
    }
)

# Set Docker config
await service.upsert_config(
    "proj-456",
    docker_image="python:3.11-slim",
    environment_vars={
        "PYTHONUNBUFFERED": "1"
    },
    working_directory="/app",
    execution_timeout=600
)
```

### Retrieve and Update Config
```python
# Get current config
config = await service.get_config("proj-123")

if config:
    print(f"Docker image: {config.docker_image}")
    print(f"Timeout: {config.execution_timeout}")
    print(f"Environment: {config.environment_vars}")
else:
    # Create default config
    config = await service.upsert_config("proj-123")
```
