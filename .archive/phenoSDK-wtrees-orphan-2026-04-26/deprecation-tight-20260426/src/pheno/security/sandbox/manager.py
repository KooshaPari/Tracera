"""High-level sandbox manager that mirrors Morph's original infrastructure module.

This module centralises sandbox configuration, path validation, permission checks, and
execution helpers so application code can depend on a single SDK surface.
"""

from __future__ import annotations

import datetime
import hashlib
import os
import stat
import subprocess
import tempfile
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pheno.logging.core.logger import get_logger

if TYPE_CHECKING:
    from collections.abc import Iterator

logger = get_logger("pheno.security.sandbox.manager")


# ---------------------------------------------------------------------------
# Dataclass definitions
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class PermissionResult:
    """
    Result of a permission check.
    """

    allowed: bool
    reason: str | None = None
    risk_level: str = "low"  # low, medium, high, critical
    warnings: list[str] = field(default_factory=list)
    alternative_path: str | None = None


@dataclass(slots=True)
class SandboxSecuritySettings:
    """
    Security configuration used by the sandbox manager.
    """

    allowed_paths: list[str] = field(default_factory=lambda: [str(Path.cwd())])
    blocked_paths: list[str] = field(default_factory=lambda: ["/etc", "/sys", "/proc", "/dev"])
    allowed_extensions: set[str] = field(
        default_factory=lambda: {
            ".py",
            ".json",
            ".yaml",
            ".yml",
            ".txt",
            ".md",
            ".ts",
            ".js",
            ".css",
            ".html",
            ".csv",
        },
    )
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_files_accessed: int = 1000
    max_execution_time: int = 300  # seconds
    max_memory_mb: int = 1024
    max_network_connections: int = 10
    sandbox_mode: bool = True
    require_confirmation: bool = True


@dataclass(slots=True)
class SandboxResourceLimits:
    """
    Resource limits for sandboxed operations.
    """

    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_files_accessed: int = 1000
    max_execution_time: int = 300  # 5 minutes
    max_memory_mb: int = 1024
    max_network_connections: int = 10


@dataclass(slots=True)
class SandboxContext:
    """
    Context for sandboxed operations.
    """

    operation_id: str
    workspace: Path
    allowed_paths: set[str]
    blocked_paths: set[str]
    file_operations: set[str] = field(default_factory=set)
    network_allowed: bool = True
    execution_time_limit: int = 300
    created_at: datetime.datetime = field(default_factory=datetime.datetime.now)


# ---------------------------------------------------------------------------
# Path validation
# ---------------------------------------------------------------------------


class PathSecurityValidator:
    """
    Validates file paths against security policies.
    """

    def __init__(self, settings: SandboxSecuritySettings):
        self.settings = settings
        self.logger = get_logger("pheno.security.sandbox.path_security")

        # Dangerous path patterns that should never be accessed.
        self.dangerous_patterns = [
            r"\.\./.*",  # Directory traversal
            r"^~[^/]",  # Home directory expansion (except ~user)
            r"/etc/.*",  # System configuration
            r"/proc/.*",  # Process filesystem
            r"/sys/.*",  # System filesystem
            r"/dev/.*",  # Device files
        ]

        # Sensitive file patterns that warrant warnings.
        self.sensitive_patterns = [
            r".*\.pem$",
            r".*\.key$",
            r".*\.p12$",
            r".*\.(ssh|rsa|dsa)_id$",
            r".*\.gnupg/.*",
            r"\.env(\.|$)",
            r"config\.json$",
            r"credentials\.",
            r"secrets\.",
            r"\.vault",
        ]

        import re

        self._compiled_dangerous = [re.compile(p) for p in self.dangerous_patterns]
        self._compiled_sensitive = [re.compile(p) for p in self.sensitive_patterns]

    def validate_path(self, path: str | Path, operation: str = "read") -> PermissionResult:
        """
        Validate a file path against security policies.
        """
        target = Path(path)
        result = PermissionResult(allowed=True)

        try:
            abs_path = target.resolve()
            path_str = str(abs_path)

            # Reject dangerous paths outright.
            for pattern in self._compiled_dangerous:
                if pattern.search(path_str):
                    result.allowed = False
                    result.reason = f"Path matches dangerous pattern: {pattern.pattern}"
                    result.risk_level = "critical"
                    return result

            # Flag sensitive paths.
            for pattern in self._compiled_sensitive:
                if pattern.search(path_str):
                    result.warnings.append(f"Accessing potentially sensitive file: {path_str}")
                    result.risk_level = "high"

            # Check blocked directories.
            for blocked in self.settings.blocked_paths:
                blocked_path = Path(blocked).resolve()
                if abs_path.is_relative_to(blocked_path):
                    result.allowed = False
                    result.reason = f"Path is in blocked directory: {blocked}"
                    result.risk_level = "high"
                    return result

            # Check allowed directories.
            allowed = False
            for allowed_dir in self.settings.allowed_paths:
                allowed_path = Path(allowed_dir).resolve()
                if abs_path.is_relative_to(allowed_path):
                    allowed = True
                    break

            if not allowed:
                result.allowed = False
                result.reason = "Path not in allowed directories"
                result.risk_level = "medium"
                workspace_safe = Path("workspace") / target.name
                if not workspace_safe.exists():
                    result.alternative_path = str(workspace_safe)

            # Enforce extension allowlist if file exists.
            if (
                abs_path.suffix
                and self.settings.allowed_extensions
                and abs_path.suffix not in self.settings.allowed_extensions
            ):
                result.warnings.append(f"File extension not in allowlist: {abs_path.suffix}")
                result.risk_level = "medium"

            if abs_path.exists() and abs_path.is_file():
                size = abs_path.stat().st_size
                if size > self.settings.max_file_size:
                    result.allowed = False
                    result.reason = (
                        f"File too large: {size} bytes (max: {self.settings.max_file_size})"
                    )
                    result.risk_level = "high"
                    return result

                file_stat = abs_path.stat()
                if operation in {"write", "execute"} and file_stat.st_mode & stat.S_IWOTH:
                    result.warnings.append("File is world-writable")
                    result.risk_level = "high"

        except Exception as exc:  # pragma: no cover - defensive logging
            result.allowed = False
            result.reason = f"Path validation error: {exc}"
            result.risk_level = "high"
            self.logger.exception("Path validation failed for %s: %s", path, exc)

        return result

    def sanitize_path(self, path: str | Path, workspace: Path | None = None) -> Path:
        """
        Sanitize a path to be safe for use.
        """
        workspace = workspace or Path.cwd()
        target = Path(path)
        if not target.is_absolute():
            target = workspace / target

        parts: list[str] = []
        for part in target.resolve().parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part in {".", ""}:
                continue
            else:
                parts.append(part)

        return Path(*parts)


# ---------------------------------------------------------------------------
# Resource management helpers
# ---------------------------------------------------------------------------


class ResourceManager:
    """
    Manages resource usage for sandboxed operations.
    """

    def __init__(self, limits: SandboxResourceLimits):
        self.limits = limits
        self.logger = get_logger("pheno.security.sandbox.resources")
        self._file_access_count = 0
        self._start_time = datetime.datetime.now()
        self._lock = threading.Lock()

    def check_file_access(self, file_path: Path, operation: str) -> bool:
        """
        Check if file access is allowed.
        """
        with self._lock:
            self._file_access_count += 1

            if self._file_access_count > self.limits.max_files_accessed:
                self.logger.error("File access limit exceeded: %s", self._file_access_count)
                return False

            if file_path.exists() and file_path.is_file():
                size = file_path.stat().st_size
                if size > self.limits.max_file_size:
                    self.logger.error("File size limit exceeded: %s", size)
                    return False

            return True

    def check_time_limit(self) -> bool:
        """
        Check if execution time limit is exceeded.
        """
        elapsed = (datetime.datetime.now() - self._start_time).total_seconds()
        return elapsed < self.limits.max_execution_time

    def get_usage_stats(self) -> dict[str, Any]:
        """
        Get current resource usage statistics.
        """
        elapsed = (datetime.datetime.now() - self._start_time).total_seconds()
        return {
            "files_accessed": self._file_access_count,
            "elapsed_seconds": elapsed,
            "time_remaining": max(0, self.limits.max_execution_time - elapsed),
            "limit_files": self.limits.max_files_accessed,
            "limit_time": self.limits.max_execution_time,
        }


# ---------------------------------------------------------------------------
# Sandbox manager
# ---------------------------------------------------------------------------


class SandboxManager:
    """
    Main sandbox management system.
    """

    def __init__(self, settings: SandboxSecuritySettings | None = None):
        self.settings = settings or SandboxSecuritySettings()
        self.logger = get_logger("pheno.security.sandbox")
        self.path_validator = PathSecurityValidator(self.settings)
        self.resource_limits = SandboxResourceLimits(
            max_file_size=self.settings.max_file_size,
            max_files_accessed=self.settings.max_files_accessed,
            max_execution_time=self.settings.max_execution_time,
            max_memory_mb=self.settings.max_memory_mb,
            max_network_connections=self.settings.max_network_connections,
        )
        self.resource_manager = ResourceManager(self.resource_limits)
        self._active_contexts: dict[str, SandboxContext] = {}
        self._operation_history: list[dict[str, Any]] = []

    @contextmanager
    def create_sandbox(
        self,
        workspace: Path | None = None,
        operation_id: str | None = None,
    ) -> Iterator[SandboxContext]:
        """
        Create a sandboxed execution context.
        """
        workspace = workspace or Path.cwd()

        if operation_id is None:
            operation_id = hashlib.md5(
                f"{datetime.datetime.now().isoformat()}".encode(),
            ).hexdigest()[:8]

        context = SandboxContext(
            operation_id=operation_id,
            workspace=workspace.resolve(),
            allowed_paths=set(self.settings.allowed_paths),
            blocked_paths=set(self.settings.blocked_paths),
            execution_time_limit=self.resource_limits.max_execution_time,
        )

        self._active_contexts[operation_id] = context
        self.logger.info("Sandbox created: %s", operation_id)

        try:
            yield context
        finally:
            self._cleanup_sandbox(operation_id)

    def _cleanup_sandbox(self, operation_id: str) -> None:
        """
        Clean up sandbox context.
        """
        if operation_id in self._active_contexts:
            del self._active_contexts[operation_id]
            self.logger.debug("Sandbox cleaned up: %s", operation_id)

    def validate_file_operation(
        self,
        file_path: str | Path,
        operation: str = "read",
        context: SandboxContext | None = None,
    ) -> PermissionResult:
        """
        Validate a file operation within the sandbox.
        """
        path = Path(file_path)

        result = self.path_validator.validate_path(path, operation)

        # Additional checks for write operations.
        if operation == "write" and result.allowed:
            parent = path.parent
            parent_result = self.path_validator.validate_path(parent, "read")
            if not parent_result.allowed:
                result.allowed = False
                result.reason = f"Parent directory not accessible: {parent_result.reason}"
                result.risk_level = "high"

        # Enforce workspace boundaries when context provided.
        if context and result.allowed:
            abs_path = path.resolve()
            workspace_abs = context.workspace.resolve()

            if not abs_path.is_relative_to(workspace_abs):
                result.warnings.append(f"Operation outside workspace: {abs_path}")
                if self.settings.require_confirmation:
                    result.allowed = False
                    result.reason = "Operations outside workspace require confirmation"
                    result.risk_level = "medium"

        # Track resource limits.
        if result.allowed:
            if not self.resource_manager.check_file_access(path, operation):
                result.allowed = False
                result.reason = "Resource limits exceeded"
                result.risk_level = "high"

        self._log_operation(operation, str(path), result, context)
        return result

    def _log_operation(
        self,
        operation: str,
        path: str,
        result: PermissionResult,
        context: SandboxContext | None,
    ) -> None:
        """
        Log a file operation for audit trail.
        """
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "operation": operation,
            "path": path,
            "allowed": result.allowed,
            "reason": result.reason,
            "risk_level": result.risk_level,
            "warnings": list(result.warnings),
            "operation_id": context.operation_id if context else None,
        }
        self._operation_history.append(log_entry)

        if len(self._operation_history) > 10_000:
            self._operation_history = self._operation_history[-5_000:]

        log_method = self.logger.info if result.allowed else self.logger.warning
        log_method(
            "File operation %s: %s (%s)",
            "allowed" if result.allowed else "blocked",
            operation,
            path,
        )

        for warning in result.warnings:
            self.logger.warning("Security warning: %s", warning)

    def secure_temp_file(
        self,
        prefix: str = "pheno",
        suffix: str = "",
        context: SandboxContext | None = None,
    ) -> Path:
        """
        Create a secure temporary file.
        """
        temp_dir = Path(tempfile.gettempdir())
        temp_file = (
            temp_dir / f"{prefix}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{suffix}"
        )
        if suffix:
            temp_file = temp_file.with_suffix(f".{suffix}")

        result = self.validate_file_operation(temp_file, "write", context)
        if not result.allowed:
            if context:
                fallback = context.workspace / "tmp" / temp_file.name
                fallback.parent.mkdir(parents=True, exist_ok=True)
                return fallback
            raise PermissionError(f"Cannot create temp file: {result.reason}")

        temp_file.parent.mkdir(parents=True, exist_ok=True)
        return temp_file

    @contextmanager
    def execute_command(
        self,
        command: list[str],
        context: SandboxContext | None = None,
        cwd: Path | None = None,
    ) -> Iterator[subprocess.Popen[str]]:
        """
        Execute a command within the sandbox.
        """
        cwd = cwd or (context.workspace if context else Path.cwd())

        cwd_result = self.validate_file_operation(cwd, "execute", context)
        if not cwd_result.allowed:
            raise PermissionError(
                f"Working directory not allowed: {cwd_result.reason}",
            )

        env = os.environ.copy()
        if context:
            env["PHENO_OPERATION_ID"] = context.operation_id
            env["PHENO_WORKSPACE"] = str(context.workspace)

        process = subprocess.Popen(
            command,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        self.logger.info("Command executed: %s", " ".join(command))

        try:
            yield process
        finally:
            if process.poll() is None:  # pragma: no cover - defensive cleanup
                process.terminate()

    def get_operation_history(
        self,
        operation_id: str | None = None,
        minutes: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get operation history for monitoring.
        """
        history = list(self._operation_history)

        if operation_id:
            history = [entry for entry in history if entry.get("operation_id") == operation_id]

        if minutes:
            cutoff = datetime.datetime.now() - datetime.timedelta(minutes=minutes)
            history = [
                entry
                for entry in history
                if datetime.datetime.fromisoformat(entry["timestamp"]) >= cutoff
            ]

        return sorted(history, key=lambda entry: entry["timestamp"], reverse=True)

    def generate_security_report(self) -> dict[str, Any]:
        """
        Generate a security summary.
        """
        recent_operations = self.get_operation_history(minutes=60)
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "active_sandboxes": len(self._active_contexts),
            "operations_last_hour": len(recent_operations),
            "blocked_operations": len([o for o in recent_operations if not o["allowed"]]),
            "high_risk_operations": len(
                [o for o in recent_operations if o["risk_level"] == "high"],
            ),
            "critical_risk_operations": len(
                [o for o in recent_operations if o["risk_level"] == "critical"],
            ),
            "recent_warnings": sum(1 for o in recent_operations if o["warnings"]),
            "security_config": {
                "sandbox_mode": self.settings.sandbox_mode,
                "require_confirmation": self.settings.require_confirmation,
                "allowed_paths_count": len(self.settings.allowed_paths),
                "blocked_paths_count": len(self.settings.blocked_paths),
            },
        }


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------

_sandbox_manager: SandboxManager | None = None


def get_sandbox_manager(
    *,
    settings: SandboxSecuritySettings | None = None,
) -> SandboxManager:
    """
    Get the global sandbox manager instance.
    """
    global _sandbox_manager
    if _sandbox_manager is None or settings is not None:
        _sandbox_manager = SandboxManager(settings=settings)
    return _sandbox_manager


@contextmanager
def secure_file_access(
    file_path: str | Path,
    operation: str = "read",
    sandbox_manager: SandboxManager | None = None,
) -> Iterator[SandboxContext]:
    """
    Context manager for secure file access.
    """
    manager = sandbox_manager or get_sandbox_manager()
    with manager.create_sandbox() as context:
        result = manager.validate_file_operation(file_path, operation, context)
        if not result.allowed:
            raise PermissionError(f"File operation not allowed: {result.reason}")
        yield context


def validate_path_security(
    path: str | Path,
    operation: str = "read",
    *,
    sandbox_manager: SandboxManager | None = None,
) -> PermissionResult:
    """
    Validate path security using the global sandbox manager.
    """
    manager = sandbox_manager or get_sandbox_manager()
    return manager.validate_file_operation(path, operation)


@contextmanager
def sandbox_execution(
    workspace: Path | None = None,
    *,
    sandbox_manager: SandboxManager | None = None,
) -> Iterator[SandboxContext]:
    """
    Context manager for sandboxed execution.
    """
    manager = sandbox_manager or get_sandbox_manager()
    with manager.create_sandbox(workspace=workspace) as context:
        yield context


__all__ = [
    "PathSecurityValidator",
    "PermissionResult",
    "ResourceManager",
    "SandboxContext",
    "SandboxManager",
    "SandboxResourceLimits",
    "SandboxSecuritySettings",
    "get_sandbox_manager",
    "sandbox_execution",
    "secure_file_access",
    "validate_path_security",
]
