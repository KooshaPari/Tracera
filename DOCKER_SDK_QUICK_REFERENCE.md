# Docker SDK for Python - Quick Reference Guide

## Installation

```bash
# Using pip
pip install docker

# Using bun (per project requirements)
bun add docker

# Optional: async support
pip install aiodocker
bun add aiodocker
```

## Quick Start - Synchronous

```python
import docker

# Connect to Docker daemon
client = docker.from_env()

# Run a simple container
output = client.containers.run(
    'alpine',
    'echo "Hello from Docker"'
)
print(output)  # b'Hello from Docker\n'

# List running containers
containers = client.containers.list()
for container in containers:
    print(f"{container.name}: {container.status}")

# Clean up
client.close()
```

## Quick Start - Asynchronous

```python
import asyncio
import aiodocker

async def main():
    docker = aiodocker.Docker()

    # Create container
    config = {
        'Image': 'alpine',
        'Cmd': ['echo', 'Hello async']
    }

    container = await docker.containers.create_or_replace(
        config=config,
        name='async-test'
    )

    await container.start()
    await container.wait()

    await docker.close()

asyncio.run(main())
```

---

## Common Operations

### Container Lifecycle

| Operation | Synchronous | Async (aiodocker) |
|-----------|-------------|------------------|
| Create | `client.containers.create()` | `docker.containers.create_or_replace()` |
| Run | `client.containers.run()` | Create + start |
| Start | `container.start()` | `await container.start()` |
| Stop | `container.stop(timeout=10)` | `await container.stop(timeout=10)` |
| Remove | `container.remove(force=True)` | `await container.delete(force=True)` |
| Wait | `container.wait()` | `await container.wait()` |
| Logs | `container.logs()` | `await container.log()` |

### Container Configuration

```python
# Environment variables
environment = {'DEBUG': 'true', 'PORT': '8080'}

# Volume mounts
volumes = {
    '/host/data': {'bind': '/container/data', 'mode': 'rw'},
    '/host/config': {'bind': '/app/config', 'mode': 'ro'}
}

# Port mappings
ports = {'8080/tcp': 8080, '5432/tcp': 5432}

# Resource limits
from docker.types import HostConfig

host_config = HostConfig(
    memory='512m',       # Memory limit
    memswap_limit='1g',  # Swap limit
    nano_cpus=int(1e9),  # 1 CPU
    cpu_shares=1024
)

# Security options
host_config = HostConfig(
    user='1000',         # Non-root user
    cap_drop=['ALL'],    # Drop all capabilities
    read_only=True,      # Read-only filesystem
    security_opt=['no-new-privileges:true']
)
```

---

## Security Hardening Patterns

### Minimal Secure Configuration

```python
from docker.types import HostConfig

# Create secure container
container = client.containers.create(
    image='myapp:latest',
    command='python app.py',
    user='1000:1000',  # Non-root
    host_config=HostConfig(
        cap_drop=['ALL'],  # No capabilities
        read_only=True,    # Read-only fs
        security_opt=['no-new-privileges:true'],
        tmpfs={
            '/tmp': 'size=100m,mode=1777'
        }
    ),
    environment={
        'LOG_LEVEL': 'INFO'
    }
)
```

### No Docker Socket Mounting

```python
# BAD (SECURITY RISK)
# DON'T DO THIS:
volumes = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock', 'mode': 'rw'}}

# GOOD: Use safe alternatives
# Option 1: Docker API
environment = {'DOCKER_HOST': 'tcp://docker-api:2375'}

# Option 2: Kaniko for builds
# docker run -v /workspace:/workspace gcr.io/kaniko-project/executor

# Option 3: Rootless Docker
# Configure rootless mode on host
```

---

## Resource Limits Quick Reference

### Memory

```python
from docker.types import HostConfig

# 512 MB hard limit
HostConfig(mem_limit='512m')

# 512 MB memory + 256 MB swap
HostConfig(mem_limit='512m', memswap_limit='768m')
```

### CPU

```python
from docker.types import HostConfig

# 0.5 CPU cores
HostConfig(nano_cpus=int(0.5 * 1e9))

# 1.0 CPU cores
HostConfig(nano_cpus=int(1.0 * 1e9))

# Specific cores (0 and 2)
HostConfig(cpuset_cpus='0,2')
```

### I/O

```python
from docker.types import HostConfig

# 1000 read ops/sec, 500 write ops/sec
HostConfig(
    device_read_iops=1000,
    device_write_iops=500
)
```

---

## Error Handling

```python
import docker
from docker.errors import (
    ContainerError,
    ImageNotFound,
    APIError,
    NotFound
)

try:
    # Run container
    container = client.containers.run('myimage', 'mycommand')

except ImageNotFound:
    print("Image not found - pull it first")
    client.images.pull('myimage:latest')

except ContainerError as e:
    print(f"Container exited with code {e.exit_status}")
    print(f"Command: {e.command}")

except APIError as e:
    print(f"Docker API error: {e}")

except NotFound:
    print("Container not found")

except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Async Patterns

### Concurrent Containers

```python
import asyncio
import aiodocker

async def run_container(docker, image, name):
    config = {'Image': image, 'Cmd': ['sleep', '5']}
    container = await docker.containers.create_or_replace(
        config=config, name=name
    )
    await container.start()
    return container

async def main():
    docker = aiodocker.Docker()

    # Run 5 containers concurrently
    containers = await asyncio.gather(
        run_container(docker, 'alpine', 'c1'),
        run_container(docker, 'alpine', 'c2'),
        run_container(docker, 'alpine', 'c3'),
        run_container(docker, 'alpine', 'c4'),
        run_container(docker, 'alpine', 'c5'),
    )

    # Wait for all to finish
    await asyncio.gather(*[c.wait() for c in containers])

    # Cleanup
    for container in containers:
        await container.delete()

    await docker.close()

asyncio.run(main())
```

### Streaming Logs

```python
import asyncio
import aiodocker

async def stream_logs(docker, container_id):
    container = docker.containers.container(container_id)

    async with container.log(stdout=True, stderr=True, follow=True) as logs:
        async for line in logs:
            print(line.decode('utf-8').rstrip())

asyncio.run(stream_logs(docker, 'container_id'))
```

---

## Cleanup Patterns

### Remove Single Container

```python
import docker

client = docker.from_env()

try:
    container = client.containers.get('container_id')

    # Stop if running
    if container.status == 'running':
        container.stop(timeout=10)

    # Remove with volumes
    container.remove(v=True)

except docker.errors.NotFound:
    print("Container not found")
```

### Cleanup All Stopped Containers

```python
# Stop and remove all
for container in client.containers.list(all=True):
    if container.status == 'running':
        container.stop(timeout=10)
    container.remove(v=True)

# Or use prune
client.containers.prune()
client.images.prune()
client.volumes.prune()
```

### Cleanup Orphaned Resources

```python
# Remove dangling volumes
result = client.volumes.prune()
print(f"Removed {len(result['VolumesDeleted'])} volumes")

# Remove dangling images
result = client.images.prune(filters={'dangling': True})
print(f"Removed {len(result['ImagesDeleted'])} images")

# Remove unused networks
result = client.networks.prune()
print(f"Removed {result['NetworksDeleted']} networks")
```

---

## Timeout Management

### Container with Timeout

```python
import docker
import time

client = docker.from_env()

def run_with_timeout(image, command, timeout=30):
    """Run container with timeout (blocking)."""
    container = client.containers.run(
        image,
        command,
        detach=True
    )

    try:
        # Wait with timeout
        result = container.wait(timeout=timeout)
        return result['StatusCode']
    except docker.errors.APIError:
        # Timeout - kill container
        container.kill()
        raise

# Usage
try:
    exit_code = run_with_timeout(
        'python:3.11',
        'python -c "import time; time.sleep(10)"',
        timeout=5
    )
except Exception as e:
    print(f"Execution failed: {e}")
```

### Async Timeout

```python
import asyncio
import aiodocker

async def run_with_timeout(docker, image, command, timeout=30):
    """Run container with async timeout."""
    config = {'Image': image, 'Cmd': command}
    container = await docker.containers.create_or_replace(config=config)

    try:
        await container.start()
        result = await asyncio.wait_for(
            container.wait(),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        await container.delete(force=True)
        raise
```

---

## Graceful Shutdown

### Signal Handling in Application

```python
import signal
import asyncio
import logging

logger = logging.getLogger(__name__)

class GracefulShutdown:
    def __init__(self, timeout=30):
        self.timeout = timeout
        self._shutdown = asyncio.Event()
        signal.signal(signal.SIGTERM, self._handle_signal)
        signal.signal(signal.SIGINT, self._handle_signal)

    def _handle_signal(self, signum, frame):
        logger.info(f"Received signal {signum}")
        self._shutdown.set()

    async def wait(self):
        await self._shutdown.wait()

# In your app
async def main():
    shutdown = GracefulShutdown()

    try:
        # Run your app
        await asyncio.wait_for(shutdown.wait(), timeout=300)
    finally:
        logger.info("Cleaning up...")
        # Cleanup code here

asyncio.run(main())
```

### Dockerfile with Proper Shutdown

```dockerfile
FROM python:3.11-slim

# Install tini for signal forwarding
RUN apt-get update && apt-get install -y tini

WORKDIR /app
COPY app.py .

# Use tini as init to forward signals
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "app.py"]
```

---

## Execution Within Containers

### Execute Command

```python
import docker

client = docker.from_env()
container = client.containers.get('container_id')

# Execute command
exec_id = client.api.exec_create(
    container.id,
    'ls -la /app',
    user='appuser',
    workdir='/app'
)

output = client.api.exec_start(exec_id['Id'], stream=False)
print(output.decode('utf-8'))

# Check exit code
exec_info = client.api.exec_inspect(exec_id['Id'])
print(f"Exit code: {exec_info['ExitCode']}")
```

### Stream Command Output

```python
# Stream output
for line in client.api.exec_start(
    exec_id['Id'],
    stream=True,
    decode=True
):
    print(line.rstrip())
```

---

## Network Configuration

### Connect to Network

```python
import docker

client = docker.from_env()

# Get or create network
try:
    network = client.networks.get('mynet')
except docker.errors.NotFound:
    network = client.networks.create('mynet', driver='bridge')

# Create container on network
container = client.containers.run(
    'alpine',
    'sleep 1000',
    detach=True,
    network='mynet',
    name='app'
)

# Or connect existing
network.connect(container)
```

### Port Exposure

```python
# Expose ports
container = client.containers.run(
    'nginx',
    detach=True,
    ports={
        '80/tcp': 8080,      # container:host
        '443/tcp': 8443,
    }
)

# Get port mappings
ports = container.ports
print(ports)  # {'80/tcp': [{'HostIp': '', 'HostPort': '8080'}]}
```

---

## Image Operations

### Pull Image

```python
import docker

client = docker.from_env()

# Pull image with progress
for line in client.api.pull('python:3.11-slim', stream=True, decode=True):
    if 'status' in line:
        print(line['status'])
```

### Build Image

```python
# Build from Dockerfile
tag = 'myapp:1.0'

for line in client.api.build(
    path='/path/to/dockerfile/dir',
    dockerfile='Dockerfile',
    tag=tag,
    stream=True,
    decode=True
):
    if 'stream' in line:
        print(line['stream'].rstrip())
```

### Push Image

```python
# First login
client.login(username='user', password='pass', registry='docker.io')

# Push
for line in client.api.push(
    'myrepo/myimage:latest',
    stream=True,
    decode=True
):
    if 'status' in line:
        print(line['status'])
```

---

## Common Patterns Summary

| Task | Pattern |
|------|---------|
| Run command | `containers.run(image, command, detach=True)` |
| Run securely | Add `user='1000'`, `cap_drop=['ALL']` |
| With timeout | `container.wait(timeout=30)` |
| Get logs | `container.logs(stream=False)` |
| Stop gracefully | `container.stop(timeout=10)` |
| Execute in running | `client.api.exec_create()` + `exec_start()` |
| Resource limits | Pass `host_config=HostConfig(...)` |
| Async operations | Use `aiodocker` + `asyncio` |
| Cleanup | `container.remove(v=True)` or `.prune()` |

---

## Performance Tips

1. **Use `detach=True`** for long-running containers
2. **Stream logs** instead of buffering entire output
3. **Reuse client connection** - don't create new client each time
4. **Use semaphores** to limit concurrent container creation
5. **Pre-pull images** before running containers at scale
6. **Use layer caching** in multi-stage builds
7. **Compress volumes** for faster I/O

---

## Debugging

### Check Docker Daemon

```python
import docker

client = docker.from_env()

try:
    client.ping()
    print("Docker daemon is running")
except Exception as e:
    print(f"Docker not available: {e}")
```

### Get System Info

```python
info = client.info()
print(f"Containers: {info['Containers']}")
print(f"Running: {info['ContainersRunning']}")
print(f"Images: {info['Images']}")
```

### List Everything

```python
# Containers
for c in client.containers.list(all=True):
    print(f"{c.name}: {c.status}")

# Images
for img in client.images.list():
    print(img.tags)

# Networks
for net in client.networks.list():
    print(f"{net.name}: {net.driver}")

# Volumes
for vol in client.volumes.list():
    print(vol.name)
```

---

**Quick Reference Version**: 1.0
**For Full Details**: See DOCKER_SDK_RESEARCH.md
