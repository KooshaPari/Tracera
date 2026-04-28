"""Service for security and compliance."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SecurityComplianceService:
    """Service for security and compliance."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize service.

        Args:
            session: SQLAlchemy async session for database operations.
        """
        self.session = session
        self.audit_log: list[dict[str, Any]] = []
        self.encryption_enabled = False

    def enable_encryption(self) -> dict[str, Any]:
        """Enable data encryption."""
        self.encryption_enabled = True
        return {
            "encryption_enabled": True,
            "status": "Encryption enabled successfully",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def disable_encryption(self) -> dict[str, Any]:
        """Disable data encryption."""
        self.encryption_enabled = False
        return {
            "encryption_enabled": False,
            "status": "Encryption disabled successfully",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    def is_encryption_enabled(self) -> bool:
        """Check if encryption is enabled."""
        return self.encryption_enabled

    def log_audit_event(
        self,
        event_type: str,
        user_id: str,
        resource: str,
        action: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Log an audit event."""
        event = {
            "event_type": event_type,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "details": details or {},
            "timestamp": datetime.now(UTC).isoformat(),
        }

        self.audit_log.append(event)

        return {
            "logged": True,
            "event_id": len(self.audit_log),
            "status": "Audit event logged successfully",
        }

    def get_audit_log(
        self,
        user_id: str | None = None,
        event_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Get audit log entries."""
        log = self.audit_log

        if user_id:
            log = [e for e in log if e["user_id"] == user_id]

        if event_type:
            log = [e for e in log if e["event_type"] == event_type]

        return log

    def get_audit_stats(self) -> dict[str, Any]:
        """Get audit log statistics."""
        event_types: dict[str, int] = {}
        users = set()

        for event in self.audit_log:
            event_type = event["event_type"]
            event_types[event_type] = event_types.get(event_type, 0) + 1
            users.add(event["user_id"])

        return {
            "total_events": len(self.audit_log),
            "unique_users": len(users),
            "event_types": event_types,
        }

    def hash_sensitive_data(self, data: str) -> str:
        """Hash sensitive data."""
        return hashlib.sha256(data.encode()).hexdigest()

    def validate_access_control(
        self,
        user_id: str,
        resource: str,
        action: str,
    ) -> dict[str, Any]:
        """Validate access control."""
        # Simple access control validation
        allowed_actions = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "viewer": ["read"],
        }

        # Default to viewer role
        role = "viewer"

        user_actions = allowed_actions.get(role, [])
        is_allowed = action in user_actions

        return {
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "allowed": is_allowed,
            "role": role,
        }

    def generate_compliance_report(self) -> dict[str, Any]:
        """Generate compliance report."""
        audit_stats = self.get_audit_stats()

        return {
            "generated_at": datetime.now(UTC).isoformat(),
            "encryption_enabled": self.encryption_enabled,
            "audit_stats": audit_stats,
            "compliance_status": ("COMPLIANT" if self.encryption_enabled else "NON_COMPLIANT"),
            "recommendations": [
                "Enable encryption for sensitive data",
                "Review audit logs regularly",
                "Implement role-based access control",
                "Use strong authentication",
            ],
        }

    def clear_audit_log(self) -> dict[str, Any]:
        """Clear audit log."""
        count = len(self.audit_log)
        self.audit_log.clear()

        return {
            "cleared_count": count,
            "status": "Audit log cleared successfully",
        }
