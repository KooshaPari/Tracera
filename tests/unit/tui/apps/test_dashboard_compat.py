"""Tests for the dashboard compatibility module."""

from __future__ import annotations


def test_dashboard_compat_import() -> None:
    """Compatibility module should import the enhanced dashboard app."""
    from tracertm.tui.apps.dashboard_compat import EnhancedDashboardApp

    assert EnhancedDashboardApp is not None
