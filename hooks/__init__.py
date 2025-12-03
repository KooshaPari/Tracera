"""
Hooks - CLI integration hooks

Provides pre-discovery, post-selection, and execution hooks for CLI tools.
"""

from hooks.semantic_discovery import pre_discovery_hook, SemanticDiscoveryHook
from hooks.cli_executor import execute_cli_command, CLIExecutor
from hooks.cursor_agent_hook import cursor_agent_pre_discovery, CursorAgentHook
from hooks.claude_cli_hook import claude_cli_pre_discovery, ClaudeCliHook
from hooks.auggie_hook import auggie_pre_discovery, AuggieHook
from hooks.droid_hook import droid_pre_discovery, DroidHook

__all__ = [
    "pre_discovery_hook",
    "execute_cli_command",
    "SemanticDiscoveryHook",
    "CLIExecutor",
    "cursor_agent_pre_discovery",
    "CursorAgentHook",
    "claude_cli_pre_discovery",
    "ClaudeCliHook",
    "auggie_pre_discovery",
    "AuggieHook",
    "droid_pre_discovery",
    "DroidHook",
]

