"""
Permission checking and enforcement utilities.
"""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from pheno.logging.core.logger import get_logger

logger = get_logger("pheno.security.sandbox.permission_checker")


class Permission(Enum):
    """
    File system permissions.
    """

    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    DELETE = "delete"
    CREATE = "create"


@dataclass(slots=True)
class PermissionConfig:
    """
    Configuration for permission checking.
    """

    # Default permissions
    default_read: bool = True
    default_write: bool = False
    default_execute: bool = False
    default_delete: bool = False
    default_create: bool = False

    # Permission mappings
    permission_mappings: dict[str, list[Permission]] = None

    # User/group restrictions
    allowed_users: set[str] = None
    allowed_groups: set[str] = None
    restricted_users: set[str] = None
    restricted_groups: set[str] = None

    def __post_init__(self):
        if self.permission_mappings is None:
            self.permission_mappings = {}
        if self.allowed_users is None:
            self.allowed_users = set()
        if self.allowed_groups is None:
            self.allowed_groups = set()
        if self.restricted_users is None:
            self.restricted_users = set()
        if self.restricted_groups is None:
            self.restricted_groups = set()


class PermissionError(Exception):
    """
    Base exception for permission errors.
    """



class AccessDeniedError(PermissionError):
    """
    Raised when access is denied.
    """

    def __init__(self, path: str, permission: Permission, reason: str = ""):
        self.path = path
        self.permission = permission
        self.reason = reason
        super().__init__(
            f"Access denied for '{path}' with permission '{permission.value}': {reason}",
        )


class InsufficientPermissionsError(PermissionError):
    """
    Raised when user has insufficient permissions.
    """

    def __init__(self, required_permissions: list[Permission], user_permissions: list[Permission]):
        self.required_permissions = required_permissions
        self.user_permissions = user_permissions
        super().__init__(
            f"Insufficient permissions. Required: {[p.value for p in required_permissions]}, "
            f"User has: {[p.value for p in user_permissions]}",
        )


class PermissionChecker:
    """
    Checks and enforces file system permissions.
    """

    def __init__(self, config: PermissionConfig | None = None):
        self.config = config or PermissionConfig()
        self._current_user = self._get_current_user()
        self._current_groups = self._get_current_groups()

    def check_permission(self, path: str | Path, permission: Permission) -> bool:
        """
        Check if current user has permission for path.
        """
        try:
            path = Path(path)

            # Check if path exists
            if not path.exists():
                return self.config.default_create if permission == Permission.CREATE else False

            # Check user/group restrictions
            if not self._check_user_group_access(path):
                return False

            # Check file system permissions
            if not self._check_filesystem_permission(path, permission):
                return False

            # Check custom permission mappings
            return self._check_custom_permissions(path, permission)

        except (OSError, PermissionError):
            return False

    def require_permission(self, path: str | Path, permission: Permission) -> None:
        """
        Require permission for path, raise exception if not granted.
        """
        if not self.check_permission(path, permission):
            raise AccessDeniedError(str(path), permission)

    def check_multiple_permissions(
        self, path: str | Path, permissions: list[Permission],
    ) -> dict[Permission, bool]:
        """
        Check multiple permissions for a path.
        """
        results = {}
        for permission in permissions:
            results[permission] = self.check_permission(path, permission)
        return results

    def require_multiple_permissions(
        self, path: str | Path, permissions: list[Permission],
    ) -> None:
        """
        Require multiple permissions for path.
        """
        missing_permissions = []
        for permission in permissions:
            if not self.check_permission(path, permission):
                missing_permissions.append(permission)

        if missing_permissions:
            user_permissions = [p for p in permissions if self.check_permission(path, p)]
            raise InsufficientPermissionsError(missing_permissions, user_permissions)

    def get_effective_permissions(self, path: str | Path) -> list[Permission]:
        """
        Get all effective permissions for a path.
        """
        effective_permissions = []

        for permission in Permission:
            if self.check_permission(path, permission):
                effective_permissions.append(permission)

        return effective_permissions

    def _check_user_group_access(self, path: Path) -> bool:
        """
        Check if current user/group has access to path.
        """
        try:
            path.stat()

            # Check restricted users/groups
            if self._current_user in self.config.restricted_users:
                return False

            if any(group in self.config.restricted_groups for group in self._current_groups):
                return False

            # Check allowed users/groups if specified
            if self.config.allowed_users and self._current_user not in self.config.allowed_users:
                return False

            return not (self.config.allowed_groups and not any(group in self.config.allowed_groups for group in self._current_groups))

        except OSError:
            return False

    def _check_filesystem_permission(self, path: Path, permission: Permission) -> bool:
        """
        Check file system level permissions.
        """
        try:
            stat_info = path.stat()
            file_mode = stat_info.st_mode

            # Check owner permissions
            if stat_info.st_uid == os.getuid():
                if permission == Permission.READ and not (file_mode & stat.S_IRUSR):
                    return False
                if permission == Permission.WRITE and not (file_mode & stat.S_IWUSR):
                    return False
                return not (permission == Permission.EXECUTE and not file_mode & stat.S_IXUSR)

            # Check group permissions
            if stat_info.st_gid in [g.gr_gid for g in os.getgroups()]:
                if permission == Permission.READ and not (file_mode & stat.S_IRGRP):
                    return False
                if permission == Permission.WRITE and not (file_mode & stat.S_IWGRP):
                    return False
                return not (permission == Permission.EXECUTE and not file_mode & stat.S_IXGRP)

            # Check other permissions
            if permission == Permission.READ and not (file_mode & stat.S_IROTH):
                return False
            if permission == Permission.WRITE and not (file_mode & stat.S_IWOTH):
                return False
            return not (permission == Permission.EXECUTE and not file_mode & stat.S_IXOTH)

        except OSError:
            return False

    def _check_custom_permissions(self, path: Path, permission: Permission) -> bool:
        """
        Check custom permission mappings.
        """
        path_str = str(path)

        for pattern, allowed_permissions in self.config.permission_mappings.items():
            if path_str.startswith(pattern):
                return permission in allowed_permissions

        return True

    def _get_current_user(self) -> str:
        """
        Get current user name.
        """
        try:
            import pwd

            return pwd.getpwuid(os.getuid()).pw_name
        except (ImportError, KeyError):
            return str(os.getuid())

    def _get_current_groups(self) -> list[str]:
        """
        Get current user groups.
        """
        try:
            import grp

            groups = []
            for gid in os.getgroups():
                try:
                    groups.append(grp.getgrgid(gid).gr_name)
                except KeyError:
                    groups.append(str(gid))
            return groups
        except ImportError:
            return [str(gid) for gid in os.getgroups()]

    def set_permission_mapping(self, pattern: str, permissions: list[Permission]) -> None:
        """
        Set permission mapping for a path pattern.
        """
        self.config.permission_mappings[pattern] = permissions
        logger.debug(f"Set permission mapping for '{pattern}': {[p.value for p in permissions]}")

    def remove_permission_mapping(self, pattern: str) -> bool:
        """
        Remove permission mapping for a path pattern.
        """
        if pattern in self.config.permission_mappings:
            del self.config.permission_mappings[pattern]
            logger.debug(f"Removed permission mapping for '{pattern}'")
            return True
        return False
