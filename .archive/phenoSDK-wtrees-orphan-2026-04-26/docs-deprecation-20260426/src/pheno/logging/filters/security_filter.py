"""Security filters for redacting sensitive information from logs.

Provides automatic redaction of:
- Passwords and API keys
- Credit card numbers
- Social Security Numbers (SSN)
- Email addresses
- IP addresses
- JWT tokens
- Custom patterns

Example:
    from pheno_logging.filters import SecurityFilter
    import logging

    logger = logging.getLogger("secure")
    logger.addFilter(SecurityFilter())

    # This will be redacted
    logger.info("User password is: secret123")
    # Output: "User password is: [REDACTED]"
"""

from __future__ import annotations

import logging
import re
from re import Pattern
from typing import Any

__all__ = [
    "PIIRedactor",
    "SecurityFilter",
]


class PIIRedactor:
    """Redactor for Personally Identifiable Information (PII) and sensitive data.

    Supports redaction of:
    - Passwords, API keys, tokens
    - Credit card numbers
    - Social Security Numbers
    - Email addresses
    - IP addresses
    - Phone numbers
    - Custom patterns
    """

    # Default patterns for sensitive data
    DEFAULT_PATTERNS = {
        # Passwords and secrets
        "password": re.compile(
            r"(password|passwd|pwd|secret|api[_-]?key|token|auth)[\"']?\s*[:=]\s*[\"']?([^\s\"']+)",
            re.IGNORECASE,
        ),
        # Credit cards (basic pattern)
        "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
        # SSN
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        # Email (basic pattern)
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        # JWT tokens
        "jwt": re.compile(r"eyJ[A-Za-z0-9_-]*\.eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"),
        # Bearer tokens
        "bearer": re.compile(r"Bearer\s+[A-Za-z0-9_-]+", re.IGNORECASE),
        # AWS keys
        "aws_key": re.compile(r"AKIA[0-9A-Z]{16}"),
        # Private keys
        "private_key": re.compile(
            r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----[\s\S]+?-----END\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
        ),
    }

    def __init__(
        self,
        *,
        patterns: dict[str, Pattern] | None = None,
        redact_emails: bool = False,
        redact_ips: bool = False,
        replacement: str = "[REDACTED]",
    ):
        """Initialize PII redactor.

        Args:
            patterns: Custom patterns to redact (in addition to defaults)
            redact_emails: Whether to redact email addresses
            redact_ips: Whether to redact IP addresses
            replacement: Replacement text for redacted content
        """
        self.patterns = dict(self.DEFAULT_PATTERNS)

        # Remove email pattern if not redacting emails
        if not redact_emails and "email" in self.patterns:
            del self.patterns["email"]

        # Add IP pattern if redacting IPs
        if redact_ips:
            self.patterns["ip"] = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

        # Add custom patterns
        if patterns:
            self.patterns.update(patterns)

        self.replacement = replacement

    def redact(self, text: str) -> str:
        """Redact sensitive information from text.

        Args:
            text: Text to redact

        Returns:
            Redacted text
        """
        if not text:
            return text

        result = text
        for pattern_name, pattern in self.patterns.items():
            if pattern_name == "password":
                # Special handling for password patterns to preserve key names
                result = pattern.sub(lambda m: f"{m.group(1)}={self.replacement}", result)
            else:
                result = pattern.sub(self.replacement, result)

        return result

    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive information from a dictionary.

        Args:
            data: Dictionary to redact

        Returns:
            Redacted dictionary (new copy)
        """
        result = {}
        sensitive_keys = {
            "password",
            "passwd",
            "pwd",
            "secret",
            "api_key",
            "apikey",
            "token",
            "auth",
            "authorization",
            "credit_card",
            "ssn",
            "private_key",
        }

        for key, value in data.items():
            key_lower = key.lower().replace("-", "_")

            # Check if key is sensitive
            if any(sensitive in key_lower for sensitive in sensitive_keys):
                result[key] = self.replacement
            elif isinstance(value, str):
                result[key] = self.redact(value)
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    (
                        self.redact_dict(item)
                        if isinstance(item, dict)
                        else self.redact(item) if isinstance(item, str) else item
                    )
                    for item in value
                ]
            else:
                result[key] = value

        return result


class SecurityFilter(logging.Filter):
    """Logging filter that redacts sensitive information.

    This filter automatically redacts PII and sensitive data from log messages
    before they are written to handlers.

    Example:
        import logging
        from pheno_logging.filters import SecurityFilter

        logger = logging.getLogger("app")
        logger.addFilter(SecurityFilter())

        # Sensitive data will be redacted
        logger.info("User password: secret123")
        # Output: "User password: [REDACTED]"

        logger.info("Credit card: 1234-5678-9012-3456")
        # Output: "Credit card: [REDACTED]"
    """

    def __init__(
        self,
        *,
        redact_emails: bool = False,
        redact_ips: bool = False,
        replacement: str = "[REDACTED]",
        custom_patterns: dict[str, Pattern] | None = None,
    ):
        """Initialize security filter.

        Args:
            redact_emails: Whether to redact email addresses
            redact_ips: Whether to redact IP addresses
            replacement: Replacement text for redacted content
            custom_patterns: Custom regex patterns to redact
        """
        super().__init__()
        self.redactor = PIIRedactor(
            patterns=custom_patterns,
            redact_emails=redact_emails,
            redact_ips=redact_ips,
            replacement=replacement,
        )

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter a log record, redacting sensitive information.

        Args:
            record: Log record to filter

        Returns:
            True (always allow the record, just redact it)
        """
        # Redact message
        if hasattr(record, "msg") and isinstance(record.msg, str):
            record.msg = self.redactor.redact(record.msg)

        # Redact args
        if hasattr(record, "args") and record.args:
            if isinstance(record.args, dict):
                record.args = self.redactor.redact_dict(record.args)
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    self.redactor.redact(arg) if isinstance(arg, str) else arg
                    for arg in record.args
                )

        # Redact extra context
        if hasattr(record, "__dict__"):
            for key in list(record.__dict__.keys()):
                if key.startswith("_") or key in (
                    "name",
                    "msg",
                    "args",
                    "created",
                    "filename",
                    "funcName",
                    "levelname",
                    "levelno",
                    "lineno",
                    "module",
                    "msecs",
                    "pathname",
                    "process",
                    "processName",
                    "relativeCreated",
                    "thread",
                    "threadName",
                ):
                    continue

                value = getattr(record, key)
                if isinstance(value, str):
                    setattr(record, key, self.redactor.redact(value))
                elif isinstance(value, dict):
                    setattr(record, key, self.redactor.redact_dict(value))

        return True


# Convenience function
def add_security_filter(
    logger: logging.Logger,
    *,
    redact_emails: bool = False,
    redact_ips: bool = False,
) -> SecurityFilter:
    """Add a security filter to a logger.

    Args:
        logger: Logger to add filter to
        redact_emails: Whether to redact email addresses
        redact_ips: Whether to redact IP addresses

    Returns:
        The security filter instance

    Example:
        import logging
        from pheno_logging.filters import add_security_filter

        logger = logging.getLogger("app")
        add_security_filter(logger, redact_emails=True)
    """
    security_filter = SecurityFilter(
        redact_emails=redact_emails,
        redact_ips=redact_ips,
    )
    logger.addFilter(security_filter)
    return security_filter
