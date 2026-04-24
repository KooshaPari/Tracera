"""Docker container orchestration for QA Integration (STORY-002).

Manages container lifecycle for test/recording executions.
Uses Docker CLI via subprocess to avoid extra dependency.
"""

from __future__ import annotations

import asyncio
import os
import subprocess
from pathlib import Path
from typing import Any


class DockerOrchestratorError(Exception):
    """Raised when Docker operations fail."""


class DockerOrchestrator:
    """Orchestrates Docker containers for execution runs."""

    def __init__(self, docker_host: str | None = None) -> None:
        """Initialize orchestrator.

        Args:
            docker_host: DOCKER_HOST override (e.g. unix:///var/run/docker.sock).
        """
        self._docker_host = docker_host or os.getenv("DOCKER_HOST", "")

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        if self._docker_host:
            env["DOCKER_HOST"] = self._docker_host
        return env

    async def _run(self, *args: str, timeout: int = 120) -> tuple[int, str, str]:
        """Run docker CLI; returns (returncode, stdout, stderr)."""
        cmd = ["docker", *list(args)]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self._env(),
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except TimeoutError as e:
            proc.kill()
            await proc.wait()
            msg = f"Docker command timed out after {timeout}s: {' '.join(cmd)}"
            raise DockerOrchestratorError(msg) from e
        return proc.returncode or 0, stdout.decode(), stderr.decode()

    async def is_available(self) -> bool:
        """Return True if Docker daemon is reachable."""
        code, _, stderr = await self._run("info", timeout=10)
        return code == 0 and "Cannot connect" not in stderr

    async def create_and_start(
        self,
        image: str,
        *,
        project_id: str,
        execution_id: str,
        mount_source: Path | str | None = None,
        mount_target: str = "/workspace",
        read_only_mount: bool = True,
        env_vars: dict[str, str] | None = None,
        working_dir: str | None = None,
        network_mode: str = "bridge",
        resource_limits: dict[str, Any] | None = None,
        command: list[str] | None = None,
        timeout: int = 600,
    ) -> str:
        """Create and start a container; return container ID.

        Args:
            image: Docker image (e.g. node:20-alpine).
            project_id: Project ID (for container label).
            execution_id: Execution ID (for container label).
            mount_source: Host path to mount (e.g. project dir).
            mount_target: Path inside container.
            read_only_mount: Mount read-only if True.
            env_vars: Environment variables to set.
            working_dir: Working directory in container.
            network_mode: Docker network mode.
            resource_limits: Optional CPU/memory limits (e.g. {"memory": "512m"}).
            command: Override CMD (default: keep image CMD).
            timeout: Max seconds to wait for start.

        Returns:
            Container ID (12-char short id).

        Raises:
            DockerOrchestratorError: If create/start fails.
        """
        args = [
            "run",
            "-d",
            "--rm",
            "--label",
            f"tracertm.project={project_id}",
            "--label",
            f"tracertm.execution={execution_id}",
            "--network",
            network_mode,
        ]
        if mount_source:
            path = Path(mount_source).resolve()
            if path.exists():
                ro = ":ro" if read_only_mount else ""
                args.extend(["-v", f"{path!s}:{mount_target}{ro}"])
        if env_vars:
            for k, v in env_vars.items():
                args.extend(["-e", f"{k}={v}"])
        if working_dir:
            args.extend(["-w", working_dir])
        if resource_limits:
            if "memory" in resource_limits:
                args.extend(["--memory", str(resource_limits["memory"])])
            if "cpus" in resource_limits:
                args.extend(["--cpus", str(resource_limits["cpus"])])
        args.append(image)
        if command:
            args.extend(command)

        code, stdout, stderr = await self._run(*args, timeout=timeout)
        if code != 0:
            msg = f"Docker run failed: {stderr.strip() or stdout.strip()}"
            raise DockerOrchestratorError(msg)
        return stdout.strip()[:12]

    async def stop(self, container_id: str, timeout: int = 30) -> None:
        """Stop a running container (SIGTERM then SIGKILL)."""
        code, _, stderr = await self._run("stop", "-t", str(timeout), container_id, timeout=timeout + 5)
        if code != 0 and "No such container" not in stderr:
            msg = f"Docker stop failed: {stderr.strip()}"
            raise DockerOrchestratorError(msg)

    async def exec(
        self,
        container_id: str,
        cmd: list[str],
        *,
        timeout: int = 300,
    ) -> tuple[int, str, str]:
        """Run a command inside a running container. Returns (exit_code, stdout, stderr)."""
        args = ["exec", container_id, *cmd]
        code, stdout, stderr = await self._run(*args, timeout=timeout)
        return code, stdout, stderr

    async def copy_from(
        self,
        container_id: str,
        container_path: str,
        host_path: Path | str,
        timeout: int = 60,
    ) -> None:
        """Copy a file/dir from container to host (docker cp)."""
        host_path = Path(host_path).resolve()
        host_path.parent.mkdir(parents=True, exist_ok=True)
        code, _, stderr = await self._run("cp", f"{container_id}:{container_path}", str(host_path), timeout=timeout)
        if code != 0:
            msg = f"Docker cp failed: {stderr.strip()}"
            raise DockerOrchestratorError(msg)
