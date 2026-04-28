"""
Secure file system operations.
"""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pheno.logging.core.logger import get_logger

from .path_validator import PathValidationConfig, PathValidator
from .permission_checker import PermissionChecker, PermissionConfig

if TYPE_CHECKING:
    from pathlib import Path

logger = get_logger("pheno.security.sandbox.file_system")


@dataclass(slots=True)
class FileSystemConfig:
    """
    Configuration for secure file system.
    """

    path_config: PathValidationConfig | None = None
    permission_config: PermissionConfig | None = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    allow_overwrite: bool = False
    create_directories: bool = True


class FileSystemError(Exception):
    """
    Base exception for file system errors.
    """



class FileAccessDeniedError(FileSystemError):
    """
    Raised when file access is denied.
    """



class SecureFileSystem:
    """
    Secure file system operations.
    """

    def __init__(self, config: FileSystemConfig | None = None):
        self.config = config or FileSystemConfig()
        self.path_validator = PathValidator(self.config.path_config)
        self.permission_checker = PermissionChecker(self.config.permission_config)

    def read_file(self, path: str | Path) -> str:
        """
        Read file securely.
        """
        validated_path = self.path_validator.validate_path(path)
        self.permission_checker.require_permission(validated_path, Permission.READ)

        try:
            with open(validated_path, encoding="utf-8") as f:
                return f.read()
        except PermissionError as e:
            raise FileAccessDeniedError(f"Read access denied for {path}: {e}")

    def write_file(self, path: str | Path, content: str) -> None:
        """
        Write file securely.
        """
        validated_path = self.path_validator.validate_path(path)

        # Check if file exists and overwrite is not allowed
        if validated_path.exists() and not self.config.allow_overwrite:
            raise FileSystemError(f"File {path} exists and overwrite is not allowed")

        self.permission_checker.require_permission(validated_path, Permission.WRITE)

        # Create directory if needed
        if self.config.create_directories:
            validated_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(validated_path, "w", encoding="utf-8") as f:
                f.write(content)
        except PermissionError as e:
            raise FileAccessDeniedError(f"Write access denied for {path}: {e}")

    def delete_file(self, path: str | Path) -> None:
        """
        Delete file securely.
        """
        validated_path = self.path_validator.validate_path(path)
        self.permission_checker.require_permission(validated_path, Permission.DELETE)

        try:
            validated_path.unlink()
        except PermissionError as e:
            raise FileAccessDeniedError(f"Delete access denied for {path}: {e}")

    def list_directory(self, path: str | Path) -> list[str]:
        """
        List directory contents securely.
        """
        validated_path = self.path_validator.validate_path(path)
        self.permission_checker.require_permission(validated_path, Permission.READ)

        try:
            return [item.name for item in validated_path.iterdir()]
        except PermissionError as e:
            raise FileAccessDeniedError(f"List access denied for {path}: {e}")

    def create_directory(self, path: str | Path) -> None:
        """
        Create directory securely.
        """
        validated_path = self.path_validator.validate_path(path)
        self.permission_checker.require_permission(validated_path, Permission.CREATE)

        try:
            validated_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            raise FileAccessDeniedError(f"Create access denied for {path}: {e}")

    def file_exists(self, path: str | Path) -> bool:
        """
        Check if file exists securely.
        """
        try:
            validated_path = self.path_validator.validate_path(path)
            return validated_path.exists()
        except Exception:
            return False

    def get_file_size(self, path: str | Path) -> int:
        """
        Get file size securely.
        """
        validated_path = self.path_validator.validate_path(path)
        self.permission_checker.require_permission(validated_path, Permission.READ)

        try:
            return validated_path.stat().st_size
        except PermissionError as e:
            raise FileAccessDeniedError(f"Access denied for {path}: {e}")

    def copy_file(self, src: str | Path, dst: str | Path) -> None:
        """
        Copy file securely.
        """
        src_path = self.path_validator.validate_path(src)
        dst_path = self.path_validator.validate_path(dst)

        self.permission_checker.require_permission(src_path, Permission.READ)
        self.permission_checker.require_permission(dst_path, Permission.WRITE)

        try:
            shutil.copy2(src_path, dst_path)
        except PermissionError as e:
            raise FileAccessDeniedError(f"Copy access denied: {e}")

    def move_file(self, src: str | Path, dst: str | Path) -> None:
        """
        Move file securely.
        """
        src_path = self.path_validator.validate_path(src)
        dst_path = self.path_validator.validate_path(dst)

        self.permission_checker.require_permission(src_path, Permission.READ)
        self.permission_checker.require_permission(dst_path, Permission.WRITE)

        try:
            shutil.move(str(src_path), str(dst_path))
        except PermissionError as e:
            raise FileAccessDeniedError(f"Move access denied: {e}")
