from __future__ import annotations

from utils.env import env_override_enabled, get_env, reload_env


def test_env_override_disabled_uses_os(monkeypatch):
    monkeypatch.setenv("ZEN_MCP_FORCE_ENV_OVERRIDE", "false")
    reload_env({"ZEN_MCP_FORCE_ENV_OVERRIDE": "false"})

    monkeypatch.setenv("MY_KEY", "from-os")
    assert env_override_enabled() is False
    assert get_env("MY_KEY") == "from-os"


def test_env_override_enabled_prefers_dotenv_mapping(monkeypatch):
    # Put a conflicting value in the process env
    monkeypatch.setenv("MY_KEY", "from-os")
    # Enable override and provide mapping value
    reload_env({"ZEN_MCP_FORCE_ENV_OVERRIDE": "true", "MY_KEY": "from-dotenv"})

    assert env_override_enabled() is True
    # Should return mapping value, not os environ
    assert get_env("MY_KEY") == "from-dotenv"

    # Absent keys should return None when override is on
    assert get_env("MISSING_KEY") is None
