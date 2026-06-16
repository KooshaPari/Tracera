"""Pytest configuration and shared fixtures for NFR-TRC-012 self-tracing.

This conftest.py registers the TraceabilityPlugin and provides shared fixtures
for tests throughout the test suite. It enables automatic evidence emission
during test execution as part of the self-tracing requirement.
"""

from __future__ import annotations

import pytest

from tracertm.self_tracing.pytest_plugin import TraceabilityPlugin

# Register the traceability plugin
pytest_plugins = [
    "tracertm.self_tracing.pytest_plugin",
]


@pytest.fixture(scope="session")
def traceability_plugin() -> TraceabilityPlugin:
    """Provide access to the traceability plugin instance.

    This allows tests to query evidence records and coverage records
    that were collected during the test session.

    Returns:
        TraceabilityPlugin instance managing evidence collection.
    """
    return TraceabilityPlugin()


@pytest.fixture
def stability_seed() -> int:
    """Provide a stable seed for reproducible test data.

    Returns:
        Integer seed (42) for use in random/UUID generation within tests.
    """
    return 42
