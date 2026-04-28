"""
Security sandbox implementation.
"""

from __future__ import annotations

import os
import shutil
import sys
import tempfile
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

from .path_validator import PathValidationConfig, PathValidator
from .permission_checker import PermissionChecker, PermissionConfig

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger("pheno.security.sandbox.sandbox")


@dataclass(slots=True)
class SandboxConfig:
    """
    Configuration for security sandbox.
    """

    # Path validation
    path_config: PathValidationConfig | None = None

    # Permission checking
    permission_config: PermissionConfig | None = None

    # Resource limits
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_files: int = 1000
    max_directories: int = 100

    # Isolation
    isolated_filesystem: bool = True
    temp_dir: str | None = None

    # Security
    allow_network: bool = False
    allow_subprocess: bool = False
    allow_imports: list[str] = None

    def __post_init__(self):
        if self.path_config is None:
            self.path_config = PathValidationConfig()
        if self.permission_config is None:
            self.permission_config = PermissionConfig()
        if self.allow_imports is None:
            self.allow_imports = []


class SandboxError(Exception):
    """
    Base exception for sandbox errors.
    """



class SandboxViolationError(SandboxError):
    """
    Raised when sandbox security is violated.
    """



class ResourceLimitError(SandboxError):
    """
    Raised when resource limits are exceeded.
    """



class SecuritySandbox:
    """
    Security sandbox for safe code execution.
    """

    def __init__(self, config: SandboxConfig | None = None):
        self.config = config or SandboxConfig()
        self.path_validator = PathValidator(self.config.path_config)
        self.permission_checker = PermissionChecker(self.config.permission_config)
        self._temp_dir: str | None = None
        self._original_cwd: str | None = None
        self._original_modules = set(sys.modules.keys())

    def __enter__(self):
        """
        Enter sandbox context.
        """
        self._setup_sandbox()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit sandbox context.
        """
        self._cleanup_sandbox()

    def _setup_sandbox(self) -> None:
        """
        Setup sandbox environment.
        """
        logger.debug("Setting up security sandbox")

        # Create temporary directory if needed
        if self.config.isolated_filesystem:
            self._temp_dir = tempfile.mkdtemp(prefix="pheno_sandbox_")
            self._original_cwd = os.getcwd()
            os.chdir(self._temp_dir)

        # Restrict imports if specified
        if self.config.allow_imports:
            self._restrict_imports()

    def _cleanup_sandbox(self) -> None:
        """
        Cleanup sandbox environment.
        """
        logger.debug("Cleaning up security sandbox")

        # Restore working directory
        if self._original_cwd:
            os.chdir(self._original_cwd)

        # Remove temporary directory
        if self._temp_dir and os.path.exists(self._temp_dir):
            shutil.rmtree(self._temp_dir, ignore_errors=True)

        # Restore modules
        self._restore_modules()

    def _restrict_imports(self) -> None:
        """
        Restrict module imports.
        """
        original_import = __builtins__["__import__"]

        def restricted_import(name, *args, **kwargs):
            if name not in self.config.allow_imports:
                raise SandboxViolationError(f"Import of '{name}' is not allowed")
            return original_import(name, *args, **kwargs)

        __builtins__["__import__"] = restricted_import

    def _restore_modules(self) -> None:
        """
        Restore original modules.
        """
        # Remove modules that were added during sandbox execution
        current_modules = set(sys.modules.keys())
        added_modules = current_modules - self._original_modules

        for module_name in added_modules:
            if module_name in sys.modules:
                del sys.modules[module_name]

    def execute_safely(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute function safely within sandbox.
        """
        with self:
            return func(*args, **kwargs)

    def validate_path(self, path: str | os.PathLike) -> str:
        """
        Validate path within sandbox.
        """
        validated_path = self.path_validator.validate_path(path)
        return str(validated_path)

    def check_permission(self, path: str | os.PathLike, permission: str) -> bool:
        """
        Check permission for path within sandbox.
        """
        from .permission_checker import Permission

        perm = Permission(permission)
        return self.permission_checker.check_permission(path, perm)

    def get_sandbox_info(self) -> dict[str, Any]:
        """
        Get information about sandbox state.
        """
        return {
            "temp_dir": self._temp_dir,
            "original_cwd": self._original_cwd,
            "isolated_filesystem": self.config.isolated_filesystem,
            "max_file_size": self.config.max_file_size,
            "max_files": self.config.max_files,
            "max_directories": self.config.max_directories,
            "allow_network": self.config.allow_network,
            "allow_subprocess": self.config.allow_subprocess,
            "allowed_imports": self.config.allow_imports,
        }
