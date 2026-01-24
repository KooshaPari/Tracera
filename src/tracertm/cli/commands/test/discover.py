"""
Test discovery module for language-specific test runners.

Stub implementation to fix import errors.
"""

DOMAIN_MAPPING = {
    "cli": {
        "python": ["tests/unit/cli/**/*.py"],
        "go": [],
        "typescript": []
    },
    "api": {
        "python": ["tests/unit/api/**/*.py"],
        "go": [],
        "typescript": []
    },
}


def discover_all_tests() -> dict[str, list[str]]:
    """Discover all tests across all languages."""
    return {"python": [], "go": [], "typescript": []}


class GoTestDiscoverer:
    """Discover Go tests."""

    def discover(self) -> list[str]:
        return []


class PythonTestDiscoverer:
    """Discover Python tests."""

    def discover(self) -> list[str]:
        return []


class TypeScriptTestDiscoverer:
    """Discover TypeScript tests."""

    def discover(self) -> list[str]:
        return []
