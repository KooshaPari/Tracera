"""TUI Kit Core Module.

Core components for building terminal user interfaces.
"""

from .components import (  # Enums and dataclasses; Protocols; Core systems; Base classes; Layout implementations
    BaseComponent,
    Component,
    ComponentState,
    ContainerComponent,
    EventHandling,
    LifecycleHooks,
    PluginIntegration,
    StateManagement,
)
from .theming import (  # Color utilities; Palettes; Accessibility; Theme components; Cascade system; Default themes
    AccessibilityMode,
    AnimationSettings,
    ColorBlindType,
    ColorPalette,
    RGBColor,
    SpacingSettings,
    Specificity,
    StyleRule,
    Theme,
    ThemeEngine,
    TypographySettings,
    WCAGLevel,
)

__all__ = [
    # Accessibility
    "AccessibilityMode",
    "AnimationSettings",
    # Component system
    "BaseComponent",
    "CascadeResolver",
    "ColorBlindType",
    # Palettes
    "ColorPalette",
    "Component",
    "ComponentState",
    "ContainerComponent",
    "EventHandling",
    "LifecycleHooks",
    "PluginIntegration",
    # Color utilities
    "RGBColor",
    "SpacingSettings",
    "Specificity",
    "StateManagement",
    "StyleRule",
    # Theme components
    "Theme",
    # Cascade system
    "ThemeEngine",
    "TypographySettings",
    "WCAGLevel",
    # Default themes (removed - use ThemeEngine to create themes)
]
