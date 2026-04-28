"""
Design token settings for the theming system.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TypographySettings:
    """
    Typography settings for a theme.
    """

    font_family: str = "system-ui, -apple-system, sans-serif"
    font_size_base: str = "14px"
    font_size_small: str = "12px"
    font_size_large: str = "16px"
    font_size_xlarge: str = "20px"
    font_weight_normal: int = 400
    font_weight_medium: int = 500
    font_weight_semibold: int = 600
    font_weight_bold: int = 700
    line_height_tight: float = 1.2
    line_height_normal: float = 1.5
    line_height_relaxed: float = 1.75


@dataclass
class SpacingSettings:
    """
    Spacing settings for a theme.
    """

    xs: str = "4px"
    sm: str = "8px"
    md: str = "16px"
    lg: str = "24px"
    xl: str = "32px"
    xxl: str = "48px"
    xxxl: str = "64px"


@dataclass
class AnimationSettings:
    """
    Animation settings for a theme.
    """

    enabled: bool = True
    duration_fast: float = 0.15
    duration_normal: float = 0.3
    duration_slow: float = 0.5
    easing_ease: str = "ease"
    easing_ease_in: str = "ease-in"
    easing_ease_out: str = "ease-out"
    easing_ease_in_out: str = "ease-in-out"


__all__ = ["AnimationSettings", "SpacingSettings", "TypographySettings"]
