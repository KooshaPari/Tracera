"""
Dark Theme - Default dark color scheme.
"""

from pheno.ui.tui.theme_manager import ColorScheme, Theme

DarkTheme = Theme(
    name="dark",
    colors=ColorScheme(
        primary="#0178d4",
        secondary="#666666",
        accent="#ffc107",
        background="#1e1e1e",
        surface="#2d2d2d",
        text="#ffffff",
        text_dim="#888888",
        success="#4caf50",
        warning="#ff9800",
        error="#f44336",
        info="#2196f3",
    ),
)
