"""
Hooks - CLI integration hooks

Provides pre-discovery, post-selection, and execution hooks for CLI tools.
"""

from hooks.auggie_hook import AuggieHook, auggie_pre_discovery
from hooks.claude_cli_hook import ClaudeCliHook, claude_cli_pre_discovery
from hooks.cli_executor import CLIExecutor, execute_cli_command
from hooks.cursor_agent_hook import CursorAgentHook, cursor_agent_pre_discovery
from hooks.droid_hook import DroidHook, droid_pre_discovery
from hooks.semantic_discovery import SemanticDiscoveryHook, pre_discovery_hook

__all__ = [
    "AuggieHook",
    "CLIExecutor",
    "ClaudeCliHook",
    "CursorAgentHook",
    "DroidHook",
    "SemanticDiscoveryHook",
    "auggie_pre_discovery",
    "claude_cli_pre_discovery",
    "cursor_agent_pre_discovery",
    "droid_pre_discovery",
    "execute_cli_command",
    "pre_discovery_hook",
]
