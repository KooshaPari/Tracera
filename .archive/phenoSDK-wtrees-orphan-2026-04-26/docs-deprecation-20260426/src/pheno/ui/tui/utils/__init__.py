"""
TUI-Kit Utils - Utility functions and helpers.
"""

from pheno.ui.tui.box_drawing import BoxDrawing, draw_border, draw_box
from pheno.ui.tui.colors import ColorUtils, darken, hex_to_rgb, lighten, rgb_to_hex
from pheno.ui.tui.keyboard import (
    KeyboardShortcuts,
    get_shortcut,
    get_shortcuts,
    register_shortcut,
)

__all__ = [
    "BoxDrawing",
    "ColorUtils",
    "KeyboardShortcuts",
    "darken",
    "draw_border",
    "draw_box",
    "get_shortcut",
    "get_shortcuts",
    "hex_to_rgb",
    "lighten",
    "register_shortcut",
    "rgb_to_hex",
]
