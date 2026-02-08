"""Integration tests for Epic 3: Command aliases (FR33).

Tests command alias resolution.
"""

from tracertm.cli.aliases import ALIASES, get_aliases_for_command, resolve_alias


def test_alias_resolution() -> None:
    """Test alias resolution (FR33)."""
    # Test common aliases
    assert resolve_alias("p list") == "project list"
    assert resolve_alias("i list") == "item list"
    assert resolve_alias("v list") == "view list"
    assert resolve_alias("q --filter status=todo") == "query --filter status=todo"
    assert resolve_alias("s test") == "search test"
    assert resolve_alias("e --format json") == "export --format json"


def test_get_aliases_for_command() -> None:
    """Test getting aliases for a command."""
    aliases = get_aliases_for_command("project")
    assert "p" in aliases
    assert "proj" in aliases

    aliases = get_aliases_for_command("item")
    assert "i" in aliases
    assert "items" in aliases


def test_aliases_dict_completeness() -> None:
    """Test that aliases dict has expected entries."""
    # Verify key commands have aliases
    assert "project" in ALIASES.values()
    assert "item" in ALIASES.values()
    assert "view" in ALIASES.values()
    assert "query" in ALIASES.values()
    assert "search" in ALIASES.values()
    assert "export" in ALIASES.values()


def test_alias_no_match() -> None:
    """Test alias resolution when no alias exists."""
    # Commands without aliases should pass through
    assert resolve_alias("unknown command") == "unknown command"
    assert resolve_alias("config init") == "config init"
