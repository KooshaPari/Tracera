# Docker SDK for Python - Research Index

Complete research on Docker SDK, container orchestration, security, and async patterns.

---

## Documents Overview

### 1. **DOCKER_SDK_RESEARCH.md** (Main Research Document)
**Comprehensive technical deep-dive with implementation details**

- **Section 1**: Docker SDK (docker-py) fundamentals
  - Package information and architecture
  - Container lifecycle management (create, run, stop, remove)
  - Container execution with command handling

- **Section 2**: Security Best Practices
  - Non-root user execution
  - Linux capability management
  - Read-only filesystem and volume mounting
  - Seccomp profile configuration

- **Section 3**: Resource Constraints and Limits
  - CPU and memory limit configuration
  - Example configurations for different workloads

- **Section 4**: Async Container Orchestration with aiodocker
  - Async container manager implementation
  - Concurrent container operations

- **Section 5**: Cleanup Strategies
  - Container cleanup patterns
  - Orphaned resource tracking and cleanup

- **Section 6**: Timeout and Graceful Shutdown
  - Signal handling in containers
  - Graceful shutdown implementation
  - Container timeout management

- **Section 7**: Docker-in-Docker Security
  - Security risks of socket mounting
  - Safe alternatives (Kaniko, rootless Docker)

- **Section 8**: CI/CD Integration Patterns
  - Registry authentication
  - Image building and pushing

**Best for**: Understanding concepts, learning patterns, detailed implementation reference

**File**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/DOCKER_SDK_RESEARCH.md`

---

### 2. **DOCKER_SDK_QUICK_REFERENCE.md** (Quick Reference)
**Quick lookup guide for common operations and patterns**

- Installation instructions
- Quick start examples (sync and async)
- Common operations table
- Container configuration snippets
- Security hardening patterns
- Resource limits quick reference
- Error handling patterns
- Async patterns
- Cleanup patterns
- Timeout management
- Graceful shutdown
- Command execution
- Network configuration
- Image operations
- Common patterns summary
- Performance tips
- Debugging guides

**Best for**: Quick lookups, copy-paste code snippets, refreshing memory

**File**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/DOCKER_SDK_QUICK_REFERENCE.md`

---

### 3. **DOCKER_SDK_ASYNC_EXAMPLES.py** (Runnable Code)
**Production-ready async container management implementation**

- Data models (ContainerStatus, ContainerConfig, ExecutionResult)
- SecureAsyncContainerManager class
  - Secure container creation with hardened defaults
  - Non-root execution, dropped capabilities, read-only filesystem
  - Timeout handling and graceful shutdown
  - Log streaming and retrieval

- AsyncBatchOperationManager class
  - Batch container execution
  - Concurrent operation management
  - Automatic retry with exponential backoff
  - Run-until-success pattern

- GracefulShutdownManager class
  - Signal handling (SIGTERM, SIGINT)
  - Graceful task cancellation

- Complete working examples
  - Simple single container execution
  - Batch multi-container execution
  - Automatic retry pattern
  - Real-time log streaming
  - Timeout handling

- Logging and error handling throughout

**Best for**: Understanding async patterns, copy-paste ready code, learning by example

**File**: `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/DOCKER_SDK_ASYNC_EXAMPLES.py`

---

## Key Topics Covered

### Container Lifecycle Management

**Sync Pattern**:
```python
import docker
client = docker.from_env()
container = client.containers.run('image', 'command', detach=True)
container.stop(timeout=10)
container.remove(v=True)
```

**Async Pattern**:
```python
import aiodocker
docker = aiodocker.Docker()
container = await docker.containers.create_or_replace(config)
await container.start()
await container.stop()
```

---

### Security Best Practices

1. **Non-Root Execution**
   ```python
   user='1000',  # UID, not name
   ```

2. **Dropped Capabilities**
   ```python
   cap_drop=['ALL'],  # Start with nothing
   cap_add=['NET_BIND_SERVICE']  # Add only what's needed
   ```

3. **Read-Only Filesystem**
   ```python
   read_only=True,
   tmpfs={'/tmp': 'size=100m,mode=1777'}
   ```

4. **No Docker Socket**
   ```python
   # WRONG: /var/run/docker.sock mounting
   # RIGHT: Use Kaniko, rootless Docker, or TCP API
   ```

---

### Async Patterns

1. **Concurrent Execution**
   - Semaphore-based concurrency limiting
   - Gather multiple operations
   - Proper timeout and cleanup

2. **Graceful Shutdown**
   - Signal handlers (SIGTERM/SIGINT)
   - Task cancellation
   - Cleanup on shutdown

3. **Error Handling & Retry**
   - Exponential backoff retry
   - Timeout management
   - Result aggregation

---

### Resource Constraints

```python
# Memory: 512 MB hard limit
mem_limit='512m'

# CPU: 0.5 cores (50%)
nano_cpus=int(0.5 * 1e9)

# CPU cores: bind to cores 0,1
cpuset_cpus='0,1'

# I/O: limit read/write operations per second
device_read_iops=1000
device_write_iops=500
```

---

### Cleanup Strategies

1. **Single Container**
   ```python
   container.stop(timeout=10)
   container.remove(v=True)
   ```

2. **All Stopped Containers**
   ```python
   client.containers.prune()
   ```

3. **Orphaned Resources**
   - Dangling volumes: `client.volumes.prune()`
   - Dangling images: `client.images.prune(filters={'dangling': True})`
   - Unused networks: `client.networks.prune()`

---

## Usage Recommendations

### Choose Based on Your Use Case

| Use Case | Document | Language |
|----------|----------|----------|
| Learning concepts | DOCKER_SDK_RESEARCH.md | Markdown |
| Quick lookup | DOCKER_SDK_QUICK_REFERENCE.md | Markdown |
| Implementing features | DOCKER_SDK_ASYNC_EXAMPLES.py | Python |
| Integration | DOCKER_SDK_RESEARCH.md + Examples | Both |

### Reading Path Recommendations

**For Beginners**:
1. Start with DOCKER_SDK_QUICK_REFERENCE.md (overview)
2. Read simple examples from DOCKER_SDK_ASYNC_EXAMPLES.py
3. Reference DOCKER_SDK_RESEARCH.md for detailed patterns

**For Implementation**:
1. Review relevant sections in DOCKER_SDK_RESEARCH.md
2. Check DOCKER_SDK_QUICK_REFERENCE.md for syntax
3. Copy/adapt from DOCKER_SDK_ASYNC_EXAMPLES.py

**For Security Review**:
1. Read Section 2 of DOCKER_SDK_RESEARCH.md
2. Check security patterns in DOCKER_SDK_QUICK_REFERENCE.md
3. Review hardening in SecureAsyncContainerManager

**For Async/Concurrency**:
1. Read Section 4 & 6 of DOCKER_SDK_RESEARCH.md
2. Study AsyncBatchOperationManager in DOCKER_SDK_ASYNC_EXAMPLES.py
3. Reference async patterns in DOCKER_SDK_QUICK_REFERENCE.md

---

## Technology Stack

### Python Packages

- **docker** (v7.1.0+) - Official Docker SDK
- **aiodocker** (v0.25+) - Async Docker SDK
- **asyncio** - Built-in async support
- **signal** - Signal handling

### Key Concepts

- **docker-py**: Synchronous Docker Engine API bindings
- **aiodocker**: Asyncio-based Docker HTTP API wrapper
- **HostConfig**: Container runtime configuration (memory, CPU, security)
- **DockerClient**: High-level client (synchronous)
- **Docker**: aiodocker client class (asynchronous)

---

## Critical Security Points

### Never Do This

```python
# CRITICAL VULNERABILITY: Docker socket mounting
volumes = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}}
# This grants full Docker daemon control to the container
# Equivalent to giving root access to the entire host
```

### Always Do This

```python
# Use secure defaults
user='1000',                           # Non-root
cap_drop=['ALL'],                      # Drop capabilities
read_only=True,                        # Read-only FS
security_opt=['no-new-privileges:true'],
tmpfs={'/tmp': 'size=100m'}           # Writable temp
```

---

## Testing the Examples

### Prerequisites

```bash
# Install dependencies
pip install docker aiodocker

# Or with bun
bun add docker aiodocker
```

### Run Async Examples

```bash
python DOCKER_SDK_ASYNC_EXAMPLES.py
```

This will run:
1. Simple example - single container
2. Batch example - multiple containers
3. Retry example - automatic retry
4. Streaming example - log streaming
5. Timeout example - timeout handling

### Expected Output

```
2026-01-28 10:30:45,123 - __main__ - INFO - === Simple Example ===
2026-01-28 10:30:45,234 - __main__ - INFO - Created container: abc1234...
2026-01-28 10:30:45,345 - __main__ - INFO - Started container: abc1234...
2026-01-28 10:30:46,456 - __main__ - INFO - Container abc1234... completed...
2026-01-28 10:30:46,567 - __main__ - INFO - Exit code: 0
2026-01-28 10:30:46,678 - __main__ - INFO - Output:
Hello from Docker
```

---

## Integration Points

### With Project Structure

The research and examples are designed to integrate with:

- **STORY-002**: ExecutionService with Docker lifecycle
- **CI/CD pipelines**: Image building and pushing
- **Container orchestration**: Batch operations and scaling
- **Async task queues**: Worker management

### Dependency Management

Based on project instructions (using bun):

```bash
# Add to project
bun add docker aiodocker

# In Python code
from docker import client as docker_client
import aiodocker
```

---

## Best Practices Summary

### Security Hardening

1. Never run as root
2. Drop all capabilities
3. Use read-only root filesystem
4. Apply seccomp profiles
5. Never mount Docker socket
6. Use network isolation
7. Scan images for vulnerabilities

### Resource Management

1. Always set memory limits
2. Set CPU limits appropriately
3. Use tmpfs for temporary files
4. Clean up after execution
5. Monitor resource usage
6. Implement backpressure

### Async Patterns

1. Use semaphores for concurrency
2. Implement proper timeout handling
3. Handle signals for graceful shutdown
4. Always cleanup resources
5. Use context managers
6. Log operations and errors

### CI/CD

1. Build without Docker socket (Kaniko)
2. Authenticate with tokens, not passwords
3. Scan images before pushing
4. Use minimal base images
5. Implement layer caching
6. Tag images consistently

---

## References

### Official Documentation

- [Docker SDK for Python](https://docker-py.readthedocs.io/)
- [Docker Engine API](https://docs.docker.com/engine/api/)
- [Docker Security](https://docs.docker.com/engine/security/)
- [aiodocker Documentation](https://aiodocker.readthedocs.io/)

### Key Resources Used

- Docker SDK GitHub: https://github.com/docker/docker-py
- aiodocker GitHub: https://github.com/aio-libs/aiodocker
- Docker Security Docs: https://docs.docker.com/engine/security/
- OWASP Docker Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html

---

## Document Maintenance

**Research Date**: January 28, 2026
**Docker SDK Version**: 7.1.0+ (stable)
**aiodocker Version**: 0.25.0+
**Python Version**: 3.9+
**Last Updated**: January 28, 2026

### Future Updates Needed For

- Docker SDK v8.0+ releases
- aiodocker v1.0+ releases
- New security best practices
- Additional async patterns
- Performance optimizations

---

## Quick Navigation

### By Topic

| Topic | Primary Doc | Section |
|-------|------------|---------|
| Getting Started | Quick Reference | Installation & Quick Start |
| Container Lifecycle | Research | Section 1 |
| Security | Research | Section 2 |
| Resource Limits | Research | Section 3 |
| Async Operations | Research & Examples | Section 4 & Examples |
| Cleanup | Research | Section 5 |
| Graceful Shutdown | Research | Section 6 |
| Docker-in-Docker | Research | Section 7 |
| CI/CD | Research | Section 8 |

### By Experience Level

| Level | Start Here | Then Read | Then Study |
|-------|-----------|-----------|-----------|
| Beginner | Quick Ref | Research Sec 1 | Examples |
| Intermediate | Research Sec 1-3 | Quick Ref | Examples |
| Advanced | Research All | Examples | Custom impl |

---

**Navigation Complete - See referenced documents for detailed content**
