"""
Accessibility helpers for the theming system.
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from .color_utils import RGBColor

if TYPE_CHECKING:
    from .theme import Theme


class ColorBlindType(Enum):
    """
    Types of color blindness.
    """

    PROTANOPIA = "protanopia"
    DEUTERANOPIA = "deuteranopia"
    TRITANOPIA = "tritanopia"
    ACHROMATOPSIA = "achromatopsia"


class AccessibilityMode:
    """
    Accessibility mode utilities for theme adaptation.
    """

    @staticmethod
    def apply_high_contrast(theme: Theme) -> Theme:
        palette = theme.palette
        palette.text = palette.text.darken(0.3)
        palette.text_secondary = palette.text_secondary.darken(0.2)
        palette.border = palette.border.darken(0.2)
        return theme

    @staticmethod
    def apply_colorblind_support(theme: Theme, colorblind_type: ColorBlindType) -> Theme:
        palette = theme.palette

        if colorblind_type == ColorBlindType.PROTANOPIA:
            palette.error = RGBColor.from_hex("#ff6b6b")
            palette.warning = RGBColor.from_hex("#ffa726")
        elif colorblind_type == ColorBlindType.DEUTERANOPIA:
            palette.success = RGBColor.from_hex("#4caf50")
            palette.info = RGBColor.from_hex("#2196f3")
        elif colorblind_type == ColorBlindType.TRITANOPIA:
            palette.info = RGBColor.from_hex("#00bcd4")
            palette.accent = RGBColor.from_hex("#ff9800")
        elif colorblind_type == ColorBlindType.ACHROMATOPSIA:
            for attr_name in [
                "primary",
                "secondary",
                "accent",
                "success",
                "warning",
                "error",
                "info",
            ]:
                color = getattr(palette, attr_name)
                _, _, l = color.to_hsl()
                grayscale = RGBColor.from_hsl(0, 0, l)
                setattr(palette, attr_name, grayscale)

        return theme

    @staticmethod
    def apply_reduced_motion(theme: Theme) -> Theme:
        theme.animations.enabled = False
        theme.animations.duration = 0.0
        return theme


__all__ = ["AccessibilityMode", "ColorBlindType"]
