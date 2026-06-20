"""Sandbox provider interface.

Implementations: LocalFilesystemSandboxProvider (first), optional Vercel later.
"""

from typing import Any, Protocol

from tracertm.agent.types import SandboxConfig, SandboxMetadata


class SandboxProvider(Protocol):
    """Protocol for sandbox lifecycle: create, exec, write, cleanup."""

    async def create_sandbox(self, config: SandboxConfig, session_id: str) -> SandboxMetadata:
        """Create a sandbox for the given session. Returns metadata with sandbox_id and sandbox_root."""
        ...

    async def execute_command(self, sandbox_id: str, command: str) -> dict[str, Any]:
        """Execute a command inside the sandbox. Returns result dict (e.g. stdout, stderr, returncode)."""
        ...

    async def write_file(self, sandbox_id: str, path: str, content: str) -> dict[str, Any]:
        """Write content to a file under the sandbox root. Path is relative to sandbox root."""
        ...

    async def cleanup_sandbox(self, sandbox_id: str) -> bool:
        """Clean up and optionally destroy the sandbox. Returns True if cleaned."""
        ...
