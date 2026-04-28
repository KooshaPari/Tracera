"""
Project type definitions.
"""

from __future__ import annotations

from enum import Enum


class ProjectType(Enum):
    """
    Types of projects supported by the command engine.
    """

    PYTHON = "python"
    NODE = "node"
    DOCKER = "docker"
    RUST = "rust"
    GO = "go"
    JAVA = "java"
    UNKNOWN = "unknown"


__all__ = ["ProjectType"]
