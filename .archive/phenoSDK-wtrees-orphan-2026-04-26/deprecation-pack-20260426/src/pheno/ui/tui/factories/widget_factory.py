"""
WidgetFactory - Dynamic widget creation system.

Provides template-based widget creation and factory pattern.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

try:
    from textual.widget import Widget

    HAS_TEXTUAL = True
except ImportError:
    HAS_TEXTUAL = False
    Widget = object


@dataclass
class WidgetTemplate:
    """
    Widget template definition.
    """

    widget_type: str
    config: dict[str, Any] = field(default_factory=dict)
    children: list = field(default_factory=list)
    style: dict[str, Any] = field(default_factory=dict)


class WidgetFactory:
    """Factory for creating widgets from templates.

    Features:
    - Template-based creation
    - Widget type registration
    - Configuration presets
    - Nested widget creation
    """

    def __init__(self):
        self._widget_types: dict[str, type[Widget]] = {}
        self._templates: dict[str, WidgetTemplate] = {}
        self._creators: dict[str, Callable] = {}

    def register_widget_type(self, name: str, widget_class: type[Widget]) -> None:
        """
        Register a widget type.
        """
        self._widget_types[name] = widget_class

    def register_template(self, name: str, template: WidgetTemplate) -> None:
        """
        Register a widget template.
        """
        self._templates[name] = template

    def register_creator(self, name: str, creator: Callable) -> None:
        """
        Register a custom widget creator function.
        """
        self._creators[name] = creator

    def create_from_template(self, template_name: str, **overrides) -> Widget | None:
        """
        Create widget from registered template.
        """
        if template_name not in self._templates:
            return None

        template = self._templates[template_name]

        # Merge template config with overrides
        config = {**template.config, **overrides}

        return self.create_widget(template.widget_type, **config)

    def create_widget(self, widget_type: str, **config) -> Widget | None:
        """
        Create widget by type name.
        """
        # Check for custom creator
        if widget_type in self._creators:
            return self._creators[widget_type](**config)

        # Check for registered type
        if widget_type not in self._widget_types:
            return None

        widget_class = self._widget_types[widget_type]

        try:
            return widget_class(**config)
        except Exception as e:
            print(f"Error creating widget {widget_type}: {e}")
            return None

    def create_from_dict(self, spec: dict[str, Any]) -> Widget | None:
        """
        Create widget from dictionary specification.
        """
        widget_type = spec.get("type")
        if not widget_type:
            return None

        config = spec.get("config", {})
        widget = self.create_widget(widget_type, **config)

        if not widget:
            return None

        # Apply styles
        if "style" in spec:
            for key, value in spec["style"].items():
                try:
                    setattr(widget.styles, key, value)
                except Exception as e:
                    print(f"Error applying style {key}: {e}")

        # Create children
        if "children" in spec:
            for child_spec in spec["children"]:
                child = self.create_from_dict(child_spec)
                if child:
                    try:
                        widget.mount(child)
                    except Exception as e:
                        print(f"Error mounting child: {e}")

        return widget

    def create_preset(self, preset_name: str) -> Widget | None:
        """
        Create widget from preset configuration.
        """
        presets = {
            "log_viewer": {
                "type": "LogViewer",
                "config": {"max_entries": 1000, "auto_scroll": True, "show_stats": True},
            },
            "progress_widget": {
                "type": "ProgressWidget",
                "config": {"show_individual": True, "show_summary": True, "compact": False},
            },
            "metrics_table": {
                "type": "MetricsTable",
                "config": {"auto_refresh": True, "show_sparklines": True, "show_trends": True},
            },
            "status_dashboard": {"type": "StatusDashboard", "config": {"update_interval": 5.0}},
        }

        if preset_name not in presets:
            return None

        return self.create_from_dict(presets[preset_name])


# Global factory instance
_widget_factory = WidgetFactory()


def get_widget_factory() -> WidgetFactory:
    """
    Get global widget factory instance.
    """
    return _widget_factory


def create_widget(widget_type: str, **config) -> Widget | None:
    """
    Convenience function to create widget.
    """
    return _widget_factory.create_widget(widget_type, **config)
