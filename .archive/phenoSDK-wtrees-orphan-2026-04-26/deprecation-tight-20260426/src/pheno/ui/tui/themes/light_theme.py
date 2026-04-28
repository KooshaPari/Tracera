"""
Light Theme - Light color scheme.
"""

from pheno.ui.tui.theme_manager import ColorScheme, Theme

LightTheme = Theme(
    name="light",
    colors=ColorScheme(
        primary="#0066cc",
        secondary="#999999",
        accent="#ff9800",
        background="#ffffff",
        surface="#f5f5f5",
        text="#000000",
        text_dim="#666666",
        success="#2e7d32",
        warning="#f57c00",
        error="#c62828",
        info="#1976d2",
    ),
)
