"""Service for TUI (Terminal User Interface) management.

Functional Requirements: FR-APP-001
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class UIComponentType(StrEnum):
    """UI component types."""

    DASHBOARD = "dashboard"
    TABLE = "table"
    FORM = "form"
    MODAL = "modal"
    SIDEBAR = "sidebar"
    HEADER = "header"
    FOOTER = "footer"
    CHART = "chart"


@dataclass
class UIComponent:
    """UI component definition."""

    name: str
    component_type: UIComponentType
    title: str
    data: dict[str, Any] = field(default_factory=dict)
    actions: list[str] = field(default_factory=list)


class TUIService:
    """Service for managing TUI components and interactions."""

    def __init__(self) -> None:
        """Initialize."""
        self.components: dict[str, UIComponent] = {}
        self.current_view: str | None = None
        self.event_handlers: dict[str, list[Callable]] = {}
        self.theme: str = "dark"
        self.mouse_enabled: bool = True

    def register_component(
        self,
        name: str,
        component_type: UIComponentType,
        title: str,
        data: dict[str, Any] | None = None,
    ) -> UIComponent:
        """Register a UI component."""
        component = UIComponent(
            name=name,
            component_type=component_type,
            title=title,
            data=data or {},
        )

        self.components[name] = component
        return component

    def get_component(self, name: str) -> UIComponent | None:
        """Get component by name."""
        return self.components.get(name)

    def list_components(self, component_type: UIComponentType | None = None) -> list[UIComponent]:
        """List all components, optionally filtered by type."""
        components = list(self.components.values())

        if component_type:
            components = [c for c in components if c.component_type == component_type]

        return components

    def update_component_data(self, name: str, data: dict[str, Any]) -> UIComponent | None:
        """Update component data."""
        component = self.get_component(name)
        if component:
            component.data.update(data)
            return component
        return None

    def set_current_view(self, view_name: str) -> bool:
        """Set current active view."""
        if view_name in self.components:
            self.current_view = view_name
            return True
        return False

    def get_current_view(self) -> UIComponent | None:
        """Get current active view."""
        if self.current_view:
            return self.get_component(self.current_view)
        return None

    def register_event_handler(self, event_name: str, handler: Callable) -> None:
        """Register event handler."""
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def trigger_event(self, event_name: str, *args: object, **kwargs: object) -> list[object]:
        """Trigger event and execute all handlers."""
        results = []
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    result = handler(*args, **kwargs)
                    results.append(result)
                except (OSError, ValueError) as e:
                    results.append({"error": str(e)})
        return results

    def set_theme(self, theme: str) -> None:
        """Set UI theme."""
        valid_themes = ["dark", "light", "high_contrast"]
        if theme in valid_themes:
            self.theme = theme

    def get_theme(self) -> str:
        """Get current theme."""
        return self.theme

    def enable_mouse(self) -> None:
        """Enable mouse support."""
        self.mouse_enabled = True

    def disable_mouse(self) -> None:
        """Disable mouse support."""
        self.mouse_enabled = False

    def is_mouse_enabled(self) -> bool:
        """Check if mouse is enabled."""
        return self.mouse_enabled

    def get_ui_stats(self) -> dict[str, Any]:
        """Get UI statistics."""
        by_type: dict[str, int] = {}
        for component in self.components.values():
            comp_type = component.component_type.value
            by_type[comp_type] = by_type.get(comp_type, 0) + 1

        return {
            "total_components": len(self.components),
            "by_type": by_type,
            "current_view": self.current_view,
            "theme": self.theme,
            "mouse_enabled": self.mouse_enabled,
            "total_event_handlers": len(self.event_handlers),
        }

    def create_dashboard(
        self,
        name: str,
        title: str,
        widgets: list[str],
    ) -> UIComponent:
        """Create a dashboard with multiple widgets."""
        return self.register_component(
            name=name,
            component_type=UIComponentType.DASHBOARD,
            title=title,
            data={"widgets": widgets},
        )

    def create_table(
        self,
        name: str,
        title: str,
        columns: list[str],
        rows: list[dict[str, Any]],
    ) -> UIComponent:
        """Create a table component."""
        return self.register_component(
            name=name,
            component_type=UIComponentType.TABLE,
            title=title,
            data={"columns": columns, "rows": rows},
        )
