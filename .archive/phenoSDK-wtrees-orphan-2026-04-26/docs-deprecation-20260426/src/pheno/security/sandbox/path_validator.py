"""
Path validation and sanitization utilities.
"""

from __future__ import annotations

import os
import re
import urllib.parse
from dataclasses import dataclass
from pathlib import Path

from pheno.logging.core.logger import get_logger

logger = get_logger("pheno.security.sandbox.path_validator")


@dataclass(slots=True)
class PathValidationConfig:
    """
    Configuration for path validation.
    """

    # Allowed patterns
    allowed_patterns: list[str] = None
    blocked_patterns: list[str] = None

    # Path restrictions
    max_path_length: int = 4096
    allow_absolute_paths: bool = False
    allow_symlinks: bool = False
    allow_hidden_files: bool = False

    # Directory traversal prevention
    prevent_traversal: bool = True
    traversal_patterns: list[str] = None

    # File extensions
    allowed_extensions: set[str] = None
    blocked_extensions: set[str] = None

    # Base directories
    allowed_base_dirs: list[str] = None
    restricted_dirs: list[str] = None

    def __post_init__(self):
        if self.allowed_patterns is None:
            self.allowed_patterns = []
        if self.blocked_patterns is None:
            self.blocked_patterns = []
        if self.traversal_patterns is None:
            self.traversal_patterns = [
                "../",
                "..\\",
                "..%2f",
                "..%5c",
                "%2e%2e%2f",
                "%2e%2e%5c",
                "....//",
                "....\\\\",
                "..%252f",
                "..%255c",
            ]
        if self.allowed_extensions is None:
            self.allowed_extensions = set()
        if self.blocked_extensions is None:
            self.blocked_extensions = {".exe", ".bat", ".cmd", ".com", ".scr", ".pif"}
        if self.allowed_base_dirs is None:
            self.allowed_base_dirs = []
        if self.restricted_dirs is None:
            self.restricted_dirs = ["/etc", "/sys", "/proc", "/dev", "C:\\Windows", "C:\\System32"]


class PathValidationError(Exception):
    """
    Base exception for path validation errors.
    """



class TraversalAttemptError(PathValidationError):
    """
    Raised when directory traversal is detected.
    """

    def __init__(self, path: str, pattern: str):
        self.path = path
        self.pattern = pattern
        super().__init__(
            f"Directory traversal attempt detected in path '{path}' with pattern '{pattern}'",
        )


class InvalidPathError(PathValidationError):
    """
    Raised when path is invalid.
    """

    def __init__(self, path: str, reason: str):
        self.path = path
        self.reason = reason
        super().__init__(f"Invalid path '{path}': {reason}")


class PathValidator:
    """
    Validates and sanitizes file paths for security.
    """

    def __init__(self, config: PathValidationConfig | None = None):
        self.config = config or PathValidationConfig()
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> dict:
        """
        Compile regex patterns for performance.
        """
        return {
            "allowed": [re.compile(pattern) for pattern in self.config.allowed_patterns],
            "blocked": [re.compile(pattern) for pattern in self.config.blocked_patterns],
            "traversal": [
                re.compile(re.escape(pattern), re.IGNORECASE)
                for pattern in self.config.traversal_patterns
            ],
        }

    def validate_path(self, path: str | Path) -> Path:
        """
        Validate and sanitize a path.
        """
        if isinstance(path, str):
            path = Path(path)

        path_str = str(path)

        # Basic validation
        self._validate_basic(path_str)

        # Check for traversal attempts
        if self.config.prevent_traversal:
            self._check_traversal(path_str)

        # Check patterns
        self._check_patterns(path_str)

        # Check extensions
        self._check_extensions(path)

        # Check base directories
        self._check_base_directories(path)

        # Check path length
        if len(path_str) > self.config.max_path_length:
            raise InvalidPathError(
                path_str, f"Path too long (>{self.config.max_path_length} chars)",
            )

        # Resolve and normalize path
        try:
            resolved_path = path.resolve()
        except (OSError, ValueError) as e:
            raise InvalidPathError(path_str, f"Cannot resolve path: {e}")

        # Check for symlinks if not allowed
        if not self.config.allow_symlinks and self._is_symlink(resolved_path):
            raise InvalidPathError(path_str, "Symlinks not allowed")

        # Check for hidden files if not allowed
        if not self.config.allow_hidden_files and self._is_hidden(resolved_path):
            raise InvalidPathError(path_str, "Hidden files not allowed")

        return resolved_path

    def sanitize_path(self, path: str | Path) -> Path:
        """
        Sanitize a path by removing dangerous elements.
        """
        if isinstance(path, str):
            path = Path(path)

        # URL decode if needed
        path_str = urllib.parse.unquote(str(path))
        path = Path(path_str)

        # Remove traversal patterns
        if self.config.prevent_traversal:
            path_str = self._remove_traversal_patterns(str(path))
            path = Path(path_str)

        # Normalize path separators
        path_str = str(path).replace("\\", "/")
        path = Path(path_str)

        # Remove double slashes
        path_str = re.sub(r"/+", "/", str(path))
        return Path(path_str)


    def is_safe_path(self, path: str | Path) -> bool:
        """
        Check if a path is safe without raising exceptions.
        """
        try:
            self.validate_path(path)
            return True
        except PathValidationError:
            return False

    def _validate_basic(self, path_str: str) -> None:
        """
        Basic path validation.
        """
        if not path_str:
            raise InvalidPathError(path_str, "Empty path")

        # Check for null bytes
        if "\x00" in path_str:
            raise InvalidPathError(path_str, "Null bytes not allowed")

        # Check for absolute paths if not allowed
        if not self.config.allow_absolute_paths and os.path.isabs(path_str):
            raise InvalidPathError(path_str, "Absolute paths not allowed")

    def _check_traversal(self, path_str: str) -> None:
        """
        Check for directory traversal attempts.
        """
        for pattern in self._compiled_patterns["traversal"]:
            if pattern.search(path_str):
                raise TraversalAttemptError(path_str, pattern.pattern)

        # Additional checks for encoded patterns
        decoded_path = urllib.parse.unquote(path_str)
        for pattern in self._compiled_patterns["traversal"]:
            if pattern.search(decoded_path):
                raise TraversalAttemptError(path_str, f"Encoded traversal: {pattern.pattern}")

    def _check_patterns(self, path_str: str) -> None:
        """
        Check path against allowed/blocked patterns.
        """
        # Check blocked patterns first
        for pattern in self._compiled_patterns["blocked"]:
            if pattern.search(path_str):
                raise InvalidPathError(path_str, f"Path matches blocked pattern: {pattern.pattern}")

        # Check allowed patterns if any are defined
        if self._compiled_patterns["allowed"]:
            matches_allowed = any(
                pattern.search(path_str) for pattern in self._compiled_patterns["allowed"]
            )
            if not matches_allowed:
                raise InvalidPathError(path_str, "Path does not match any allowed patterns")

    def _check_extensions(self, path: Path) -> None:
        """
        Check file extensions.
        """
        if not path.suffix:
            return

        extension = path.suffix.lower()

        # Check blocked extensions
        if extension in self.config.blocked_extensions:
            raise InvalidPathError(str(path), f"File extension '{extension}' is blocked")

        # Check allowed extensions if any are defined
        if self.config.allowed_extensions and extension not in self.config.allowed_extensions:
            raise InvalidPathError(str(path), f"File extension '{extension}' is not allowed")

    def _check_base_directories(self, path: Path) -> None:
        """
        Check if path is within allowed base directories.
        """
        if not self.config.allowed_base_dirs:
            return

        try:
            resolved_path = path.resolve()
        except (OSError, ValueError):
            return  # Will be caught by other validations

        # Check if path is within any allowed base directory
        is_allowed = False
        for base_dir in self.config.allowed_base_dirs:
            try:
                base_path = Path(base_dir).resolve()
                if resolved_path.is_relative_to(base_path):
                    is_allowed = True
                    break
            except (OSError, ValueError):
                continue

        if not is_allowed:
            raise InvalidPathError(str(path), "Path is not within allowed base directories")

        # Check if path is within restricted directories
        for restricted_dir in self.config.restricted_dirs:
            try:
                restricted_path = Path(restricted_dir).resolve()
                if resolved_path.is_relative_to(restricted_path):
                    raise InvalidPathError(
                        str(path), f"Path is within restricted directory: {restricted_dir}",
                    )
            except (OSError, ValueError):
                continue

    def _remove_traversal_patterns(self, path_str: str) -> str:
        """
        Remove traversal patterns from path.
        """
        result = path_str

        for pattern in self.config.traversal_patterns:
            result = result.replace(pattern, "")

        # Remove multiple slashes
        return re.sub(r"/+", "/", result)


    def _is_symlink(self, path: Path) -> bool:
        """
        Check if path is a symlink.
        """
        try:
            return path.is_symlink()
        except (OSError, ValueError):
            return False

    def _is_hidden(self, path: Path) -> bool:
        """
        Check if path is hidden.
        """
        try:
            return any(part.startswith(".") for part in path.parts)
        except (OSError, ValueError):
            return False

    def get_relative_path(self, path: str | Path, base_dir: str | Path) -> Path:
        """
        Get relative path from base directory.
        """
        path = Path(path)
        base_dir = Path(base_dir)

        try:
            resolved_path = path.resolve()
            resolved_base = base_dir.resolve()

            if not resolved_path.is_relative_to(resolved_base):
                raise InvalidPathError(str(path), "Path is not within base directory")

            return resolved_path.relative_to(resolved_base)

        except (OSError, ValueError) as e:
            raise InvalidPathError(str(path), f"Cannot get relative path: {e}")

    def create_safe_path(self, base_dir: str | Path, *path_parts: str) -> Path:
        """
        Create a safe path by joining parts.
        """
        base_dir = Path(base_dir)

        # Validate each part
        safe_parts = []
        for part in path_parts:
            if not part:
                continue

            # Basic validation for each part
            if ".." in part or "/" in part or "\\" in part:
                raise InvalidPathError(part, "Path part contains dangerous characters")

            if part.startswith("."):
                raise InvalidPathError(part, "Path part starts with dot")

            safe_parts.append(part)

        # Join parts
        full_path = base_dir / Path(*safe_parts)

        # Validate the complete path
        return self.validate_path(full_path)
