"""Local filesystem sandbox provider.

Creates one directory per session under a base path; all tool operations
(read_file, write_file, run_command) are scoped to that directory.
"""

import asyncio
import contextlib
import logging
import os
import tempfile
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tracertm.agent.types import (
    SandboxConfig,
    SandboxMetadata,
    SandboxStatus,
)

logger = logging.getLogger(__name__)


def _get_base_dir() -> str:
    """Base directory for session sandboxes. Env AGENT_SANDBOX_BASE_DIR or temp."""
    base = os.getenv("AGENT_SANDBOX_BASE_DIR", "").strip()
    if base:
        return base
    return str(Path(tempfile.gettempdir()) / "tracertm_agent_sandboxes")


class LocalFilesystemSandboxProvider:
    """Sandbox provider using local directories under a base path."""

    def __init__(self, base_dir: str | None = None) -> None:
        """Initialize the local filesystem sandbox provider.

        Args:
            base_dir: Optional base directory for sandboxes; defaults to env/temp.
        """
        self._base_dir = (base_dir or _get_base_dir()).rstrip("/")
        self._metadata: dict[str, SandboxMetadata] = {}

    def _session_dir(self, session_id: str) -> str:
        return str(Path(self._base_dir) / session_id)

    async def create_sandbox(self, config: SandboxConfig, session_id: str) -> SandboxMetadata:
        """Create a sandbox directory for the session. Reuses same path if already exists."""
        sandbox_id = session_id or str(uuid.uuid4())
        path = self._session_dir(sandbox_id)

        await asyncio.to_thread(os.makedirs, path, exist_ok=True)

        metadata = SandboxMetadata(
            sandbox_id=sandbox_id,
            status=SandboxStatus.READY,
            created_at=datetime.now(UTC),
            started_at=datetime.now(UTC),
            vcpus=config.vcpus,
            memory_mb=config.memory_mb,
            timeout_seconds=config.timeout_seconds,
            sandbox_root=path,
        )
        self._metadata[sandbox_id] = metadata
        logger.debug("Local sandbox created: %s at %s", sandbox_id, path)
        return metadata

    async def execute_command(self, sandbox_id: str, command: str) -> dict[str, Any]:
        """Run command in the sandbox root. Returns dict with stdout, stderr, returncode.

        The command string is safely parsed into arguments using shlex to prevent
        shell injection vulnerabilities while still supporting complex commands.
        """
        if sandbox_id not in self._metadata:
            msg = f"Sandbox not found: {sandbox_id}"
            raise ValueError(msg)
        root = self._metadata[sandbox_id].sandbox_root
        if not root:
            msg = f"Sandbox has no root: {sandbox_id}"
            raise ValueError(msg)

        def run() -> dict[str, str | int]:
            import shlex
            import subprocess

            # Safely parse command string into argument list without using shell=True
            try:
                cmd_args = shlex.split(command)
            except ValueError as e:
                # If parsing fails, return error
                return {
                    "stdout": "",
                    "stderr": f"Command parsing error: {e!s}",
                    "returncode": 1,
                }
            result = subprocess.run(
                cmd_args,
                shell=False,
                cwd=root,
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            return {
                "stdout": result.stdout or "",
                "stderr": result.stderr or "",
                "returncode": result.returncode,
            }

        return await asyncio.to_thread(run)

    async def write_file(self, sandbox_id: str, path: str, content: str) -> dict[str, Any]:
        """Write file under sandbox root. Path is relative to sandbox root."""
        if sandbox_id not in self._metadata:
            msg = f"Sandbox not found: {sandbox_id}"
            raise ValueError(msg)
        root = self._metadata[sandbox_id].sandbox_root
        if not root:
            msg = f"Sandbox has no root: {sandbox_id}"
            raise ValueError(msg)

        full = Path(root) / path.lstrip("/")

        def _path_escapes() -> bool:
            return not str(full.resolve()).startswith(str(Path(root).resolve()))

        if await asyncio.to_thread(_path_escapes):
            msg = "Path escapes sandbox root"
            raise ValueError(msg)

        def do_write() -> None:
            full.parent.mkdir(parents=True, exist_ok=True)
            full.write_text(content, encoding="utf-8")

        await asyncio.to_thread(do_write)
        return {"path": str(full), "written": len(content)}

    async def cleanup_sandbox(self, sandbox_id: str) -> bool:
        """Optionally remove sandbox directory. For persistence we can no-op and return True."""
        if sandbox_id not in self._metadata:
            return False
        metadata = self._metadata[sandbox_id]
        metadata.status = SandboxStatus.CLEANED
        metadata.completed_at = datetime.now(UTC)
        # Do not delete directory by default so chat/session can persist
        remove = os.getenv("AGENT_SANDBOX_CLEANUP_REMOVE_DIR", "").lower() in {"1", "true", "yes"}
        root = metadata.sandbox_root
        if remove and root is not None and await asyncio.to_thread(Path(root).is_dir):
            await asyncio.to_thread(_rmtree_safe, root)
        del self._metadata[sandbox_id]
        logger.debug("Sandbox cleaned: %s", sandbox_id)
        return True


def _rmtree_safe(path: str) -> None:
    import shutil

    with contextlib.suppress(OSError):
        shutil.rmtree(path, ignore_errors=True)
