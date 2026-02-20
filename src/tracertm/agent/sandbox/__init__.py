"""Sandbox providers: local filesystem and (future) Vercel."""

from tracertm.agent.sandbox.base import SandboxProvider
from tracertm.agent.sandbox.local_fs import LocalFilesystemSandboxProvider

__all__ = [
    "LocalFilesystemSandboxProvider",
    "SandboxProvider",
]
