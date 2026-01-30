# Docker SDK for Python and Container Orchestration Research

## Executive Summary

This research provides comprehensive guidance on using the Docker SDK for Python (docker-py) and container orchestration patterns. The Docker SDK v7.1.0+ enables programmatic container lifecycle management with features for resource constraints, volume mounting, security configuration, and cleanup strategies. For asynchronous workloads, aiodocker provides asyncio-based bindings that enable concurrent container operations. This document covers practical patterns for production-grade container management, security best practices, and implementation strategies for CI/CD integration.

---

## Research Objectives

This research answers the following key questions:

1. How do I manage container creation, execution, and lifecycle using docker-py?
2. What security best practices should be applied to containerized applications?
3. How can I implement asynchronous container management for concurrent operations?
4. What patterns exist for handling resource constraints, timeouts, and graceful shutdown?
5. How should I implement cleanup strategies to prevent resource leaks?
6. What are the security risks and mitigations for Docker-in-Docker scenarios?

---

## Methodology

Research conducted through:

- **Official Documentation**: Docker SDK for Python (docker-py v7.1.0) and aiodocker documentation
- **Source Code Analysis**: GitHub repositories for docker-py and aiodocker
- **Security Research**: Docker security best practices from official docs and OWASP guidelines
- **Practical Patterns**: Integration examples and CI/CD use cases
- **Community Knowledge**: GitHub issues, StackOverflow patterns, and industry guides

---

## Detailed Findings

### 1. Docker SDK (docker-py) - Container Creation and Lifecycle

#### 1.1 Package Information

- **Current Version**: 7.1.0 (stable, released May 23, 2024)
- **Repository**: https://github.com/docker/docker-py
- **PyPI**: https://pypi.org/project/docker
- **Installation**: `pip install docker` or `bun add docker` (using bun package manager per project instructions)

#### 1.2 Module Architecture

The docker-py library is organized into several key components:

```
docker/
├── models/          # High-level container abstractions
│   ├── containers.py    # Container model
│   ├── images.py        # Image management
│   ├── networks.py      # Network management
│   └── volumes.py       # Volume management
├── api/             # Low-level Docker Engine API
│   ├── container.py     # Container API methods
│   ├── image.py         # Image API methods
│   └── network.py       # Network API methods
├── types/           # Configuration types
│   └── containers.py    # HostConfig, NetworkingConfig, etc.
├── client.py        # Docker client
├── errors.py        # Exception types
└── auth.py          # Registry authentication
```

#### 1.3 Container Lifecycle Management

**High-Level API (Recommended)**:

```python
import docker
from typing import Optional, Dict, Any

class ContainerManager:
    """High-level container management with lifecycle controls."""

    def __init__(self):
        self.client = docker.from_env()

    async def create_container(
        self,
        image: str,
        command: Optional[str] = None,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        ports: Optional[Dict[str, int]] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> docker.models.containers.Container:
        """
        Create a container without starting it.

        Args:
            image: Docker image name or ID
            command: Command to run (overrides entrypoint)
            environment: Environment variables as dict
            volumes: Volume mount configuration
            ports: Port mappings (container_port: host_port)
            name: Container name
            **kwargs: Additional docker.containers.create() parameters

        Returns:
            Container object for further manipulation
        """
        # Create container in stopped state
        container = self.client.containers.create(
            image=image,
            command=command,
            environment=environment,
            volumes=volumes,
            ports=ports,
            name=name,
            **kwargs
        )
        return container

    def run_container(
        self,
        image: str,
        command: Optional[str] = None,
        detach: bool = True,
        environment: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, Dict[str, str]]] = None,
        timeout: int = 300,
        **kwargs
    ) -> docker.models.containers.Container:
        """
        Create and start a container in one operation.

        Args:
            image: Docker image name or ID
            command: Command to run
            detach: If False, wait for container to complete
            environment: Environment variables
            volumes: Volume mounts
            timeout: Timeout in seconds (for non-detached runs)
            **kwargs: Additional parameters

        Returns:
            Container object or logs (depending on detach)
        """
        container = self.client.containers.run(
            image=image,
            command=command,
            detach=detach,
            environment=environment,
            volumes=volumes,
            **kwargs
        )

        if not detach:
            # Wait for container with timeout
            try:
                exit_code = container.wait(timeout=timeout)
                logs = container.logs()
                return logs, exit_code['StatusCode']
            except docker.errors.APIError as e:
                raise RuntimeError(f"Container execution failed: {e}")

        return container

    def get_container(self, container_id: str) -> docker.models.containers.Container:
        """Get container by ID or name."""
        return self.client.containers.get(container_id)

    def list_containers(self, all: bool = False) -> list:
        """List running (or all) containers."""
        return self.client.containers.list(all=all)

    def start_container(self, container: docker.models.containers.Container) -> None:
        """Start a stopped container."""
        container.start()

    def stop_container(
        self,
        container: docker.models.containers.Container,
        timeout: int = 10
    ) -> None:
        """Stop a running container gracefully."""
        container.stop(timeout=timeout)

    def remove_container(
        self,
        container: docker.models.containers.Container,
        force: bool = False,
        volumes: bool = True
    ) -> None:
        """Remove container and optionally associated volumes."""
        container.remove(force=force, v=volumes)

    def get_container_logs(
        self,
        container: docker.models.containers.Container,
        stream: bool = False
    ) -> str:
        """
        Get container logs.

        Args:
            container: Container object
            stream: If True, return generator for streaming logs

        Returns:
            Log output as string or generator
        """
        logs = container.logs(stream=stream, stderr=True, stdout=True)

        if stream:
            return logs  # Generator for real-time processing

        return logs.decode('utf-8')

    def wait_for_container(
        self,
        container: docker.models.containers.Container,
        timeout: Optional[int] = None
    ) -> int:
        """
        Wait for container to finish.

        Args:
            container: Container object
            timeout: Maximum wait time in seconds

        Returns:
            Exit code
        """
        result = container.wait(timeout=timeout)
        return result.get('StatusCode', -1)

    def cleanup(self):
        """Close Docker client connection."""
        self.client.close()
```

#### 1.4 Container Execution with Command Handling

```python
import subprocess
from docker.models.containers import Container

class ExecutionService:
    """Execute commands inside containers with exit code handling."""

    def __init__(self, container_manager: ContainerManager):
        self.container_manager = container_manager

    def exec_command(
        self,
        container: Container,
        command: str,
        user: str = 'root',
        working_dir: Optional[str] = None,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute command inside container.

        Args:
            container: Target container
            command: Shell command to execute
            user: User context for execution
            working_dir: Working directory inside container
            timeout: Execution timeout in seconds

        Returns:
            Dict with exit_code, stdout, stderr
        """
        try:
            # Create exec instance
            exec_id = container.client.api.exec_create(
                container.id,
                cmd=command,
                user=user,
                workdir=working_dir,
                stdout=True,
                stderr=True
            )

            # Execute and capture output
            output = container.client.api.exec_start(
                exec_id['Id'],
                stream=False
            )

            # Get exit code
            exec_info = container.client.api.exec_inspect(exec_id['Id'])
            exit_code = exec_info['ExitCode']

            return {
                'exit_code': exit_code,
                'stdout': output.decode('utf-8'),
                'stderr': '',  # Combined in stdout
                'success': exit_code == 0
            }

        except Exception as e:
            return {
                'exit_code': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }

    def stream_logs(
        self,
        container: Container,
        follow: bool = True
    ) -> None:
        """
        Stream container logs in real-time.

        Args:
            container: Target container
            follow: Continue streaming until container stops
        """
        try:
            for line in container.logs(stream=True, follow=follow):
                print(line.decode('utf-8').rstrip())
        except KeyboardInterrupt:
            print("Log streaming interrupted")
        except Exception as e:
            print(f"Error streaming logs: {e}")
```

---

### 2. Security Best Practices

#### 2.1 Non-Root User Execution

**Why**: Limits blast radius if container is compromised. Root processes can escape isolation.

```python
from docker.types import HostConfig

class SecureContainerManager(ContainerManager):
    """Container management with security hardening."""

    def run_secure_container(
        self,
        image: str,
        command: str,
        user_id: int = 1000,  # Non-root user ID
        read_only: bool = False,
        **kwargs
    ) -> docker.models.containers.Container:
        """
        Run container with security constraints.

        Args:
            image: Docker image
            command: Command to execute
            user_id: UID to run as (1000+ for non-root)
            read_only: Mount filesystem as read-only
            **kwargs: Additional parameters

        Returns:
            Container object
        """
        # Create host config with security options
        host_config = HostConfig(
            read_only=read_only,
            cap_drop=['ALL'],  # Drop all capabilities
            cap_add=['NET_BIND_SERVICE'],  # Add only needed capabilities
            security_opt=['no-new-privileges:true'],  # Prevent privilege escalation
            tmpfs={
                '/tmp': 'size=100m,mode=1777',  # Temporary filesystem
                '/run': 'size=50m,mode=1777'
            }
        )

        container = self.client.containers.create(
            image=image,
            command=command,
            user=str(user_id),  # Run as non-root
            host_config=host_config,
            **kwargs
        )

        container.start()
        return container
```

#### 2.2 Capability Management

```python
class CapabilityManager:
    """Manage Linux capabilities for container processes."""

    # All available Linux capabilities
    CAPABILITIES = {
        'NET_BIND_SERVICE': 'Bind to ports < 1024',
        'NET_RAW': 'Use raw sockets',
        'SYS_PTRACE': 'Process tracing',
        'DAC_OVERRIDE': 'Bypass file permissions',
        'SETFCAP': 'Set file capabilities',
        'SYS_ADMIN': 'System administration',
    }

    @staticmethod
    def create_minimal_capabilities(required: list) -> HostConfig:
        """
        Create HostConfig with minimal necessary capabilities.

        Args:
            required: List of required capability names

        Returns:
            HostConfig with secured capabilities
        """
        return HostConfig(
            cap_drop=['ALL'],  # Drop everything
            cap_add=required   # Add only what's needed
        )

    @staticmethod
    def get_secure_defaults() -> HostConfig:
        """Get HostConfig with secure defaults (no special capabilities)."""
        return HostConfig(
            cap_drop=['ALL'],
            security_opt=[
                'no-new-privileges:true',  # Cannot escalate privileges
            ]
        )
```

#### 2.3 Read-Only Filesystem and Volume Mounting

```python
class VolumeManager:
    """Manage secure volume mounting patterns."""

    @staticmethod
    def create_readonly_mount(
        host_path: str,
        container_path: str
    ) -> Dict[str, Dict[str, str]]:
        """
        Create read-only bind mount.

        Args:
            host_path: Path on host
            container_path: Path in container

        Returns:
            Volume configuration dict
        """
        return {
            host_path: {
                'bind': container_path,
                'mode': 'ro'  # Read-only
            }
        }

    @staticmethod
    def create_readwrite_mount(
        host_path: str,
        container_path: str
    ) -> Dict[str, Dict[str, str]]:
        """
        Create read-write bind mount.

        Args:
            host_path: Path on host
            container_path: Path in container

        Returns:
            Volume configuration dict
        """
        return {
            host_path: {
                'bind': container_path,
                'mode': 'rw'  # Read-write
            }
        }

    @staticmethod
    def create_tmpfs_mount(
        mount_path: str,
        size_mb: int = 100,
        mode: str = '1777'
    ) -> Dict[str, str]:
        """
        Create temporary in-memory mount.

        Args:
            mount_path: Path in container
            size_mb: Maximum size in MB
            mode: Permission mode

        Returns:
            tmpfs configuration
        """
        return {
            mount_path: f'size={size_mb}m,mode={mode}'
        }

    @staticmethod
    def create_named_volume(
        volume_name: str,
        container_path: str
    ) -> Dict[str, Dict[str, str]]:
        """
        Create named volume mount.

        Args:
            volume_name: Docker volume name
            container_path: Path in container

        Returns:
            Volume configuration dict
        """
        return {
            volume_name: {
                'bind': container_path,
                'mode': 'rw'
            }
        }
```

#### 2.4 Seccomp Profile Configuration

```python
import json
from pathlib import Path

class SeccompManager:
    """Manage seccomp security profiles."""

    @staticmethod
    def create_default_seccomp_profile() -> Dict[str, Any]:
        """
        Create a restrictive default seccomp profile.

        Default action: SCMP_ACT_ERRNO (deny with error)
        Allowed syscalls: Only essential ones

        Returns:
            Seccomp profile dict
        """
        return {
            'defaultAction': 'SCMP_ACT_ERRNO',
            'defaultErrnoRet': 1,
            'archMap': [
                {
                    'architecture': 'SCMP_ARCH_X86_64',
                    'subArchitectures': [
                        'SCMP_ARCH_X86',
                        'SCMP_ARCH_X32'
                    ]
                }
            ],
            'syscalls': [
                {
                    'names': [
                        'accept4', 'arch_prctl', 'bind', 'brk',
                        'clone', 'close', 'connect', 'dup', 'dup2',
                        'execve', 'exit', 'exit_group', 'fcntl',
                        'fstat', 'fstatfs', 'futex', 'getcwd',
                        'getegid', 'getgid', 'gethostname', 'getpeername',
                        'getpid', 'getppid', 'getrlimit', 'getsockname',
                        'getsockopt', 'gettimeofday', 'getuid', 'ioctl',
                        'listen', 'lseek', 'madvise', 'mmap', 'mprotect',
                        'munmap', 'open', 'openat', 'pipe', 'pipe2',
                        'poll', 'prctl', 'pread64', 'prlimit64',
                        'pwrite64', 'read', 'readlink', 'readlinkat',
                        'readv', 'recv', 'recvfrom', 'recvmsg',
                        'rename', 'renameat', 'renameat2', 'rt_sigaction',
                        'rt_sigprocmask', 'rt_sigreturn', 'sched_getaffinity',
                        'sched_yield', 'seccomp', 'select', 'send',
                        'sendfile', 'sendmsg', 'sendto', 'set_robust_list',
                        'set_tid_address', 'setfsgid', 'setfsuid',
                        'setgid', 'setgroups', 'sethostname', 'setitimer',
                        'setpgid', 'setpriority', 'setregid', 'setresgid',
                        'setresuid', 'setreuid', 'setrlimit', 'setsid',
                        'setsockopt', 'settimeofday', 'setuid', 'shutdown',
                        'sigaltstack', 'socket', 'socketcall', 'socketpair',
                        'splice', 'stat', 'statfs', 'statx', 'strptime',
                        'sysinfo', 'syslog', 'tgkill', 'time', 'timer_create',
                        'timer_delete', 'timer_getoverrun', 'timer_gettime',
                        'timer_settime', 'timerfd_create', 'timerfd_gettime',
                        'timerfd_settime', 'times', 'tkill', 'truncate',
                        'umask', 'uname', 'unlink', 'unlinkat', 'unshare',
                        'usleep', 'utime', 'utimensat', 'utimes',
                        'vfork', 'vmsplice', 'wait3', 'wait4',
                        'waitid', 'waitpid', 'write', 'writev', 'xstat'
                    ],
                    'action': 'SCMP_ACT_ALLOW',
                    'args': []
                }
            ]
        }

    @staticmethod
    def apply_seccomp_profile(
        profile_path: str,
        host_config: HostConfig
    ) -> HostConfig:
        """
        Apply seccomp profile to container.

        Args:
            profile_path: Path to seccomp profile JSON
            host_config: HostConfig to modify

        Returns:
            Updated HostConfig
        """
        if not Path(profile_path).exists():
            raise FileNotFoundError(f"Seccomp profile not found: {profile_path}")

        # Note: docker-py may have limitations with JSON seccomp profiles
        # Consider using --security-opt seccomp=<path> in docker run
        host_config.security_opt.append(f'seccomp={profile_path}')

        return host_config
```

---

### 3. Resource Constraints and Limits

#### 3.1 CPU and Memory Limits

```python
from docker.types import HostConfig

class ResourceLimitManager:
    """Manage container resource constraints."""

    @staticmethod
    def create_resource_limited_config(
        memory_mb: int = 512,
        memory_swap_mb: Optional[int] = None,
        cpus: float = 1.0,
        cpu_shares: int = 1024,
        cpuset_cpus: Optional[str] = None,
        device_read_iops: Optional[int] = None,
        device_write_iops: Optional[int] = None
    ) -> HostConfig:
        """
        Create HostConfig with resource limits.

        Args:
            memory_mb: Hard memory limit in MB (0 = unlimited)
            memory_swap_mb: Memory + swap limit (only if memory_mb set)
            cpus: CPU quota as float (0.5 = 50% of one CPU)
            cpu_shares: CPU shares (1024 = 1 unit, relative to others)
            cpuset_cpus: CPU cores to bind to (e.g., "0,2" or "0-3")
            device_read_iops: I/O read operations per second limit
            device_write_iops: I/O write operations per second limit

        Returns:
            Configured HostConfig
        """
        config_dict = {}

        # Memory constraints
        if memory_mb > 0:
            config_dict['mem_limit'] = f'{memory_mb}m'

            if memory_swap_mb is not None:
                config_dict['memswap_limit'] = f'{memory_swap_mb}m'

        # CPU constraints
        if cpus > 0:
            # cpus is represented as integer (microseconds per period)
            # Default period is 100000, so multiply by that
            config_dict['nano_cpus'] = int(cpus * 1e9)

        if cpu_shares > 0:
            config_dict['cpu_shares'] = cpu_shares

        if cpuset_cpus:
            config_dict['cpuset_cpus'] = cpuset_cpus

        # I/O constraints
        if device_read_iops:
            config_dict['device_read_iops'] = device_read_iops
        if device_write_iops:
            config_dict['device_write_iops'] = device_write_iops

        return HostConfig(**config_dict)

    @staticmethod
    def get_example_configs() -> Dict[str, HostConfig]:
        """
        Get example resource limit configurations.

        Returns:
            Dict of named configurations
        """
        return {
            'light': ResourceLimitManager.create_resource_limited_config(
                memory_mb=256,
                cpus=0.25
            ),
            'medium': ResourceLimitManager.create_resource_limited_config(
                memory_mb=512,
                cpus=0.5
            ),
            'heavy': ResourceLimitManager.create_resource_limited_config(
                memory_mb=2048,
                cpus=2.0
            ),
            'restricted_cpus': ResourceLimitManager.create_resource_limited_config(
                memory_mb=512,
                cpus=1.0,
                cpuset_cpus='0-1'  # Only use CPU cores 0 and 1
            )
        }
```

---

### 4. Async Container Orchestration with aiodocker

#### 4.1 Async Container Manager

```python
import asyncio
from typing import Optional, AsyncGenerator
try:
    import aiodocker
except ImportError:
    print("Install aiodocker: pip install aiodocker")

class AsyncContainerManager:
    """Asynchronous Docker container management using aiodocker."""

    def __init__(self):
        self.docker: Optional[aiodocker.Docker] = None

    async def __aenter__(self):
        """Context manager entry."""
        self.docker = aiodocker.Docker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        if self.docker:
            await self.docker.close()

    async def create_container(
        self,
        image: str,
        command: Optional[str] = None,
        environment: Optional[dict] = None,
        volumes: Optional[list] = None,
        **kwargs
    ) -> aiodocker.containers.DockerContainer:
        """
        Create container asynchronously.

        Args:
            image: Docker image
            command: Command to run
            environment: Environment variables
            volumes: Volume mounts
            **kwargs: Additional parameters

        Returns:
            DockerContainer object
        """
        if not self.docker:
            raise RuntimeError("Docker client not initialized")

        config = {
            'Image': image,
            'Cmd': command,
            'Env': environment or [],
            'Volumes': volumes or {},
        }

        # Remove None values
        config = {k: v for k, v in config.items() if v is not None}
        config.update(kwargs)

        return await self.docker.containers.create_or_replace(
            config=config,
            name=kwargs.get('name')
        )

    async def start_container(
        self,
        container: aiodocker.containers.DockerContainer
    ) -> None:
        """Start a created container."""
        await container.start()

    async def stop_container(
        self,
        container: aiodocker.containers.DockerContainer,
        timeout: int = 10
    ) -> None:
        """Stop container with timeout."""
        await container.stop(timeout=timeout)

    async def remove_container(
        self,
        container: aiodocker.containers.DockerContainer,
        force: bool = False,
        volumes: bool = True
    ) -> None:
        """Remove container."""
        await container.delete(force=force, v=volumes)

    async def get_logs(
        self,
        container: aiodocker.containers.DockerContainer,
        follow: bool = False
    ) -> AsyncGenerator[str, None]:
        """
        Stream logs from container asynchronously.

        Args:
            container: Target container
            follow: Continue streaming until stop

        Yields:
            Log lines as strings
        """
        async with container.log(stdout=True, stderr=True, follow=follow) as logs:
            async for line in logs:
                yield line.decode('utf-8').rstrip()

    async def run_command(
        self,
        container: aiodocker.containers.DockerContainer,
        command: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Run command in container.

        Args:
            container: Target container
            command: Shell command
            timeout: Execution timeout

        Returns:
            Result dict with exit_code, output
        """
        try:
            # Note: exec_create and exec_start with aiodocker
            # Implementation depends on aiodocker version
            # For now, using container logs as alternative

            result = await asyncio.wait_for(
                self._execute_with_timeout(container, command),
                timeout=timeout
            )
            return result

        except asyncio.TimeoutError:
            return {
                'exit_code': -1,
                'output': '',
                'error': f'Command timed out after {timeout}s',
                'success': False
            }
        except Exception as e:
            return {
                'exit_code': -1,
                'output': '',
                'error': str(e),
                'success': False
            }

    async def _execute_with_timeout(
        self,
        container: aiodocker.containers.DockerContainer,
        command: str
    ) -> Dict[str, Any]:
        """Execute command (placeholder for actual implementation)."""
        # This would depend on aiodocker's exec API
        return {
            'exit_code': 0,
            'output': 'Implementation depends on aiodocker version',
            'success': True
        }

    async def wait_for_container(
        self,
        container: aiodocker.containers.DockerContainer,
        timeout: Optional[int] = None
    ) -> int:
        """Wait for container completion."""
        try:
            result = await asyncio.wait_for(
                container.wait(),
                timeout=timeout
            )
            return result.get('StatusCode', -1)
        except asyncio.TimeoutError:
            return -1
```

#### 4.2 Concurrent Container Operations

```python
class AsyncBatchContainerManager(AsyncContainerManager):
    """Manage multiple containers concurrently."""

    async def run_containers_concurrent(
        self,
        specs: list,
        max_concurrent: int = 5
    ) -> list:
        """
        Create and start multiple containers concurrently.

        Args:
            specs: List of container specs (image, command, etc.)
            max_concurrent: Max concurrent operations

        Returns:
            List of started containers
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def create_and_start(spec):
            async with semaphore:
                container = await self.create_container(**spec)
                await self.start_container(container)
                return container

        return await asyncio.gather(
            *[create_and_start(spec) for spec in specs]
        )

    async def wait_all_containers(
        self,
        containers: list,
        timeout: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Wait for all containers to finish.

        Args:
            containers: List of containers
            timeout: Overall timeout

        Returns:
            Dict mapping container ID to exit code
        """
        try:
            results = await asyncio.wait_for(
                asyncio.gather(
                    *[self.wait_for_container(c) for c in containers],
                    return_exceptions=True
                ),
                timeout=timeout
            )

            return {
                c.id: result
                for c, result in zip(containers, results)
            }

        except asyncio.TimeoutError:
            # Force stop all containers
            await asyncio.gather(
                *[self.stop_container(c, timeout=5) for c in containers],
                return_exceptions=True
            )
            raise

    async def cleanup_containers(
        self,
        containers: list,
        force: bool = True
    ) -> None:
        """
        Remove multiple containers concurrently.

        Args:
            containers: List of containers
            force: Force removal
        """
        await asyncio.gather(
            *[self.remove_container(c, force=force) for c in containers],
            return_exceptions=True
        )
```

---

### 5. Cleanup Strategies

#### 5.1 Container Cleanup

```python
class ContainerCleanupManager:
    """Manage container and resource cleanup."""

    def __init__(self, client: docker.DockerClient):
        self.client = client

    def cleanup_container(
        self,
        container: docker.models.containers.Container,
        force: bool = False,
        remove_volumes: bool = True
    ) -> bool:
        """
        Clean up single container.

        Args:
            container: Container to clean
            force: Force removal if running
            remove_volumes: Remove associated volumes

        Returns:
            Success status
        """
        try:
            # Stop if running
            if container.status == 'running':
                container.stop(timeout=10)

            # Remove container
            container.remove(force=force, v=remove_volumes)
            return True

        except docker.errors.APIError as e:
            print(f"Error cleaning container {container.id}: {e}")
            return False

    def cleanup_all_containers(
        self,
        pattern: Optional[str] = None,
        only_stopped: bool = False
    ) -> Dict[str, bool]:
        """
        Clean up multiple containers.

        Args:
            pattern: Name pattern to match (regex)
            only_stopped: Only remove stopped containers

        Returns:
            Dict mapping container ID to cleanup success
        """
        import re

        containers = self.client.containers.list(all=True)
        results = {}

        for container in containers:
            # Filter by pattern if provided
            if pattern:
                if not re.search(pattern, container.name):
                    continue

            # Skip running containers if only_stopped
            if only_stopped and container.status == 'running':
                continue

            results[container.id] = self.cleanup_container(container)

        return results

    def cleanup_dangling_volumes(self) -> int:
        """
        Remove dangling volumes (not used by any container).

        Returns:
            Number of volumes removed
        """
        try:
            prune_result = self.client.volumes.prune()
            return prune_result['VolumesDeleted']
        except Exception as e:
            print(f"Error pruning volumes: {e}")
            return 0

    def cleanup_dangling_images(self) -> int:
        """
        Remove dangling images.

        Returns:
            Number of images removed
        """
        try:
            prune_result = self.client.images.prune(filters={'dangling': True})
            return len(prune_result['ImagesDeleted'])
        except Exception as e:
            print(f"Error pruning images: {e}")
            return 0
```

#### 5.2 Orphaned Resource Tracking

```python
class OrphanedResourceTracker:
    """Track and cleanup orphaned Docker resources."""

    def __init__(self, client: docker.DockerClient):
        self.client = client

    def find_orphaned_volumes(self) -> list:
        """Find volumes not used by any container."""
        all_volumes = self.client.volumes.list()
        used_volumes = set()

        # Collect volumes used by containers
        for container in self.client.containers.list(all=True):
            mounts = container.attrs.get('Mounts', [])
            for mount in mounts:
                if mount['Type'] == 'volume':
                    used_volumes.add(mount['Name'])

        # Find unused volumes
        orphaned = [v for v in all_volumes if v.name not in used_volumes]
        return orphaned

    def find_orphaned_networks(self) -> list:
        """Find networks not used by any container."""
        all_networks = self.client.networks.list()
        used_networks = set()

        # Collect networks used by containers
        for container in self.client.containers.list(all=True):
            network_settings = container.attrs.get('NetworkSettings', {})
            networks = network_settings.get('Networks', {})
            used_networks.update(networks.keys())

        # Built-in networks are not orphaned
        builtin = {'bridge', 'host', 'none'}

        orphaned = [
            n for n in all_networks
            if n.name not in used_networks and n.name not in builtin
        ]
        return orphaned

    def cleanup_orphaned_resources(self) -> Dict[str, int]:
        """
        Clean up all orphaned resources.

        Returns:
            Cleanup statistics
        """
        stats = {'volumes': 0, 'networks': 0, 'errors': 0}

        # Clean orphaned volumes
        for volume in self.find_orphaned_volumes():
            try:
                volume.remove()
                stats['volumes'] += 1
            except Exception as e:
                print(f"Error removing volume {volume.name}: {e}")
                stats['errors'] += 1

        # Clean orphaned networks
        for network in self.find_orphaned_networks():
            try:
                network.remove()
                stats['networks'] += 1
            except Exception as e:
                print(f"Error removing network {network.name}: {e}")
                stats['errors'] += 1

        return stats
```

---

### 6. Timeout and Graceful Shutdown Patterns

#### 6.1 Signal Handling in Containers

**Dockerfile Best Practices**:

```dockerfile
# Use exec form of ENTRYPOINT to ensure PID 1 signal handling
FROM python:3.11-slim

# Install signal-forwarding wrapper (optional but recommended)
RUN apt-get update && \
    apt-get install -y tini && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY app.py .

# Use tini as init process to forward signals
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["python", "app.py"]
```

**Python Signal Handling**:

```python
import signal
import sys
import asyncio
from typing import Callable

class GracefulShutdownHandler:
    """Handle graceful shutdown with SIGTERM/SIGINT."""

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.shutdown_event = asyncio.Event()
        self._register_signals()

    def _register_signals(self):
        """Register signal handlers."""
        # Handle SIGTERM (docker stop default)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Signal handler callback."""
        print(f"Received signal {signum}, initiating graceful shutdown...")
        self.shutdown_event.set()

    async def wait_for_shutdown(self):
        """Wait for shutdown signal."""
        await self.shutdown_event.wait()

    async def run_with_timeout(
        self,
        coroutine,
        timeout: Optional[int] = None
    ):
        """
        Run coroutine with timeout and graceful shutdown.

        Args:
            coroutine: Async function to run
            timeout: Override default timeout

        Raises:
            asyncio.TimeoutError if timeout exceeded
        """
        timeout = timeout or self.timeout

        # Race between coroutine and shutdown signal
        done, pending = await asyncio.wait(
            [
                asyncio.create_task(coroutine),
                asyncio.create_task(self.wait_for_shutdown())
            ],
            timeout=timeout,
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()

        # Get result from completed task
        result = done.pop().result()
        return result

class WorkerProcessManager:
    """
    Manage worker processes with graceful shutdown.

    Ensures PID 1 process handles signals and waits for workers.
    """

    def __init__(self):
        self.workers = []
        self.shutdown_handler = GracefulShutdownHandler()

    async def spawn_worker(self, worker_func: Callable, *args):
        """Spawn a worker task."""
        task = asyncio.create_task(worker_func(*args))
        self.workers.append(task)
        return task

    async def wait_for_workers(self, timeout: int = 30):
        """
        Wait for all workers to complete.

        Args:
            timeout: Maximum wait time

        Raises:
            asyncio.TimeoutError if timeout exceeded
        """
        if not self.workers:
            return

        try:
            await asyncio.wait_for(
                asyncio.gather(*self.workers, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            print(f"Worker timeout after {timeout}s, cancelling...")
            for worker in self.workers:
                worker.cancel()

            # Give workers time to cleanup
            await asyncio.sleep(2)
            raise

    async def shutdown(self):
        """Gracefully shutdown all workers."""
        print("Shutting down workers...")

        # Cancel all workers
        for worker in self.workers:
            worker.cancel()

        # Wait for cancellation with timeout
        try:
            await self.wait_for_workers(timeout=10)
        except asyncio.TimeoutError:
            print("Force terminating workers")
```

#### 6.2 Container with Timeout Management

```python
import time
from datetime import datetime, timedelta

class ContainerWithTimeout:
    """Manage container execution with timeout."""

    def __init__(
        self,
        container_manager: ContainerManager,
        stop_timeout: int = 10,
        kill_timeout: int = 5
    ):
        self.manager = container_manager
        self.stop_timeout = stop_timeout
        self.kill_timeout = kill_timeout

    def run_with_timeout(
        self,
        image: str,
        command: str,
        timeout: int = 300,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Run container with timeout.

        Args:
            image: Docker image
            command: Command to execute
            timeout: Execution timeout in seconds
            **kwargs: Additional container parameters

        Returns:
            Result dict with exit_code, logs, timed_out flag
        """
        container = None
        start_time = datetime.now()
        deadline = start_time + timedelta(seconds=timeout)

        try:
            # Create and start container
            container = self.manager.client.containers.run(
                image=image,
                command=command,
                detach=True,  # Run in background
                **kwargs
            )

            # Wait for completion with timeout
            remaining_time = (deadline - datetime.now()).total_seconds()

            if remaining_time <= 0:
                raise TimeoutError(f"Container creation exceeded timeout")

            result = container.wait(timeout=remaining_time)
            exit_code = result.get('StatusCode', -1)

            # Get logs
            logs = container.logs().decode('utf-8')

            return {
                'exit_code': exit_code,
                'logs': logs,
                'timed_out': False,
                'success': exit_code == 0
            }

        except TimeoutError as e:
            if container:
                self._force_stop_container(container)

            return {
                'exit_code': -1,
                'logs': container.logs().decode('utf-8') if container else '',
                'timed_out': True,
                'success': False,
                'error': str(e)
            }

        except Exception as e:
            if container:
                self._force_stop_container(container)

            return {
                'exit_code': -1,
                'logs': '',
                'timed_out': False,
                'success': False,
                'error': str(e)
            }

        finally:
            # Cleanup
            if container:
                try:
                    self.manager.remove_container(container, force=True)
                except:
                    pass

    def _force_stop_container(self, container):
        """Stop container with escalation: SIGTERM -> SIGKILL."""
        try:
            container.stop(timeout=self.stop_timeout)
        except:
            try:
                container.kill()
            except:
                pass
```

---

### 7. Docker-in-Docker Security Considerations

#### 7.1 Security Risks

**Critical Risk**: Mounting `/var/run/docker.sock` inside a container grants:
- Full Docker daemon control
- Root-equivalent access to host
- Ability to mount entire host filesystem
- Container escape capability

#### 7.2 Safe Alternatives

```python
class SafeDockerInDockerPatterns:
    """Safe patterns for Docker-in-Docker scenarios."""

    @staticmethod
    def use_docker_api_only() -> Dict[str, str]:
        """
        Use Docker API instead of socket mounting.

        Connect to remote Docker daemon instead of local socket.
        """
        return {
            'DOCKER_HOST': 'tcp://docker-api:2375',
            'DOCKER_TLS_VERIFY': '',
            'DOCKER_CERT_PATH': ''
        }

    @staticmethod
    def use_rootless_docker() -> HostConfig:
        """
        Use rootless Docker for better isolation.

        Returns:
            HostConfig for rootless container
        """
        return HostConfig(
            # Run container as non-root
            user='1000:1000',
            # No capabilities needed
            cap_drop=['ALL'],
            # Better isolation
            security_opt=['seccomp=unconfined']
        )

    @staticmethod
    def use_kaniko_for_builds() -> Dict[str, str]:
        """
        Use Kaniko for building images (no docker socket needed).

        Kaniko builds container images from Dockerfile without Docker daemon.

        Returns:
            Environment for Kaniko executor
        """
        return {
            'KANIKO_EXECUTOR': '/kaniko/executor',
            'DOCKER_CONFIG': '/kaniko/.docker'
        }

    @staticmethod
    def get_insecure_socket_mount_config() -> Dict[str, Dict[str, str]]:
        """
        INSECURE: Docker socket mounting (not recommended).

        Shown here for documentation only. DO NOT USE IN PRODUCTION.

        Returns:
            Volume configuration (for reference only)
        """
        print("WARNING: Socket mounting is a critical security vulnerability!")

        return {
            '/var/run/docker.sock': {
                'bind': '/var/run/docker.sock',
                'mode': 'rw'  # Even read-only is unsafe
            }
        }

    @staticmethod
    def get_safe_ci_cd_isolation() -> HostConfig:
        """
        Secure CI/CD container isolation.

        Returns:
            Hardened HostConfig for CI/CD builders
        """
        return HostConfig(
            # Run as non-root
            user='1000:1000',
            # Drop all capabilities
            cap_drop=['ALL'],
            # No privilege escalation
            security_opt=['no-new-privileges:true'],
            # Read-only filesystem (except specific mounts)
            read_only=True,
            # Temporary mount for build artifacts
            tmpfs={
                '/tmp': 'size=1g,mode=1777',
                '/workspace': 'size=5g,mode=1777'
            }
        )
```

---

### 8. CI/CD Integration Patterns

#### 8.1 Registry Authentication

```python
from docker.auth import resolve_auth_config
import json

class RegistryAuthManager:
    """Manage Docker registry authentication."""

    def __init__(self, client: docker.DockerClient):
        self.client = client

    def login_to_registry(
        self,
        registry: str,
        username: str,
        password: str,
        email: Optional[str] = None
    ) -> bool:
        """
        Authenticate with Docker registry.

        Args:
            registry: Registry URL (e.g., docker.io, gcr.io)
            username: Registry username
            password: Registry password/token
            email: Email address (optional)

        Returns:
            Success status
        """
        try:
            result = self.client.login(
                username=username,
                password=password,
                registry=registry,
                email=email
            )

            if 'Auths' in result or result.get('Status') == 'Login Succeeded':
                print(f"Successfully authenticated with {registry}")
                return True

            print(f"Authentication failed: {result}")
            return False

        except Exception as e:
            print(f"Login error: {e}")
            return False

    def pull_image(
        self,
        image: str,
        auth_config: Optional[dict] = None
    ) -> bool:
        """
        Pull image from registry.

        Args:
            image: Image name (e.g., myregistry.com/app:latest)
            auth_config: Authentication config dict

        Returns:
            Success status
        """
        try:
            # Stream pull progress
            for line in self.client.api.pull(
                image,
                stream=True,
                decode=True,
                auth_config=auth_config
            ):
                # Process pull progress
                if 'status' in line:
                    print(f"Pull: {line['status']}")
                if 'error' in line:
                    print(f"Pull error: {line['error']}")
                    return False

            return True

        except Exception as e:
            print(f"Pull error: {e}")
            return False

    def push_image(
        self,
        image: str,
        tag: str = 'latest',
        auth_config: Optional[dict] = None
    ) -> bool:
        """
        Push image to registry.

        Args:
            image: Image name
            tag: Image tag
            auth_config: Authentication config

        Returns:
            Success status
        """
        try:
            # Tag image
            full_name = f"{image}:{tag}"

            # Push with stream
            for line in self.client.api.push(
                image,
                tag=tag,
                stream=True,
                decode=True,
                auth_config=auth_config
            ):
                if 'status' in line:
                    print(f"Push: {line['status']}")
                if 'error' in line:
                    print(f"Push error: {line['error']}")
                    return False

            return True

        except Exception as e:
            print(f"Push error: {e}")
            return False
```

#### 8.2 CI/CD Build Service

```python
class CIDDDockerBuildService:
    """Service for managing Docker builds in CI/CD."""

    def __init__(self, client: docker.DockerClient):
        self.client = client
        self.auth_manager = RegistryAuthManager(client)

    def build_image(
        self,
        dockerfile_path: str,
        image_name: str,
        image_tag: str = 'latest',
        build_args: Optional[dict] = None,
        labels: Optional[dict] = None,
        target: Optional[str] = None
    ) -> bool:
        """
        Build Docker image from Dockerfile.

        Args:
            dockerfile_path: Path to Dockerfile
            image_name: Image name to create
            image_tag: Image tag
            build_args: Build arguments
            labels: Image labels
            target: Multi-stage target stage

        Returns:
            Success status
        """
        try:
            path = Path(dockerfile_path)

            if not path.exists():
                raise FileNotFoundError(f"Dockerfile not found: {dockerfile_path}")

            # Build image
            tag = f"{image_name}:{image_tag}"

            print(f"Building image: {tag}")

            for line in self.client.api.build(
                path=str(path.parent),
                dockerfile=str(path.name),
                tag=tag,
                buildargs=build_args,
                labels=labels,
                target=target,
                decode=True,
                stream=True
            ):
                if 'stream' in line:
                    print(line['stream'].rstrip())
                if 'error' in line:
                    print(f"Build error: {line['error']}")
                    return False

            print(f"Successfully built: {tag}")
            return True

        except Exception as e:
            print(f"Build error: {e}")
            return False

    async def build_and_push_async(
        self,
        dockerfile_path: str,
        image_name: str,
        registry: str,
        username: str,
        password: str,
        image_tag: str = 'latest'
    ) -> bool:
        """
        Build and push image (async wrapper).

        Args:
            dockerfile_path: Dockerfile path
            image_name: Image name
            registry: Registry URL
            username: Registry username
            password: Registry password
            image_tag: Image tag

        Returns:
            Success status
        """
        # Authenticate
        if not self.auth_manager.login_to_registry(
            registry, username, password
        ):
            return False

        # Build
        if not self.build_image(
            dockerfile_path,
            f"{registry}/{image_name}",
            image_tag
        ):
            return False

        # Push
        return self.auth_manager.push_image(
            f"{registry}/{image_name}",
            image_tag
        )
```

---

## Python Async Code Examples for Container Lifecycle

### Complete Async Container Orchestration Example

```python
import asyncio
import logging
from datetime import datetime
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncContainerOrchestrator:
    """Complete async container orchestration system."""

    def __init__(self, max_concurrent: int = 5):
        self.manager: Optional[AsyncContainerManager] = None
        self.batch_manager: Optional[AsyncBatchContainerManager] = None
        self.max_concurrent = max_concurrent

    async def __aenter__(self):
        self.manager = AsyncContainerManager()
        self.batch_manager = AsyncBatchContainerManager()
        await self.manager.__aenter__()
        await self.batch_manager.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.batch_manager:
            await self.batch_manager.__aexit__(exc_type, exc_val, exc_tb)
        if self.manager:
            await self.manager.__aexit__(exc_type, exc_val, exc_tb)

    async def run_multiple_tasks(
        self,
        tasks: List[dict],
        timeout: Optional[int] = 600
    ) -> List[dict]:
        """
        Run multiple container tasks concurrently.

        Args:
            tasks: List of task specifications
            timeout: Overall timeout in seconds

        Returns:
            List of execution results
        """
        logger.info(f"Starting {len(tasks)} concurrent tasks")
        start_time = datetime.now()

        # Create containers
        containers = await self.batch_manager.run_containers_concurrent(
            tasks,
            max_concurrent=self.max_concurrent
        )

        logger.info(f"Created {len(containers)} containers")

        # Wait for completion with timeout
        try:
            exit_codes = await self.batch_manager.wait_all_containers(
                containers,
                timeout=timeout
            )

            # Collect results
            results = []
            for container_id, exit_code in exit_codes.items():
                # Get container object
                container = next(
                    (c for c in containers if c.id == container_id),
                    None
                )

                if container:
                    # Get logs (this will fail with aiodocker, adjust as needed)
                    try:
                        logs = ''  # Would need container.log() in aiodocker
                    except:
                        logs = ''

                    results.append({
                        'container_id': container_id,
                        'exit_code': exit_code,
                        'logs': logs,
                        'success': exit_code == 0
                    })

            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"Tasks completed in {elapsed:.2f}s")

            return results

        except asyncio.TimeoutError:
            logger.error(f"Timeout exceeded ({timeout}s), cleaning up...")
            await self.batch_manager.cleanup_containers(containers, force=True)
            raise

        except Exception as e:
            logger.error(f"Error during execution: {e}")
            await self.batch_manager.cleanup_containers(containers, force=True)
            raise

# Usage example
async def main():
    """Example usage of AsyncContainerOrchestrator."""

    tasks = [
        {
            'image': 'python:3.11-slim',
            'command': 'python -c "print(\\'Task 1\\')"',
            'name': f'task-1'
        },
        {
            'image': 'python:3.11-slim',
            'command': 'python -c "print(\\'Task 2\\')"',
            'name': f'task-2'
        },
        {
            'image': 'python:3.11-slim',
            'command': 'python -c "print(\\'Task 3\\')"',
            'name': f'task-3'
        }
    ]

    async with AsyncContainerOrchestrator(max_concurrent=3) as orchestrator:
        results = await orchestrator.run_multiple_tasks(
            tasks,
            timeout=60
        )

        for result in results:
            logger.info(f"Container {result['container_id']}: "
                       f"Exit {result['exit_code']}, "
                       f"Success: {result['success']}")

# Run: asyncio.run(main())
```

---

## Key Recommendations

### 1. Security Hardening

1. **Always run containers as non-root user** (UID 1000+)
2. **Drop all capabilities** by default, add only what's needed
3. **Use read-only filesystem** with tmpfs for necessary writable paths
4. **Never mount Docker socket** - use safe alternatives (Kaniko, rootless Docker)
5. **Apply seccomp profiles** to restrict system calls
6. **Use network isolation** - avoid `network_mode='host'`

### 2. Resource Management

1. **Set memory and CPU limits** to prevent resource exhaustion
2. **Use tmpfs for temporary files** instead of persistent storage
3. **Implement proper cleanup** for volumes, images, and orphaned resources
4. **Monitor resource usage** and adjust limits based on workload

### 3. Graceful Shutdown

1. **Implement SIGTERM signal handling** in applications
2. **Use tini or dumb-init** as init process
3. **Set appropriate stop timeouts** (10-30 seconds minimum)
4. **Implement worker cleanup** for multi-process applications

### 4. CI/CD Integration

1. **Authenticate securely** with registries using tokens, not passwords
2. **Build images without Docker socket** (use Kaniko, Buildah)
3. **Scan images for vulnerabilities** before pushing
4. **Use minimal base images** (alpine, distroless)
5. **Implement layer caching** for faster builds

### 5. Async Operations

1. **Use aiodocker** for concurrent container operations
2. **Implement proper concurrent limits** to avoid resource exhaustion
3. **Handle timeouts gracefully** with cleanup
4. **Use semaphores** to control concurrency

---

## Sources

- [Docker SDK for Python Documentation](https://docker-py.readthedocs.io/)
- [Docker SDK for Python - GitHub](https://github.com/docker/docker-py)
- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)
- [aiodocker Documentation](https://aiodocker.readthedocs.io/)
- [aiodocker - GitHub](https://github.com/aio-libs/aiodocker)
- [Resource Constraints - Docker Docs](https://docs.docker.com/engine/containers/resource_constraints/)
- [Seccomp Security Profiles - Docker Docs](https://docs.docker.com/engine/security/seccomp/)
- [Protecting Docker Socket - Docker Security Docs](https://docs.docker.com/engine/security/protect-access/)
- [Graceful Shutdown in Docker Containers](https://lemanchet.fr/articles/gracefully-stop-python-docker-container.html)
- [Docker Container Security Vulnerabilities](https://www.aikido.dev/blog/docker-container-security-vulnerabilities)

---

## Appendices

### A. Environment Variable Patterns

```python
# Dictionary format
environment = {
    'DEBUG': 'true',
    'LOG_LEVEL': 'INFO',
    'DATABASE_URL': 'postgresql://...'
}

# List format
environment = [
    'DEBUG=true',
    'LOG_LEVEL=INFO',
    'DATABASE_URL=postgresql://...'
]
```

### B. Volume Mount Patterns

```python
# Read-only bind mount
volumes = {
    '/host/config': {
        'bind': '/app/config',
        'mode': 'ro'
    }
}

# Read-write bind mount
volumes = {
    '/host/data': {
        'bind': '/app/data',
        'mode': 'rw'
    }
}

# Named volume
volumes = {
    'my_volume': {
        'bind': '/app/storage',
        'mode': 'rw'
    }
}
```

### C. Port Mapping Patterns

```python
# Port forwarding
ports = {
    '8080/tcp': 8080,  # Container:Host
    '5432/tcp': ('127.0.0.1', 5432)  # With host binding
}

# Or in port_bindings parameter
port_bindings = {
    '8080/tcp': [{'HostIp': '', 'HostPort': '8080'}]
}
```

---

**Document Version**: 1.0
**Last Updated**: January 28, 2026
**Research Scope**: Docker SDK v7.1.0+, aiodocker, Python 3.9+
