"""
Profile definitions for the TUI configuration system.
"""

from enum import StrEnum


class ConfigProfile(StrEnum):
    """
    Supported configuration profiles.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

    def __str__(self) -> str:
        return self.value


__all__ = ["ConfigProfile"]
