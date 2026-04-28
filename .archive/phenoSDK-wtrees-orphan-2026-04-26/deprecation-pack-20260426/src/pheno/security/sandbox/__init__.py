"""Pheno Security Sandbox Module.

This module provides comprehensive security sandboxing capabilities.
It consolidates generic security patterns that can be used across all projects in the Pheno ecosystem.

Key Features:
- Path validation and sanitization
- Permission checking and enforcement
- Directory traversal prevention
- File system access control
- Resource isolation
- Security policy enforcement
"""

from .file_system import (
    FileAccessDeniedError,
    FileSystemConfig,
    FileSystemError,
    SecureFileSystem,
)
from .manager import (
    PathSecurityValidator,
    PermissionResult,
    ResourceManager,
    SandboxContext,
    SandboxManager,
    SandboxResourceLimits,
    SandboxSecuritySettings,
    get_sandbox_manager,
    sandbox_execution,
    secure_file_access,
    validate_path_security,
)
from .path_validator import (
    InvalidPathError,
    PathValidationConfig,
    PathValidationError,
    PathValidator,
    TraversalAttemptError,
)
from .permission_checker import (
    AccessDeniedError,
    InsufficientPermissionsError,
    PermissionChecker,
    PermissionConfig,
    PermissionError,
)
from .policy import PolicyManager, PolicyRule, PolicyViolationError, SecurityPolicy
from .resource_limits import (
    ResourceExhaustedError,
    ResourceLimitConfig,
    ResourceLimits,
    ResourceMonitor,
)
from .sandbox import (
    ResourceLimitError,
    SandboxConfig,
    SandboxError,
    SandboxViolationError,
    SecuritySandbox,
)

__all__ = [
    "AccessDeniedError",
    "FileAccessDeniedError",
    "FileSystemConfig",
    "FileSystemError",
    "InsufficientPermissionsError",
    "InvalidPathError",
    "PathSecurityValidator",
    "PathValidationConfig",
    "PathValidationError",
    # Path validation
    "PathValidator",
    # Permission checking
    "PermissionChecker",
    "PermissionConfig",
    "PermissionError",
    # Manager facade
    "PermissionResult",
    "PolicyManager",
    "PolicyRule",
    "PolicyViolationError",
    "ResourceExhaustedError",
    "ResourceLimitConfig",
    "ResourceLimitError",
    # Resource limits
    "ResourceLimits",
    "ResourceManager",
    "ResourceMonitor",
    "SandboxConfig",
    "SandboxContext",
    "SandboxError",
    "SandboxManager",
    "SandboxResourceLimits",
    "SandboxSecuritySettings",
    "SandboxViolationError",
    # File system
    "SecureFileSystem",
    # Policy
    "SecurityPolicy",
    # Sandbox
    "SecuritySandbox",
    "TraversalAttemptError",
    "get_sandbox_manager",
    "sandbox_execution",
    "secure_file_access",
    "validate_path_security",
]

__version__ = "1.0.0"
