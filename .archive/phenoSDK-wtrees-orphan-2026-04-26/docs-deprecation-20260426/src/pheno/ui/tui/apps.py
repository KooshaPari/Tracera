"""
Factory helpers for building preconfigured TUI applications.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .themes import DarkTheme, LightTheme, ThemeManager, get_theme_manager
from .widgets import (
    LogViewer,
    OAuthStatusWidget,
    ProgressWidget,
    ResourceStatusWidget,
    ServerStatusWidget,
    StatusDashboard,
)

if TYPE_CHECKING:
    from collections.abc import Iterable


def _apply_theme(theme: str) -> None:
    manager: ThemeManager = get_theme_manager()
    if theme == "dark":
        manager.set_theme(DarkTheme())
    elif theme == "light":
        manager.set_theme(LightTheme())


def create_tui_app(
    title: str = "TUI App",
    subtitle: str = "",
    theme: str = "dark",
    widgets: Iterable | None = None,
    layout: str = "vertical",
    bindings: list | None = None,
    **kwargs,
):
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Grid, Horizontal, Vertical
        from textual.widgets import Footer, Header, Static, TabbedContent, TabPane
    except ImportError as exc:  # pragma: no cover - runtime guard
        raise ImportError("Textual is required for create_tui_app") from exc

    widgets = list(widgets or [])
    bindings = bindings or [("q", "quit", "Quit")]

    class GeneratedApp(App):
        BINDINGS = bindings

        def __init__(self, **app_kwargs):
            merged = {**kwargs, **app_kwargs}
            super().__init__(**merged)
            self.title = title
            self.sub_title = subtitle
            _apply_theme(theme)

        def compose(self) -> ComposeResult:  # type: ignore[override]
            yield Header(show_clock=True)

            if not widgets:
                yield Static("No widgets provided")
            elif layout == "vertical":
                with Vertical():
                    for widget in widgets:
                        yield widget
            elif layout == "horizontal":
                with Horizontal():
                    for widget in widgets:
                        yield widget
            elif layout == "grid":
                with Grid():
                    for widget in widgets:
                        yield widget
            elif layout == "tabbed":
                with TabbedContent():
                    for index, widget in enumerate(widgets, start=1):
                        tab_name = getattr(widget, "name", f"Tab {index}")
                        with TabPane(tab_name):
                            yield widget
            else:
                with Vertical():
                    for widget in widgets:
                        yield widget

            yield Footer()

    return GeneratedApp


def create_status_app(
    title: str = "Status Dashboard",
    update_interval: float = 5.0,
    show_oauth: bool = True,
    show_server: bool = True,
    show_resources: bool = True,
    **kwargs,
):
    widgets: list = []
    if show_oauth or show_server or show_resources:
        widgets.append(StatusDashboard(update_interval=update_interval))
    else:
        if show_oauth:
            widgets.append(OAuthStatusWidget())
        if show_server:
            widgets.append(ServerStatusWidget())
        if show_resources:
            widgets.append(ResourceStatusWidget())

    return create_tui_app(
        title=title,
        layout="vertical",
        widgets=widgets,
        bindings=[
            ("q", "quit", "Quit"),
            ("r", "refresh", "Refresh"),
            ("space", "toggle_pause", "Pause/Resume"),
        ],
        **kwargs,
    )


def create_progress_app(
    title: str = "Progress Monitor",
    show_individual: bool = True,
    show_summary: bool = True,
    with_logs: bool = True,
    **kwargs,
):
    widgets: list = []
    widgets.append(
        ProgressWidget(
            show_individual=show_individual,
            show_summary=show_summary,
            compact=False,
        ),
    )

    if with_logs:
        widgets.append(
            LogViewer(
                max_entries=1000,
                auto_scroll=True,
                show_stats=True,
            ),
        )

    layout = "horizontal" if with_logs else "vertical"

    return create_tui_app(
        title=title,
        layout=layout,
        widgets=widgets,
        bindings=[
            ("q", "quit", "Quit"),
            ("c", "clear_logs", "Clear Logs") if with_logs else ("r", "refresh", "Refresh"),
            ("p", "pause", "Pause"),
        ],
        **kwargs,
    )


def create_log_viewer_app(
    title: str = "Log Viewer",
    max_entries: int = 1000,
    auto_scroll: bool = True,
    show_stats: bool = True,
    **kwargs,
):
    viewer = LogViewer(max_entries=max_entries, auto_scroll=auto_scroll, show_stats=show_stats)
    return create_tui_app(
        title=title,
        widgets=[viewer],
        layout="vertical",
        bindings=[
            ("q", "quit", "Quit"),
            ("c", "clear_logs", "Clear Logs"),
            ("f", "filter", "Filter"),
        ],
        **kwargs,
    )


__all__ = [
    "create_log_viewer_app",
    "create_progress_app",
    "create_status_app",
    "create_tui_app",
]
