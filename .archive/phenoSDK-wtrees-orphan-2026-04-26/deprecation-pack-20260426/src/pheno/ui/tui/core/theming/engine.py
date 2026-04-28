"""
Theme engine with CSS-like cascade support.
"""

from __future__ import annotations

from typing import Any

from .cascade import Specificity, StyleRule
from .theme import Theme


class ThemeEngine:
    """
    Main theme engine with CSS-like cascade resolution.
    """

    def __init__(self):
        self.rules: list[StyleRule] = []
        self.themes: dict[str, Theme] = {}
        self.current_theme: str = "default"
        self._cache: dict[str, dict[str, Any]] = {}

    def add_theme(self, theme: Theme):
        """
        Add a theme to the engine.
        """
        self.themes[theme.name] = theme

    def set_theme(self, name: str):
        """
        Set the current theme.
        """
        if name not in self.themes:
            raise ValueError(f"Theme '{name}' not found")
        self.current_theme = name
        self._cache.clear()

    def add_rule(self, selector: str, properties: dict[str, Any], source_order: int = 0):
        """
        Add a style rule.
        """
        rule = StyleRule(
            selector=selector,
            properties=properties,
            specificity=Specificity.from_selector(selector),
            source_order=source_order,
        )
        self.rules.append(rule)
        self._cache.clear()

    def resolve(self, element: str, **context) -> dict[str, Any]:
        """Resolve styles for an element using cascade.

        Args:
            element: Element name/selector
            **context: Additional context (id, classes, etc.)

        Returns:
            dict: Resolved style properties
        """
        cache_key = f"{element}:{hash(str(sorted(context.items())))}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Find matching rules
        matching_rules = []
        for rule in self.rules:
            if self._matches_selector(rule.selector, element, **context):
                matching_rules.append(rule)

        # Sort by specificity and source order
        matching_rules.sort(key=lambda r: (r.specificity, r.source_order), reverse=True)

        # Merge properties
        resolved = {}
        for rule in matching_rules:
            resolved.update(rule.properties)

        # Apply theme colors
        if self.current_theme in self.themes:
            theme = self.themes[self.current_theme]
            resolved = self._apply_theme_colors(resolved, theme)

        self._cache[cache_key] = resolved
        return resolved

    def _matches_selector(self, selector: str, element: str, **context) -> bool:
        """
        Check if selector matches element and context.
        """
        # Simple selector matching (can be extended)
        if selector == element:
            return True

        if selector.startswith("#") and context.get("id") == selector[1:]:
            return True

        return bool(selector.startswith(".") and selector[1:] in context.get("classes", []))

    def _apply_theme_colors(self, properties: dict[str, Any], theme: Theme) -> dict[str, Any]:
        """
        Apply theme colors to properties.
        """
        result = properties.copy()
        palette = theme.palette

        for key, value in properties.items():
            if isinstance(value, str) and value.startswith("$"):
                color_name = value[1:]
                if hasattr(palette, color_name):
                    result[key] = getattr(palette, color_name).to_hex()

        return result

    def clear_cache(self):
        """
        Clear the style cache.
        """
        self._cache.clear()

    def export_theme(self, name: str) -> dict[str, Any]:
        """
        Export theme as dictionary.
        """
        if name not in self.themes:
            raise ValueError(f"Theme '{name}' not found")
        return self.themes[name].to_dict()

    def import_theme(self, data: dict[str, Any]):
        """
        Import theme from dictionary.
        """
        theme = Theme.from_dict(data)
        self.add_theme(theme)
