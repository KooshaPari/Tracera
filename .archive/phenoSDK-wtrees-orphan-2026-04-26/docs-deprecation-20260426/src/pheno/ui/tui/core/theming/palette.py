"""
Color palette utilities for the theming system.
"""

from __future__ import annotations

from dataclasses import dataclass

from .color_utils import RGBColor


@dataclass
class ColorPalette:
    """
    Comprehensive color palette with semantic names.
    """

    primary: RGBColor
    secondary: RGBColor
    accent: RGBColor
    background: RGBColor
    surface: RGBColor
    text: RGBColor
    text_secondary: RGBColor
    text_muted: RGBColor
    border: RGBColor
    success: RGBColor
    warning: RGBColor
    error: RGBColor
    info: RGBColor

    @classmethod
    def from_base_color(cls, base_color: str | RGBColor) -> ColorPalette:
        """
        Generate a complete palette from a base color.
        """
        primary = RGBColor.from_hex(base_color) if isinstance(base_color, str) else base_color

        h, s, l = primary.to_hsl()
        secondary = RGBColor.from_hsl((h + 0.5) % 1.0, s, l)
        accent = RGBColor.from_hsl((h + 0.33) % 1.0, s, l)
        background = RGBColor.from_hsl(h, 0.1, 0.98)
        surface = RGBColor.from_hsl(h, 0.1, 0.95)
        text = RGBColor.from_hsl(h, 0.1, 0.1)
        text_secondary = RGBColor.from_hsl(h, 0.1, 0.4)
        text_muted = RGBColor.from_hsl(h, 0.1, 0.6)
        border = RGBColor.from_hsl(h, 0.1, 0.8)

        # Semantic colors
        success = RGBColor.from_hex("#10b981")
        warning = RGBColor.from_hex("#f59e0b")
        error = RGBColor.from_hex("#ef4444")
        info = RGBColor.from_hex("#3b82f6")

        return cls(
            primary=primary,
            secondary=secondary,
            accent=accent,
            background=background,
            surface=surface,
            text=text,
            text_secondary=text_secondary,
            text_muted=text_muted,
            border=border,
            success=success,
            warning=warning,
            error=error,
            info=info,
        )

    def get_color(self, name: str) -> RGBColor:
        """
        Get color by name, falling back to the primary color.
        """
        return getattr(self, name, self.primary)

    def to_dict(self) -> dict[str, str]:
        """
        Convert palette to dictionary of hex strings.
        """
        return {
            "primary": self.primary.to_hex(),
            "secondary": self.secondary.to_hex(),
            "accent": self.accent.to_hex(),
            "background": self.background.to_hex(),
            "surface": self.surface.to_hex(),
            "text": self.text.to_hex(),
            "text_secondary": self.text_secondary.to_hex(),
            "text_muted": self.text_muted.to_hex(),
            "border": self.border.to_hex(),
            "success": self.success.to_hex(),
            "warning": self.warning.to_hex(),
            "error": self.error.to_hex(),
            "info": self.info.to_hex(),
        }


__all__ = ["ColorPalette"]
