"""
ThemeManager - Theme management and switching.

Provides theme configuration and dynamic switching.
"""

from dataclasses import dataclass, field


@dataclass
class ColorScheme:
    """
    Color scheme definition.
    """

    primary: str = "#0178d4"
    secondary: str = "#666666"
    accent: str = "#ffc107"
    background: str = "#1e1e1e"
    surface: str = "#2d2d2d"
    text: str = "#ffffff"
    text_dim: str = "#888888"
    success: str = "#4caf50"
    warning: str = "#ff9800"
    error: str = "#f44336"
    info: str = "#2196f3"


@dataclass
class Theme:
    """
    Theme definition.
    """

    name: str
    colors: ColorScheme
    css_variables: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """
        Initialize CSS variables from colors.
        """
        if not self.css_variables:
            self.css_variables = {
                "--primary": self.colors.primary,
                "--secondary": self.colors.secondary,
                "--accent": self.colors.accent,
                "--background": self.colors.background,
                "--surface": self.colors.surface,
                "--text": self.colors.text,
                "--text-dim": self.colors.text_dim,
                "--success": self.colors.success,
                "--warning": self.colors.warning,
                "--error": self.colors.error,
                "--info": self.colors.info,
            }

    def get_css(self) -> str:
        """
        Generate CSS from theme.
        """
        css_lines = [":root {"]

        for var, value in self.css_variables.items():
            css_lines.append(f"    {var}: {value};")

        css_lines.append("}")

        return "\n".join(css_lines)


class ThemeManager:
    """Theme manager for TUI applications.

    Features:
    - Theme registration
    - Dynamic theme switching
    - Custom theme creation
    - Theme persistence
    """

    def __init__(self):
        self._themes: dict[str, Theme] = {}
        self._current_theme: str | None = None
        self._callbacks = []

    def register_theme(self, theme: Theme) -> None:
        """
        Register a theme.
        """
        self._themes[theme.name] = theme

    def unregister_theme(self, name: str) -> bool:
        """
        Unregister a theme.
        """
        if name in self._themes:
            del self._themes[name]
            return True
        return False

    def set_theme(self, name: str) -> bool:
        """
        Set active theme.
        """
        if name not in self._themes:
            return False

        old_theme = self._current_theme
        self._current_theme = name

        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(old_theme, name)
            except Exception as e:
                print(f"Theme callback error: {e}")

        return True

    def get_theme(self, name: str | None = None) -> Theme | None:
        """
        Get theme by name (or current theme if None).
        """
        if name is None:
            name = self._current_theme

        return self._themes.get(name) if name else None

    def get_current_theme_name(self) -> str | None:
        """
        Get current theme name.
        """
        return self._current_theme

    def list_themes(self) -> list:
        """
        List available theme names.
        """
        return list(self._themes.keys())

    def create_custom_theme(
        self,
        name: str,
        base_theme: str | None = None,
        color_overrides: dict[str, str] | None = None,
    ) -> Theme:
        """
        Create a custom theme.
        """
        # Start with base theme if specified
        if base_theme and base_theme in self._themes:
            base = self._themes[base_theme]
            colors = ColorScheme(**dict(vars(base.colors).items()))
        else:
            colors = ColorScheme()

        # Apply overrides
        if color_overrides:
            for key, value in color_overrides.items():
                if hasattr(colors, key):
                    setattr(colors, key, value)

        # Create theme
        theme = Theme(name=name, colors=colors)
        self.register_theme(theme)

        return theme

    def add_theme_callback(self, callback) -> None:
        """
        Add callback for theme changes.
        """
        self._callbacks.append(callback)

    def remove_theme_callback(self, callback) -> None:
        """
        Remove theme callback.
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)


# Global theme manager instance
_theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """
    Get global theme manager instance.
    """
    return _theme_manager
