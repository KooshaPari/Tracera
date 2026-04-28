"""Keyboard shortcut utilities.

Provides keyboard shortcut management and handling.
"""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Shortcut:
    """
    Keyboard shortcut definition.
    """

    key: str
    description: str
    action: Callable
    category: str = "General"


class KeyboardShortcuts:
    """Keyboard shortcut manager.

    Features:
    - Shortcut registration
    - Category organization
    - Conflict detection
    - Help text generation
    """

    def __init__(self):
        self._shortcuts: dict[str, Shortcut] = {}
        self._categories: dict[str, list[Shortcut]] = {}

    def register(
        self, key: str, description: str, action: Callable, category: str = "General",
    ) -> bool:
        """
        Register a keyboard shortcut.
        """
        # Check for conflicts
        if key in self._shortcuts:
            print(f"Warning: Shortcut '{key}' already registered")
            return False

        shortcut = Shortcut(key=key, description=description, action=action, category=category)

        self._shortcuts[key] = shortcut

        # Add to category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(shortcut)

        return True

    def unregister(self, key: str) -> bool:
        """
        Unregister a shortcut.
        """
        if key not in self._shortcuts:
            return False

        shortcut = self._shortcuts[key]

        # Remove from shortcuts
        del self._shortcuts[key]

        # Remove from category
        if shortcut.category in self._categories:
            self._categories[shortcut.category] = [
                s for s in self._categories[shortcut.category] if s.key != key
            ]

        return True

    def get_shortcut(self, key: str) -> Shortcut | None:
        """
        Get shortcut by key.
        """
        return self._shortcuts.get(key)

    def execute(self, key: str, *args, **kwargs) -> bool:
        """
        Execute shortcut action.
        """
        shortcut = self.get_shortcut(key)

        if not shortcut:
            return False

        try:
            shortcut.action(*args, **kwargs)
            return True
        except Exception as e:
            print(f"Error executing shortcut '{key}': {e}")
            return False

    def get_category(self, category: str) -> list[Shortcut]:
        """
        Get all shortcuts in a category.
        """
        return self._categories.get(category, [])

    def get_all_categories(self) -> list[str]:
        """
        Get list of all categories.
        """
        return list(self._categories.keys())

    def get_help_text(self) -> str:
        """
        Generate help text for all shortcuts.
        """
        lines = ["Keyboard Shortcuts:\n"]

        for category in sorted(self._categories.keys()):
            lines.append(f"\n{category}:")

            shortcuts = sorted(self._categories[category], key=lambda s: s.key)

            for shortcut in shortcuts:
                lines.append(f"  {shortcut.key:15s} {shortcut.description}")

        return "\n".join(lines)

    def clear(self) -> None:
        """
        Clear all shortcuts.
        """
        self._shortcuts.clear()
        self._categories.clear()


# Global shortcuts instance
_shortcuts = KeyboardShortcuts()


def get_shortcuts() -> KeyboardShortcuts:
    """
    Get global shortcuts instance.
    """
    return _shortcuts


def register_shortcut(
    key: str, description: str, action: Callable, category: str = "General",
) -> bool:
    """
    Register a global shortcut.
    """
    return _shortcuts.register(key, description, action, category)


def get_shortcut(key: str) -> Shortcut | None:
    """
    Get global shortcut.
    """
    return _shortcuts.get_shortcut(key)
